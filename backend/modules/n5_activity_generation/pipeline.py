# =============================================================================
# pipeline.py — N5 Activity Generation
#
# Entry: generate_activities(data) → {"activities": [...], "metadata": {...}}
# Strategy: Pure LLM (Groq) activity generation.
# Schema: matches N5 __init__.py
# =============================================================================

import json
import random
import re
import hashlib
import time
from typing import Dict, List, Optional, Tuple, Union

from config import setup_logging
from .config import TARGET_ACT_COUNT
logger = setup_logging("N5")

from backend.shared.maps.activity_tags import ALL_TAGS
from . import llm_provider
from .schemas import N5GenerateInput


VALID_ACTIVITY_TYPES = {
    "food", "adventure", "culture", "nightlife", "shopping",
    "relaxation", "nature", "photography", "experience",
}
VALID_TAGS = sorted(ALL_TAGS.keys())
VALID_TAGS_SET = set(ALL_TAGS.keys())

# =============================================================================
# PUBLIC ENTRY POINT
# =============================================================================

def generate_activities(data: Union[N5GenerateInput, dict]) -> dict:
    t0 = time.time()
    
    # ─── Step 0: Early Exit Check ────────────────────────────────────────────
    if TARGET_ACT_COUNT <= 0:
        logger.info("module=N5 op=generate status=ok msg=\"Skipping generation (config set to 0)\"")
        return {
            "activities": [], 
            "metadata": {
                "per_location": [],
                "latency_ms": int((time.time() - t0) * 1000)
            }
        }

    user, locations = _parse_input(data)
    all_activities: List[Dict] = []
    llm_metas: List[Dict] = []

    for loc in locations:
        loc_id   = loc["location_id"]
        loc_name = loc["metadata"].get("name") or ""
        loc_desc = loc["metadata"].get("description") or ""
        loc_tags = loc["metadata"].get("tags") or []

        raw_activities, meta_out = _generate_for_location(
            location_name=loc_name,
            location_description=loc_desc,
            location_tags=loc_tags,
            user_tags=user.get("tags", []),
            user_text=user.get("text", "")
        )
        llm_metas.append({"location_id": loc_id, **meta_out})

        if raw_activities:
            mapped_activities = []
            for act in raw_activities:
                mapped_activities.append(_map_llm_to_output(act, loc_id))
            
            deduped = _deduplicate(mapped_activities)
            all_activities.extend(deduped)

    elapsed_ms = int((time.time() - t0) * 1000)
    total_tokens = sum(m.get("usage", {}).get("total_tokens", 0) for m in llm_metas if m.get("usage"))
    logger.info("module=N5 op=generate duration_ms=%d status=ok in_count=%d out_count=%d tokens=%d", elapsed_ms, len(locations), len(all_activities), total_tokens)
    return {
        "activities": all_activities, 
        "metadata": {
            "per_location": llm_metas,
            "latency_ms": elapsed_ms
        }
    }


# =============================================================================
# INPUT PARSING
# =============================================================================

def _parse_input(data: Union[N5GenerateInput, dict]) -> Tuple[Dict, List[Dict]]:
    """Validate and extract user, locations from input dict."""
    validated = N5GenerateInput.model_validate(data) if isinstance(data, dict) else data
    
    user = validated.user.model_dump()
    user_tags = user.get("tags") or []
    user["tags"] = [str(t).lower() for t in user_tags]
        
    normalized_locs = []
    for loc in validated.locations:
        loc_id = loc.location_id
        meta = loc.metadata.model_dump() if loc.metadata else {}
        normalized_locs.append({
            "location_id": loc_id,
            "metadata": {
                "name":        meta.get("name") or loc_id,
                "description": meta.get("description") or "",
                "tags":        [t.lower() for t in (meta.get("tags") or [])],
                "coordinates": meta.get("coordinates"),
                "address":     meta.get("address"),
            }
        })
        
    return user, normalized_locs


# =============================================================================
# LLM GENERATION
# =============================================================================

