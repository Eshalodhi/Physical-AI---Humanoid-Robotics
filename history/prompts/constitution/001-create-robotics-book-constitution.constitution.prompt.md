---
id: 001
title: Create Robotics Book Constitution
stage: constitution
date: 2025-12-15
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["constitution", "physical-ai", "robotics", "docusaurus", "rag-chatbot"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

/sp.constitution

Project: Physical AI & Humanoid Robotics – A Hands-On Guide to Embodied Intelligence

Core principles:

* Accuracy through verification against official documentation and established tools
* Clarity for a technical audience (students and developers with AI, Python, and computer science background)
* Reproducibility (all code examples, simulations, and hardware configurations must be executable with clear setup instructions)
* Rigor (prioritize official sources, open-source repositories, and peer-reviewed works on embodied AI and robotics)
* Practicality (focus on accessible hardware tiers and cloud alternatives to lower barriers to entry)

Key standards:

* All technical claims, commands, and configurations must be traceable to primary sources (e.g., ROS 2 documentation, NVIDIA Isaac developer guides, official hardware specs)
* Citation format: APA style for academic references; inline links and code comments for tools and repositories
* Source types: minimum 60% from official documentation and trusted open-source projects (ROS.org, docs.nvidia.com, GitHub repos of tools used)
* Plagiarism check: 0% tolerance; all written content must be original, with proper attribution for quoted material
* Writing clarity: Flesch-Kincaid grade level 12–14; define technical terms on first use and include glossaries where needed
* Code standards: Python 3.10+, ROS 2 Humble/Iron conventions, modular design, comprehensive comments, error handling, and reproducible setup via requirements.txt or Colcon
* Book format: Docusaurus-compatible Markdown/MDX files with frontmatter, embedded runnable code blocks (where possible), diagrams (Mermaid or external images), and interactive elements
* Visuals: Include clear diagrams, screenshots, and photos of hardware setups with proper captions and sources

Constraints:

* Structure: Introduction + 4 core modules (matching the quarter outline) + Capstone Project + Appendices (hardware options, troubleshooting, resources)
* Minimum sources: 25 (official docs, research papers on VLA/embodied AI, hardware datasheets, open-source examples)
* Total content: Equivalent to 150–250 pages when rendered (detailed tutorials with code and explanations)
* Deployment: Fully functional Docusaurus site hosted on GitHub Pages
* Integrated RAG chatbot: Embedded in the published book using OpenAI Agents/ChatKit SDKs, FastAPI backend, Neon Serverless Postgres for metadata/storage, Qdrant Cloud Free Tier for vector embeddings; must support queries on entire book content and on user-selected text only
* Hardware recommendations: Cover budget-friendly (Jetson + proxy robots), mid-tier, and premium options; always include cloud-based alternatives for simulation-heavy work

Success criteria:

* Book successfully builds and deploys to GitHub Pages with working navigation, search, and responsive design
* All code examples are reproducible in the specified environments (Ubuntu 22.04, ROS 2 Humble, NVIDIA Isaac Sim where applicable)
* RAG chatbot is fully embedded, passes tests for accuracy on book content, and correctly handles scoped queries on selected text
* Zero unverified technical claims or undetected plagiarism
* Content achieves educational goals: readers can progress from ROS 2 basics to building a voice-controlled simulated (or real) humanoid robot
* Passes internal technical review for completeness, clarity, and hands-on value

## Response snapshot

Created constitution v1.0.0 for "Physical AI & Humanoid Robotics – A Hands-On Guide to Embodied Intelligence" project. Constitution includes:

- 5 Core Principles: Accuracy Through Verification, Clarity for Technical Audience, Reproducibility (NON-NEGOTIABLE), Rigor in Source Selection, Practicality and Accessibility
- Key Standards: Code standards (Python 3.10+, ROS 2), Content format (Docusaurus MDX), Citation standards (APA)
- Constraints: Structure requirements, Technical infrastructure (GitHub Pages, RAG chatbot with FastAPI/Neon/Qdrant)
- Success Criteria: Deployment, Reproducibility, RAG Chatbot, Content Quality, Educational outcomes
- Governance: Authority, Amendment process (semantic versioning), Compliance verification

Templates validated for compatibility: plan-template.md, spec-template.md, tasks-template.md all align with constitution structure.

## Outcome

- Impact: Established project governance and quality standards for robotics book
- Tests: N/A (constitution document)
- Files: .specify/memory/constitution.md (created)
- Next prompts: /sp.specify to begin first feature specification
- Reflection: User provided comprehensive requirements; all translated to testable MUST statements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
