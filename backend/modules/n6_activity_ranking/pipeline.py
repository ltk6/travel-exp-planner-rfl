# =============================================================================
# N6 Activity Ranking Pipeline
#
# Score = W_SEMANTIC * semantic(4 channels, weights from get_weights)
#       + W_ATTRIBUTE * attribute(physical axes + completeness)
#
# Tags are handled exclusively inside semantic via the aug_tags channel.
# Attribute scoring is purely physical preference fit + data completeness.
# =============================================================================
from __future__ import annotations

import hashlib
import heapq
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from config import setup_logging
logger = setup_logging("N6")

from backend.shared.weights import get_weights
from backend.shared.math import cosine as _cosine_fn
from .preferences import infer_user_preferences
from .schemas import N6RankInput


# Top-level split
W_SEMANTIC  = 0.60
W_ATTRIBUTE = 0.40

# Attribute sub-weights (must sum to 1.0)
_ATTR_PHYS_W = 0.70   # physical axes fit: intensity / physical / social
_ATTR_COMP_W = 0.30   # data completeness

# Completeness field weights (must sum to 1.0)
_COMPLETENESS_WEIGHTS = {
    "description":   0.45,
    "tags":          0.30,
    "image_url":     0.10,
    "rating":        0.10,
    "opening_hours": 0.05,
}


# =============================================================================
# SEMANTIC SCORING  — all 4 channels, weights from get_weights()
# =============================================================================

def _cosine(a: list[float] | None, b: list[float] | None) -> float:
    if a and b and len(a) != len(b):
        logger.warning("[N6] Vector length mismatch: %d vs %d", len(a), len(b))
    return _cosine_fn(a, b)


def _semantic_score(
    user_vectors: Dict,
    act_vectors: Dict,
    weights: Dict[str, float],
) -> Tuple[float, bool]:
    """
    Weighted cosine similarity across all 4 channels.

    Channel mapping (user → activity):
        aug_tags  → aug_tags  (fallback to 'text' when activity has no aug_tags)
        aug_text  → text
        text      → text
        img_desc  → text

    Weights come from get_weights(text_k, tags_k) — not hardcoded.
    Returns (score [0,1], was_matched). was_matched=False → no channel had vectors.
    """
    channel_map = [
        # (user_key, act_key, weight_key)
        ("aug_tags", "aug_tags", "aug_tags"),
        ("aug_text", "text",     "aug_text"),
        ("text",     "text",     "text"),
        ("img_desc", "text",     "img_desc"),
    ]

    sum_score, total_weight = 0.0, 0.0

    for u_key, a_key, w_key in channel_map:
        w = weights.get(w_key, 0.0)
        if w == 0.0:
            continue

        v_user = user_vectors.get(u_key)
        v_act  = act_vectors.get(a_key)

        # Fallback: if activity has no aug_tags vector, compare against its text vector
        if not v_act and a_key == "aug_tags":
            v_act = act_vectors.get("text")

        if v_user and v_act:
            sim = _cosine(v_user, v_act)
            sum_score    += ((sim + 1.0) / 2.0) * w   # map [-1,1] → [0,1]
            total_weight += w

    if total_weight > 0:
        return sum_score / total_weight, True
    return 0.5, False


# =============================================================================
# ATTRIBUTE SCORING  — physical preference fit + completeness
# =============================================================================

def _physical_axes_score(
    activity: Dict,
    user_prefs: Dict[str, Optional[float]],
) -> float:
    """
    Measure fit between the activity's intensity / physical_level / social_level
    and the user preferences inferred by preferences.py.

    Returns 0.5 (neutral) when the user expressed no preference on any axis,
    or when the activity has no attribute data.
    """
    metadata = activity.get("metadata", {}) or {}
    signals  = activity.get("signals",  {}) or {}

    axis_fits: List[float] = []
    for axis, meta_key in [
        ("intensity", "intensity"),
        ("physical",  "physical_level"),
        ("social",    "social_level"),
    ]:
        u_pref = user_prefs.get(axis)
        if u_pref is None:
            continue   # no user preference → skip axis

        # Prefer signals (DB-cached) → metadata → root activity dict
        m_val = signals.get(meta_key) or metadata.get(meta_key) or activity.get(meta_key)
        if m_val is not None:
            axis_fits.append(max(0.0, 1.0 - abs(float(u_pref) - float(m_val))))

    return sum(axis_fits) / len(axis_fits) if axis_fits else 0.5


