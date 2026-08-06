from __future__ import annotations

from fastapi import APIRouter

from config import setup_logging

logger = setup_logging("N18.routes")

router = APIRouter()

# ── Sub-routers ───────────────────────────────────────────────────────────────
from .locations import locations_router
from .activities import activities_router
from .explore import explore_router
from .general import general_router
from .profile import profile_router

router.include_router(locations_router)
router.include_router(activities_router)
router.include_router(explore_router)
router.include_router(general_router)
router.include_router(profile_router)
