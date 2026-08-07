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

### Key Decisions (ADRs)

- **ADR-0001:** Establish Markdown Architecture Decision Records (MADR) format.
- **ADR-0002:** The system will temporarily retain the monolithic hub-and-spoke topology (Phase 0) but must be decoupled from the host OS via containerization.

---

*(Future phases will append their highlights here).*
