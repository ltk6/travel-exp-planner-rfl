# Engineering Backlog

Living scrum backlog. Tasks are defined phase-by-phase as each phase becomes active, rather than planned upfront. Completed and reviewed tasks are permanently erase from existent.

---

## Active Sprint: Close Phase 0–1 Gaps

**Goal:** Close all Phase 0–1 carry-over gaps so `docker compose` is 100% deterministic and self-contained on Ubuntu before starting Phase 2 feature work.

---

### PH1-GAP-01: Alembic migrations `[M · 3h]`
> *Done when:* `docker compose run --rm n18 alembic upgrade head` exits 0 on blank DB and creates all tables idempotently.

- [ ] Add `alembic` to `requirements.txt`.
- [ ] Initialize `backend/n18_orchestrator/migrations/` via `alembic init`.
- [ ] Configure `env.py` to read `PG_URI` dynamically from environment without hardcoding.
- [ ] Generate initial revision from current SQLAlchemy schemas.
- [ ] Add migration execution step into Compose startup / entrypoint script.
- [ ] Validate migration executes cleanly against a wiped `pgvector` container.

---

### PH1-GAP-02: Idempotent seed script in Compose `[M · 2h]`
> *Done when:* Fresh stack contains seeded vector locations and re-running seed produces no duplicate records.

- [ ] Review `backend/n3_database/seeds/seed_with_vectors.py` for idempotent upsert / conflict handling.
- [ ] Add one-shot `seed` service (or startup flag) to `docker-compose.yml`.
- [ ] Gate seed execution on N1 healthy status so embeddings generate reliably.
- [ ] Test re-running `docker compose run --rm seed` leaves table row count unchanged.

---

### PH1-GAP-03: Cached HuggingFace model volume for N1 `[M · 1h]`
> *Done when:* Restarting stack without `-v` re-uses cached model on disk in under 30s.

- [ ] Verify `hf_cache` volume is bound to `ENV HF_HOME=/app/hf_cache` in `Dockerfile.n1`.
- [ ] Verify first run caches model files to host volume.
- [ ] Test `docker compose down` (without `-v`) followed by `up` — N1 healthy within 30s.
- [ ] Document `hf_cache` mount in `docs/bring-up.md` v0.

---

### PH1-GAP-04: Compose service profiles `[M · 2h]`
> *Done when:* `docker compose --profile core up` launches only base app services; secondary services require explicit profile flags.

- [ ] Add `profiles:` tags to `docker-compose.yml`:
  - `core`: `db`, `n1_embedding`, `n18_orchestrator`, `n16_web_ui`
  - `ci`: `registry`
  - `tunnel`: Cloudflare tunnel sidecar
  - `obs`: Prometheus, Grafana
  - `chaos`: Toxiproxy
- [ ] Declare local `registry:2` service under `ci` profile for Phase 2 pipeline.
- [ ] Verify healthchecks exist on all `core` services (`n18` `/health`, `n1` `/health`, `db` `pg_isready`).
- [ ] Verify `docker compose --profile core up -d` starts cleanly and shows healthy statuses.

---

### PH1-GAP-05: Configurable LLM upstream URL for N5 `[M · 1h]`
> *Done when:* N5 reads `LLM_BASE_URL` from env and can route to mock simulator or real Groq.

- [ ] Replace hardcoded `GROQ_API_URL` in `backend/modules/n5_activity_generation/config.py` with `os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1/chat/completions")`.
- [ ] Update `llm_provider.py` references to use `LLM_BASE_URL`.
- [ ] Add `LLM_BASE_URL` to `docker-compose.yml` under `n18_orchestrator`.
- [ ] Add empty `LLM_BASE_URL=` to `.env.example`.
- [ ] Smoke test routing requests to local mock / httpbin endpoint.

---
