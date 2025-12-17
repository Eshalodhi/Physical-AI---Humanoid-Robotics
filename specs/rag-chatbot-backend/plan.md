# Implementation Plan: RAG Ingestion Pipeline (Hackathon Edition)

**Branch**: `feature/rag-ingestion` | **Date**: 2025-12-16 | **Spec**: Deliverable #2
**Style**: Single-file hackathon implementation

---

## Goal

Build a **single-file RAG ingestion pipeline** (`main.py`) that:
1. Fetches all deployed book pages from GitHub Pages URLs
2. Cleans HTML to extract pure text content
3. Chunks text intelligently (300-800 tokens with overlap)
4. Generates embeddings using Cohere
5. Upserts vectors into Qdrant Cloud with rich metadata

**No FastAPI server** in this version — pure ingestion script for hackathon demo.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     main.py - Single File                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐              │
│  │ get_all_   │──▶│ extract_   │──▶│ chunk_     │              │
│  │ urls()     │   │ text()     │   │ text()     │              │
│  └────────────┘   └────────────┘   └────────────┘              │
│        │                │                │                      │
│        │                │                ▼                      │
│        │                │         ┌────────────┐               │
│        │                │         │  embed()   │               │
│        │                │         │  (Cohere)  │               │
│        │                │         └────────────┘               │
│        │                │                │                      │
│        │                │                ▼                      │
│        │                │         ┌────────────┐               │
│        │                │         │ save_to_   │               │
│        │                │         │ qdrant()   │               │
│        │                │         └────────────┘               │
│        │                │                                       │
│        ▼                ▼                                       │
│  ┌─────────────────────────────────────────────┐               │
│  │              __main__ block                  │               │
│  │  1. Load .env                               │               │
│  │  2. Create Qdrant collection                │               │
│  │  3. For each URL: fetch → clean → chunk     │               │
│  │  4. Batch embed all chunks                  │               │
│  │  5. Upsert to Qdrant                        │               │
│  │  6. Print summary                           │               │
│  └─────────────────────────────────────────────┘               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

External Services:
┌────────────┐    ┌────────────┐    ┌────────────┐
│  GitHub    │    │  Cohere    │    │  Qdrant    │
│  Pages     │    │  API       │    │  Cloud     │
│  (URLs)    │    │ (embed)    │    │ (vectors)  │
└────────────┘    └────────────┘    └────────────┘
```

---

## File Structure

```
backend/
├── main.py              # Single-file ingestion pipeline (ALL CODE HERE)
├── .env                 # API keys (gitignored)
├── .env.example         # Template for required keys
├── pyproject.toml       # uv project config
└── uv.lock              # uv lockfile (auto-generated)
```

**That's it.** No app/, no services/, no routers/. One file.

---

## Book URLs to Fetch

Base URL: `https://{username}.github.io/physical-ai-robotics-book/docs/`

```python
BOOK_URLS = [
    # Introduction
    "intro/",
    "intro/01-foundations",
    "intro/02-digital-to-physical",
    "intro/03-humanoid-landscape",
    "intro/04-sensor-systems",

    # Module 1: ROS 2
    "module1-ros2/01-architecture",
    "module1-ros2/02-nodes-topics",
    "module1-ros2/03-python-packages",
    "module1-ros2/04-launch-files",
    "module1-ros2/05-urdf",
    "module1-ros2/06-python-agents",

    # Module 2: Simulation
    "module2-simulation/01-gazebo-setup",
    "module2-simulation/02-urdf-sdf",
    "module2-simulation/03-physics",
    "module2-simulation/04-sensors",
    "module2-simulation/05-unity",
    "module2-simulation/06-environments",

    # Module 3: NVIDIA Isaac
    "module3-isaac/01-isaac-overview",
    "module3-isaac/02-synthetic-data",
    "module3-isaac/03-perception",
    "module3-isaac/04-nav2",
    "module3-isaac/05-rl-basics",
    "module3-isaac/06-sim-to-real",

    # Module 4: VLA
    "module4-vla/01-foundation-models",
    "module4-vla/02-vla-architectures",
    "module4-vla/03-fine-tuning",
    "module4-vla/04-deployment",
    "module4-vla/05-advanced-topics",
]
```

**Total: ~27 pages**

---

## Implementation Tasks

### Phase 1: Project Setup with uv

