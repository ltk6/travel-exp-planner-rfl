from __future__ import annotations

from fastapi import APIRouter

from config import setup_logging
from backend.n18_orchestrator.utils import err
from backend.n18_orchestrator.services import get_all_locations_cached, get_image_urls

logger = setup_logging("N18.locations")

explore_router = APIRouter()


# ── Service logic ─────────────────────────────────────────────────────────────

def explore_locations_service() -> dict:
    locations = get_all_locations_cached()
    out = []
    for loc in locations:
        loc_id = loc.get("location_id")
        imgs = get_image_urls(loc_id) if loc_id else []
        out.append({
            "location_id":  loc_id,
            "metadata":     loc.get("metadata"),
            "geo":          loc.get("geo"),
            "image":        imgs[0] if imgs else None,
            "images_count": len(imgs),
        })
    return {"status": "success", "total": len(out), "data": out}


# ── Routes ────────────────────────────────────────────────────────────────────

@explore_router.post("/explore")
async def list_locations() -> dict:
    """Slim list of all locations for Explore mode — no vectors, one thumbnail per location."""
    try:
        return explore_locations_service()
    except Exception as exc:
        logger.error("Explore locations failed: %s", exc)
        err(str(exc), 500)
