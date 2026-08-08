# 3. N1 Is the Only Extracted Spoke (Phase 1)

**Date:** 2026-08-08
**Status:** Accepted

## Context

The system uses a hub-and-spoke topology (ADR-0002). Extracting all modules into independent services in Phase 1 adds deployment overhead and complicates early testing.

## Decision

Extract only N1 as a standalone microservice (spoke) in Phase 1. All other modules run as in-process pipelines inside the N18 orchestrator.

## Consequences

- **Positive:** Deployment complexity stays low while the hub-and-spoke pattern is validated.
- **Positive:** The HTTP REST communication path between N18 and N1 (ADR-0004) is proven before scaling to other modules.
- **Negative:** Remaining modules stay tightly coupled to N18 and require extraction in later phases.