| # | Task | Command/Action | Output |
|---|------|----------------|--------|
| 1.1 | Clean backend directory | Remove old app/ folder, keep only essentials | Clean slate |
| 1.2 | Initialize uv project | `uv init --name rag-pipeline` | pyproject.toml |
| 1.3 | Add dependencies | `uv add cohere qdrant-client httpx beautifulsoup4 tiktoken python-dotenv` | uv.lock |
| 1.4 | Create .env.example | Template with all required keys | .env.example |
| 1.5 | Create .env from template | Copy and fill in real keys | .env |

### Phase 2: Implement main.py Functions

| # | Function | Purpose | Lines |
|---|----------|---------|-------|
| 2.1 | `load_config()` | Load .env, return settings dict | ~15 |
| 2.2 | `get_all_urls()` | Return list of full book URLs | ~20 |
| 2.3 | `extract_text_from_url(url)` | Fetch HTML, clean, return text + metadata | ~50 |
| 2.4 | `chunk_text(text, metadata)` | Split into 300-800 token chunks with overlap | ~60 |
| 2.5 | `embed_texts(texts)` | Batch embed using Cohere | ~20 |
| 2.6 | `create_collection()` | Create Qdrant collection if not exists | ~25 |
| 2.7 | `save_chunks_to_qdrant(chunks, embeddings)` | Upsert with payload | ~30 |
| 2.8 | `main()` | Orchestrate full pipeline | ~40 |

**Estimated total: ~260 lines**

### Phase 3: Testing & Verification

| # | Test | Expected Result |
|---|------|-----------------|
| 3.1 | Run `python main.py` | Full pipeline executes |
| 3.2 | Check Qdrant dashboard | Collection "hackathon" with vectors |
| 3.3 | Verify chunk count | ~100-200 chunks total |
| 3.4 | Test search manually | Relevant results for sample query |

---

## Dependencies

```toml
# pyproject.toml
[project]
name = "rag-pipeline"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "cohere>=5.0.0",
    "qdrant-client>=1.7.0",
    "httpx>=0.26.0",
    "beautifulsoup4>=4.12.0",
    "tiktoken>=0.5.0",
    "python-dotenv>=1.0.0",
]
```

---

## Environment Variables

```bash
# .env.example

# Cohere API (for embeddings)
COHERE_API_KEY=your-cohere-api-key

# Qdrant Cloud
QDRANT_URL=https://xxx.region.cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION=hackathon

# Book Configuration
BOOK_BASE_URL=https://username.github.io/physical-ai-robotics-book/docs/

# Optional: OpenAI fallback
OPENAI_API_KEY=sk-your-openai-key
```

---

## main.py Structure

```python
"""
RAG Ingestion Pipeline - Hackathon Edition
Single-file implementation for Physical AI Book

Run: uv run python main.py
"""

import os
import hashlib
from typing import Optional
from dataclasses import dataclass

import cohere
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import tiktoken

# ============================================================
# CONFIGURATION
# ============================================================

BOOK_URLS = [...]  # Full list of page paths

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class Chunk:
    id: str
    content: str
    title: str
    section: str
    url: str
    module: str
    chunk_index: int
    token_count: int
    embedding: Optional[list[float]] = None

# ============================================================
# FUNCTIONS
# ============================================================

def load_config() -> dict:
    """Load environment variables."""
    ...

def get_all_urls(base_url: str) -> list[str]:
    """Generate full URLs for all book pages."""
    ...

def extract_text_from_url(url: str) -> tuple[str, dict]:
    """Fetch URL, clean HTML, extract text and metadata."""
    ...

def chunk_text(text: str, metadata: dict) -> list[Chunk]:
    """Split text into overlapping chunks."""
    ...

def embed_texts(texts: list[str], client: cohere.Client) -> list[list[float]]:
    """Generate embeddings using Cohere."""
    ...

def create_collection(client: QdrantClient, name: str, dim: int) -> None:
    """Create Qdrant collection if not exists."""
    ...

def save_chunks_to_qdrant(chunks: list[Chunk], client: QdrantClient, collection: str) -> int:
    """Upsert chunks with embeddings to Qdrant."""
    ...

def main():
    """Run the full ingestion pipeline."""
    ...

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
```

---

## HTML Cleaning Strategy

### Elements to Remove (Docusaurus-specific)

```python
REMOVE_SELECTORS = [
    "nav",
    "header",
    "footer",
    ".navbar",
    ".menu",
    ".sidebar",
    ".pagination-nav",
    ".table-of-contents",
    ".theme-doc-breadcrumbs",
    ".theme-doc-footer",
    ".theme-edit-this-page",
    "script",
    "style",
    "noscript",
    ".hash-link",
    "[aria-hidden='true']",
]
```

### Content Extraction

