# 6. Env Secrets Management (Phase 1)

**Date:** 2026-08-08
**Status:** Accepted

## Context

Containerization requires a method to inject API keys and DB credentials without hardcoding them into images.

## Decision

Implement `.env`-based injection where global and service-specific configurations load values independently.

## Consequences

- **Positive:** Prevents secret exposure by enforcing `.gitignore` and using `.env.example` templates.
- **Negative:** Requires manual coordination of `.env` files across separate development environments.
