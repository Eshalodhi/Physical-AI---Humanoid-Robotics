# Tasks: RAG Ingestion Pipeline (Hackathon Edition)

**Input**: Design documents from `/specs/rag-chatbot-backend/`
**Prerequisites**: plan.md (required)

**Tests**: No tests requested - focusing on hackathon-speed implementation

**Organization**: Tasks organized by functional area for single-file implementation

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different concerns, no dependencies)
- Include exact file paths in descriptions
- All implementation happens in `backend/main.py`

## Path Conventions

- **Single file**: `backend/main.py` (all code)
- **Config**: `backend/.env`, `backend/.env.example`
- **Project**: `backend/pyproject.toml`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Clean slate and uv project setup

- [x] T001 Remove old multi-file structure from backend/ (rm -rf app/ scripts/ routers/ services/ models/)
- [x] T002 Remove old config files from backend/ (rm -f requirements.txt README.md)
- [x] T003 Initialize uv project with `uv init --name rag-pipeline` in backend/
- [x] T004 Add core dependencies with `uv add cohere qdrant-client httpx beautifulsoup4 tiktoken python-dotenv` in backend/
- [x] T005 [P] Create .env.example with COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION, BOOK_BASE_URL in backend/.env.example
- [x] T006 [P] Create .env from .env.example and fill with real API keys in backend/.env

**Checkpoint**: Clean backend/ with only pyproject.toml, uv.lock, .env.example, .env

---

## Phase 2: Foundational (main.py Skeleton)

**Purpose**: Create main.py with imports, constants, and Chunk dataclass

**⚠️ CRITICAL**: This establishes the single-file structure

- [x] T007 Create main.py with module docstring and all imports in backend/main.py
- [x] T008 Add BOOK_URLS constant list (27 page paths) in backend/main.py (adapted to local file mode: BOOK_DOCS_PATH, FILE_EXTENSIONS)
- [x] T009 Add REMOVE_SELECTORS constant list (Docusaurus cleanup selectors) in backend/main.py (adapted to MDX cleanup regex)
- [x] T010 Add Chunk dataclass with id, content, title, section, url, module, chunk_index, token_count, embedding fields in backend/main.py (adapted: file_path instead of url)

**Checkpoint**: main.py skeleton with imports, constants, and data structures ready

---

## Phase 3: URL & Fetch Functions

**Goal**: Implement URL generation and HTML fetching/cleaning

**Independent Test**: `get_all_local_files()` returns file paths; `extract_text_from_file()` returns clean text

- [x] T011 Implement `get_all_local_files(base_path: str) -> list[Path]` function in backend/main.py (adapted from URL mode)
- [x] T012 Implement `extract_text_from_file(file_path: Path) -> tuple[str, dict]` function with file reading in backend/main.py (adapted from URL mode)
- [x] T013 Add MDX/MD cleaning logic using regex patterns in backend/main.py (adapted: frontmatter extraction, JSX removal)
- [x] T014 Add metadata extraction (title from frontmatter/heading, module from path) in backend/main.py

**Checkpoint**: Can read and clean any local MDX/MD file

---

## Phase 4: Chunking Function

**Goal**: Implement text chunking with tiktoken

**Independent Test**: `chunk_text()` splits text into 300-800 token chunks with overlap

- [x] T015 Implement `chunk_text(text: str, metadata: dict, target_size: int = 500, overlap: int = 50) -> list[Chunk]` function in backend/main.py
- [x] T016 Add tiktoken tokenizer initialization (cl100k_base encoding) in backend/main.py
- [x] T017 Add deterministic chunk ID generation using hashlib.sha256 in backend/main.py (converted to int for Qdrant)
- [x] T018 Add chunk boundary handling and overlap logic in backend/main.py

**Checkpoint**: Can chunk any text into properly-sized pieces with metadata

---

## Phase 5: Embedding Function

**Goal**: Implement Cohere batch embedding

**Independent Test**: `embed_texts()` returns list of 1024-dim vectors

- [x] T019 Implement `embed_texts(texts: list[str], client: cohere.Client) -> list[list[float]]` function in backend/main.py
- [x] T020 Add batch processing logic (96 texts per Cohere API call) in backend/main.py
- [x] T021 Add progress printing for embedding batches in backend/main.py

**Checkpoint**: Can embed any list of texts using Cohere

---

## Phase 6: Qdrant Functions

**Goal**: Implement Qdrant collection creation and vector upsert

**Independent Test**: `create_collection()` creates "hackathon" collection; `save_chunks_to_qdrant()` upserts vectors

- [x] T022 Implement `create_collection(client: QdrantClient, name: str, dim: int = 1024) -> None` function in backend/main.py
- [x] T023 Add collection existence check before creation in backend/main.py
- [x] T024 Implement `save_chunks_to_qdrant(chunks: list[Chunk], client: QdrantClient, collection: str) -> int` function in backend/main.py
- [x] T025 Add batch upsert logic (100 points per batch) with rich payload in backend/main.py

**Checkpoint**: Can create Qdrant collection and store vectors with metadata

