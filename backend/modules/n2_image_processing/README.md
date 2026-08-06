# Module N2: Image Processing

`N2` is the vision-to-text bridge in the pipeline. It accepts raw image bytes, optimizes the image for the configured vision model, and returns a short Vietnamese scene description that downstream modules (like N1) can embed and rank semantically.

---

## Directory Structure

```text
backend/modules/n2_image_processing/
├── __init__.py         # Public API exports (process_image, N2ImageInput, etc.)
├── pipeline.py         # Entry points, image compression, and Groq Vision API logic
├── schemas.py          # Validation schemas (Input/Output contracts)
├── config.py           # Local model configurations
└── requirements.txt    # Local dependencies
```

---

## Quick Start

You can import and execute the module directly:

```python
from backend.modules.n2_image_processing import process_image, N2ImageInput

# Read sample image bytes
with open("test_image.jpg", "rb") as f:
    image_bytes = f.read()

# Option 1: Execute using a dictionary payload
payload_dict = {"image": image_bytes}
result_dict = process_image(payload_dict)

# Option 2: Execute using a Pydantic object
payload_obj = N2ImageInput(image=image_bytes)
result_obj = process_image(payload_obj)

print(result_obj)
# Output:
# {
#     "img_desc": "Bãi biển cát trắng mịn màng hoang sơ dưới nắng chiều vàng rực rỡ...",
#     "metadata": {
#         "model": "llama-3.2-11b-vision-preview",
#         "latency_ms": 1240.5,
#         "usage": { "prompt_tokens": 128, "completion_tokens": 45, "total_tokens": 173 }
#     }
# }
```

---

## API & Data Contracts

### Public API Signature

```python
def process_image(data: Union[N2ImageInput, dict[str, Any]]) -> dict[str, Any]
```

### Input Schema (`N2ImageInput`)

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `image` | `bytes` / `None` | `None` | Raw binary image bytes to process. |

*If `image` is `None` or missing, N2 returns immediately with `img_desc: ""` and does not call the upstream API.*

### Output Schema (`N2ImageOutput`)

The returned dictionary conforms to the following schema structure:

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `img_desc` | `str` | `""` | Travel-rich Vietnamese scene description (max 50 words). |
| `metadata` | `dict[str, Any]` | `None` | Diagnostic data containing `model`, `latency_ms`, and API `usage` or error info. |

---

## Developer Guidelines

1. **Local Image Optimization:** The pipeline automatically downscales images exceeding `1560 × 1560` pixels and compresses them into high-quality JPEGs to reduce request payload sizes and latency.
2. **Error Resilience:** This module does not raise unhandled API/network exceptions to the orchestrator. If the LLM vision endpoint is down, it returns a blank description with error logs in the `metadata` dictionary.
3. **Vietnamese Descriptions:** Prompt templates enforce writing descriptive Vietnamese outputs directly to improve alignment with the SentenceTransformers embeddings in N1.
