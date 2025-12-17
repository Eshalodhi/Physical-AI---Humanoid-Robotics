<!--
SYNC IMPACT REPORT
==================
Version change: (new) → 1.0.0
Modified principles: N/A (initial creation)
Added sections:
  - Core Principles (5 principles)
  - Key Standards
  - Constraints
  - Success Criteria
  - Governance
Removed sections: N/A
Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ Compatible (Constitution Check section exists)
  - .specify/templates/spec-template.md: ✅ Compatible (Requirements section aligns)
  - .specify/templates/tasks-template.md: ✅ Compatible (Phase structure aligns)
Follow-up TODOs: None
-->

# Physical AI & Humanoid Robotics Constitution

A Hands-On Guide to Embodied Intelligence

## Core Principles

### I. Accuracy Through Verification

All technical content MUST be verified against official documentation and established tools before inclusion. This principle is NON-NEGOTIABLE.

- Every technical claim, command, and configuration MUST be traceable to primary sources
- Primary sources include: ROS 2 documentation, NVIDIA Isaac developer guides, official hardware specifications
- Internal knowledge or assumptions are NEVER sufficient; external verification is REQUIRED
- When verification is not possible, content MUST be flagged with `[NEEDS VERIFICATION]`

### II. Clarity for Technical Audience

Content MUST be written for students and developers with backgrounds in AI, Python, and computer science.

- Writing clarity: Flesch-Kincaid grade level 12–14
- Technical terms MUST be defined on first use
- Glossaries MUST be included where needed
- Explanations MUST assume familiarity with programming concepts but not domain-specific robotics knowledge
- Complex concepts MUST include diagrams, examples, or both

### III. Reproducibility (NON-NEGOTIABLE)

All code examples, simulations, and hardware configurations MUST be executable with clear setup instructions.

- Every code block MUST be tested in the specified environment before publication
- Target environments: Ubuntu 22.04, ROS 2 Humble/Iron, NVIDIA Isaac Sim (where applicable)
- Setup instructions MUST include: dependencies, environment variables, system requirements
- Reproducibility MUST be validated via `requirements.txt` or Colcon workspace configurations
- If a code example cannot be made reproducible, it MUST NOT be included

### IV. Rigor in Source Selection

Content MUST prioritize official sources, open-source repositories, and peer-reviewed works on embodied AI and robotics.

- Minimum 60% of sources MUST be from official documentation and trusted open-source projects
- Trusted sources: ROS.org, docs.nvidia.com, GitHub repos of tools used, peer-reviewed papers
- Citation format: APA style for academic references; inline links and code comments for tools/repositories
- Minimum 25 sources required across the complete work
- Plagiarism tolerance: 0% — all written content MUST be original with proper attribution

### V. Practicality and Accessibility

Content MUST focus on accessible hardware tiers and cloud alternatives to lower barriers to entry.

- Hardware recommendations MUST cover three tiers:
  - Budget-friendly: Jetson + proxy robots
  - Mid-tier: Standard development setups
  - Premium: Full humanoid platforms
- Cloud-based alternatives MUST be provided for simulation-heavy work
- Cost considerations MUST be explicitly stated for hardware recommendations
- Readers MUST be able to progress from basics to advanced topics using any tier

## Key Standards

### Code Standards

- **Language**: Python 3.10+
- **Framework**: ROS 2 Humble/Iron conventions
- **Design**: Modular architecture with clear separation of concerns
- **Documentation**: Comprehensive comments explaining "why" not just "what"
- **Error Handling**: Explicit error handling with meaningful messages
- **Dependencies**: Managed via `requirements.txt` or Colcon

### Content Format

- **File Format**: Docusaurus-compatible Markdown/MDX files with frontmatter
- **Code Blocks**: Embedded runnable code blocks where possible
- **Diagrams**: Mermaid syntax preferred; external images with proper captions and sources
- **Interactive Elements**: Include where they enhance learning
- **Visuals**: Clear diagrams, screenshots, and photos of hardware setups with captions

### Citation Standards

- Academic references: APA style
- Tool/repository references: Inline links with code comments
- All quoted material MUST have proper attribution
- Source verification MUST be documented

## Constraints

### Structure Requirements

- **Organization**: Introduction + 4 core modules (matching quarter outline) + Capstone Project + Appendices
- **Appendices**: Hardware options, troubleshooting, resources
- **Total Content**: Equivalent to 150–250 pages when rendered
- **Navigation**: Logical progression from ROS 2 basics to voice-controlled humanoid robot

### Technical Infrastructure

- **Deployment**: Fully functional Docusaurus site hosted on GitHub Pages
- **Search**: Working site-wide search functionality
- **Design**: Responsive design for multiple device types

### RAG Chatbot Requirements

- **SDK**: OpenAI Agents/ChatKit SDKs
- **Backend**: FastAPI
- **Database**: Neon Serverless Postgres for metadata/storage
- **Vector Store**: Qdrant Cloud Free Tier for embeddings
- **Capabilities**:
  - Query entire book content
  - Query user-selected text only (scoped queries)
  - Accuracy validation on book content

## Success Criteria

### Deployment Criteria

- [ ] Book successfully builds and deploys to GitHub Pages
- [ ] Navigation functions correctly across all sections
- [ ] Search returns relevant results
- [ ] Responsive design works on desktop, tablet, and mobile

### Reproducibility Criteria

- [ ] All code examples execute successfully in Ubuntu 22.04
- [ ] ROS 2 Humble examples work as documented
- [ ] NVIDIA Isaac Sim examples function where applicable
- [ ] Setup instructions are complete and accurate

### RAG Chatbot Criteria

- [ ] Chatbot is embedded and accessible from published book
- [ ] Full-content queries return accurate, relevant responses
- [ ] Scoped queries (selected text) function correctly
- [ ] Response accuracy passes validation tests

### Content Quality Criteria

- [ ] Zero unverified technical claims
- [ ] Zero undetected plagiarism
- [ ] All sources properly cited (minimum 25)
- [ ] Flesch-Kincaid grade level 12–14 maintained

### Educational Criteria

- [ ] Readers can progress from ROS 2 basics to advanced topics
- [ ] Capstone project (voice-controlled simulated/real humanoid robot) is achievable
- [ ] Content passes internal technical review for completeness, clarity, and hands-on value

## Governance

### Authority

This Constitution supersedes all other project practices. All contributions, reviews, and decisions MUST verify compliance with these principles.

### Amendment Process

1. Proposed amendments MUST be documented with rationale
2. Amendments require review against existing content for impact assessment
3. Breaking changes require migration plan
4. All amendments MUST update the version number per semantic versioning:
   - **MAJOR**: Backward-incompatible principle changes or removals
   - **MINOR**: New principles/sections added or materially expanded
   - **PATCH**: Clarifications, wording fixes, non-semantic refinements

### Compliance Verification

- All pull requests MUST pass Constitution compliance check
- Technical claims MUST include source references
- Code examples MUST include reproduction verification
- Content complexity MUST be justified against Principle V (Practicality)

### Review Expectations

- Technical accuracy review against official documentation
- Reproducibility validation in target environments
- Citation completeness check
- Accessibility assessment for all hardware tiers

**Version**: 1.0.0 | **Ratified**: 2025-12-15 | **Last Amended**: 2025-12-15
