# Architecture: Current State (As-Is)

Phase 0 baseline snapshot — August 2026.

## Topology

Monolith. All backend modules (N1–N17) run in-process inside N18 (FastAPI, `:8000`). N18 imports modules directly via `services.py` and calls them synchronously. Pydantic V2 contracts enforce boundaries.

N1 Embedding is additionally deployed as a standalone service on `:8001`.

N16 (Next.js, `:3000`) talks to N18 over REST.

| Component | Location | Port |
|---|---|---|
| N18 — FastAPI Orchestrator | `backend/n18_orchestrator/` | `:8000` |
| N1 — Embedding Service | `backend/services/n1_embedding/` | `:8001` |
| N16 — Next.js Frontend | `frontend/n16_web_ui/` | `:3000` |
| N3 — Database | `backend/n3_database/` | Supabase (remote) |
| N0–N6, N17 — Modules | `backend/modules/` | in-process |

## Database

N3 routes all DB access through `db_manager.py`. Connects to managed Supabase PostgreSQL with `pgvector`. A `CircuitBreaker` in `db_manager.py` fails-fast on connection loss. N18 caches location data to disk (`location_cache.json`).

## Execution Model

No containers. `run.bat` creates a venv, installs deps, port-checks running services, and spawns N1, N18, and N16 as separate processes.

## Known Risks

1. **No isolation.** N1 (BGE-M3, ~1GB) shares memory with N18. A spike in N1 crashes the API.
2. **Cloud DB dependency.** Supabase free tier — vendor lock-in and availability risk.
3. **N5 → Groq blocking.** N5 calls Groq synchronously. A `429` blocks N18 workers, cascading into full system failure. To be tested in Phase 3.
