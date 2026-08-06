from __future__ import annotations

import os

from fastapi import APIRouter
from fastapi.responses import Response

from config import GROQ_API_KEY, setup_logging
from backend.n18_orchestrator.utils import err
from backend.n18_orchestrator.services import IMG_CACHE_DIR, get_all_locations_cached

logger = setup_logging("N18.general")

general_router = APIRouter()

# 1x1 transparent PNG used when an image is not found
_TRANSPARENT_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00"
    b"\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
)


# ── Routes ────────────────────────────────────────────────────────────────────

@general_router.get("/health")
async def health() -> dict:
    from backend.modules.n5_activity_generation.llm_provider import get_llm_chain

    # N1 embedding model
    try:
        from backend.modules.n1_embedding.embedder import get_model
        n1_status = "ok" if get_model() is not None else "not_loaded"
    except Exception as exc:
        logger.error("N1 embedding model failed to load: %s", exc)
        n1_status = "error"

    # N3 database
    try:
        from backend.n3_database.db_manager import _get_connection
        conn = _get_connection()
        conn.close()
        n3_status = "db_connected"
    except Exception:
        n3_status = "file_storage"

    chain = get_llm_chain()
    return {
        "status": "ok",
        "services": {
            "n1_embedding":   n1_status,
            "n3_database":    n3_status,
            "llms_available": bool(GROQ_API_KEY),
        },
        "pipeline": ["n1", "n2", "n3", "n4", "n5", "n6"],
        "llm_chain": [
            {"name": p["name"], "model": p["model"], "rpm_limit": p["rpm_limit"]}
            for p in chain
        ],
    }


@general_router.get("/api/images/{filename:path}")
async def serve_image(filename: str) -> Response:
    """Serve location images from N18's local disk cache, fetching from PostgreSQL on miss."""
    if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
        err("Invalid filename", 400)

    file_path = os.path.join(IMG_CACHE_DIR, filename)

    # 1. Disk cache hit
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                img_bytes = f.read()
            return Response(
                content=img_bytes,
                media_type="image/jpeg",
                headers={"Cache-Control": "public, max-age=86400"},
            )
        except Exception as exc:
            logger.warning("Failed to read image from local cache %s: %s", filename, exc)

    # 2. Cache miss — fetch from PostgreSQL
    try:
        base = filename.rsplit(".", 1)[0]
        if "_" not in base:
            err("Image not found", 404)
        location_id, idx_str = base.rsplit("_", 1)
        idx = int(idx_str)

        from backend.n3_database import get_location_image_by_index
        img_bytes = get_location_image_by_index(location_id, idx)

        if not img_bytes:
            return Response(content=_TRANSPARENT_PNG, media_type="image/png")

        # Write to disk cache
        try:
            os.makedirs(IMG_CACHE_DIR, exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(img_bytes)
        except Exception as exc:
            logger.warning("Failed to write image to local cache %s: %s", filename, exc)

        return Response(
            content=img_bytes,
            media_type="image/jpeg",
            headers={"Cache-Control": "public, max-age=86400"},
        )
    except Exception as exc:
        logger.error("Error serving image: %s", exc)
        err(str(exc), 500)


@general_router.post("/cache/reset")
async def reset_cache() -> dict:
    """Force a full cache refresh from N3."""
    get_all_locations_cached(force_refresh=True)
    return {"status": "success", "message": "Cache successfully refreshed from N3"}


@general_router.get("/cache/fingerprint")
async def get_fingerprint() -> dict:
    """Return the current DB version fingerprint."""
    from backend.n3_database.db_manager import get_db_fingerprint
    return {"fingerprint": get_db_fingerprint()}
