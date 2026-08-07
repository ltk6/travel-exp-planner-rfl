# Agent Guidelines: Travel Experience Planner
These rules define the repository-specific styling and workflow conventions that the coding assistant MUST follow.
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

## Documentation Style
- **Tone & Voice:** Use a direct, active, and professional tone. Avoid conversational fluff, academic phrasing, and AI idioms ("utilizing", "leveraging"). Lead with facts.
- **Formatting:** Keep documents minimalistic. Use clean hierarchies and standard Git markdown. Keep tables to one concise sentence per row.
- **Content:** Preserve actionable details (timing, test counts, outputs), but do not embed study guides, tutorials, or redundant walkthroughs. Cross-reference existing docs instead of restating.
- **Structure:** Use **Goal → Tasks → Docs → Deliverables** for plans. Consolidate repeated triggers into reference tables.
- **Maintenance:** Proactively update `README.md` files to reflect structural or contract changes.

## Project Structure
- **`backend/modules/`** — In-process pipeline modules (N0–N6, N17). Run inside the N18 orchestrator process.
- **`backend/services/`** — Standalone microservices with their own `app.py` entrypoint (e.g., `n1_embedding`). Communicate over HTTP REST.
- **`backend/n18_orchestrator/`** — Central API gateway. Coordinates modules and services.
- **`backend/n3_database/`** — Database layer (PostgreSQL + file fallback).
- **`backend/shared/`** — Cross-cutting utilities (weights, math helpers).
- **`frontend/n16_web_ui/`** — Next.js frontend.
- **`config/`** — Global config module. Loads `.env`, exposes shared settings (API keys, DB URI, logging).
- When a module is migrated to a service, leave a `README.md` signpost in the old `modules/` folder.

## Configuration Architecture
- **Global config (`config/__init__.py`):** Shared values only (DB credentials, API keys, logging). Loads `.env` via `python-dotenv`.
- **Service-specific configs (`n18_orchestrator/config.py`, `services/n1_embedding/config.py`):** Local settings only (ports, model names, feature flags). Each loads `.env` independently for self-contained execution.
- **In-process module configs (`modules/n5_.../config.py`):** Hardcoded constants only. No `.env` loading needed (inherits from host process).
- **Rule:** Global and local configs never import each other. Application code imports shared values from global config and local values from local config separately.

## Git Workflow
- Use **trunk-based development**. Cut feature branches directly off `main`.
- Merge completed features back into `main` via fast-forward or squash merge.
- Delete feature branches after merge.
- Tag milestones (e.g., `phase0-freeze`).

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

## Ignored Directories
- **`notes/`**: Ignore files in this directory. Do not attempt to format, edit, or delete files in the `notes/` directory, as they are not tracked by version control and are used as scratchpads, unless explicitly instructed by the user.