def _completeness_score(activity: Dict) -> float:
    """
    0.0 → 1.0 — rewards activities that have full descriptive data for display.
    desc + tags account for 75 % of the weight.
    """
    md = activity.get("metadata") or {}
    sg = activity.get("signals")  or {}
    score = 0.0

    if md.get("description") and str(md["description"]).strip():
        score += _COMPLETENESS_WEIGHTS["description"]
    if md.get("tags") or md.get("categories_raw"):
        score += _COMPLETENESS_WEIGHTS["tags"]
    if sg.get("image_url"):
        score += _COMPLETENESS_WEIGHTS["image_url"]
    if sg.get("rating") is not None:
        score += _COMPLETENESS_WEIGHTS["rating"]
    if sg.get("opening_hours"):
        score += _COMPLETENESS_WEIGHTS["opening_hours"]

    return score


def _attribute_score(
    activity: Dict,
    user_prefs: Dict[str, Optional[float]],
) -> float:
    """Combined attribute score: physical axes fit + data completeness."""
    phys_score = _physical_axes_score(activity, user_prefs)
    comp_score = _completeness_score(activity)
    return _ATTR_PHYS_W * phys_score + _ATTR_COMP_W * comp_score


# =============================================================================
# REASON BUILDER
# =============================================================================

_REASON_BY_TYPE = {
    "nature":      ["Khám phá cảnh quan tuyệt đẹp", "Hòa mình vào thiên nhiên {intensity_hint}đậm chất địa phương"],
    "adventure":   ["Thử thách bản thân với hoạt động {intensity_hint}đầy phấn khích", "Trải nghiệm cảm giác mạnh {intensity_hint}giữa thiên nhiên"],
    "food":        ["Thưởng thức tinh túy ẩm thực đặc trưng", "Khám phá hương vị địa phương độc đáo"],
    "culture":     ["Tìm hiểu chiều sâu văn hóa bản địa", "Trải nghiệm di sản và phong tục truyền thống"],
    "relaxation":  ["Phút giây thư giãn nhẹ nhàng", "Tìm lại sự cân bằng trong không gian yên bình"],
    "nightlife":   ["Sôi động và lung linh về đêm", "Khám phá nhịp sống về đêm đầy sắc màu"],
    "shopping":    ["Săn tìm những món quà lưu niệm độc bản", "Ghé thăm không gian mua sắm đậm chất địa phương"],
    "photography": ["Ghi lại những khoảnh khắc {intensity_hint}tuyệt đẹp", "Lưu giữ kỷ niệm qua những khung hình nghệ thuật"],
    "experience":  ["Kết nối sâu sắc với nhịp sống địa phương", "Trải nghiệm thực tế {intensity_hint}đầy chân thực và gần gũi"],
}
_REASON_DEFAULT  = ["Lựa chọn tuyệt vời cho hành trình của bạn", "Trải nghiệm thú vị không nên bỏ lỡ"]
_INTENSITY_LABELS = [(0.7, "mạnh mẽ"), (0.4, "vừa sức"), (0.0, "nhẹ nhàng")]


