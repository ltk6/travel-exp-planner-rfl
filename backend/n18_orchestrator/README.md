# N18: API Orchestrator

`N18` is the primary orchestrator and API gateway layer of the system. Built with FastAPI, it exposes asynchronous HTTP endpoints, enforces security/access headers, manages caching of location records and images, handles user auth session mappings, and coordinates the flow between AI spokes (N1–N17).

## Directory Structure

```text
backend/n18_orchestrator/
├── __init__.py         # Public API exports (app FastAPI instance)
├── app.py              # Application configuration, CORS, and middleware setup
├── config.py           # Endpoint ports, allowed origins, and route groupings
├── routes/             # Grouped API endpoints (locations, activities, profile, general)
├── services.py         # Lazy-loaded dependencies and orchestration service functions
├── utils.py            # Diagnostic tools and custom JSON/error formatters
├── location_cache.json # High-performance local cache of location vectors
├── requirements.txt    # Local orchestrator package dependencies
└── README.md           # This documentation
```

## Quick Start

Run the application using an ASGI server (e.g., `uvicorn`):

```python
import uvicorn
from backend.n18_orchestrator import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

## API Endpoints & Routes

### Public Endpoints

| Endpoint | Method | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `/health` | GET | No | Runtime state and server health stats. |
| `/recommend` | POST | Yes | Run embedding (N1), image description (N2), and location ranking (N4). |
| `/activities` | POST | No | Generate (N5) and rank (N6) custom activities for a target location. |
| `/locations` | GET | No | Fetch candidate locations for exploration view. |
| `/api/images/<file>` | GET | No | Lazily retrieve and cache location images. |

### Feedback & Caching Endpoints

| Endpoint | Method | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `/feedback/locations` | POST | Yes | Refine location recommendation list with user feedback (N17). |
| `/feedback/activities`| POST | Yes | Refine generated activities with user feedback (N17). |
| `/cache/reset` | POST | Yes | Force cache rebuild using PostgreSQL database records (N3). |

### Authentication & Profiles

| Endpoint | Method | Auth Required | Description |
| :--- | :--- | :--- | :--- |
| `/api/auth/register` | POST | No | Register new user account. |
| `/api/auth/login` | POST | No | Authenticate user credentials and return user ID. |
| `/api/profile/history`| POST | Yes | Log recommendation session output into user history (N3). |
| `/api/profile/history/<uid>`| GET | Yes | Retrieve full recommendation query history for user. |

## Request & Security Filters

### 1. Internal API Key Validation
Protected routes require the client to present the validation key in the request header:
```text
X-Internal-Key: <internal_api_secret_key>
```
*Requests with invalid keys are rejected with `401 Unauthorized`.*

### 2. Idempotency Guard
To prevent duplicate execution of long-running AI queries (e.g., double-clicks), N18 uses middleware to calculate a SHA-256 fingerprint of the request path + sorted JSON payload. Parallel matching requests are rejected with a `409 Conflict` until the first completes.

## Developer Guidelines

- **Lifespan Warmup:** The orchestrator uses a FastAPI lifespan handler to pre-load SentenceTransformer models, preventing initial request timeouts.
- **Dynamic Loading:** Services import heavy dependencies and sub-modules dynamically to ensure fast system startup.
- **Error Resilience:** Route handlers wrap spoke calls in middleware to log faults and return clean JSON instead of crashing.
