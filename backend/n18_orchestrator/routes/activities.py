from __future__ import annotations

from fastapi import APIRouter, Request
import time

from backend.services.n1_embedding.schemas import N1EmbedInput

from backend.modules.n5_activity_generation.schemas import (
    N5GenerateInput, N5UserInput, N5LocationItem, N5LocationMetadata,
)
from backend.modules.n6_activity_ranking.schemas import N6RankInput, UserInput
from backend.modules.n17_feedback_processing.schemas import N17FeedbackInput
from config import setup_logging
from backend.n18_orchestrator.config import TOP_K_ACTIVITIES
from backend.n18_orchestrator.utils import err, safe_vec
from backend.n18_orchestrator.services import (
    light_embed,
    light_embed_batch,
    generate_activities,
    rank_activities,
    process_feedback,
)

logger = setup_logging("N18.activities")

activities_router = APIRouter()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_enriched_activity(ra: dict, original: dict, fallback_loc_id: str) -> dict:
    """Merge a ranked activity (score/reason) with its original full dict into the frontend shape."""
    md  = original.get("metadata", {}) or {}
    plc = original.get("place", {}) or {}
    sg  = original.get("signals", {}) or {}
    return {
        "activity_id": ra.get("activity_id"),
        "location_id": original.get("location_id") or ra.get("location_id") or fallback_loc_id,
        "score":  ra.get("score", 0),
        "reason": ra.get("reason", ""),
        "metadata": {
            "name":           md.get("name") or original.get("name") or "Trải nghiệm",
            "description":    md.get("description") or original.get("description") or "",
            "activity_type":  md.get("activity_type") or original.get("activity_type") or "nature",
            "indoor_outdoor": md.get("indoor_outdoor") or original.get("indoor_outdoor"),
            "tags":           md.get("tags", []) or original.get("tags", []),
            "source":         original.get("source") or "n5_generation",
            "coordinates":    plc.get("coordinates") or original.get("coordinates"),
            "distance_m":     plc.get("distance_from_anchor_m"),
            "rating":         sg.get("rating") or original.get("rating"),
            "image_url":      sg.get("image_url") or original.get("image_url"),
            "website":        sg.get("website") or original.get("website"),
            "opening_hours":  sg.get("opening_hours") or original.get("opening_hours"),
        },
    }


# ── Service logic ─────────────────────────────────────────────────────────────

