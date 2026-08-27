# Project Highlights & Metrics Log

Living document. Updated at the end of every phase.

---

## Phase 0 — Baseline (August)

**Status:** Completed.

### Quantified Achievements & Metrics

- **Architecture Audit:** Documented in [`architecture-as-is.md`](../architecture-as-is.md).
- **Infrastructure Cost:** $0 locally. Supabase free tier for DB (vendor lock-in risk).
- **Latency Baseline:** Recorded from local `benchmarks/results/results.json` under light concurrency:
  - `/health` (Liveness): 25.4ms P95
  - `/health/deep` (Readiness/DB): 33.0ms P95
  - `/locations` (Vector Search): 681.2ms P95
  - `/explore` (Cache Hit): 1440.2ms P95
  - `/feedback/locations` (N17 + Search): 3395.6ms P95
  - `/activities` (LLM Generation): 10010.4ms P95
  - `/feedback/activities` (N17 + LLM): 17470.0ms P95
- **Reliability Risk:** N5 calls Groq synchronously. A `429` blocks N18 workers → cascade failure. To be tested in Phase 3.

### Vendor Incidents

- **Pre-Phase 0 — Groq deprecated `meta-llama/llama-4-scout-17b`:** Was part of an earlier LLM chain iteration. Removed by Groq before Phase 0 baseline work began; no impact on recorded benchmarks.
- **2026-08-27 — [INC-001: Groq mass model deprecation](../incidents/2026-08-27-groq-model-deprecation.md):** `llama-3.3-70b-versatile` and `llama-3.1-8b-instant` removed. Surviving chain: `qwen3.6 → qwen3.8 → gpt-oss-120b → gpt-oss-20b`. All models capped at 8K TPM. Resolved < 1 hour.

### Key Decisions (ADRs)

- **ADR-0001:** Establish Markdown Architecture Decision Records (MADR) format.
- **ADR-0002:** The system will temporarily retain the monolithic hub-and-spoke topology (Phase 0) but must be decoupled from the host OS via containerization.

---

## Phase 1 — Containerization & Local Stack (September)

**Status:** Completed.

### Deliverables Shipped

- **N1 Service Extraction:** `backend/services/n1_embedding/` — standalone FastAPI service with `/embed`, `/light-embed`, `/embed-batch`, `/light-embed-batch`, and `/health` endpoints.
- **Dockerfiles:** Multi-stage builds for N1 (`Dockerfile.n1`), N18 (`Dockerfile.n18`), N16 (`Dockerfile.n16`). All include non-root users and healthchecks. Multi-arch targets (`linux/amd64` + `linux/arm64`) flagged for Phase 2 CI builds.
- **Compose Stack:** `docker-compose.yml` — DB (`pgvector/pgvector:pg16`), N1, N18, N16 on a shared bridge network. Supabase dependency removed; local PostgreSQL + pgvector replaces it.
- **Secrets Baseline:** `.env.example` with all required keys; `.env` excluded via `.gitignore`.
- **Backup Script:** `scripts/pg_dump_cron.sh` — local Postgres volume backup.
- **Service Contract:** `docs/n1-embed-api.md` — N1 API contract documenting all endpoints.
- **Outstanding:** Container network diagram not yet produced. Carry into Phase 2 documentation sprint.

### Key Decisions (ADRs)

- **ADR-0003:** N1 is the only extracted spoke in Phase 1; all other modules remain in-process.
- **ADR-0004:** HTTP REST over gRPC for N1 ↔ N18 communication.
- **ADR-0005:** Docker Compose before Kubernetes for local development orchestration.
- **ADR-0006:** `.env`-based secrets injection with `.gitignore` enforcement; migration path to K8s Secrets in Phase 4.
- **ADR-0007 (Phase 2):** Self-hosted Jenkins over GitHub Actions — drafted during Phase 1 close.

---

*(Future phases will append their highlights here).*
