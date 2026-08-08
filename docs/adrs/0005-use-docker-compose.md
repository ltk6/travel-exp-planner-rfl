# 5. Use Docker Compose (Phase 1)

**Date:** 2026-08-08
**Status:** Proposed

## Context

The system must transition from host-bound `run.bat` scripts to a containerized stack for Phase 1 portability.

## Decision

Use Docker Compose as the primary orchestration tool for local development in Phase 1 to link N1, N18, and N16.

## Consequences

- **Positive:** Reduces setup to a single command and standardizes environment variables across services.
- **Negative:** Lacks native Kubernetes features like NetworkPolicies, which are deferred to Phase 4.
