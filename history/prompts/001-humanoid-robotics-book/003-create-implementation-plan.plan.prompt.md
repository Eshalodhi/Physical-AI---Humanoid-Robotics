---
id: 003
title: Create Implementation Plan for Book
stage: plan
date: 2025-12-15
surface: agent
model: claude-opus-4-5-20251101
feature: 001-humanoid-robotics-book
branch: 001-humanoid-robotics-book
user: user
command: /sp.plan
labels: ["plan", "architecture", "docusaurus", "rag-chatbot", "implementation"]
links:
  spec: specs/001-humanoid-robotics-book/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-humanoid-robotics-book/plan.md
  - specs/001-humanoid-robotics-book/research.md
  - specs/001-humanoid-robotics-book/data-model.md
  - specs/001-humanoid-robotics-book/quickstart.md
  - specs/001-humanoid-robotics-book/contracts/chatbot-api.yaml
tests:
  - null
---

## Prompt

/sp.plan

User requested comprehensive implementation plan with:
- Architecture Sketch: Component diagram showing Docusaurus, chatbot widget, FastAPI backend, Qdrant, Neon, OpenAI
- Section Structure: Phase 0 Research, Phase 1 Foundation, Phase 2 Content Modules, Phase 3 Chatbot Integration, Phase 4 Deployment
- Research Approach: Research-concurrent strategy (research during chapter writing)
- Quality Validation: Build success, navigation checks, search validation, Lighthouse score, chatbot accuracy
- Decisions to Document: Theme selection, chatbot embedding, chunking strategy, simulation platform selection, pricing approach
- Testing Strategy: Per-chapter code validation in Ubuntu 22.04, RAG chatbot test suite (40 queries)
- Phase Organization: Four phases with clear dependencies and deliverables

## Response snapshot

Created comprehensive implementation plan with 6 artifacts:

**plan.md** - Full implementation plan including:
- Technical Context (languages, dependencies, storage, testing)
- Constitution Check (5 principles validated PASS)
- Project Structure (documentation + source code layouts)
- Architecture Diagram (Mermaid flowchart)
- Component Responsibilities table
- 5 Architectural Decision Records (ADR-001 to ADR-005)
- Research approach with primary/secondary sources
- Quality validation checklists (chapter-level and book-level)
- Testing strategy (per-chapter, chatbot, deployment)
- 4 Implementation phases with dependencies

**research.md** - 8 architectural decisions documented:
- D-001: SSG Selection (Docusaurus 3.x)
- D-002: RAG Architecture (FastAPI + managed services)
- D-003: Content Chunking (semantic by section, 500 tokens, 50 overlap)
- D-004: Chatbot Widget (custom React component)
- D-005: Simulation Platform (Gazebo primary, Isaac Sim advanced)
- D-006: ROS 2 Distribution (Humble LTS)
- D-007: Code Testing Environment (Docker Ubuntu 22.04)
- D-008: Citation Management (APA format, per-chapter references)

**data-model.md** - Entity models including:
- Content Domain: Module, Chapter, Section, CodeExample, Citation, ModuleProject, GlossaryTerm, HardwareOption
- Chatbot Domain: ChatbotQuery, ChatbotResponse, ContentChunk, ChatSession, EmbeddingJob
- Postgres schema (6 tables with indexes)
- Qdrant collection schema

**contracts/chatbot-api.yaml** - OpenAPI 3.1 specification:
- /chat/query (POST) - Submit questions
- /chat/feedback (POST) - User feedback
- /sessions CRUD endpoints
- /health and /health/ready probes
- /admin/reindex for content updates
- Full request/response schemas

**quickstart.md** - Development setup guide:
- Prerequisites (Node.js, Python, Docker, API keys)
- Repository setup instructions
- Three running options (Full Stack, Book Only, Docker Compose)
- Development workflows (writing content, testing, embedding updates)
- Project structure overview
- Common commands reference
- Troubleshooting section

## Outcome

- Impact: Complete implementation blueprint for Physical AI book with all architectural decisions documented
- Tests: N/A (planning phase)
- Files: plan.md, research.md, data-model.md, quickstart.md, contracts/chatbot-api.yaml
- Next prompts: /sp.tasks to generate implementation tasks, /sp.adr for significant decisions
- Reflection: Research-concurrent approach validated against constitution principles; all 5 pass

## Evaluation notes (flywheel)

- Failure modes observed: PowerShell command format required adjustment (pwsh vs powershell.exe)
- Graders run and results (PASS/FAIL): Constitution Check PASS (5/5 principles)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
