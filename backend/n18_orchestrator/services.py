"""
N18 Orchestrator — Lazy-loading service proxies + location cache.
All module contracts are imported from individual module schemas.py files.
"""

from __future__ import annotations

import base64
import json
import os
import time

import logging

from config import setup_logging

logger = setup_logging("N18.services")

# ── Lazy-loading module proxies ───────────────────────────────────────────────
# Each function self-replaces on first call so subsequent calls are direct.

def get_all_locations(*args, **kwargs):
    global get_all_locations
    from backend.n3_database import get_all_locations as fn
    get_all_locations = fn
    return fn(*args, **kwargs)

def get_db_fingerprint(*args, **kwargs):
    global get_db_fingerprint
    from backend.n3_database.db_manager import get_db_fingerprint as fn
    get_db_fingerprint = fn
    return fn(*args, **kwargs)


def embed(*args, **kwargs):
    global embed
    from backend.modules.n1_embedding import embed as fn
    embed = fn
    return fn(*args, **kwargs)

def embed_batch(*args, **kwargs):
    global embed_batch
    from backend.modules.n1_embedding import embed_batch as fn
    embed_batch = fn
    return fn(*args, **kwargs)

def light_embed(*args, **kwargs):
    global light_embed
    from backend.modules.n1_embedding import light_embed as fn
    light_embed = fn
    return fn(*args, **kwargs)

def light_embed_batch(*args, **kwargs):
    global light_embed_batch
    from backend.modules.n1_embedding import light_embed_batch as fn
    light_embed_batch = fn
    return fn(*args, **kwargs)

def process_image(*args, **kwargs):
    global process_image
    from backend.modules.n2_image_processing import process_image as fn
    process_image = fn
    return fn(*args, **kwargs)

def rank_locations(*args, **kwargs):
    global rank_locations
    from backend.modules.n4_location_ranking import rank_locations as fn
    rank_locations = fn
    return fn(*args, **kwargs)

def rank_activities(*args, **kwargs):
    global rank_activities
    from backend.modules.n6_activity_ranking.pipeline import rank_activities as fn
    rank_activities = fn
    return fn(*args, **kwargs)

def generate_activities(*args, **kwargs):
    global generate_activities
    from backend.modules.n5_activity_generation.pipeline import generate_activities as fn
    generate_activities = fn
    return fn(*args, **kwargs)

def process_feedback(*args, **kwargs):
    global process_feedback
    from backend.modules.n17_feedback_processing import process_feedback as fn
    process_feedback = fn
    return fn(*args, **kwargs)

# ── Location image cache ──────────────────────────────────────────────────────
_CACHE_DIR = os.path.dirname(__file__)
CACHE_FILE = os.path.join(_CACHE_DIR, "location_cache.json")
IMG_CACHE_DIR = os.path.join(_CACHE_DIR, "image_cache")
os.makedirs(IMG_CACHE_DIR, exist_ok=True)

_CACHED_LOCATIONS_DATA: list | None = None
_CACHED_FINGERPRINT: str | None = None

# Short TTL to avoid hammering Postgres on every request
_FP_TTL_SEC = 10.0
_FP_CACHE: dict = {"value": None, "expires": 0.0}


def _fingerprint_cached() -> str:
    now = time.time()
    if _FP_CACHE["value"] is not None and now < _FP_CACHE["expires"]:
        return _FP_CACHE["value"]
    fp = get_db_fingerprint()
    _FP_CACHE["value"] = fp
    _FP_CACHE["expires"] = now + _FP_TTL_SEC
    return fp


def get_all_locations_cached(force_refresh: bool = False) -> list:
    """
    Hybrid cache: RAM → disk (location_cache.json) → N3 database.
    Images are excluded from cache to keep footprint small (lazy-served via /api/images/).
    """
    global _CACHED_LOCATIONS_DATA, _CACHED_FINGERPRINT

    current_fp = _fingerprint_cached()

    if not force_refresh:
        # 1. RAM hit
        if _CACHED_LOCATIONS_DATA and _CACHED_FINGERPRINT == current_fp:
            return _CACHED_LOCATIONS_DATA

        # 2. Disk hit
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                if cached.get("fingerprint") == current_fp:
                    _CACHED_LOCATIONS_DATA = cached.get("data", [])
                    _CACHED_FINGERPRINT = current_fp
                    logger.info("Cache Hit (Disk): loaded %d locations", len(_CACHED_LOCATIONS_DATA))
                    return _CACHED_LOCATIONS_DATA
            except Exception as exc:
                logger.warning("Failed to read disk cache: %s", exc)

    # 3. Miss — fetch from N3
    logger.info("Cache Miss: fetching fresh data from N3 (lazy images)...")
    raw = get_all_locations(include_images=False)
    if raw.get("status") != "success":
        return []

    locations = raw.get("data", [])
    for loc in locations:
        loc["images"] = []

    _CACHED_LOCATIONS_DATA = locations
    _CACHED_FINGERPRINT = current_fp

    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"fingerprint": current_fp, "data": locations}, f, ensure_ascii=False)
    except Exception as exc:
        logger.warning("Failed to write disk cache: %s", exc)

    return _CACHED_LOCATIONS_DATA


def get_image_urls(location_id: str) -> list[str]:
    """Return lazy image URLs served by /api/images/{filename}."""
    return [
        f"/api/images/{location_id}_0.jpg",
        f"/api/images/{location_id}_1.jpg",
        f"/api/images/{location_id}_2.jpg",
    ]



