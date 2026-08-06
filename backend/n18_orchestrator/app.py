from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import time
from threading import Lock

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ── Path setup ────────────────────────────────────────────────────────────────
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root not in sys.path:
    sys.path.insert(0, _root)

from config import (
    setup_logging,
    INTERNAL_API_KEY,
)
from backend.n18_orchestrator.config import (
    PROTECTED_ROUTES,
    ALLOWED_ORIGINS,
    API_HOST as HOST,
    API_PORT as PORT,
    API_DEBUG as DEBUG,
)
from backend.n18_orchestrator.routes import router

logger = setup_logging("N18")

# ── Request deduplication state ───────────────────────────────────────────────
_active_requests: set[str] = set()
_active_requests_lock = Lock()

_SKIP_DEDUP_PATHS = {"/cache/reset", "/feedback/recommend", "/feedback/activities"}

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="N18 Orchestrator",
    description="Travel experience planner orchestration API (FastAPI).",
    version="1.0.0",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Middleware ────────────────────────────────────────────────────────────────

@app.middleware("http")
async def _lifecycle_middleware(request: Request, call_next):
    start = time.time()
    path = request.url.path
    fp = None

    # 1. Internal API key check for protected routes
    if path in PROTECTED_ROUTES:
        provided = request.headers.get("X-Internal-Key", "")
        if not hmac.compare_digest(provided, INTERNAL_API_KEY):
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    # 2. Idempotency / request deduplication for POST (excluding specific paths)
    if request.method == "POST" and path not in _SKIP_DEDUP_PATHS:
        try:
            body_bytes = await request.body()
            body_dict = json.loads(body_bytes) if body_bytes else {}
            serialized = json.dumps(body_dict, sort_keys=True)
            fp = hashlib.sha256(f"{path}:{serialized}".encode()).hexdigest()
            with _active_requests_lock:
                if fp in _active_requests:
                    logger.warning("⚠️ Duplicate request: %s (fp=%s)", path, fp[:12])
                    return JSONResponse({"error": "Duplicate request in progress"}, status_code=409)
                _active_requests.add(fp)
        except Exception as exc:
            logger.warning("Failed to compute request fingerprint: %s", exc)

    try:
        response = await call_next(request)
    finally:
        if fp:
            with _active_requests_lock:
                _active_requests.discard(fp)
        duration = time.time() - start
        logger.info("[%s] %s took %.4fs", request.method, path, duration)

    return response

# ── Include routes ────────────────────────────────────────────────────────────
app.include_router(router)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from backend.n3_database import init_profile_db
    try:
        init_profile_db()
    except Exception as exc:
        logger.error("Cannot initialize profile table: %s", exc)

    try:
        import uvicorn
        logger.info("N18 — Starting on http://%s:%d (debug=%s)", HOST, PORT, DEBUG)
        uvicorn.run(app, host=HOST, port=PORT, log_level="info")
    except ImportError:
        logger.error(
            "uvicorn is not installed. Install it with: pip install uvicorn[standard]"
        )
        sys.exit(1)
