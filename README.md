# Travel Experience Planner

A travel planning system utilizing semantic retrieval, multimodal inputs, and dynamic LLM generation. The frontend is built with Next.js, and the backend API orchestrator is powered by FastAPI (N18).

## Core Features

- **Multi-modal Semantic Search:** Processes user preferences through text and images.
- **Dynamic Activity Generation:** Generates contextual itineraries using Groq LLMs based on real locations.
- **Feedback Loop:** Ingests user feedback to refine recommendations in real-time.

## Technology Stack

- **Frontend:** Next.js
- **Backend Orchestrator:** FastAPI (N18)
- **LLM Engine:** Groq (Llama3/Mixtral)
- **Embeddings:** SentenceTransformers (`intfloat/multilingual-e5-small` & `BAAI/bge-m3`)
- **Database:** PostgreSQL with `pgvector`

## Quick Start

### Requirements

- Python 3.10+
- Node.js 18+ and npm
- PostgreSQL (with pgvector extension)

### Environment Configuration

```bash
# Backend configuration
cp .env.example .env
# Edit .env and populate: PG_URI, GROQ_API_KEY, INTERNAL_API_KEY

# Frontend configuration
cd frontend/n16_web_ui
cp .env.local.example .env.local
# Edit .env.local and populate: INTERNAL_API_KEY
```

### Run Locally (Windows)

```bat
run.bat
```

The script automates the following:
1. Creates and activates the Python virtual environment.
2. Installs Python dependencies from `requirements.txt`.
3. Installs Node.js dependencies for Next.js.
4. Boots the backend on `:8000` and frontend on `:3000`.
5. Launches the default browser at `http://127.0.0.1:3000`.

### Service Endpoints

| Service | URL |
|---|---|
| Frontend (Next.js) | http://127.0.0.1:3000 |
| Backend API | http://127.0.0.1:8000 |
| Health Check | http://127.0.0.1:8000/health |

## Data Pipeline

The system includes tools to format and ingest location data into the vector database:
- **Vector Generation:** Run `python backend/n3_database/seeds/embed_locations.py` to generate embeddings for new locations in `locations.json`. Outputs to `locations_with_vectors.json`.

## Architecture (Phase 0 Baseline)

The system operates on a hub-and-spoke architecture. Modules N1-N17 execute in-process within the core N18 FastAPI orchestrator. Boundaries are enforced via Pydantic V2 contracts.

| Module | Function |
|---|---|
| N0 | Sample module template |
| N1 | Embedding generation (BGE-M3, E5) |
| N2 | Image processing to text |
| N3 | PostgreSQL persistence (locations, users, history) |
| N4 | Location ranking (cosine similarity) |
| N5 | Activity generation (LLM) |
| N6 | Activity ranking |
| N16 | Next.js Frontend |
| N17 | Feedback processing |
| N18 | FastAPI Orchestrator |

*(Note: N7-N15 are deprecated or superseded components).*

### Current Operational Risks

The baseline architecture relies on an in-process execution model without container isolation, leading to environmental fragility. The database relies on a managed cloud instance, violating the zero-cost local-first objective.

**Primary Risk:** The N5 Activity Generation module relies on a single upstream LLM provider. Synchronous execution means an API rate limit (`429 Too Many Requests`) will block N18 worker threads, causing a cascading system failure. Addressing this fragility through microservice extraction and resilience patterns is the focus of subsequent roadmap phases.

---
*Note: This repository is a continued iteration of the original `travel-exp-planner`. See LICENSE for details.*