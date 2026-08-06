from __future__ import annotations

from fastapi import APIRouter, Header
from itsdangerous import URLSafeTimedSerializer

from backend.n3_database.schemas import N3RegisterInput, N3LoginInput, N3SaveHistoryInput
from backend.n3_database.db_manager import register_user, login_user, save_rec_turn, get_user_history
from config import INTERNAL_API_KEY, setup_logging
from backend.n18_orchestrator.utils import err

logger = setup_logging("N18.profile")

profile_router = APIRouter()

# ── Token helpers ─────────────────────────────────────────────────────────────
_SECRET_KEY = INTERNAL_API_KEY if INTERNAL_API_KEY else "default-travel-secret-key-1823901"
_serializer = URLSafeTimedSerializer(_SECRET_KEY)
_TOKEN_MAX_AGE = 2592000  # 30 days


def _generate_token(user_id: int) -> str:
    return _serializer.dumps({"user_id": user_id})


def _verify_token(token: str) -> int:
    data = _serializer.loads(token, max_age=_TOKEN_MAX_AGE)
    return int(data["user_id"])


def _extract_bearer(authorization: str | None) -> str:
    """Parse 'Bearer <token>' header and raise 401 on failure."""
    if not authorization or not authorization.startswith("Bearer "):
        err("Yêu cầu đăng nhập", 401)
    return authorization.split(" ", 1)[1]


def _authenticated_user_id(authorization: str | None) -> int:
    token = _extract_bearer(authorization)
    try:
        return _verify_token(token)
    except Exception:
        err("Token không hợp lệ hoặc đã hết hạn", 401)


# ── Routes ────────────────────────────────────────────────────────────────────

@profile_router.post("/api/auth/register")
async def api_register(body: dict) -> dict:
    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        err("Thiếu username hoặc password")

    validated = N3RegisterInput.model_validate({"username": username, "password": password})
    res = register_user(validated.username, validated.password)
    if res.get("status") == "success" and "user_id" in res:
        res["token"] = _generate_token(res["user_id"])
    return res


@profile_router.post("/api/auth/login")
async def api_login(body: dict) -> dict:
    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        err("Thiếu username hoặc password")

    validated = N3LoginInput.model_validate({"username": username, "password": password})
    res = login_user(validated.username, validated.password)
    if res.get("status") == "success" and "user_id" in res:
        res["token"] = _generate_token(res["user_id"])
    return res


@profile_router.post("/api/feedback")
async def api_save_app_feedback(body: dict) -> dict:
    """Submit general app feedback from guests or logged-in users."""
    content = body.get("content", "")
    if not content or not content.strip():
        err("Nội dung feedback không được để trống")

    from backend.n3_database.db_manager import save_app_feedback
    return save_app_feedback(body.get("name", ""), body.get("email", ""), content)


@profile_router.post("/api/profile/history")
async def api_save_history(
    body: dict,
    authorization: str | None = Header(default=None),
) -> dict:
    """Persist a recommendation turn to the user's history."""
    token_user_id = _authenticated_user_id(authorization)

    user_id    = body.get("user_id")
    input_data = body.get("input_data")
    output_data = body.get("output_data")
    history_id = body.get("history_id")

    if not user_id or not input_data or not output_data:
        err("Thiếu parameters lưu lịch sử")
    if int(user_id) != token_user_id:
        err("Không có quyền lưu lịch sử cho người dùng này", 403)

    validated = N3SaveHistoryInput.model_validate({
        "user_id":    user_id,
        "input_data": input_data,
        "output_data": output_data,
        "history_id": history_id,
    })
    return save_rec_turn(validated.user_id, validated.input_data, validated.output_data, validated.history_id)


@profile_router.get("/api/profile/history/{user_id}")
async def api_get_history(
    user_id: int,
    authorization: str | None = Header(default=None),
) -> dict:
    """Retrieve all recommendation history for a user (requires auth)."""
    token_user_id = _authenticated_user_id(authorization)
    if user_id != token_user_id:
        err("Không có quyền xem lịch sử của người dùng này", 403)
    return get_user_history(user_id)
