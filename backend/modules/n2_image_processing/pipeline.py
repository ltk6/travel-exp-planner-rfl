import json
import base64
import urllib.request
from PIL import Image
import io
import time
from typing import Union

from config import GROQ_API_KEY, setup_logging
from .config import GROQ_VISION_MODEL, GROQ_API_URL, USER_AGENT
logger = setup_logging("N2")

from .schemas import N2ImageInput, N2ImageOutput

def process_image(data: Union[N2ImageInput, dict]) -> dict:
    """
    The sole public API function of Module N2 (image processing).
    Uses Groq Vision (Llama 3.2 Vision).
    Input:  {"image": bytes}
    Output: {"img_desc": "..."}
    """
    start_time = time.perf_counter()
    validated = N2ImageInput.model_validate(data) if isinstance(data, dict) else data
    image_bytes = validated.image
    if not image_bytes:
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        logger.warning("module=N2 op=process_image duration_ms=%d status=error error_type=no_image", latency_ms)
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return N2ImageOutput(
            img_desc="",
            metadata={"error": "No image provided", "latency_ms": latency_ms}
        ).model_dump()

    # Image optimization

    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Optimize for Vision API: Downscale if too large and compress
        img.thumbnail((1560, 1560)) 
        
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Image optimized

        prompt = """
        Bạn là chuyên gia mô tả địa điểm du lịch.
        Quan sát ảnh và viết MỘT đoạn văn ngắn gọn, súc tích, giàu tính gợi hình bằng Tiếng Việt.

        YÊU CẦU TUYỆT ĐỐI:
        - Tối đa 50 từ — KHÔNG được vượt quá.
        - Nêu rõ: loại địa điểm, đặc điểm nổi bật nhất, cảm xúc/không khí.
        - Dùng ngôn ngữ biểu cảm, chọn lọc (không liệt kê dài dòng).
        - KHÔNG dùng lời dẫn 'Trong ảnh có...' hay 'Tôi thấy...'.
        - KHÔNG mô tả biển số xe, nhãn hiệu, ngày giờ.
        - Chỉ trả về đoạn văn, không giải thích thêm.
        """

        payload = {
            "model": GROQ_VISION_MODEL,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        }
                    }
                ]
            }],
            "max_tokens": 300,
        }

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            GROQ_API_URL, data=req_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        usage = result.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        # usage captured

        choices = result.get("choices", [])
        if not choices:
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            logger.warning("module=N2 op=process_image duration_ms=%d status=error error_type=empty_response", latency_ms)
            return N2ImageOutput(
                img_desc="", 
                metadata={"error": "Empty response from model", "latency_ms": latency_ms}
            ).model_dump()

        text = choices[0].get("message", {}).get("content", "")
        if not text:
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            logger.warning("module=N2 op=process_image duration_ms=%d status=error error_type=no_text", latency_ms)
            return N2ImageOutput(
                img_desc="", 
                metadata={"error": "No text returned (possible safety block or invalid image)", "latency_ms": latency_ms}
            ).model_dump()

        latency_ms = int((time.perf_counter() - start_time) * 1000)
        logger.info("module=N2 op=process_image duration_ms=%d status=ok in_bytes=%d out_chars=%d tokens=%d", latency_ms, len(image_bytes), len(text), prompt_tokens + completion_tokens)
        metadata = {
            "model": GROQ_VISION_MODEL,
            "latency_ms": latency_ms,
            "usage": {
                "prompt_tokens":     prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens":      prompt_tokens + completion_tokens,
            },
        }

        return N2ImageOutput(
            img_desc=text.strip(),
            metadata=metadata,
        ).model_dump()

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        logger.error("module=N2 op=process_image duration_ms=%d status=error error_type=http_error code=%s", latency_ms, e.code)
        return N2ImageOutput(
            img_desc="", 
            metadata={
                "error": f"HTTPError: {e.code} - {error_body}",
                "model": GROQ_VISION_MODEL, 
                "latency_ms": latency_ms
            }
        ).model_dump()
    except Exception as e:
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        logger.error("module=N2 op=process_image duration_ms=%d status=error error_type=exception msg=\"%s\"", latency_ms, str(e)[:50])
        return N2ImageOutput(
            img_desc="",
            metadata={
                "error": str(e),
                "model": GROQ_VISION_MODEL, 
                "latency_ms": latency_ms
            }
        ).model_dump()
