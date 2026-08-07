# Travel Experience Planner

Travel planning system with semantic retrieval, multimodal inputs, and dynamic LLM generation. 

Application code is frozen. Feature development will resume via a CD sprint after containerization, orchestration, and reliability milestones are complete.

## Core Features
- **Multi-modal Semantic Search:** Processes user preferences through text and images.
- **Dynamic Activity Generation:** Generates contextual itineraries via Groq LLMs based on real locations.
- **Feedback Loop:** Ingests user feedback to refine real-time recommendations.

## Technology Stack
- **Frontend:** Next.js
- **Backend Orchestrator:** FastAPI (N18)
- **LLM Engine:** Groq (Llama3/Mixtral)
- **Embeddings:** SentenceTransformers (`intfloat/multilingual-e5-small` & `BAAI/bge-m3`)
- **Database:** PostgreSQL with `pgvector`

## Quick Start (Windows)
Requires Python 3.10+, Node.js 18+, and PostgreSQL with `pgvector`.

```bash
# Backend configuration
cp .env.example .env
# Edit .env and populate: PG_URI, GROQ_API_KEY, INTERNAL_API_KEY

# Frontend configuration
cd frontend/n16_web_ui
cp .env.local.example .env.local
# Edit .env.local and populate: INTERNAL_API_KEY
```

```bat
run.bat
```
The script creates the virtual environment, installs dependencies, boots the backend on `:8000`, the frontend on `:3000`, and launches the browser.

### Service Endpoints
| Service | URL |
|---|---|
| Frontend (Next.js) | http://127.0.0.1:3000 |
| Backend API | http://127.0.0.1:8000 |
| Health Check | http://127.0.0.1:8000/health |

## Data Pipeline
- **Vector Generation:** `python backend/n3_database/seeds/embed_locations.py` generates embeddings for locations in `locations.json`, outputting to `locations_with_vectors.json`.

## Architecture (Phase 0 Baseline)
The system uses a Hub-and-Spoke topology. Modules N1-N17 execute in-process within the N18 FastAPI orchestrator. Boundaries are enforced via Pydantic V2 contracts.

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

*(Note: N7-N15 are deprecated).*

### Current Operational Risks
- **No isolation:** In-process execution model lacks container boundaries. Memory exhaustion in N1 crashes the N18 API.
- **Cloud dependency:** Database relies on a managed cloud instance (Supabase).
- **Synchronous blocking:** N5 calls Groq synchronously. A `429` blocks N18 worker threads, causing a system-wide cascading failure.

---
*See [`docs/plans/roadmap.md`](docs/plans/roadmap.md) for the full infrastructure hardening roadmap.*
*Continued iteration of the original `travel-exp-planner`. See LICENSE.*