```python
def extract_text_from_url(url: str) -> tuple[str, dict]:
    # Fetch page
    response = httpx.get(url, timeout=30, follow_redirects=True)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove unwanted elements
    for selector in REMOVE_SELECTORS:
        for element in soup.select(selector):
            element.decompose()

    # Extract main content
    article = soup.select_one("article") or soup.select_one("main")

    # Get title
    title = soup.select_one("h1")
    title_text = title.get_text(strip=True) if title else "Unknown"

    # Extract text
    text = article.get_text(separator="\n", strip=True) if article else ""

    # Determine module from URL
    module = url.split("/docs/")[1].split("/")[0] if "/docs/" in url else "unknown"

    return text, {
        "title": title_text,
        "url": url,
        "module": module,
    }
```

---

## Chunking Algorithm

```python
def chunk_text(text: str, metadata: dict, target_size: int = 500, overlap: int = 50) -> list[Chunk]:
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(tokens):
        # Get chunk tokens
        end = min(start + target_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.decode(chunk_tokens)

        # Generate deterministic ID
        chunk_id = hashlib.sha256(
            f"{metadata['url']}:{chunk_index}:{chunk_text[:50]}".encode()
        ).hexdigest()[:16]

        chunks.append(Chunk(
            id=chunk_id,
            content=chunk_text,
            title=metadata["title"],
            section=metadata.get("section", "Main"),
            url=metadata["url"],
            module=metadata["module"],
            chunk_index=chunk_index,
            token_count=len(chunk_tokens),
        ))

        # Move with overlap
        start = end - overlap
        chunk_index += 1

        # Prevent infinite loop on small remaining text
        if start >= len(tokens) - 50:
            break

    return chunks
```

---

## Cohere Embedding

```python
def embed_texts(texts: list[str], client: cohere.Client) -> list[list[float]]:
    """Batch embed texts using Cohere."""
    print(f"  Embedding {len(texts)} chunks...")

    # Cohere allows up to 96 texts per batch
    batch_size = 96
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embed(
            texts=batch,
            model="embed-english-v3.0",
            input_type="search_document",
            truncate="END",
        )
        all_embeddings.extend(response.embeddings)
        print(f"    Batch {i // batch_size + 1}: {len(batch)} texts embedded")

    return all_embeddings
```

**Cohere embed-english-v3.0**: 1024 dimensions

---

## Qdrant Operations

```python
def create_collection(client: QdrantClient, name: str, dim: int = 1024) -> None:
    """Create collection if not exists."""
    collections = [c.name for c in client.get_collections().collections]

    if name not in collections:
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        print(f"✓ Created collection '{name}'")
    else:
        print(f"✓ Collection '{name}' already exists")


def save_chunks_to_qdrant(chunks: list[Chunk], client: QdrantClient, collection: str) -> int:
    """Upsert chunks to Qdrant."""
    points = [
        PointStruct(
            id=chunk.id,
            vector=chunk.embedding,
            payload={
                "content": chunk.content,
                "title": chunk.title,
                "section": chunk.section,
                "url": chunk.url,
                "module": chunk.module,
                "chunk_index": chunk.chunk_index,
                "token_count": chunk.token_count,
            },
        )
        for chunk in chunks
        if chunk.embedding is not None
    ]

    # Upsert in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(collection_name=collection, points=batch)

    return len(points)
```

---

## Main Execution Block

