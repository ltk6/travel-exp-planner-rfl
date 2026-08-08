# Agent Guidelines: Travel Experience Planner

These rules define the repository-specific styling and workflow conventions that the coding assistant MUST follow.

---

## Commit Conventions

- Use the **Conventional Commits** standard.
- Prefix commits with a lowercase verb: `feat`, `fix`, `refactor`, `chore`, `docs`.
- Specify the module scope in parentheses where applicable:
  - `feat(n1): ...`
  - `refactor(n18): ...`
  - `fix(n3): ...`
- Write commit messages in a concise, lowercase, and direct format.
  - Examples:
    - `feat(n1): add light embedding and align to n0 template`
    - `refactor(n16): remove legacy APIs and update n18 integration`
    - `fix(n3): add connection timeout and fix schema bug`
    - `chore(phase0): complete architecture audit and standardize docs`

---

## Documentation Style

- **Tone & Voice:** Use a direct, active, and professional tone. Avoid conversational fluff, academic phrasing, and AI idioms ("utilizing", "leveraging"). Lead with facts.
- **Formatting:** Keep documents minimalistic. Use clean hierarchies and standard Git markdown. Keep tables to one concise sentence per row.
- **Content:** Preserve actionable details (timing, test counts, outputs), but do not embed study guides, tutorials, or redundant walkthroughs. Cross-reference existing docs instead of restating.
- **Structure:** Use **Goal → Tasks → Docs → Deliverables** for plans. Consolidate repeated triggers into reference tables.
- **Maintenance:** Proactively update `README.md` files to reflect structural or contract changes.

---

## Project Structure

- **`backend/modules/`** — In-process pipeline modules (N0–N6, N17). Run inside the N18 orchestrator process.
- **`backend/services/`** — Standalone microservices with their own `app.py` entrypoint (e.g., `n1_embedding`). Communicate over HTTP REST.
- **`backend/n18_orchestrator/`** — Central API gateway. Coordinates modules and services.
- **`backend/n3_database/`** — Database layer (PostgreSQL + file fallback).
- **`backend/shared/`** — Cross-cutting utilities (weights, math helpers).
- **`frontend/n16_web_ui/`** — Next.js frontend.
- **`config/`** — Global config module. Loads `.env`, exposes shared settings (API keys, DB URI, logging).
- When a module is migrated to a service, leave a `README.md` signpost in the old `modules/` folder.

---

## Module Naming

- All pipeline modules and services follow the `N<number>` naming convention (e.g., N0, N1, N18).
- Do not introduce new modules without an assigned N-number. Check the roadmap and existing module list before naming.
- Directory names use the full identifier: `n1_embedding`, `n18_orchestrator`, `n3_database`.

---

## Configuration Architecture

- **Global config (`config/__init__.py`):** Shared values only (DB credentials, API keys, logging). Loads `.env` via `python-dotenv`.
- **Service-specific configs (`n18_orchestrator/config.py`, `services/n1_embedding/config.py`):** Local settings only (ports, model names, feature flags). Each loads `.env` independently for self-contained execution.
- **In-process module configs (`modules/n5_.../config.py`):** Hardcoded constants only. No `.env` loading needed (inherits from host process).
- **Rule:** Global and local configs never import each other. Application code imports shared values from global config and local values from local config separately.

---

## Secrets Handling

- Never write real values into `.env.example`. Keys only, no values.
- Never commit `.env` files. The `.gitignore` must cover them.
- If a secret is needed for a test, use an environment variable injected at runtime.

---

## ADR Conventions

- ADRs live in `docs/adrs/`. File format: `<number>-<short-slug>.md` (e.g., `0004-http-rest-over-grpc.md`).
- Number sequentially. Check the highest existing number before creating a new ADR.
- Create and draft ADRs **before starting development** to validate the design and align scope.
- Update the ADR if implementation details force a shift in the core decision mid-development.
- Create an ADR when a decision is non-obvious, has trade-offs, or will be referenced by future work. Do not create ADRs for trivial implementation details.
- Structure: **Context → Decision → Consequences**. Consequences must include negatives.
- Status values: `Proposed` (before work), `Accepted` (upon verification), `Superseded by ADR-XXXX`, `Deprecated`.

---

## Phase Awareness

- The project is divided into phases 0–8. See `docs/plans/roadmap.md` for scope and timing.
- Do not implement features scoped to a future phase unless explicitly instructed.
- When adding code or docs, tag the relevant phase in comments or front matter where the roadmap does so (e.g., `(Phase 1)`).
- The current active phase is determined by the roadmap. Do not assume; check it.

---

## Testing Conventions

- Unit tests live adjacent to the module under test or in a top-level `tests/` directory. Do not scatter test files into unrelated directories.
- Run tests with `pytest` from the repo root unless a module has its own runner documented in its `README.md`.
- Do not delete or skip existing tests without a documented reason.

---

## Scope Discipline

- Stay within the stated task. Do not refactor adjacent code, rename unrelated files, or add unrequested features.
- If a task requires a change that would affect multiple modules, flag it before proceeding.

---

## Git Workflow

- Use **trunk-based development**. Cut feature branches directly off `main`.
- Merge completed features back into `main` via fast-forward or squash merge.
- Delete feature branches after merge.
- Tag milestones (e.g., `phase0-freeze`).

---

## Pull Request Guidelines

- Write PR descriptions in a minimalistic and structured format.
- Include a concise "Summary" explaining the architectural goal and impact of the changes.
- Include a "Key Changes" bulleted list detailing the modifications grouped by component.
  - Example:
    ```markdown
    ### Summary
    [Brief summary explaining the architectural goal and impact of the changes]

    ### Key Changes
    - **[Component Name]:** [Detail of modification]
    - **[Component Name]:** [Detail of modification]
    ```

---

## Ignored Directories

- **`notes/`**: Ignore files in this directory. Do not attempt to format, edit, or delete files in the `notes/` directory, as they are not tracked by version control and are used as scratchpads, unless explicitly instructed by the user.

---

## Project Context

- **Roadmap Reference**: Always refer to `docs/plans/roadmap.md` to understand the overarching goal of this repository. It is a 10-month, triple-track (Network, Software, DevOps) internship preparation capstone executed by a solo student developer, building upon a legacy group-project monolith. Do not assume this is a standard enterprise team environment.
- **Doc Tree Reference**: Always refer to `docs/plans/docs-tree.md` for the planned and actual documentation structure. Use it to determine where new documents belong and to check what already exists before creating files.
