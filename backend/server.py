"""
RAG Query Server - FastAPI Backend
Serves the chatbot widget with semantic search over the book content.

Run: uv run uvicorn server:app --reload --port 8000
"""

import os
from typing import Optional
from contextlib import asynccontextmanager

import cohere
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient


# =============================================================================
# Configuration
# =============================================================================

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "hackathon")

# Validate config
if not all([COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY]):
    raise ValueError("Missing required environment variables. Check .env file.")


# =============================================================================
# Clients (initialized on startup)
# =============================================================================

cohere_client: Optional[cohere.Client] = None
qdrant_client: Optional[QdrantClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize clients on startup, cleanup on shutdown."""
    global cohere_client, qdrant_client

    print("[STARTUP] Initializing clients...")
    cohere_client = cohere.Client(COHERE_API_KEY)
    qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    # Verify collection exists
    collections = [c.name for c in qdrant_client.get_collections().collections]
    if QDRANT_COLLECTION not in collections:
        print(f"[WARNING] Collection '{QDRANT_COLLECTION}' not found. Run main.py first to ingest data.")
    else:
        print(f"[OK] Connected to collection '{QDRANT_COLLECTION}'")

    print("[OK] Server ready!")
    yield

    print("[SHUTDOWN] Cleaning up...")


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="RAG Query API",
    description="Semantic search API for Physical AI & Humanoid Robotics Book",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        # Add your production domain here
        # "https://your-username.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Request/Response Models
# =============================================================================

class QueryRequest(BaseModel):
    """Request model for /query endpoint."""
    query: str
    top_k: int = 5


class QuerySelectedTextRequest(BaseModel):
    """Request model for /query-selected-text endpoint."""
    selected_text: str
    question: str
    top_k: int = 5


class Source(BaseModel):
    """A source document from the search results."""
    title: str
    module: str
    content: str
    score: float
    file_path: Optional[str] = None


class QueryResponse(BaseModel):
    """Response model for query endpoints."""
    answer: str
    sources: list[Source]
    query: str


# =============================================================================
# Helper Functions
# =============================================================================

def clean_text(text: str) -> str:
    """
    Clean MDX/JSX/HTML content to produce readable plain text.

    Aggressively removes all code artifacts and boilerplate for clean, readable prose.
    """
    import re

    if not text:
        return ""

    # Remove frontmatter (--- ... ---)
    text = re.sub(r'^---[\s\S]*?---\n*', '', text, flags=re.MULTILINE)

    # Remove import statements
    text = re.sub(r'^import\s+.*$', '', text, flags=re.MULTILINE)

    # Remove Python docstrings (triple quotes)
    text = re.sub(r'"""[\s\S]*?"""', '', text)
    text = re.sub(r"'''[\s\S]*?'''", '', text)

    # Remove boilerplate sections - learning objectives, prerequisites, etc.
    # Match "By the end of..." blocks up to next substantive paragraph
    text = re.sub(r'By the end of this[^P]*?(?=Physical AI|The |This |In |For |$)', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'Before starting this[^P]*?(?=Physical AI|The |This |In |For |$)', '', text, flags=re.IGNORECASE | re.DOTALL)

    # Remove any remaining individual boilerplate lines
    lines = text.split('\n')
    cleaned_lines = []
    skip_patterns = [
        'By the end of this',
        'Before starting this',
        'you will be able to',
        'ensure you have',
        'Background:',
        'Curiosity:',
        'Mindset:',
        'Basic understanding',
        'Interest in robotics',
        'Readiness to think',
        'Define Physical AI',
        'Explain why embodiment',
        'Identify the key',
        'Understand the convergence',
        # More patterns for chapter intros
        'Software:',
        'Hardware:',
        'Module:',
        'Completed Module',
        'GPU recommended',
        'ROS 2 Humble installed',
        'Ubuntu 22.04',
        # Bullet-style learning objectives
        'Launch basic',
        'Configure world',
        'Set up and configure',
        'Work with',
        'Connect',
        # More prerequisites and objectives
        'Knowledge:',
        'Familiarity with',
        'Describe the',
        'Basic Linux',
        'Real-time |',  # Table rows
        '| Limited |',
        '| Supported |',
        # Timeline entries
        ': ROS',
        'Becomes Industry',
        'Development Begins',
        'First Release',
        # More learning objectives
        'Compare RT-',
        'Choose appropriate',
        'Chapter:',
        'Transformer architecture',
        'GPU with',
        'VRAM',
        'Plugins Services',
        'FUSE TR HEAD',
        # Code-like content
        'imagesize:',
        'numactions:',
        'int =',
    ]
    for line in lines:
        line_stripped = line.strip()
        # Skip empty lines
        if not line_stripped:
            continue
        # Strip markdown from line for better pattern matching
        line_clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', line_stripped)  # **bold**
        line_clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', line_clean)  # [text](url)
        line_clean = re.sub(r'^[\s\-\*]+', '', line_clean)  # Leading bullets
        # Skip lines matching skip patterns (check both raw and cleaned)
        if any(pattern.lower() in line_clean.lower() for pattern in skip_patterns):
            continue
        if any(pattern.lower() in line_stripped.lower() for pattern in skip_patterns):
            continue
        # Skip lines that are just bullet points with learning objective verbs
        if re.match(r'^[•\-\*\s]*(Define|Explain|Identify|Understand|Install|Configure|Launch|Create|Build|Implement|Set up|Work with)\s', line_stripped, re.IGNORECASE):
            continue
        # Skip very short lines (likely artifacts)
        if len(line_stripped) < 20 and not line_stripped.endswith('.'):
            continue
        cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)

    # Remove MDX admonitions completely
    text = re.sub(r':::\w+[\s\S]*?:::', '', text)
    text = re.sub(r':::.*', '', text)

    # Remove ALL code blocks including partial/unclosed ones
    text = re.sub(r'```mermaid[\s\S]*?```', '', text)
    text = re.sub(r'```\w*[\s\S]*?```', '', text)
    # Remove unclosed code blocks (start of block to end of text)
    text = re.sub(r'```\w*[\s\S]*$', '', text)
    # Remove orphaned code block content (subgraph, flowchart, etc.)
    text = re.sub(r'\bsubgraph\s+\w+\[.*?\]', '', text)
    text = re.sub(r'\bflowchart\s+\w+', '', text)
    text = re.sub(r'\bend\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'-->', '', text)
    text = re.sub(r'<-->', '', text)

    # Remove mermaid/diagram artifacts
    text = re.sub(r'\[diagram\]', '', text)
    text = re.sub(r'\[code\]', '', text)
    text = re.sub(r'\[code example\]', '', text)
    text = re.sub(r'\[configuration example\]', '', text)

    # Remove all HTML/JSX tags
    text = re.sub(r'<[^>]+/?>', '', text)
    text = re.sub(r'</\w+>', '', text)

    # Remove HTML comments
    text = re.sub(r'<!--[\s\S]*?-->', '', text)

    # Remove JSX artifacts
    text = re.sub(r'\bclassName\s*=\s*["\'][^"\']*["\']', '', text)
    text = re.sub(r'\bstyle\s*=\s*\{[^}]*\}', '', text)
    text = re.sub(r'title="[^"]*"', '', text)

    # Remove code-like patterns and Mermaid diagram syntax
    text = re.sub(r'\w+\[\w+:.*?\]', '', text)  # Node1["label"]
    text = re.sub(r'\w+\[[^\]]+\]', '', text)   # Any[text in brackets]
    text = re.sub(r'P\d+\[.*?\]', '', text)     # P1[Publisher: ...]
    text = re.sub(r'S\d+\[.*?\]', '', text)     # S1[Subscriber: ...]
    text = re.sub(r'A[CS]\[.*?\]', '', text)    # AC[Action Client: ...]
    text = re.sub(r'[A-Z]{2,}\[[^\]]*$', '', text, flags=re.MULTILINE)  # Unclosed brackets like AS[Action...
    text = re.sub(r'\w+_\w+\s*=\s*\w+', '', text)  # variable_name = value

    # Remove shell commands
    text = re.sub(r'^sudo\s+apt\s+install.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^ros2\s+launch.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^ros2\s+run.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'ros-humble-\S+', '', text)  # Package names
    text = re.sub(r'\\\s*$', '', text, flags=re.MULTILINE)  # Line continuations

    # Remove Python/code syntax
    text = re.sub(r'from\s+\w+(\.\w+)*\s+import\s+.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*#.*$', '', text, flags=re.MULTILINE)  # Python comments
    text = re.sub(r'\bdef\s+\w+\(.*?\):', '', text)
    text = re.sub(r'\bclass\s+\w+.*?:', '', text)
    text = re.sub(r'\bpass\b', '', text)  # Remove 'pass' statements
    text = re.sub(r'\breturn\s+\w+', '', text)  # Remove return statements
    text = re.sub(r'\bself\.\w*', '', text)  # Remove self. references
    text = re.sub(r'\bfor\s+\w+\s+in\s+range\(.*?\)', '', text)  # for loops
    text = re.sub(r'\.ModuleList\(.*?\)', '', text)  # PyTorch
    text = re.sub(r'FiLMLayer\([^)]*\)', '', text)  # Specific function calls
    text = re.sub(r'\w+dim\b', '', text)  # hiddendim, embeddim, etc.
    text = re.sub(r'\bnum_\w+', '', text)  # num_layers, num_heads, etc.

    # Clean markdown tables - remove any lines with multiple pipe separators
    text = re.sub(r'\|[-:]+\|[-:|\s]+\|', '', text)  # Table header separator
    # Remove lines containing 2+ pipe characters (table rows)
    lines = text.split('\n')
    text = '\n'.join(line for line in lines if line.count('|') < 2)

    # Remove markdown formatting but keep text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)    # Images
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)  # Headers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)        # Inline code

    # Clean lists - convert to simple text
    text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)

    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)

    # Remove orphaned brackets and special chars
    text = re.sub(r'\[\]', '', text)
    text = re.sub(r'\(\)', '', text)
    text = re.sub(r'\{\}', '', text)
    text = re.sub(r'[<>]', '', text)

    # Remove single characters on their own lines (diagram node labels)
    text = re.sub(r'^\s*[A-Z]\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

    # Clean whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = '\n'.join(line.strip() for line in text.split('\n'))
    text = re.sub(r'^\s*\n', '', text, flags=re.MULTILINE)  # Remove empty lines

    # Final cleanup
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'\n\n+', '\n\n', text)
    text = text.strip()

    return text


def embed_query(text: str) -> list[float]:
    """Generate embedding for a query using Cohere."""
    response = cohere_client.embed(
        texts=[text],
        model="embed-english-v3.0",
        input_type="search_query",
    )
    return response.embeddings[0]


def search_qdrant(query_vector: list[float], top_k: int = 5) -> list[dict]:
    """Search Qdrant for similar documents. Returns cleaned content for display."""
    results = qdrant_client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
    ).points

    sources = []
    for r in results:
        payload = r.payload or {}
        raw_content = payload.get("content", "")

        # Clean the content for readable display
        cleaned_content = clean_text(raw_content)

        sources.append({
            "title": payload.get("title", "Unknown"),
            "module": payload.get("module", "unknown"),
            "content": cleaned_content,  # Cleaned for display
            "score": r.score or 0.0,
            "file_path": payload.get("file_path", ""),
        })

    return sources


def extract_relevant_content(content: str, query: str) -> str:
    """Extract the most relevant paragraph(s) from content based on query terms."""
    if not content:
        return ""

    # Split into paragraphs
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

    if not paragraphs:
        return content

    # Simple keyword matching to find most relevant paragraphs
    query_terms = set(query.lower().split())
    scored_paragraphs = []

    for para in paragraphs:
        # Skip very short paragraphs
        if len(para) < 50:
            continue

        para_lower = para.lower()
        score = sum(1 for term in query_terms if term in para_lower)

        # Bonus for paragraphs that look like definitions or explanations
        if any(phrase in para_lower for phrase in ['refers to', 'is a', 'means', 'defined as', 'the key']):
            score += 2

        scored_paragraphs.append((score, para))

    if not scored_paragraphs:
        return content[:800] if len(content) > 800 else content

    # Sort by score and take top paragraphs
    scored_paragraphs.sort(key=lambda x: x[0], reverse=True)

    # Build answer from top-scoring paragraphs
    result = []
    total_len = 0
    for score, para in scored_paragraphs:
        if total_len + len(para) > 1000:
            break
        result.append(para)
        total_len += len(para)

    return '\n\n'.join(result) if result else scored_paragraphs[0][1]


def generate_answer(query: str, sources: list[dict], context: str = None) -> str:
    """Generate a clean, readable answer from the retrieved sources.

    Note: For full generative answers, upgrade to Cohere paid plan and use command-r-plus.
    This free-tier version returns the most relevant content directly.
    """
    if not sources:
        return "I couldn't find relevant information for your question in the book."

    # Get the best matching source (content is already cleaned by search_qdrant)
    best_source = sources[0]
    content = best_source['content']

    # Extract the most relevant paragraphs
    content = extract_relevant_content(content, query)

    # Truncate to reasonable length for answer
    if len(content) > 1200:
        # Try to break at sentence boundary
        truncated = content[:1200]
        last_period = truncated.rfind('.')
        if last_period > 600:
            content = truncated[:last_period + 1]
        else:
            content = truncated + "..."

    # Build a helpful response
    answer_parts = []

    if context:
        answer_parts.append("Regarding your question about the selected text:\n\n")

    # Add the main content
    answer_parts.append(content)

    # Add references to other sources if available
    if len(sources) > 1:
        other_titles = list(set(s['title'] for s in sources[1:3] if s['title'] != best_source['title']))
        if other_titles:
            answer_parts.append(f"\n\n---\n**Related chapters:** {', '.join(other_titles)}")

    return "".join(answer_parts)


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "RAG Query API",
        "collection": QDRANT_COLLECTION,
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    try:
        # Check Qdrant connection
        collections = qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]

        return {
            "status": "healthy",
            "qdrant": "connected",
            "cohere": "configured",
            "collection": QDRANT_COLLECTION,
            "collection_exists": QDRANT_COLLECTION in collection_names,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Search the knowledge base and generate an answer.

    This endpoint:
    1. Embeds the query using Cohere
    2. Searches Qdrant for similar documents
    3. Generates an answer using the retrieved context
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        # 1. Embed the query
        query_vector = embed_query(request.query)

        # 2. Search for relevant documents
        sources = search_qdrant(query_vector, request.top_k)

        if not sources:
            return QueryResponse(
                answer="I couldn't find any relevant information in the book for your question.",
                sources=[],
                query=request.query,
            )

        # 3. Generate answer
        answer = generate_answer(request.query, sources)

        return QueryResponse(
            answer=answer,
            sources=[Source(**s) for s in sources],
            query=request.query,
        )

    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/query-selected-text", response_model=QueryResponse)
async def query_selected_text(request: QuerySelectedTextRequest):
    """
    Answer a question about selected text from the book.

    This endpoint:
    1. Combines the selected text with the question for context
    2. Searches for related content in the knowledge base
    3. Generates an answer considering both the selection and retrieved context
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if not request.selected_text.strip():
        raise HTTPException(status_code=400, detail="Selected text cannot be empty")

    try:
        # Create a combined query for better search results
        combined_query = f"{request.question} {request.selected_text[:200]}"

        # 1. Embed the combined query
        query_vector = embed_query(combined_query)

        # 2. Search for relevant documents
        sources = search_qdrant(query_vector, request.top_k)

        # 3. Generate answer with selected text as additional context
        answer = generate_answer(
            request.question,
            sources,
            context=request.selected_text[:1000]
        )

        return QueryResponse(
            answer=answer,
            sources=[Source(**s) for s in sources],
            query=request.question,
        )

    except Exception as e:
        print(f"[ERROR] Query-selected-text failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


# =============================================================================
# Run with: uv run uvicorn server:app --reload --port 8000
# =============================================================================