```python
def main():
    """Run the full ingestion pipeline."""
    print("=" * 60)
    print("RAG INGESTION PIPELINE - HACKATHON EDITION")
    print("=" * 60)

    # 1. Load configuration
    load_dotenv()
    config = {
        "cohere_key": os.getenv("COHERE_API_KEY"),
        "qdrant_url": os.getenv("QDRANT_URL"),
        "qdrant_key": os.getenv("QDRANT_API_KEY"),
        "collection": os.getenv("QDRANT_COLLECTION", "hackathon"),
        "base_url": os.getenv("BOOK_BASE_URL"),
    }
    print("\n✓ Configuration loaded")

    # 2. Initialize clients
    cohere_client = cohere.Client(config["cohere_key"])
    qdrant_client = QdrantClient(url=config["qdrant_url"], api_key=config["qdrant_key"])
    print("✓ Clients initialized")

    # 3. Create collection
    create_collection(qdrant_client, config["collection"])

    # 4. Get all URLs
    urls = get_all_urls(config["base_url"])
    print(f"\n📚 Found {len(urls)} pages to process")

    # 5. Process each URL
    all_chunks = []
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url}")

        try:
            text, metadata = extract_text_from_url(url)
            if not text.strip():
                print("  ⚠ No content extracted, skipping")
                continue

            chunks = chunk_text(text, metadata)
            all_chunks.extend(chunks)
            print(f"  ✓ Extracted {len(chunks)} chunks")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue

    print(f"\n📦 Total chunks: {len(all_chunks)}")

    # 6. Generate embeddings
    print("\n🔢 Generating embeddings...")
    texts = [c.content for c in all_chunks]
    embeddings = embed_texts(texts, cohere_client)

    # Attach embeddings to chunks
    for chunk, embedding in zip(all_chunks, embeddings):
        chunk.embedding = embedding

    # 7. Save to Qdrant
    print("\n💾 Saving to Qdrant...")
    saved = save_chunks_to_qdrant(all_chunks, qdrant_client, config["collection"])

    # 8. Summary
    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    print(f"  Pages processed: {len(urls)}")
    print(f"  Chunks created:  {len(all_chunks)}")
    print(f"  Vectors stored:  {saved}")
    print(f"  Collection:      {config['collection']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

---

## Setup Commands (Copy-Paste Ready)

```bash
# Navigate to backend
cd backend

# Clean old files (keep .env if exists)
rm -rf app/ routers/ services/ models/ scripts/ tests/
rm -f requirements.txt README.md

# Initialize with uv
uv init --name rag-pipeline

# Add dependencies
uv add cohere qdrant-client httpx beautifulsoup4 tiktoken python-dotenv

# Create .env from example
cp .env.example .env
# Edit .env with your API keys

# Run the pipeline
uv run python main.py
```

---

## Verification Steps

### 1. Check Console Output

```
============================================================
RAG INGESTION PIPELINE - HACKATHON EDITION
============================================================

✓ Configuration loaded
✓ Clients initialized
✓ Created collection 'hackathon'

📚 Found 27 pages to process

[1/27] Processing: https://xxx.github.io/physical-ai-robotics-book/docs/intro/
  ✓ Extracted 3 chunks

[2/27] Processing: https://xxx.github.io/physical-ai-robotics-book/docs/intro/01-foundations
  ✓ Extracted 8 chunks
...

📦 Total chunks: 156

🔢 Generating embeddings...
    Batch 1: 96 texts embedded
    Batch 2: 60 texts embedded

💾 Saving to Qdrant...

============================================================
INGESTION COMPLETE
============================================================
  Pages processed: 27
  Chunks created:  156
  Vectors stored:  156
  Collection:      hackathon
============================================================
```

### 2. Check Qdrant Dashboard

1. Go to Qdrant Cloud dashboard
2. Find collection "hackathon"
3. Verify vector count matches output
4. Test a sample search query

### 3. Quick Search Test (add to main.py)

```python
def test_search(query: str, client: QdrantClient, cohere_client: cohere.Client, collection: str):
    """Test search with a sample query."""
    # Embed query
    response = cohere_client.embed(
        texts=[query],
        model="embed-english-v3.0",
        input_type="search_query",
    )
    query_vector = response.embeddings[0]

    # Search
    results = client.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=3,
    )

    print(f"\n🔍 Search: '{query}'")
    for i, r in enumerate(results, 1):
        print(f"  {i}. [{r.score:.3f}] {r.payload['title']} - {r.payload['url']}")
        print(f"     {r.payload['content'][:100]}...")
```

---

## Success Criteria

| # | Criterion | How to Verify |
|---|-----------|---------------|
| 1 | Single main.py file | `ls backend/` shows only main.py, .env, pyproject.toml |
| 2 | uv project works | `uv run python main.py` executes |
| 3 | All URLs fetched | Console shows 27 pages processed |
| 4 | Chunks created | ~100-200 chunks in output |
| 5 | Embeddings generated | No Cohere errors |
| 6 | Qdrant populated | Dashboard shows vectors in "hackathon" |
| 7 | Search works | Test query returns relevant results |
| 8 | No local storage | Only .env and main.py exist |

---

## Timeline Estimate

| Phase | Tasks | Effort |
|-------|-------|--------|
| Phase 1 | Setup | Quick |
| Phase 2 | main.py | Core work |
| Phase 3 | Testing | Verification |

---

## Next Steps After Plan Approval

1. Run `/sp.tasks` to generate task checklist
2. Execute Phase 1 setup commands
3. Implement main.py
4. Test and verify
5. Create PHR documenting the work

---

*This plan supersedes the previous multi-file implementation. Single-file, hackathon-style, maximum speed.*
