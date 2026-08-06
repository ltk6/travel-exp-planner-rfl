"""N3: PostgreSQL-backed location persistence API."""

from __future__ import annotations

from .db_manager import (
    get_all_locations,
    get_db_fingerprint,
    init_db,
    save_location,
    init_profile_db,
    register_user,
    login_user,
    save_rec_turn,
    get_user_history,
    get_location_image_by_index,
)
from .schemas import N3RegisterInput, N3LoginInput, N3SaveHistoryInput

__all__ = [
    "get_all_locations",
    "get_db_fingerprint",
    "init_db",
    "save_location",
    "init_profile_db",
    "register_user",
    "login_user",
    "save_rec_turn",
    "get_user_history",
    "get_location_image_by_index",
    "N3RegisterInput",
    "N3LoginInput",
    "N3SaveHistoryInput",
]