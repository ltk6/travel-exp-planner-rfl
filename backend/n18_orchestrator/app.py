from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import time
from threading import Lock
from contextlib import asynccontextmanager

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

_SKIP_DEDUP_PATHS = {"/cache/reset", "/feedback/locations", "/feedback/activities"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("N18 Orchestrator booted successfully.")
    yield

app = FastAPI(
    title="N18 Orchestrator",
    description="Travel experience planner orchestration API (FastAPI).",
    version="1.0.0",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    lifespan=lifespan,
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
    import uuid
    import psutil
    from config import request_id_var
    
    req_id = str(uuid.uuid4())[:8]
    request_id_var.set(req_id)
    
    start = time.time()
    path = request.url.path
    
    process = psutil.Process()
    try:
        start_cpu = getattr(process.cpu_times(), 'user', 0) + getattr(process.cpu_times(), 'system', 0)
        start_ram = process.memory_info().rss
    except Exception:
        start_cpu, start_ram = 0, 0
        
    concurrency = len(_active_requests)
    input_mode = "unknown"
    fp = None

    request.state.stage_latencies = {}

    # 1. Internal API key check for protected routes
    if path in PROTECTED_ROUTES:
        provided = request.headers.get("X-Internal-Key", "")
        if not hmac.compare_digest(provided, INTERNAL_API_KEY):
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    if request.method == "POST" and path not in _SKIP_DEDUP_PATHS:
        try:
            body_bytes = await request.body()
            body_dict = json.loads(body_bytes) if body_bytes else {}
            
            has_dense = bool(body_dict.get("text") or body_dict.get("image") or body_dict.get("images") or body_dict.get("img_desc"))
            has_sparse = bool(body_dict.get("tags") or body_dict.get("location"))
            
            if has_dense and has_sparse:
                input_mode = "hybrid"
            elif has_dense:
                input_mode = "dense"
            elif has_sparse:
                input_mode = "sparse"
            else:
                input_mode = "empty"
                
            serialized = json.dumps(body_dict, sort_keys=True)
            fp = hashlib.sha256(f"{path}:{serialized}".encode()).hexdigest()
            with _active_requests_lock:
                if fp in _active_requests:
                    logger.warning("⚠️ Duplicate request: %s (fp=%s)", path, fp[:12])
                    return JSONResponse({"error": "Duplicate request in progress"}, status_code=409)
                _active_requests.add(fp)
        except Exception as exc:
            logger.warning("Failed to compute request fingerprint: %s", exc)

    status_msg = "ok"
    try:
        response = await call_next(request)
        if response.status_code >= 400:
            status_msg = "failed"
            
        if hasattr(request.state, "stage_latencies"):
            response.headers["X-Stage-Latencies"] = json.dumps(request.state.stage_latencies)
            
    except Exception as exc:
        status_msg = "failed"
        raise
    finally:
        if fp:
            with _active_requests_lock:
                _active_requests.discard(fp)
        duration = time.time() - start
        latency_ms = int(duration * 1000)
        
        try:
            end_cpu = getattr(process.cpu_times(), 'user', 0) + getattr(process.cpu_times(), 'system', 0)
            end_ram = process.memory_info().rss
            cpu_seconds = end_cpu - start_cpu
            ram_delta_mb = (end_ram - start_ram) / (1024 * 1024)
        except Exception:
            cpu_seconds = 0
            ram_delta_mb = 0

        stage_pct = {}
        if hasattr(request.state, "stage_latencies") and latency_ms > 0:
            for stage, ms in request.state.stage_latencies.items():
                stage_pct[stage] = round((ms / latency_ms) * 100, 1)

        logger.info(
            "ORCHESTRATOR | req_id=%s mode=%s status=%s total_ms=%d concurrency=%d cpu_s=%.3f ram_delta_mb=%.1f stages_pct=%s",
            req_id, input_mode, status_msg, latency_ms, concurrency, cpu_seconds, ram_delta_mb, json.dumps(stage_pct)
        )

    return response

# ── Include routes ────────────────────────────────────────────────────────────
app.include_router(router)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import subprocess
    import psutil
    try:
        commit_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.STDOUT).decode().strip()
    except Exception:
        commit_hash = "unknown"
    try:
        cpu_count = psutil.cpu_count(logical=True)
        ram_total = psutil.virtual_memory().total / (1024 ** 3)
        is_local = "windows" in sys.platform.lower() or os.name == 'nt' or os.getenv("IS_LOCAL") == "1"
        hardware = f"CPU={cpu_count}, RAM={ram_total:.1f}GB, Env={'local' if is_local else 'instance'}"
    except Exception:
        hardware = "unknown"
    logger.info("ONCE PER RUN | Git Commit: %s | Hardware: %s", commit_hash, hardware)

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
