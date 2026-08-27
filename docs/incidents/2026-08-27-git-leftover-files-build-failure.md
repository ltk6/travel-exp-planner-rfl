# INC-002: Build Failures from Untracked Git Leftovers

**Date:** 2026-08-27  
**Status:** Resolved  
**Author:** Solo Developer  

## Summary
A series of local Git stashes, partial commits, and leftover files from the N1 extraction refactor were left out of the main commit tree. These untracked and unresolved files broke the Docker Compose production build process for both the N18 Orchestrator and the N16 Next.js frontend.

## Timeline
- **Phase 1 Finalization:** Attempted to wrap up Phase 1 by pushing all containerization and routing fixes.
- **Git Stash Collision:** A `git stash pop` operation reintroduced raw merge conflict markers (`<<<<<<< Updated upstream`) into `backend/n3_database/requirements.txt`.
- **Ghost Requirements:** The `n1_embedding` module had been successfully migrated to a standalone service, but its legacy `backend/modules/n1_embedding/requirements.txt` was left on disk locally and referenced in the root `requirements.txt`.
- **Build Failure 1 (N18):** `Dockerfile.n18` attempted to run `pip wheel` on the root `requirements.txt`, which recursively pulled in the ghost N1 requirements. This caused the N18 container to erroneously attempt downloading heavy ML dependencies (`transformers`, `torch`), eventually crashing due to the raw git conflict markers in the database requirements.
- **Build Failure 2 (N16):** The Next.js production build (`npm run build`) failed due to a strict TypeScript error inside the `@maplibre/geojson-vt` node module. This package was only being pulled in by a dead, unused UI map component left in `profile/page.tsx`.

## Root Cause
- **Human Error in Version Control:** Relying on manual `git add` and local stashing without a clean working directory check led to critical files (like ghost requirements and dead UI components) persisting locally but breaking the isolated Docker build context.

## Resolution
1. **Removed Ghost Dependencies:** Deleted `backend/modules/n1_embedding/requirements.txt` and removed its reference from the root `requirements.txt` and `Dockerfile.n18`.
2. **Resolved Git Conflicts:** Manually removed the `<<<<<<< Updated upstream` markers from `backend/n3_database/requirements.txt`.
3. **Pruned Dead UI Code:** Removed the unused MapLibre components from `frontend/n16_web_ui/src/app/profile/page.tsx` to bypass the third-party TypeScript compilation error.

## Prevention & Next Steps (Phase 2)
This incident highlights the fragility of relying exclusively on local, manual Docker builds. 
In **Phase 2**, the implementation of a strict **CI/CD pipeline (Jenkins)** will entirely prevent this issue. An ephemeral CI runner will check out the raw repository state from GitHub and attempt a pristine build. If a file is left out of the commit, the CI build will fail in isolation, preventing broken code from ever being merged or deployed.
