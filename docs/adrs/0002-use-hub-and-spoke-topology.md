# 2. Use Hub-and-Spoke Topology

**Date:** 2026-08-06  
**Status:** Accepted

## Context
The frontend (N16) needs a structured interface to seamlessly consume multiple domain-specific ML and processing modules (N1-N17) while maintaining a foundation for future decoupling.

## Decision
Implement a Hub-and-Spoke topology.
- **The Hub:** N18 (FastAPI Orchestrator) serves as the central API gateway and orchestrator.
- **The Spokes:** Domain-specific modules (N1-N17) deliver specialized, atomic functions.
- **Execution Model:** Phase 0 imports all spokes as Python packages executing in-process within N18's memory space.
- **Contracts:** Communication between N18 and the modules is strictly typed via shared Pydantic V2 schemas (`contracts.py`) to enforce API-style boundaries.

## Consequences
- **Positive:** Reduces the local development footprint to a single backend process (`run.bat`). Provides a unified API surface. Strong typing enforces strict boundaries, simplifying future microservice extraction.
- **Negative:** Zero process isolation. Memory exhaustion in N1 crashes the N18 API. Synchronous external LLM calls in N5 block N18 worker threads; a persistent `429` upstream error causes a system-wide cascading failure.
- **Future Mitigation:** High-risk or heavy modules (starting with N1) will be extracted into independently deployable microservices. Existing Pydantic contracts will transition to network payloads.
