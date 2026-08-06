from __future__ import annotations

import base64

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.modules.n1_embedding.schemas import N1EmbedInput
from backend.modules.n2_image_processing.schemas import N2ImageInput
from backend.modules.n4_location_ranking.schemas import N4RankInput, UserVectors
from backend.modules.n17_feedback_processing.schemas import N17FeedbackInput
from config import setup_logging
from backend.n18_orchestrator.config import TOP_K_LOCATIONS, API_DEBUG
from backend.n18_orchestrator.utils import err, safe_vec
from backend.n18_orchestrator.services import (
    embed,
    rank_locations,
    process_feedback,
    process_image,
    get_all_locations_cached,
    get_image_urls,
)
from backend.shared.weights import get_weights
logger = setup_logging("N18.recommend")

locations_router = APIRouter()


# ── Service logic ─────────────────────────────────────────────────────────────

def recommend_service(body: dict) -> dict:
    text = body.get("text", "").strip()
    tags = body.get("tags", [])
    constraints = body.get("constraints", {})
    context_data = body.get("context", {})
    top_k = int(body.get("top_k_locations", TOP_K_LOCATIONS))

    logger.info("N18 — Starting recommendation flow (text='%s', tags=%s)", text, tags)

    # ── N2 — Image → img_desc ────────────────────────────────────────────────
    img_desc = body.get("img_desc", "")
    image_b64 = ""
    if not img_desc:
        image_b64 = body.get("image", "")
        if not image_b64 and body.get("images"):
            imgs = body.get("images", [])
            if isinstance(imgs, list) and imgs:
                image_b64 = imgs[0]

        if image_b64:
            try:
                logger.info("N18 — Base64 image detected. Processing via N2...")
                b64_data = image_b64.split(",")[1] if "," in image_b64 else image_b64
                img_bytes = base64.b64decode(b64_data)
                n2_result = process_image(N2ImageInput(image=img_bytes))
                img_desc = n2_result.get("img_desc", "")
                logger.info("N18 — N2 complete. img_desc='%s'", img_desc)
            except Exception as exc:
                logger.warning("N2 processing failed: %s", exc)

    # ── N1 — Build user vectors ───────────────────────────────────────────────
    logger.info("N18 — Embedding user query via N1 (BGE-M3)...")
    n1_result = embed(N1EmbedInput(text=text, tags=tags, img_desc=img_desc))

    text_k = n1_result.get("text_k", 0)
    tags_k = n1_result.get("tags_k", 0)
    vectors = n1_result.get("vectors", {})
    user_vectors = {
        "text":     safe_vec(vectors.get("text")),
        "aug_text": safe_vec(vectors.get("aug_text")),
        "aug_tags": safe_vec(vectors.get("aug_tags")),
        "img_desc": safe_vec(vectors.get("img_desc")),
    }

    # ── N3 — Fetch locations ──────────────────────────────────────────────────
    locations = get_all_locations_cached()
    logger.info("N18 — Retrieved %d location candidates from N3 cache.", len(locations))

    # ── N4 — Rank locations ───────────────────────────────────────────────────
    logger.info("N18 — Ranking via N4 (text_k=%d, tags_k=%d)...", text_k, tags_k)
    for loc in locations:
        loc["location_vectors"] = loc.get("vectors")

    n4_result = rank_locations(N4RankInput(
        text_k=text_k,
        tags_k=tags_k,
        user_vectors=UserVectors(**user_vectors),
        locations=locations,
        top_k=top_k,
    ))
    ranked = n4_result.get("locations", [])

    # ── Enrich ranked results ─────────────────────────────────────────────────
    for loc_rank in ranked:
        loc_id = loc_rank.get("location_id")
        loc_rank["images"] = get_image_urls(loc_id)
        original = next((l for l in locations if l["location_id"] == loc_id), {})
        loc_rank["metadata"] = original.get("metadata", {})
        loc_rank["geo"] = original.get("geo", {})

    top_match = ranked[0].get("location_id", "N/A") if ranked else "None"
    top_score = ranked[0].get("score", 0.0) if ranked else 0.0
    logger.info("N18 — Top match: '%s' (score=%.4f)", top_match, top_score)

    response: dict = {"locations": ranked}

    if API_DEBUG:
        response["trace"] = {
            "user": {
                "input": {
                    "text": text, "tags": tags,
                    "constraints": constraints, "context": context_data,
                    "has_image": bool(image_b64),
                },
                "n2_image": {"img_desc": img_desc},
                "n1_embedding": {
                    "text_k": text_k, "tags_k": tags_k,
                    "preprocessed": n1_result.get("preprocessed", {}),
                },
                "user_vectors": user_vectors,
                "vector_dims": {k: len(v) if v else 0 for k, v in user_vectors.items()},
            },
            "ranking": {
                "text_k": text_k, "tags_k": tags_k,
                "weights_used": get_weights(text_k, tags_k),
                "top_k": top_k, "ranked": ranked,
            },
            "debug": {
                "total_locations": len(locations),
                "pipeline": {"n1": "embedding", "n2": "image_processing",
                             "n3": "database_fetch", "n4": "location_ranking"},
            },
        }

    if body.get("refined"):
        response["refined"] = body["refined"]

    return response


def feedback_recommend_service(body: dict) -> dict:
    old_text = body.get("text", "")
    old_tags = body.get("tags", [])
    old_img_desc = body.get("img_desc", "")
    feedback = body.get("feedback", "")

    if not feedback:
        return recommend_service(body)

    logger.info("N18 (N17) — Processing recommend feedback: '%s'", feedback)
    refined = process_feedback(N17FeedbackInput(
        user_input=old_text,
        user_tags=old_tags,
        img_desc=old_img_desc,
        feedback_text=feedback,
    ))

    refined_text = refined.get("refined_text", "")
    refined_tags = refined.get("refined_tags", [])
    refined_img_desc = refined.get("refined_img_desc", "")

    if not refined_text and not refined_tags:
        logger.info("N18 (N17) returned empty refinement. Short-circuiting.")
        return {
            "status": "unchanged",
            "locations": [],
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
    logger.info("N18 (N17) — Refined. text='%s', tags=%s", new_body["text"], new_body["tags"])
    result = recommend_service(new_body)
    result["refined"] = {
        "text":        new_body["text"],
        "tags":        new_body["tags"],
        "img_desc":    new_body["img_desc"],
        "explanation": refined.get("explanation", ""),
    }
    return result


# ── Routes ────────────────────────────────────────────────────────────────────

@locations_router.post("/locations")
async def recommend(body: dict) -> dict:
    if not any(body.get(k) for k in ("text", "tags", "image", "images", "img_desc")):
        err("Provide text, tags, or image")
    try:
        return recommend_service(body)
    except Exception as exc:
        logger.error("Recommend service failed: %s", exc)
        err(str(exc), 500)


@locations_router.post("/feedback/locations")
async def feedback_recommend(body: dict) -> dict:
    if not body.get("feedback"):
        err("Missing feedback text")
    try:
        return feedback_recommend_service(body)
    except Exception as exc:
        logger.error("Feedback recommend failed: %s", exc)
        err(str(exc), 500)
