# Phase 1: Container Network Topology

This diagram illustrates the Docker Compose network topology established in Phase 1. It details how the Next.js frontend, FastAPI orchestrator, isolated embedding service, and PostgreSQL database communicate across the internal Docker bridge network (`travel-exp-planner-refloursihed_default`).

```mermaid
graph TD
    %% Define styles
    classDef frontend fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff;
    classDef backend fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff;
    classDef model fill:#8b5cf6,stroke:#6d28d9,stroke-width:2px,color:#fff;
    classDef database fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#fff;
    classDef external fill:#64748b,stroke:#334155,stroke-width:2px,color:#fff;

    %% Nodes
    User(("fa:fa-user User Browser")):::external
    N16["fa:fa-desktop N16 Web UI<br/>(Next.js)"]:::frontend
    N18["fa:fa-server N18 Orchestrator<br/>(FastAPI)"]:::backend
    N1["fa:fa-brain N1 Embedding<br/>(BGE-M3 / FastAPI)"]:::model
    DB[("fa:fa-database N3 PostgreSQL<br/>(pgvector)")]:::database
    Groq(("fa:fa-cloud Groq API<br/>(Llama 3)")):::external

    %% Host mappings
    subgraph "Docker Host (Local Machine)"
        Port3000((":3000")):::external
        Port8000((":8000")):::external
        Port8001((":8001")):::external
        Port5432((":5432")):::external

        subgraph "Docker Bridge Network"
            N16
            N18
            N1
            DB
        end
    end

    %% Connections
    User -- "http://localhost:3000" --> Port3000
    Port3000 -.-> N16

    User -- "Direct API Access" --> Port8000
    Port8000 -.-> N18
    Port8001 -.-> N1
    Port5432 -.-> DB

    N16 -- "REST API (Server-side fetch)<br/>BACKEND_URL=http://n18_orchestrator:8000" --> N18
    N18 -- "REST API (POST /embed)<br/>N1_SERVICE_URL=http://n1_embedding:8001" --> N1
    N18 -- "psycopg2 pool<br/>postgresql://...db:5432" --> DB
    N18 -- "REST API<br/>(via N5/N17 modules)" --> Groq
```

## Network Security & Routing Constraints

1. **Service Names over Localhost:** Containers must address each other using their Docker service names (e.g., `http://n18_orchestrator:8000`, `http://n1_embedding:8001`) because `127.0.0.1` inside a container resolves to itself, not the Docker host.
2. **Next.js Build-Time Baking:** Environment variables accessed by Next.js during `npm run build` (like `BACKEND_URL`) are baked into the container image. We must inject these variables as `ARG` during the Docker build stage so the Next.js API routes proxy requests to the correct internal container rather than falling back to `localhost`.
3. **Internal API Key:** An `INTERNAL_API_KEY` is enforced by N18 for backend routes. N16 injects this key into headers when making server-side `fetch` requests across the Docker network.
