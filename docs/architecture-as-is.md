# Architecture: Current State (As-Is)

*Phase 0 Baseline Snapshot*

This document outlines the architecture of the Travel Experience Planner as of the Phase 0 baseline (August). The system operates as a local monolithic hub-and-spoke application, relying on in-process execution and a managed cloud database.

## System Topology: Monolithic Hub-and-Spoke

The system is designed around a central orchestrator pattern, but all backend components currently share a single compute process and memory space.

- **N18 (FastAPI Orchestrator):** The core routing and aggregation layer. It exposes REST endpoints (e.g., `/activities`, `/explore`) on `127.0.0.1:8000`.
- **N1–N17 (The Spokes):** Domain-specific modules (e.g., N1 Embedding, N5 Activity Generation, N6 Activity Ranking) organized as Python packages within `backend/modules/`.
- **In-Process Execution:** N18 imports these modules directly (via `backend/n18_orchestrator/services.py`) and executes their entry-point functions sequentially rather than calling them over a network boundary. N18 blocks until synchronous operations complete.
- **Shared Contracts:** Both N18 and the spoke modules rely on shared Pydantic V2 schemas (e.g., `N5GenerateInput`, `N1EmbedInput`) to enforce data consistency.

## Database Dependency Layout

- **N3 (Database Module):** All database interactions route through `backend/n3_database/db_manager.py`.
- **Managed Cloud Dependency:** N3 connects to a managed Supabase PostgreSQL instance utilizing the `pgvector` extension.
- **Connection Management:** Connections are managed via a custom `CircuitBreaker` inside `db_manager.py` that fails-fast if Supabase becomes unreachable.
- **Caching:** N18 maintains a hybrid memory/disk cache (`location_cache.json`) for location data to minimize network latency.

## Frontend Architecture

- **N16 (Next.js Web UI):** The user interface is built with Next.js, running independently from the backend on `127.0.0.1:3000`. It communicates exclusively with the N18 orchestrator's REST API.

## Manual Execution Model

The system currently lacks containerization and boots via a Windows batch script (`run.bat`):

1. **Venv Setup:** Creates and activates a Python virtual environment.
2. **Dependency Checks:** Compares the timestamp of a marker file against `requirements.txt` to conditionally run `pip install`.
3. **Frontend Boot:** Checks for `node_modules` and runs `npm install` if missing.
4. **Process Launch:** Spawns two background instances: `uvicorn` for N18 and `npm run dev` for N16.
5. **Browser Launch:** Polls `127.0.0.1:3000` until responsive, then opens the default browser.

## Problem & Risk Statement

This baseline architecture carries operational risks that the roadmap addresses:

1. **Lack of Isolation:** N1 (heavy BGE-M3 vector embeddings) runs in the same memory space as N18 (I/O bound API routing). A memory spike in N1 can crash the entire API. Host-OS dependencies create environmental fragility.
2. **Cloud Dependency & Cost:** Relying on managed Supabase violates the Zero-Cost Local-First Guarantee.
3. **Single-Point Failure under Load:** N5 (Activity Generation) relies on a single LLM API provider. N18 blocks while waiting for N5's in-process function call to finish. A `429 Too Many Requests` response from the provider will exhaust N18's worker threads, causing a cascading failure across the application (to be tested in Phase 3).