def _build_reason(activity: Dict, sem_score: float, attr_score: float) -> str:
    metadata = activity.get("metadata", {}) or {}
    signals  = activity.get("signals",  {}) or {}

    activity_type = (metadata.get("activity_type") or activity.get("activity_type") or "nature").lower()
    name_act = metadata.get("name") or activity.get("name") or "Trải nghiệm"

    intensity_val = signals.get("intensity") or metadata.get("intensity") or activity.get("intensity")
    intensity = float(intensity_val or 0.5)
    intensity_hint = next(
        (label for threshold, label in _INTENSITY_LABELS if intensity >= threshold),
        "nhẹ nhàng",
    ) + " "

    templates = _REASON_BY_TYPE.get(activity_type, _REASON_DEFAULT)
    idx = int(hashlib.md5(name_act.encode()).hexdigest(), 16) % len(templates)
    body = templates[idx].format(intensity_hint=intensity_hint)

    highlights = []
    if attr_score >= 0.75:
        highlights.append("rất hợp sở thích")
    if sem_score >= 0.75:
        highlights.append("đúng ý bạn tìm")

    suffix = f" ({', '.join(highlights)})" if highlights else ""
    return f"{body}{suffix}."


# =============================================================================
# ENTRY POINT
# =============================================================================

def rank_activities(data: Union[N6RankInput, Dict[str, Any]]) -> Dict[str, Any]:
    t0 = time.time()

    validated    = N6RankInput.model_validate(data) if isinstance(data, dict) else data
    user_input   = validated.user_input.model_dump()
    user_vectors = validated.user_vectors.model_dump()
    activities   = validated.activities
    top_k        = max(1, validated.top_k)
    text_k       = validated.text_k
    tags_k       = validated.tags_k

    if not activities or top_k <= 0:
        logger.info("N6 skipping ranking (0 activities or top_k <= 0)")
        return {"activities": [], "metadata": {"latency_ms": 0}}

    logger.info("Ranking %d activities (top_k=%d)", len(activities), top_k)

    # Derived once for all activities
    user_prefs = infer_user_preferences(user_input)
    weights    = get_weights(text_k, tags_k)

    scored_heap: list = []

    for activity in activities:
        vectors = activity.get("vectors", {}) or {}

        # ── Semantic (all 4 channels, weights from get_weights) ───────────────
        sem_raw, sem_matched = _semantic_score(user_vectors, vectors, weights)
        # Map [0,1] output into useful [0,1] range — scale from centre 0.5
        sem_scaled = max(0.0, min(1.0, (sem_raw - 0.5) * 2.0)) if sem_matched else 0.5

        # ── Attribute (physical fit + completeness) ───────────────────────────
        attr_score = _attribute_score(activity, user_prefs)

        # ── Final score ───────────────────────────────────────────────────────
        # Drop semantic weight only when absolutely no channel had vectors (rare).
        w_sem  = W_SEMANTIC  if sem_matched else 0.0
        w_attr = W_ATTRIBUTE
        total_w = w_sem + w_attr
        total   = (w_sem * sem_scaled + w_attr * attr_score) / total_w if total_w > 0 else 0.5

        heap_item = (total, activity.get("activity_id"), activity.get("location_id"), activity, sem_scaled, attr_score)

        if len(scored_heap) < top_k:
            heapq.heappush(scored_heap, heap_item)
        else:
            heapq.heappushpop(scored_heap, heap_item)

    top_activities = sorted(scored_heap, key=lambda x: x[0], reverse=True)

    final_results = []
    for score, act_id, loc_id, act_item, sem_s, attr_s in top_activities:
        # Smoothstep shaping into display range [0.65, 0.95]
        norm = max(0.0, min(1.0, score))
        shaped = 3 * (norm ** 2) - 2 * (norm ** 3)
        scaled_score = round(0.65 + shaped * 0.30, 4)
        final_results.append({
            "activity_id": act_id,
            "location_id": loc_id,
            "score":       scaled_score,
            "reason":      _build_reason(act_item, sem_s, attr_s),
        })

    elapsed_ms = int((time.time() - t0) * 1000)
    logger.info("Ranking complete. Returning %d activities (latency=%dms)", len(final_results), elapsed_ms)
    return {
        "activities": final_results,
        "metadata": {
            "user_prefs": user_prefs,
            "weights":    weights,
            "text_k":     text_k,
            "tags_k":     tags_k,
            "latency_ms": elapsed_ms,
        },
    }