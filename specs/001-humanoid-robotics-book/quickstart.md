# Quickstart: Physical AI & Humanoid Robotics Book

**Feature**: 001-humanoid-robotics-book
**Created**: 2025-12-15
**Purpose**: Development environment setup guide for contributors and maintainers

---

## Prerequisites

### Required Software

| Software | Version | Purpose | Installation |
|----------|---------|---------|--------------|
| Node.js | 18.x+ | Docusaurus runtime | [nodejs.org](https://nodejs.org/) |
| npm/yarn | 8.x+/1.22+ | Package management | Included with Node.js |
| Python | 3.10+ | Chatbot backend | [python.org](https://www.python.org/) |
| Git | 2.30+ | Version control | [git-scm.com](https://git-scm.com/) |
| Docker | 24.x+ | Local services | [docker.com](https://www.docker.com/) |

### Optional (For Testing Code Examples)

| Software | Version | Purpose |
|----------|---------|---------|
| Ubuntu 22.04 | LTS | Native ROS 2 environment |
| ROS 2 Humble | LTS | Robot framework |
| WSL2 | Latest | Windows users |

### API Keys Required

- **OpenAI API Key**: For embeddings and chat completion
  - Model access: `text-embedding-3-small`, `gpt-4o-mini`
  - Get key: [platform.openai.com](https://platform.openai.com/)

---

## Repository Setup

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/[org]/physical-ai-robotics-book.git
cd physical-ai-robotics-book

# Install book site dependencies
cd book
npm install

# Install chatbot dependencies
cd ../chatbot
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Environment Configuration

Create environment files:

```bash
# Book site (.env in book/)
cp book/.env.example book/.env
```

```env
# book/.env
CHATBOT_API_URL=http://localhost:8000/v1
```

```bash
# Chatbot backend (.env in chatbot/)
cp chatbot/.env.example chatbot/.env
```

```env
# chatbot/.env
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Neon Postgres
DATABASE_URL=postgresql://user:pass@ep-xxx.region.aws.neon.tech/bookdb?sslmode=require

# Application
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000
```

---

## Running Locally

### Option A: Full Stack (Recommended)

```bash
# Terminal 1: Start chatbot backend
cd chatbot
source .venv/bin/activate
uvicorn src.main:app --reload --port 8000

# Terminal 2: Start Docusaurus dev server
cd book
npm run start
```

Access:
- Book site: http://localhost:3000
- Chatbot API: http://localhost:8000
- API docs: http://localhost:8000/docs

### Option B: Book Only (No Chatbot)

```bash
cd book
npm run start
```

The chatbot widget will show "Service unavailable" but all book content is accessible.

### Option C: Docker Compose (All Services)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Development Workflows

### Writing Content

1. **Create new chapter**:
   ```bash
   # Navigate to appropriate module
   cd book/docs/module1-ros2/

   # Create chapter file
   touch chapter6-new-topic.mdx
   ```

2. **Chapter template**:
   ```mdx
   ---
   title: "Chapter Title"
   sidebar_label: "Short Label"
   sidebar_position: 6
   description: "SEO description"
   keywords: [keyword1, keyword2]
   ---

   # Chapter Title

   ## Learning Objectives

   By the end of this chapter, you will be able to:
   - Objective 1
   - Objective 2
   - Objective 3

   ## Prerequisites

   - Completed Chapter X
   - Software: package_name >= version

   ## Introduction

   Content here...

   ## Key Takeaways

   - Takeaway 1
   - Takeaway 2

   ## References

   1. Author (Year). *Title*. URL
   ```

3. **Preview changes**:
   ```bash
   npm run start
   # Changes hot-reload automatically
   ```

### Testing Code Examples

```bash
# From book directory
npm run test:code -- --module module1

# Test specific chapter
npm run test:code -- --chapter module1/chapter3

# Generate test report
npm run test:code -- --report
```

### Updating Chatbot Embeddings

After content changes, update the vector database:

```bash
# Full reindex (all chapters)
cd chatbot
python scripts/reindex.py

# Incremental update (specific chapters)
python scripts/reindex.py --chapters module1/chapter3,module1/chapter4

# Verify embeddings
python scripts/verify_embeddings.py
```

---

## Project Structure

```
physical-ai-robotics-book/
├── book/                          # Docusaurus site
│   ├── docs/                      # MDX content
│   │   ├── intro/                 # Introduction chapters
│   │   ├── module1-ros2/          # Module 1 chapters
│   │   ├── module2-simulation/    # Module 2 chapters
│   │   ├── module3-isaac/         # Module 3 chapters
│   │   ├── module4-vla/           # Module 4 chapters
│   │   ├── capstone/              # Capstone project
│   │   └── appendices/            # Appendices A-E
│   ├── src/
│   │   ├── components/            # React components
│   │   │   └── ChatbotWidget/     # Chatbot integration
│   │   ├── css/                   # Global styles
│   │   └── pages/                 # Custom pages
│   ├── static/                    # Static assets
│   │   └── img/                   # Images
│   ├── docusaurus.config.js       # Site configuration
│   ├── sidebars.js                # Sidebar structure
│   └── package.json
│
├── chatbot/                       # FastAPI backend
│   ├── src/
│   │   ├── main.py                # FastAPI app
│   │   ├── config.py              # Settings
│   │   ├── models/                # Pydantic models
│   │   ├── services/
│   │   │   ├── embedding.py       # OpenAI embeddings
│   │   │   ├── retrieval.py       # Qdrant search
│   │   │   └── generation.py      # OpenAI chat
│   │   └── routers/
│   │       ├── chat.py            # /chat endpoints
│   │       ├── sessions.py        # /sessions endpoints
│   │       └── health.py          # /health endpoints
│   ├── scripts/
│   │   ├── reindex.py             # Embedding pipeline
│   │   ├── chunk_content.py       # Content chunking
│   │   └── verify_embeddings.py   # Validation
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── code-examples/                 # Tested code from chapters
│   ├── module1/
│   ├── module2/
│   ├── module3/
│   └── module4/
│
├── .github/
│   └── workflows/
│       ├── deploy-book.yml        # Book deployment
│       ├── deploy-chatbot.yml     # Chatbot deployment
│       └── test-examples.yml      # Code validation
│
├── docker-compose.yml             # Local development
├── specs/                         # SpecKit artifacts
└── README.md
```

---

## Common Commands

### Book Site

| Command | Description |
|---------|-------------|
| `npm run start` | Start dev server (hot reload) |
| `npm run build` | Production build |
| `npm run serve` | Serve production build locally |
| `npm run clear` | Clear Docusaurus cache |
| `npm run swizzle` | Customize Docusaurus components |

### Chatbot

| Command | Description |
|---------|-------------|
| `uvicorn src.main:app --reload` | Start dev server |
| `pytest` | Run all tests |
| `pytest -v -k test_query` | Run specific tests |
| `python scripts/reindex.py` | Update embeddings |
| `alembic upgrade head` | Run DB migrations |

### Code Examples

| Command | Description |
|---------|-------------|
| `npm run test:code` | Test all code examples |
| `npm run lint:code` | Lint Python examples |
| `npm run format:code` | Format code examples |

---

## Troubleshooting

### Book Site Issues

**Error: Node modules not found**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Error: Port 3000 already in use**
```bash
npm run start -- --port 3001
```

**Error: MDX parsing errors**
- Check for unclosed JSX tags
- Ensure code blocks have proper language identifiers
- Validate frontmatter YAML syntax

### Chatbot Issues

**Error: OpenAI API rate limit**
- Check API key is valid
- Verify billing is enabled
- Implement exponential backoff in reindex script

**Error: Qdrant connection failed**
- Verify QDRANT_URL format
- Check API key permissions
- Ensure collection exists

**Error: Database connection failed**
- Verify DATABASE_URL format includes `?sslmode=require`
- Check Neon project is active (free tier may sleep)
- Run migrations: `alembic upgrade head`

### Code Example Testing

**Error: ROS 2 not found**
- Code examples require ROS 2 Humble
- Use Docker: `docker run -it osrf/ros:humble-desktop-full`
- Or WSL2 with Ubuntu 22.04

---

## Contributing

### Branch Naming

- Feature: `feature/module1-chapter3-improvements`
- Fix: `fix/chatbot-timeout-handling`
- Docs: `docs/readme-update`

### Commit Messages

```
type(scope): description

- feat(module1): add URDF validation example
- fix(chatbot): handle empty query gracefully
- docs(appendix): update hardware pricing
```

### Pull Request Checklist

- [ ] Content follows MDX template structure
- [ ] Code examples tested in target environment
- [ ] New terms added to glossary
- [ ] Citations in APA format
- [ ] No broken internal links
- [ ] Chatbot embeddings updated (if content changed)

---

## Deployment

### Book (GitHub Pages)

Automated via GitHub Actions on push to `main`:

```yaml
# .github/workflows/deploy-book.yml
on:
  push:
    branches: [main]
    paths: ['book/**']
```

Manual deployment:
```bash
cd book
npm run build
# Deploy build/ to GitHub Pages
```

### Chatbot (Cloud Run / Render)

Automated via GitHub Actions on push to `main`:

```yaml
# .github/workflows/deploy-chatbot.yml
on:
  push:
    branches: [main]
    paths: ['chatbot/**']
```

Required secrets:
- `OPENAI_API_KEY`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `DATABASE_URL`

---

## Resources

- [Docusaurus Documentation](https://docusaurus.io/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Neon Documentation](https://neon.tech/docs)
- [ROS 2 Humble Documentation](https://docs.ros.org/en/humble/)
