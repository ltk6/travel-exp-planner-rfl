# Project Highlights & Metrics Log

This is a living document, updated at the end of every phase of the 11-Month Capstone Roadmap. It serves as the single source of truth for quantified achievements, metrics, and decision outcomes utilized for the final resumes in Phase 8.

---

## Phase 0 — Baseline (August)

**Status:** Completed.

### Quantified Achievements & Metrics

- **Architecture Audit:** Documented the monolithic, in-process execution model (`N18` orchestrator calling `N1`-`N17` directly).
- **Infrastructure Cost:** Currently $0 locally, reliant on a managed free-tier database (Supabase), presenting a vendor lock-in and availability risk.
- **Latency Baseline:** Recorded from local `benchmarks/results/results.json` under light concurrency:
  - `/health` (Liveness): 25.4ms P95
  - `/health/deep` (Readiness/DB): 33.0ms P95
  - `/locations` (Vector Search): 681.2ms P95
  - `/explore` (Cache Hit): 1440.2ms P95
  - `/feedback/locations` (N17 + Search): 3395.6ms P95
  - `/activities` (LLM Generation): 10010.4ms P95
  - `/feedback/activities` (N17 + LLM): 17470.0ms P95
- **Reliability Risk:** Identified a critical single point of failure where N5 (Activity Generation) relies on a single LLM API. Under load, a `429 Too Many Requests` response will block the N18 orchestrator's worker threads, causing a system-wide cascade failure.

### Key Decisions (ADRs)

- **ADR-0001:** Establish Markdown Architecture Decision Records (MADR) format.
- **ADR-0002:** The system will temporarily retain the monolithic hub-and-spoke topology (Phase 0) but must be decoupled from the host OS via containerization.

---

*(Future phases will append their highlights here).*
