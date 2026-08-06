# Module N17: Feedback Processing

`N17` refines a travel query after the user provides natural-language feedback. It builds a structured prompt from the current query state, calls the configured LLM chain to produce a refined parameter set, validates the returned tags, and falls back to a deterministic response if the LLM path fails.

---

## Directory Structure

```text
backend/modules/n17_feedback_processing/
├── __init__.py         # Public API exports (process_feedback, N17FeedbackInput, etc.)
├── pipeline.py         # Refinement orchestration, validation, and fallback logic
├── config.py           # LLM parameters and API endpoint configurations
├── schemas.py          # Input contract schemas
└── requirements.txt    # Local dependencies
```

---

## Quick Start

You can import and execute the module directly:

```python
from backend.modules.n17_feedback_processing import process_feedback, N17FeedbackInput

payload_dict = {
    "user_input": "Bãi biển Nha Trang",
    "user_tags": ["beach", "nature"],
    "img_desc": "",
    "feedback_text": "I want less crowded places and more budget-friendly options"
}

# Run feedback processing using a dictionary input
result = process_feedback(payload_dict)
print(result["refined_text"])
# Output: Địa điểm du lịch biển hoang sơ, yên tĩnh, chi phí thấp quanh Nha Trang
```

---

## API & Data Contracts

### Public API Signature

```python
def process_feedback(data: Union[N17FeedbackInput, dict[str, Any]]) -> dict[str, Any]
```

### Input Schema (`N17FeedbackInput`)

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `user_input` | `str` | `""` | Original free-form text query. |
| `user_tags` | `list[str]` | `[]` | List of tags selected or inferred previously. |
| `img_desc` | `str` | `""` | Visual description of any uploaded image. |
| `feedback_text` | `str` | `""` | User's feedback/instruction (e.g. "more quiet ones"). |
| `llm_chain` | `str` / `None` | `None` | Optional LLM chain/model override. |

### Output Contract

The returned dictionary conforms to the following schema structure:

| Field | Type | Description |
| :--- | :--- | :--- |
| `refined_text` | `str` | Rewritten query incorporating feedback signals. |
| `refined_tags` | `list[str]` | Filtered and refined tag list matching query needs. |
| `refined_img_desc` | `str` | Preserved or updated image description. |
| `explanation` | `str` | Explanation summary of adjustments made. |
| `metadata` | `dict[str, Any]` | Tracing metadata (latency, model usage, etc.). |

---

## Developer Guidelines

1. **Tag Filtering:** The pipeline automatically filters and normalizes tags returned by the LLM against the allowed list of tags.
2. **Fallback Strategy:** If the LLM times out or returns malformed JSON, N17 falls back gracefully to a deterministic text concatenation of `user_input + feedback_text` rather than failing.
3. **Structured Outputs:** Prompts instruct the LLM to output strictly formatted JSON matching the expected keys.