def activities_service(request: Request, body: dict) -> dict:
    text     = body.get("text", "").strip()
    img_desc = body.get("img_desc", "")
    tags     = body.get("tags", [])
    location = body.get("location", {})
    top_k    = int(body.get("top_k_activities", TOP_K_ACTIVITIES))
    stage_lats = request.state.stage_latencies

    # ── N1 — Embed user query ─────────────────────────────────────────────────
    logger.info("N18 — Embedding user query via N1 Light...")
    _t0 = time.time()
    bge_result = light_embed(N1EmbedInput(text=text, tags=tags, img_desc=img_desc))
    stage_lats["N1_light_query"] = int((time.time() - _t0) * 1000)

    text_k   = bge_result.get("text_k", 0)
    tags_k   = bge_result.get("tags_k", 0)
    raw_vecs = bge_result.get("vectors", {})
    user_vectors = {
        "text":     safe_vec(raw_vecs.get("text")),
        "aug_text": safe_vec(raw_vecs.get("aug_text")),
        "aug_tags": safe_vec(raw_vecs.get("aug_tags")),
        "img_desc": safe_vec(raw_vecs.get("img_desc")),
    }

    # ── N5 — Generate activities ──────────────────────────────────────────────
    loc_meta_raw = location.get("metadata", {}) or {}
    _t0 = time.time()
    n5_result = generate_activities(N5GenerateInput(
        user=N5UserInput(text=text, tags=tags, img_desc=img_desc),
        locations=[N5LocationItem(
            location_id=location["location_id"],
            metadata=N5LocationMetadata(
                name=loc_meta_raw.get("name") or location.get("location_id"),
                description=loc_meta_raw.get("description"),
                tags=loc_meta_raw.get("tags") or [],
            ),
        )],
    ))
    stage_lats["N5"] = int((time.time() - _t0) * 1000)
    activities = n5_result.get("activities", [])
    per_loc_meta   = n5_result.get("metadata", {}).get("per_location", [])

    # ── N1 batch — Embed generated activities ─────────────────────────────────
    logger.info("N18 — Embedding %d activities via N1 Light...", len(activities))
    n1_batch = [
        N1EmbedInput(
            text=(a.get("metadata", {}).get("name") or "") + ". " + (a.get("metadata", {}).get("description") or ""),
            tags=a.get("metadata", {}).get("tags") or [],
            img_desc="",
        )
        for a in activities
    ]
    _t0 = time.time()
    bge_results = light_embed_batch(n1_batch, task_type="passage")
    stage_lats["N1_light_batch"] = int((time.time() - _t0) * 1000)
    for i, act in enumerate(activities):
        act["vectors"] = bge_results[i].get("vectors")

    # ── N6 — Rank activities ──────────────────────────────────────────────────
    _t0 = time.time()
    n6_result = rank_activities(N6RankInput(
        text_k=text_k, tags_k=tags_k,
        user_input=UserInput(text=text, tags=tags, img_desc=img_desc),
        user_vectors=user_vectors,
        activities=activities,
        top_k=top_k,
    ))
    stage_lats["N6"] = int((time.time() - _t0) * 1000)
    ranked = n6_result.get("activities", [])

    act_map = {a["activity_id"]: a for a in activities}
    enriched = [
        _build_enriched_activity(ra, act_map.get(ra.get("activity_id"), {}), location.get("location_id"))
        for ra in ranked
    ]

    return {
        "status":       "success",
        "location_id":  location.get("location_id"),
        "activities":   enriched,
        "meta":         per_loc_meta[0] if per_loc_meta else {},
        "ranking_meta": n6_result.get("metadata", {}),
    }


def feedback_activities_service(request: Request, body: dict) -> dict:
    old_text     = body.get("text", "")
    old_tags     = body.get("tags", [])
    old_img_desc = body.get("img_desc", "")
    feedback     = body.get("feedback", "")
    stage_lats = request.state.stage_latencies

    if not feedback:
        return activities_service(request, body)

    logger.info("N17 — Processing activity feedback: '%s'", feedback)
    _t0 = time.time()
    refined = process_feedback(N17FeedbackInput(
        user_input=old_text,
        user_tags=old_tags,
        img_desc=old_img_desc,
        feedback_text=feedback,
    ))
    stage_lats["N17"] = int((time.time() - _t0) * 1000)

    refined_text = refined.get("refined_text", "")
    refined_tags = refined.get("refined_tags", [])
    refined_img_desc = refined.get("refined_img_desc", "")

    if not refined_text and not refined_tags:
        logger.info("N17 returned empty refinement (spam/invalid feedback). Short-circuiting.")
        return {
            "status": "unchanged",
            "location_id": body.get("location", {}).get("location_id"),
            "activities": [],
            "refined": {
                "explanation": refined.get("explanation", ""),
            }
        }

    new_body = {
        **body,
        "text":     refined_text if refined_text else old_text,
        "tags":     refined_tags if refined_tags else old_tags,
        "img_desc": refined_img_desc if refined_img_desc else old_img_desc,
    }
    result = activities_service(request, new_body)
    result["refined"] = {
        "text":        new_body["text"],
        "tags":        new_body["tags"],
        "img_desc":    new_body["img_desc"],
        "explanation": refined.get("explanation", ""),
    }
    return result


# ── Routes ────────────────────────────────────────────────────────────────────

@activities_router.post("/activities")
async def get_activities(request: Request, body: dict) -> dict:
    if not body.get("location"):
        err("Missing location data")
    try:
        return activities_service(request, body)
    except Exception as exc:
        logger.error("Activities service failed: %s", exc)
        err(str(exc), 500)


@activities_router.post("/feedback/activities")
async def feedback_activities(request: Request, body: dict) -> dict:
    if not body.get("feedback"):
        err("Missing feedback text")
    try:
        return feedback_activities_service(request, body)
    except Exception as exc:
        logger.error("Feedback activities failed: %s", exc)
        err(str(exc), 500)
