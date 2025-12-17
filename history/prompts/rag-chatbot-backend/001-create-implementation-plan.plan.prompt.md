---
id: 001
title: Create RAG Backend Implementation Plan
stage: plan
date: 2025-12-16
surface: agent
model: claude-opus-4-5-20251101
feature: rag-chatbot-backend
branch: master
user: Esha Khan
command: /sp.plan
labels: ["planning", "architecture", "rag", "cohere", "qdrant"]
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

You are strictly following Spec-Kit Plus methodology.

Project Context:
- The book is complete and built with Docusaurus in the sibling directory ../book/
- The published book is deployed and accessible via public URLs (GitHub Pages)
- The Markdown/MDX source files in ../book/docs/ remain the single source of truth, but ingestion may also use rendered deployed pages if needed
- All files in ../book/ must remain completely untouched

Deliverable #2: Integrated RAG Chatbot Backend (FastAPI-based)

Critical Constitution Rules:
- Never modify or suggest changes to any files in ../book/
- Never generate frontend code or integration instructions
- All work happens exclusively in the current backend directory

New Specific Implementation Requirements (must be included in the plan):
- Initialize the project using **uv** as the package manager (uv pip, uv venv, etc.)
- Set up official clients for **Cohere** (for embeddings) and **Qdrant**
- Fetch book content by crawling the deployed GitHub Pages URLs (provide a list of URLs or sitemap-based discovery)
- Clean the fetched HTML (remove navigation, headers, footers, scripts, etc.) to extract pure content
- Chunk the cleaned text (target 300–800 tokens, ~500 average, with overlap)
- Generate embeddings using **Cohere** (preferred model: embed-english-v3.0 or similar)
- Upsert vectors into Qdrant Cloud Free Tier with rich metadata (title/chapter, section, source URL, chunk index)
- Save/store chunks and metadata appropriately (payload in Qdrant + optional mirror in Neon Postgres)
- Final ingestion flow must be executable via a main function/script (e.g., python ingest.py or direct __main__ block)

Core Requirements (unchanged):
- FastAPI backend with endpoints: POST /ingest, /query, /query-selected-text
- Dual modes: Global (vector retrieval from Qdrant) and Selected-text (no retrieval)
- Use Cohere for embeddings, OpenAI for generation (gpt-4o-mini or similar)
- Neon Serverless Postgres for metadata mirroring and chat logging
- Strict grounding: answer only from context; fallback message "This information is not available in the book."
- Include source citations (chapter/section/source URL) in global responses

## Response snapshot

Created comprehensive implementation plan at `specs/rag-chatbot-backend/plan.md` covering:

1. **Architecture Overview**: Dual pipeline diagram (ingestion + query)
2. **Project Setup**: uv package manager initialization steps
3. **URL List**: 25+ book page URLs organized by module
4. **HTML Cleaning**: BeautifulSoup selectors for Docusaurus structure
5. **Chunking Strategy**: 100-800 token range with 50-token overlap
6. **Cohere Integration**: embed-english-v3.0 (1024 dimensions)
7. **Qdrant Setup**: Collection config, payload structure
8. **Postgres Schema**: Updated tables with source_url, module fields
9. **6-Phase Task Breakdown**: Setup → Services → Updates → API → Testing → Deploy
10. **Deployment Options**: Render, Railway, Fly.io configurations
11. **Acceptance Criteria**: 8 functional + 6 non-functional requirements

## Outcome

- ✅ Impact: Complete plan ready for task generation and implementation
- 🧪 Tests: N/A (planning phase)
- 📁 Files: specs/rag-chatbot-backend/plan.md created
- 🔁 Next prompts: /sp.tasks to generate detailed task breakdown
- 🧠 Reflection: Plan captures all new requirements (uv, Cohere, URL crawling) while preserving existing FastAPI structure

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Execute plan and validate URL fetching works with actual deployed book