def _generate_for_location(
    location_name: str,
    location_description: str,
    location_tags: List[str],
    user_tags: List[str],
    user_text: str = "",
) -> tuple:
    """
    Generate activities list via LLM and return with meta dict.
    """
    t0 = time.time()
    meta = {"provider_used": None, "model_used": None, "latency_ms": 0, "usage": None}

    location_name_str = location_name or "Địa điểm chưa xác định"
    location_description_str = location_description or "Không có mô tả có sẵn."
    location_tags_str = ", ".join(location_tags) if location_tags else "không có"
    tags_str = ", ".join(user_tags) if user_tags else "không có sở thích cụ thể"
    user_context = f'\n🗣️ Yêu cầu của du khách: "{user_text}"' if user_text.strip() else ""

    valid_tags_str = ", ".join(VALID_TAGS)

    prompt = f"""Bạn là một thổ địa và chuyên gia du lịch cao cấp tại Việt Nam, am hiểu sâu sắc văn hóa, địa hình và những "góc khuất" ít người biết.

NHIỆM VỤ: Tạo đúng {TARGET_ACT_COUNT} hoạt động TRẢI NGHIỆM ĐỘC ĐÁO, ĐẬM CHẤT ĐỊA PHƯƠNG cho địa điểm dưới đây.

ĐỊA ĐIỂM: {location_name_str}
MÔ TẢ: {location_description_str}
ĐẶC ĐIỂM ĐỊA ĐIỂM (tags có sẵn): {location_tags_str}
SỞ THÍCH DU KHÁCH: {tags_str}{user_context}

TIÊU CHUẨN CHẤT LƯỢNG:
1. TÊN: Gợi cảm xúc, tò mò, không sáo rỗng (VD: "Săn mây trên đỉnh Langbiang", không dùng kiểu "Tham quan X").
2. MÔ TẢ: ~50 từ, tối đa 3 câu. Tập trung vào cảm giác, âm thanh, mùi vị, hoặc 1 mẹo chỉ dân địa phương mới biết. Không dùng tính từ sáo rỗng ("tuyệt vời", "không thể bỏ lỡ", "check-in sống ảo").
3. ĐA DẠNG: Trải đều các nhóm sau theo khả năng cho phép của {TARGET_ACT_COUNT} hoạt động (không lặp lại cùng 1 nhóm quá 2 lần liên tiếp trong danh sách): vận động/cảm giác mạnh, văn hóa/tâm linh, ẩm thực, nghệ thuật/thị giác, thư giãn/chữa lành.
4. THỰC TẾ: Phải là hoạt động có thật, khả thi tại {location_name_str}.
5. KHÔNG TRÙNG LẶP: Mỗi hoạt động phải khác biệt rõ rệt về nội dung lẫn tags với các hoạt động còn lại trong danh sách.
6. TAGS: Chọn 4-8 tags CHỈ từ danh sách chuẩn sau, không tự tạo tag mới: {valid_tags_str}.

ĐỊNH DẠNG JSON (bắt buộc tuân thủ chính xác):
- Trả về DUY NHẤT 1 JSON Object chứa key 'activities'. Key này là 1 Array gồm {TARGET_ACT_COUNT} Object, mỗi Object có các field:
  - name: string
  - description: string (tối đa 3 câu, nêu bật "hồn" của trải nghiệm)
  - tags: array 4-8 string, chỉ lấy từ danh sách chuẩn
  - activity_type: string, chọn đúng 1 trong: food, adventure, culture, nightlife, shopping, relaxation, nature, photography, experience
  - intensity: float 0.0-1.0 (mức độ sôi nổi/bận rộn)
  - physical_level: float 0.0-1.0 (mức độ tiêu tốn thể lực)
  - social_level: float 0.0-1.0 (mức độ tương tác xã hội/đông người)
  - reasoning: string ngắn gọn, giải thích vì sao hoạt động này phù hợp với sở thích và địa điểm

QUY TẮC ĐẦU RA (NGHIÊM NGẶT):
- KHÔNG giải thích, KHÔNG lời dẫn, KHÔNG markdown code block (```).
- Chỉ trả về đúng 1 JSON Object hợp lệ, bắt đầu bằng '{{' và kết thúc bằng '}}'.
- Tiếng Việt tự nhiên, sang trọng, giọng chuyên gia du lịch.
- Súc tích để tránh bị cắt ngang (giới hạn 4000 token).

TRẢ LỜI (chỉ JSON Object, không kèm gì khác):"""

    # Calling LLM
    response_text, provider_used, model_used, usage = _call_llm_chain(prompt)
    
    meta.update({
        "provider_used": provider_used,
        "model_used": model_used,
        "usage": usage,
        "latency_ms": int((time.time() - t0) * 1000)
    })

    if not response_text:
        logger.warning("module=N5 op=generate_for_location status=error error_type=no_llm_response location=%s", location_name)
        return [], meta

    raw_list = _parse_llm_response(response_text)
    if not raw_list:
        logger.warning("module=N5 op=generate_for_location status=error error_type=parse_failed location=%s", location_name)
        return [], meta

    valid_activities = []
    for act in raw_list:
        if _validate_activity(act):
            # Normalize and filter tags
            cleaned = [t.lower().strip() for t in act["tags"]]
            filtered = list(dict.fromkeys(t for t in cleaned if t in VALID_TAGS_SET))
            act["tags"] = filtered if filtered else cleaned # Fallback to raw tags if nothing matched
            valid_activities.append(act)

    return valid_activities, meta


