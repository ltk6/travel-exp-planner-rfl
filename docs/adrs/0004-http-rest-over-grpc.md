# 4. HTTP REST over gRPC (Phase 1)

**Date:** 2026-08-08
**Status:** Accepted

## Context

N1 is extracted as a standalone service (ADR-0003). A communication protocol between N18 (hub) and N1 (spoke) is required.

## Decision

Use HTTP REST for inter-service communication between N18 and isolated microservices. gRPC is not adopted at this stage.

## Consequences

- **Positive:** Implementation, debugging, and tooling remain simple.
- **Positive:** Protobuf compilation and schema management are not needed in Phase 1.
- **Negative:** Latency and payload sizes may be higher than gRPC under load. (Protocol can be revisited if performance bottlenecks appear in later phases).