---

## Phase 7: Main Orchestration

**Goal**: Implement main() function that runs full pipeline

**Independent Test**: `python main.py` executes complete ingestion

- [x] T026 Implement `main()` function with configuration loading from .env in backend/main.py
- [x] T027 Add Cohere and Qdrant client initialization in main() in backend/main.py
- [x] T028 Add file processing loop with progress printing in backend/main.py (adapted from URL mode)
- [x] T029 Add embedding generation step calling embed_texts() in backend/main.py
- [x] T030 Add Qdrant save step calling save_chunks_to_qdrant() in backend/main.py
- [x] T031 Add summary printing (files, chunks, vectors, collection) in backend/main.py
- [x] T032 Add `if __name__ == "__main__": main()` entry point in backend/main.py

**Checkpoint**: Complete ingestion pipeline executable with `uv run python main.py`

---

## Phase 8: Search Test Function (Bonus)

**Goal**: Add optional search test function for verification

- [x] T033 [P] Implement `test_search(query: str, qdrant_client: QdrantClient, cohere_client: cohere.Client, collection: str)` function in backend/main.py
- [x] T034 [P] Add search test call in main() (enabled by default) in backend/main.py

**Checkpoint**: Can verify search works with sample query

---

## Phase 9: Polish & Verification

**Purpose**: Final cleanup and verification

- [x] T035 Verify backend/ contains only: main.py, .env, .env.example, pyproject.toml, uv.lock (plus .gitignore, .venv, .python-version)
- [x] T036 Run `uv run python main.py` and verify full pipeline execution (29 files, 203 chunks, 203 vectors)
- [x] T037 Check Qdrant Cloud dashboard for "hackathon" collection with vectors (verified: 203 vectors stored)
- [x] T038 Test sample search query to verify retrieval works (verified: "What is ROS 2?" returns relevant results)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Skeleton)**: Depends on Phase 1 completion
- **Phases 3-6 (Functions)**: Depend on Phase 2; can be implemented in any order
- **Phase 7 (Main)**: Depends on Phases 3-6 completion
- **Phase 8 (Search)**: Optional, can be done after Phase 7
- **Phase 9 (Polish)**: Depends on Phase 7 completion

### Task Dependencies Within Phases

```
Phase 1: T001 → T002 → T003 → T004 → [T005, T006 parallel]
Phase 2: T007 → T008 → T009 → T010
Phase 3: T011 → T012 → T013 → T014
Phase 4: T015 → T016 → T017 → T018
Phase 5: T019 → T020 → T021
Phase 6: T022 → T023 → T024 → T025
Phase 7: T026 → T027 → T028 → T029 → T030 → T031 → T032
Phase 8: [T033, T034 parallel]
Phase 9: T035 → T036 → T037 → T038
```

### Parallel Opportunities

Since this is a single-file implementation, most tasks are sequential within main.py. However:

- **Phase 1**: T005 and T006 can run in parallel (different files)
- **Phase 8**: T033 and T034 can be developed together
- **Phases 3-6**: Different developers could draft functions separately, then integrate

---

## Parallel Example: Phase 1

```bash
# After T004 completes, launch in parallel:
Task T005: "Create .env.example with API key placeholders"
Task T006: "Create .env with real API keys"
```

---

## Implementation Strategy

### Hackathon Speed (Recommended)

1. **Sprint 1**: Complete Phases 1-2 (Setup + Skeleton) - ~10 min
2. **Sprint 2**: Complete Phases 3-4 (Fetch + Chunk) - ~20 min
3. **Sprint 3**: Complete Phases 5-6 (Embed + Store) - ~15 min
4. **Sprint 4**: Complete Phase 7 (Main) - ~10 min
5. **Run and Demo**: Execute pipeline, check Qdrant dashboard

### Total Tasks: 38

| Phase | Task Count | Purpose |
|-------|------------|---------|
| Phase 1 | 6 | Setup |
| Phase 2 | 4 | Skeleton |
| Phase 3 | 4 | URL/Fetch |
| Phase 4 | 4 | Chunking |
| Phase 5 | 3 | Embedding |
| Phase 6 | 4 | Qdrant |
| Phase 7 | 7 | Main |
| Phase 8 | 2 | Search (bonus) |
| Phase 9 | 4 | Polish |

---

## Success Criteria

| # | Criterion | Verification Task |
|---|-----------|-------------------|
| 1 | Single main.py file | T035 |
| 2 | uv project works | T036 |
| 3 | All 27 URLs processed | T036 console output |
| 4 | ~100-200 chunks created | T036 console output |
| 5 | Embeddings generated | T036 no Cohere errors |
| 6 | Qdrant populated | T037 |
| 7 | Search works | T038 |
| 8 | No local storage | T035 |

---

## Notes

- All code goes in `backend/main.py` - no other Python files
- Use clear print statements for hackathon demo visibility
- Handle errors gracefully (skip failed URLs, don't crash)
- Deterministic chunk IDs enable re-running without duplicates
- Commit after each phase completion
