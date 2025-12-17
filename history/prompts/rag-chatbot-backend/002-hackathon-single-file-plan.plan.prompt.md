---
id: 002
title: Hackathon Single-File Implementation Plan
stage: plan
date: 2025-12-16
surface: agent
model: claude-opus-4-5-20251101
feature: rag-chatbot-backend
branch: master
user: Esha Khan
command: /sp.plan
labels: ["planning", "hackathon", "single-file", "cohere", "qdrant", "ingestion"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - specs/rag-chatbot-backend/plan.md
tests:
  - N/A (planning phase)
---

## Prompt

/sp.plan

You are strictly following Spec-Kit Plus methodology for this deliverable.

Project Context:
- Book is complete in sibling directory ../book/, deployed on GitHub Pages
- All book content is accessible via public URLs
- Frontend and ../book/ directory must remain 100% untouched
- This backend is a standalone service

Deliverable #2 Requirements (must be fully satisfied):
- RAG chatbot backend using FastAPI, Qdrant Cloud Free Tier, Neon Serverless Postgres, OpenAI/Cohere for embeddings
- Dual modes: global retrieval + selected-text only
- Strict grounding, source citations, chat logging

NEW TECHNICAL DECISIONS (must be followed exactly):

Implementation must be in a SINGLE file: main.py (for hackathon-style simplicity and speed)

Required features in main.py:
- Initialize project with **uv** as the package manager (uv init, uv add, etc.)
- Set up both **Cohere** client and **Qdrant** client
- Fetch deployed book pages from live URLs (not local files)
- Clean extracted HTML/text (remove navigation, headers, footers, code blocks if needed)
- Chunk text intelligently (300–800 tokens, with overlap)
- Generate embeddings using Cohere (preferred) or fallback to OpenAI
- Create Qdrant collection if not exists (collection name: "hackathon")
- Upsert chunks into Qdrant with rich metadata (title/chapter, section, url, chunk_index)
- Save nothing locally except .env and main.py

## Response snapshot

Created hackathon-style implementation plan at `specs/rag-chatbot-backend/plan.md`:

**Key Changes from Previous Plan:**
- Single file: `main.py` only (~260 lines)
- No FastAPI server (pure ingestion script)
- Removed app/, services/, routers/, models/ directories
- Focus on URL-based content fetching

**Architecture:**
```
main.py: get_all_urls() → extract_text() → chunk_text() → embed() → save_to_qdrant()
```

**Functions Defined:**
1. `load_config()` - Load .env
2. `get_all_urls()` - Return 27 book page URLs
3. `extract_text_from_url()` - Fetch + clean HTML
4. `chunk_text()` - Split into 300-800 token chunks
5. `embed_texts()` - Cohere batch embedding
6. `create_collection()` - Qdrant setup
7. `save_chunks_to_qdrant()` - Upsert with payload
8. `main()` - Orchestrate pipeline

**File Structure:**
```
backend/
├── main.py         # ALL code here
├── .env            # API keys
├── .env.example    # Template
├── pyproject.toml  # uv config
└── uv.lock         # auto-generated
```

## Outcome

- ✅ Impact: Complete hackathon-style plan ready for immediate implementation
- 🧪 Tests: N/A (planning phase)
- 📁 Files: specs/rag-chatbot-backend/plan.md updated
- 🔁 Next prompts: Implement main.py directly or run /sp.tasks for checklist
- 🧠 Reflection: Simplified from multi-file to single-file approach per user request

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Implement main.py and test with real book URLs