def _call_llm_chain(prompt: str) -> tuple:
    chain = llm_provider.get_llm_chain()
    if not chain:
        logger.warning("LLM_CHAIN empty — no models available")
        return None, None, None, None

    from .config import MAX_RETRIES, RETRY_WAIT_BASE
    from .llm_provider import RetryableError
    
    for attempt in range(MAX_RETRIES + 1):
        if attempt > 0:
            wait_time = min(60.0, (RETRY_WAIT_BASE * (3 ** (attempt - 1))) + random.random())
            logger.info("N5 Pass %d failed for all models. Retrying entire chain in %.2fs...", attempt, wait_time)
            time.sleep(wait_time)

        for provider in chain:
            logger.info("Trying Groq model=%s", provider["model"])
            try:
                result = llm_provider.generate(provider, prompt, max_tokens=4000)
                if result:
                    return result, provider["name"], provider["model"], llm_provider.get_last_usage(provider)
            except RetryableError as e:
                logger.warning("Model %s failed in pass %d (Retryable: %s)", provider["model"], attempt + 1, e)
                continue
        
    logger.error("All models in chain failed after %d attempts", MAX_RETRIES + 1)
    return None, None, None, None


def _parse_llm_response(text: str) -> Optional[List[Dict]]:
    text = text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "activities" in data:
            return data["activities"]
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    # Fallback regex search for JSON array
    bracket_start = text.find('[')
    bracket_end = text.rfind(']')
    if bracket_start != -1:
        json_str = text[bracket_start: (bracket_end + 1 if bracket_end > bracket_start else len(text))]
        json_str = re.sub(r',\s*\]', ']', json_str)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            if json_str.strip().startswith('['):
                temp_str = json_str.strip()
                while len(temp_str) > 1:
                    last_brace = temp_str.rfind('}')
                    if last_brace == -1: break
                    try:
                        return json.loads(temp_str[:last_brace + 1] + ']')
                    except json.JSONDecodeError:
                        temp_str = temp_str[:last_brace]
    return None


def _validate_activity(act: Dict) -> bool:
    for field in ["name", "description", "tags"]:
        if field not in act: return False

    if not isinstance(act.get("name"), str) or not act.get("name").strip(): return False
    if not isinstance(act.get("description"), str) or not act.get("tags"): return False

    if act.get("activity_type") not in VALID_ACTIVITY_TYPES:
        act["activity_type"] = "experience"

    for field in ("intensity", "physical_level", "social_level"):
        if field in act:
            try:
                act[field] = max(0.0, min(1.0, float(act[field])))
            except (TypeError, ValueError):
                act[field] = 0.5

    return True


# =============================================================================
# LLM → N5 OUTPUT SCHEMA MAPPING
# =============================================================================

def _map_llm_to_output(act: Dict, location_id: str) -> Dict:
    name = act.get("name", "")
    return {
        "activity_id": _make_id(location_id, "act", name),
        "location_id": location_id,
        "metadata": {
            "name":          name,
            "description":   act.get("description", ""),
            "tags":          sorted(act.get("tags", [])),
            "activity_type": act.get("activity_type", "experience"),
            "intensity":     round(act.get("intensity", 0.5), 2),
            "physical_level": round(act.get("physical_level", 0.5), 2),
            "social_level":  round(act.get("social_level", 0.5), 2),
        }
    }


def _make_id(location_id: str, prefix: str, name: str = "") -> str:
    if name:
        h = hashlib.md5(name.encode()).hexdigest()[:6]
        return f"{prefix}_{h}"
    return f"{prefix}_{random.getrandbits(16):04x}"


def _deduplicate(activities: List[Dict]) -> List[Dict]:
    seen, unique = set(), []
    for a in activities:
        name = a["metadata"]["name"].lower()
        if name not in seen:
            seen.add(name)
            unique.append(a)
    return unique