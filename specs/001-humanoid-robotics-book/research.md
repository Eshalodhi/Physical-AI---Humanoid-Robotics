# Research: Physical AI & Humanoid Robotics Book

**Feature**: 001-humanoid-robotics-book
**Date**: 2025-12-15
**Status**: Complete (Architectural Decisions Documented)

## Overview

This document captures research findings and architectural decisions for the Physical AI & Humanoid Robotics book project. Following the research-concurrent strategy, detailed technical research will occur during chapter writing. This phase documents key architectural decisions that must be made before implementation.

## Decision Log

### D-001: Static Site Generator Selection

**Question**: Which SSG should be used for the book?

**Decision**: Docusaurus 3.x

**Rationale**:
- Native React component support enables custom chatbot widget
- Built-in sidebar, search, versioning, and i18n features
- Excellent MDX support for interactive content
- Large active community with extensive plugin ecosystem
- Dark/light mode built-in
- Responsive design out-of-box

**Alternatives Considered**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Hugo | Fast builds, Go templates | No React, limited interactivity | Rejected |
| Jekyll | GitHub Pages native | Outdated, limited MDX | Rejected |
| Nextra | Next.js-based, modern | Smaller ecosystem | Considered |
| Docusaurus 3.x | React, full-featured | Heavier than Hugo | **Selected** |

**Sources**:
- Docusaurus docs: https://docusaurus.io/docs
- Comparison: https://jamstack.org/generators/

---

### D-002: RAG Architecture Pattern

**Question**: How should the RAG chatbot be architected?

**Decision**: Separate FastAPI backend with managed services

**Architecture**:
```
User Query → Chatbot Widget → FastAPI Backend
                                    ↓
                              Embedding (OpenAI)
                                    ↓
                              Retrieval (Qdrant)
                                    ↓
                              Generation (OpenAI)
                                    ↓
                              Response → Widget
```

**Rationale**:
- Separation of concerns: static site hosts content, API handles intelligence
- Managed services (Qdrant, Neon) reduce operational burden
- Free tiers available for all services
- Can scale backend independently of static site

**Component Responsibilities**:

| Component | Technology | Purpose |
|-----------|------------|---------|
| Vector Store | Qdrant Cloud | Store and query embeddings |
| Metadata DB | Neon Postgres | Sessions, analytics, chunk metadata |
| Embeddings | OpenAI text-embedding-3-small | Convert text to vectors |
| Generation | OpenAI GPT-4o-mini | Generate natural language responses |
| API | FastAPI | Route requests, orchestrate services |

**Sources**:
- Qdrant: https://qdrant.tech/documentation/
- Neon: https://neon.tech/docs
- OpenAI: https://platform.openai.com/docs

---

### D-003: Content Chunking Strategy

**Question**: How should book content be chunked for RAG retrieval?

**Decision**: Semantic chunking by section with overlap

**Strategy**:
- Primary boundary: H2/H3 headers (section breaks)
- Target chunk size: 400-600 tokens
- Overlap: 50 tokens between adjacent chunks
- Code blocks: Never split; treat as atomic units
- Metadata per chunk: chapter, section, type (text/code/diagram)

**Rationale**:
- Headers provide natural semantic boundaries
- Overlap ensures context continuity
- Code block integrity critical for accurate retrieval
- Metadata enables filtering and source attribution

**Implementation**:
```python
def chunk_mdx_content(content: str, max_tokens: int = 500):
    sections = split_by_headers(content)
    chunks = []
    for section in sections:
        if is_code_block(section):
            chunks.append(ChunkWithMetadata(section, type="code"))
        else:
            text_chunks = split_with_overlap(section, max_tokens, overlap=50)
            chunks.extend(text_chunks)
    return chunks
```

**Alternatives Rejected**:
- Fixed 512-token chunks: Risk splitting semantic units
- Full-chapter chunks: Too large, poor retrieval precision
- Sentence-level: Too granular, loses context

---

### D-004: Chatbot Widget Integration

**Question**: How should the chatbot be embedded in Docusaurus?

**Decision**: Custom React component with context awareness

**Features**:
- Floating widget accessible from all pages
- Text selection detection for scoped queries
- Theme-aware (follows Docusaurus dark/light mode)
- Persistent session across navigation
- Graceful degradation when backend unavailable

**Component Structure**:
```
src/components/ChatbotWidget/
├── index.tsx           # Main widget component
├── ChatWindow.tsx      # Message display area
├── MessageInput.tsx    # Query input with selection context
├── useTextSelection.ts # Hook for detecting selected text
└── styles.module.css   # Widget styling
```

**Rationale**:
- Custom component enables DOM access for text selection
- React integration seamless with Docusaurus
- Can use Docusaurus color mode context
- State management via React hooks or context

**Alternatives Rejected**:
- Iframe embed: Cannot access page content for scoped queries
- Third-party widget (Intercom, etc.): Less control, potential cost

---

### D-005: Simulation Platform Strategy

**Question**: Which simulation platform should be primary?

**Decision**: Gazebo primary, Isaac Sim for Module 3

**Strategy**:
- Modules 1-2: Gazebo Classic/Fortress (no GPU required)
- Module 3: Isaac Sim (RTX GPU required, cloud alternatives provided)
- Capstone: Supports both Gazebo and Isaac Sim paths

