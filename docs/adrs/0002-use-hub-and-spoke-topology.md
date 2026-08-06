# 2. Use Hub-and-Spoke Topology

Date: 2026-08-06

## Status

Accepted

## Context

The system utilizes multiple domain-specific ML and processing modules (e.g., N1 Embedding, N2 Vision, N3 Database, N5 Activity Generation). A structured interface is required for the frontend (N16) to consume these services seamlessly, while maintaining a foundation for future decoupling.

## Decision

The project implements a Hub-and-Spoke topology.

- **The Hub:** N18 (FastAPI Orchestrator) serves as the central API gateway and orchestrator.
- **The Spokes:** Domain-specific modules (N1-N17) deliver specialized, atomic functions.
- **Execution Model:** Initially (Phase 0), all spokes are imported as Python packages and execute in-process within N18, sharing a single memory space.
- **Contracts:** Communication between N18 and the modules is strictly typed via shared Pydantic V2 schemas (`contracts.py`). This enforces API-style boundaries within the monolithic codebase.

## Consequences

- **Positive:** Reduces the local development footprint to a single backend process (bootstrapped via `run.bat`). Provides a unified API surface for the frontend. Strong typing enforces strict module boundaries, easing future microservice extraction.
- **Negative:** Complete lack of process isolation. A memory exhaustion event in the N1 embedding module crashes the entire N18 API. Furthermore, N18 worker threads are blocked during synchronous external LLM calls in N5; a persistent `429 Too Many Requests` upstream error will cause a system-wide cascading failure.
- **Future Mitigation:** High-risk or heavy modules (starting with N1) will be extracted into independently deployable microservices in subsequent phases. The established Pydantic contracts will facilitate the safe transition from in-process function calls to network calls.
