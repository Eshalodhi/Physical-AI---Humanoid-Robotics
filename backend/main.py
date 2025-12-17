"""
RAG Ingestion Pipeline - Hackathon Edition
Local file-based ingestion from MDX/MD source files

Run: uv run python main.py
"""

import os
import re
import hashlib
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import cohere
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import tiktoken

# ============================================================
# CONFIGURATION
# ============================================================

# Path to book docs relative to this script
BOOK_DOCS_PATH = "../book/docs"

# File extensions to process
FILE_EXTENSIONS = [".md", ".mdx"]

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    id: int
    content: str
    title: str
    section: str
    file_path: str
    module: str
    chunk_index: int
    token_count: int
    embedding: Optional[list[float]] = None


# ============================================================
# FUNCTIONS
# ============================================================

def get_all_local_files(base_path: str) -> list[Path]:
    """Recursively find all .md and .mdx files in the docs directory."""
    base = Path(base_path)
    if not base.exists():
        print(f"[ERROR] Directory not found: {base.absolute()}")
        return []

    files = []
    for ext in FILE_EXTENSIONS:
        files.extend(base.rglob(f"*{ext}"))

    # Sort by path for consistent ordering
    files.sort(key=lambda p: str(p))
    return files


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from MDX/MD content."""
    frontmatter = {}
    body = content

    # Check for frontmatter (starts with ---)
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_content = parts[1].strip()
            body = parts[2].strip()

            # Parse simple key: value pairs
            for line in fm_content.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    frontmatter[key] = value

    return frontmatter, body


def extract_first_heading(content: str) -> Optional[str]:
    """Extract the first H1 or H2 heading from content."""
    # Match # Heading or ## Heading
    match = re.search(r'^#{1,2}\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def determine_module(file_path: Path) -> str:
    """Determine module from file path."""
    parts = file_path.parts

    # Look for module folders in path
    for part in parts:
        if part.startswith("module") or part in ["intro", "introduction"]:
            return part

    # Check parent folder
    if len(parts) >= 2:
        return parts[-2]

    return "general"


def extract_text_from_file(file_path: Path) -> tuple[str, dict]:
    """Read file content and extract metadata."""
    content = file_path.read_text(encoding="utf-8")

    # Extract frontmatter
    frontmatter, body = extract_frontmatter(content)

    # Determine title (priority: frontmatter > first heading > filename)
    title = frontmatter.get("title") or frontmatter.get("sidebar_label")
    if not title:
        title = extract_first_heading(body)
    if not title:
        title = file_path.stem.replace("-", " ").replace("_", " ").title()

    # Determine section from frontmatter or parent folder
    section = frontmatter.get("sidebar_position", "")
    if section:
        section = f"Section {section}"
    else:
        section = file_path.parent.name.replace("-", " ").title()

    # Determine module
    module = determine_module(file_path)

    # Clean the body text
    # Remove import statements (MDX)
    body = re.sub(r'^import\s+.*$', '', body, flags=re.MULTILINE)
    # Remove JSX components (basic cleanup)
    body = re.sub(r'<[A-Z][^>]*>.*?</[A-Z][^>]*>', '', body, flags=re.DOTALL)
    body = re.sub(r'<[A-Z][^/>]*/>', '', body)
    # Remove HTML comments
    body = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL)
    # Clean up extra whitespace
    body = re.sub(r'\n{3,}', '\n\n', body)
    body = body.strip()

    metadata = {
        "title": title,
        "section": section,
        "module": module,
        "file_path": str(file_path),
    }

    return body, metadata


def chunk_text(text: str, metadata: dict, target_size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Split text into overlapping chunks."""
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)

    # Skip if text is too short
    if len(tokens) < 50:
        return []

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(tokens):
        # Get chunk tokens
        end = min(start + target_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.decode(chunk_tokens)

        # Generate deterministic ID (convert to int for Qdrant)
        hash_hex = hashlib.sha256(
            f"{metadata['file_path']}:{chunk_index}:{chunk_text[:50]}".encode()
        ).hexdigest()[:16]
        chunk_id = int(hash_hex, 16)  # Convert hex to unsigned int

        chunks.append(Chunk(
            id=chunk_id,
            content=chunk_text,
            title=metadata["title"],
            section=metadata.get("section", "Main"),
            file_path=metadata["file_path"],
            module=metadata["module"],
            chunk_index=chunk_index,
            token_count=len(chunk_tokens),
        ))

        # Move with overlap
        start = end - overlap
        chunk_index += 1

        # Prevent infinite loop on small remaining text
        if start >= len(tokens) - overlap:
            break

    return chunks


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


def create_collection(client: QdrantClient, name: str, dim: int = 1024) -> None:
    """Create Qdrant collection if not exists."""
    collections = [c.name for c in client.get_collections().collections]

    if name not in collections:
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        print(f"  Created collection '{name}'")
    else:
        print(f"  Collection '{name}' already exists")


def save_chunks_to_qdrant(chunks: list[Chunk], client: QdrantClient, collection: str) -> int:
    """Upsert chunks with embeddings to Qdrant."""
    points = [
        PointStruct(
            id=chunk.id,
            vector=chunk.embedding,
            payload={
                "content": chunk.content,
                "title": chunk.title,
                "section": chunk.section,
                "file_path": chunk.file_path,
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
        print(f"    Upserted batch {i // batch_size + 1}: {len(batch)} points")

    return len(points)


def test_search(query: str, qdrant_client: QdrantClient, cohere_client: cohere.Client, collection: str):
    """Test search with a sample query."""
    # Embed query
    response = cohere_client.embed(
        texts=[query],
        model="embed-english-v3.0",
        input_type="search_query",
    )
    query_vector = response.embeddings[0]

    # Search (use query method for newer qdrant-client versions)
    results = qdrant_client.query_points(
        collection_name=collection,
        query=query_vector,
        limit=3,
    ).points

    print(f"\n[SEARCH] Query: '{query}'")
    print("-" * 50)
    for i, r in enumerate(results, 1):
        score = r.score if r.score else 0.0
        payload = r.payload or {}
        print(f"  {i}. [{score:.3f}] {payload.get('title', 'Unknown')}")
        print(f"     Module: {payload.get('module', 'Unknown')}")
        content = payload.get('content', '')[:150]
        print(f"     {content}...")
        print()


def main():
    """Run the full ingestion pipeline."""
    print("=" * 60)
    print("RAG INGESTION PIPELINE - LOCAL FILE MODE")
    print("=" * 60)

    # 1. Load configuration
    load_dotenv()
    config = {
        "cohere_key": os.getenv("COHERE_API_KEY"),
        "qdrant_url": os.getenv("QDRANT_URL"),
        "qdrant_key": os.getenv("QDRANT_API_KEY"),
        "collection": os.getenv("QDRANT_COLLECTION", "hackathon"),
    }

    # Validate config
    missing = [k for k, v in config.items() if not v]
    if missing:
        print(f"\n[ERROR] Missing environment variables: {', '.join(missing)}")
        print("   Please check your .env file")
        return

    print("\n[OK] Configuration loaded")

    # 2. Initialize clients
    cohere_client = cohere.Client(config["cohere_key"])
    qdrant_client = QdrantClient(url=config["qdrant_url"], api_key=config["qdrant_key"])
    print("[OK] Clients initialized")

    # 3. Create collection
    print("\n[SETUP] Setting up Qdrant collection...")
    create_collection(qdrant_client, config["collection"])

    # 4. Get all local files
    script_dir = Path(__file__).parent
    docs_path = script_dir / BOOK_DOCS_PATH
    files = get_all_local_files(docs_path)

    if not files:
        print(f"\n[ERROR] No .md or .mdx files found in {docs_path.absolute()}")
        print("   Make sure the book/docs directory exists with content")
        return

    print(f"\n[INFO] Found {len(files)} files to process")

    # 5. Process each file
    all_chunks = []
    failed_files = []

    for i, file_path in enumerate(files, 1):
        rel_path = file_path.relative_to(docs_path) if docs_path in file_path.parents or docs_path == file_path.parent else file_path.name
        print(f"\n[{i}/{len(files)}] Processing: {rel_path}")

        try:
            text, metadata = extract_text_from_file(file_path)
            if not text.strip():
                print("  [WARN] No content extracted, skipping")
                continue

            chunks = chunk_text(text, metadata)
            if chunks:
                all_chunks.extend(chunks)
                print(f"  [OK] '{metadata['title']}' -> {len(chunks)} chunks ({len(text)} chars)")
            else:
                print("  [WARN] Text too short for chunking, skipping")

        except Exception as e:
            print(f"  [FAIL] Error: {e}")
            failed_files.append(str(file_path))
            continue

    print(f"\n[INFO] Total chunks: {len(all_chunks)}")

    if not all_chunks:
        print("\n[ERROR] No chunks to process. Check your docs directory.")
        return

    # 6. Generate embeddings
    print("\n[EMBED] Generating embeddings...")
    texts = [c.content for c in all_chunks]
    embeddings = embed_texts(texts, cohere_client)

    # Attach embeddings to chunks
    for chunk, embedding in zip(all_chunks, embeddings):
        chunk.embedding = embedding

    # 7. Save to Qdrant
    print("\n[SAVE] Saving to Qdrant...")
    saved = save_chunks_to_qdrant(all_chunks, qdrant_client, config["collection"])

    # 8. Summary
    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    print(f"  Files processed: {len(files) - len(failed_files)}/{len(files)}")
    print(f"  Chunks created:  {len(all_chunks)}")
    print(f"  Vectors stored:  {saved}")
    print(f"  Collection:      {config['collection']}")

    if failed_files:
        print(f"\n  [WARN] Failed files ({len(failed_files)}):")
        for f in failed_files[:5]:
            print(f"    - {f}")
        if len(failed_files) > 5:
            print(f"    ... and {len(failed_files) - 5} more")

    print("=" * 60)

    # 9. Test search
    print("\n[TEST] Running sample search...")
    test_search("What is ROS 2?", qdrant_client, cohere_client, config["collection"])


if __name__ == "__main__":
    main()
