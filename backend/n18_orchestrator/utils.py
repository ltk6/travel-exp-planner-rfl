from __future__ import annotations

from fastapi import HTTPException
from fastapi.responses import JSONResponse


def err(msg: str, code: int = 400) -> HTTPException:
    """Raise a FastAPI HTTP exception. 5xx messages are sanitised."""
    if code >= 500:
        msg = "An internal server error occurred."
    raise HTTPException(status_code=code, detail=msg)


def safe_vec(v) -> list:
    """Safely coerce any vector-like value to a plain Python list."""
    if v is None:
        return []
    if isinstance(v, list):
        return v
    if hasattr(v, "tolist"):
        return v.tolist()
    try:
        return list(v)
    except (TypeError, ValueError):
        return []