**Rationale**:
- Gazebo accessibility: Runs on any Linux system
- Isaac Sim value: Photorealistic rendering, synthetic data
- Cloud alternatives: NVIDIA Omniverse Cloud for RTX access
- Reader choice: Can complete book with either platform

**Environment Requirements**:

| Platform | CPU | GPU | RAM | Disk |
|----------|-----|-----|-----|------|
| Gazebo | Modern x86_64 | None required | 8GB+ | 20GB |
| Isaac Sim | Modern x86_64 | RTX 2070+ | 32GB+ | 100GB |
| Isaac Cloud | N/A | Cloud-provided | N/A | N/A |

**Sources**:
- Gazebo: https://gazebosim.org/docs
- Isaac Sim: https://docs.nvidia.com/isaac/doc/setup.html

---

### D-006: ROS 2 Distribution Selection

**Question**: Which ROS 2 distribution should be used?

**Decision**: ROS 2 Humble Hawksbill (LTS)

**Rationale**:
- Long-term support until 2027
- Most widely adopted ROS 2 release
- Best documentation and community support
- Compatible with Ubuntu 22.04 LTS
- Isaac ROS supports Humble

**Alternatives**:
- Iron Irwini: Newer but shorter support window
- Rolling: Bleeding edge, less stable for tutorials
- Foxy: EOL May 2023, outdated

**Sources**:
- ROS 2 releases: https://docs.ros.org/en/humble/Releases.html

---

### D-007: Code Example Testing Environment

**Question**: How should code examples be validated?

**Decision**: Docker-based Ubuntu 22.04 + ROS 2 Humble environment

**Approach**:
- Base image: `osrf/ros:humble-desktop-full`
- Per-module Dockerfile extending base with module dependencies
- CI validation via GitHub Actions
- Manual testing in VM for GPU-dependent examples

**Test Matrix**:

| Module | Docker | VM Required | Reason |
|--------|--------|-------------|--------|
| Intro | Yes | No | Conceptual content |
| Module 1 | Yes | No | ROS 2 only |
| Module 2 | Yes | Gazebo GUI | Gazebo simulation |
| Module 3 | No | Yes (RTX) | Isaac Sim |
| Module 4 | Yes | No | Python/API calls |
| Capstone | Partial | Yes | Full integration |

---

### D-008: Citation and Reference Management

**Question**: How should citations be managed across chapters?

**Decision**: Per-chapter references section with central bibliography

**Format**:
- Inline: Author (Year) for academic; [Link text](url) for tools
- End of chapter: Full APA citations
- Appendix D: Complete bibliography sorted by topic

**Structure**:
```mdx
## References

1. Macenski, S., et al. (2022). Robot Operating System 2: Design,
   architecture, and uses in the wild. *Science Robotics*, 7(66).
   https://doi.org/10.1126/scirobotics.abm6074

2. ROS 2 Documentation. (2024). *Getting Started with ROS 2 Humble*.
   Retrieved from https://docs.ros.org/en/humble/
```

**Validation**:
- URL checker script during build
- Citation count verification (minimum 25)
- Source type classification (official/academic/other)

---

## Research Queue (For Chapter Writing)

The following topics require targeted research during chapter authoring:

### Introduction
- [ ] Current state of humanoid robotics (2024-2025 landscape)
- [ ] Recent embodied AI breakthroughs (RT-2, PaLM-E)
- [ ] Sensor technology specifications (LiDAR, depth cameras)

### Module 1: ROS 2
- [ ] rclpy best practices and patterns
- [ ] URDF/Xacro for humanoid robots
- [ ] ROS 2 Control framework

### Module 2: Simulation
- [ ] Gazebo Fortress vs Classic comparison
- [ ] SDF format latest features
- [ ] Unity Robotics Hub integration

### Module 3: NVIDIA Isaac
- [ ] Isaac Sim 2024.x new features
- [ ] Isaac ROS perception packages
- [ ] Synthetic data generation pipelines

### Module 4: VLA
- [ ] Whisper API vs local deployment
- [ ] VLA model architectures (RT-2, OpenVLA)
- [ ] Multi-modal integration patterns

### Capstone
- [ ] End-to-end humanoid robot examples
- [ ] Voice command parsing strategies
- [ ] Sim-to-real transfer techniques

---

## Source Inventory (Preliminary)

### Official Documentation (Primary)
1. ROS 2 Humble Documentation
2. NVIDIA Isaac Sim Documentation
3. NVIDIA Isaac ROS Documentation
4. Gazebo Documentation
5. Navigation 2 Documentation
6. OpenAI Whisper GitHub
7. Unity Robotics Hub
8. Docusaurus Documentation

### Academic Sources (Secondary)
9. Macenski et al. (2022) - ROS 2 architecture
10. Brohan et al. (2023) - RT-2 VLA model
11. Driess et al. (2023) - PaLM-E embodied LLM
12. (Additional papers identified during chapter research)

### Hardware Documentation
13. NVIDIA Jetson Documentation
14. Intel RealSense Documentation
15. Dynamixel Servo Documentation

**Current Count**: 15+ sources identified, targeting 25+ minimum
