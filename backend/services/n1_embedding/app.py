from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

# Add the repository root to sys.path so we can import 'config'
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root not in sys.path:
    sys.path.insert(0, _root)

from config import setup_logging
from .embedder import get_model, get_light_model
from .pipeline import embed, embed_batch, light_embed, light_embed_batch
from .schemas import N1EmbedInput, N1EmbedOutput

logger = setup_logging("N1.service")

_models_loaded = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _models_loaded
    logger.info("Initializing N1 service: Pre-loading embedding models...")
    try:
        # Pre-load heavy models into CPU/GPU memory on startup
        get_model()
        get_light_model()
        _models_loaded = True
        logger.info("N1 embedding models loaded successfully. Service ready.")
    except Exception as exc:
        logger.error(f"Failed to load N1 embedding models during startup: {exc}")
    yield


app = FastAPI(
    title="N1 Embedding Service",
    description="Microservice for BGE-M3 and Multilingual-E5-Small text vector embeddings",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    """Verify service health and model load state."""
    if _models_loaded:
        return {"status": "healthy", "models_loaded": True}
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "unhealthy", "models_loaded": False, "detail": "Models are loading or failed to load"},
    )


@app.post("/embed", response_model=N1EmbedOutput)
def route_embed(payload: N1EmbedInput):
    """Generate multi-channel BGE-M3 embeddings for a single input."""
    try:
        return embed(payload)
    except Exception as exc:
        logger.error(f"Error in /embed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding failed: {str(exc)}",
        )


@app.post("/light-embed", response_model=N1EmbedOutput)
def route_light_embed(payload: N1EmbedInput, task_type: str = "passage"):
    """Generate multi-channel E5 embeddings for a single input."""
    try:
        return light_embed(payload, task_type=task_type)
    except Exception as exc:
        logger.error(f"Error in /light-embed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Light embedding failed: {str(exc)}",
        )


@app.post("/embed-batch", response_model=List[N1EmbedOutput])
def route_embed_batch(payload: List[N1EmbedInput]):
    """Generate multi-channel BGE-M3 embeddings in optimal batch pass."""
    try:
        return embed_batch(payload)
    except Exception as exc:
        logger.error(f"Error in /embed-batch: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch embedding failed: {str(exc)}",
        )


@app.post("/light-embed-batch", response_model=List[N1EmbedOutput])
def route_light_embed_batch(payload: List[N1EmbedInput], task_type: str = "passage"):
    """Generate multi-channel E5 embeddings in optimal batch pass."""
    try:
        return light_embed_batch(payload, task_type=task_type)
    except Exception as exc:
        logger.error(f"Error in /light-embed-batch: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Light batch embedding failed: {str(exc)}",
        )
