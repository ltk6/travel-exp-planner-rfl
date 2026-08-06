# Module N4: Location Ranking

`N4` ranks candidate locations using weighted multi-channel cosine similarity. It accepts a query-side vector bundle and signal counters from N1, scores each candidate location across four embedding channels, and returns the top-ranked results with normalized scores and short explanation strings.

---

## Directory Structure

```text
backend/modules/n4_location_ranking/
├── __init__.py         # Public API exports (rank_locations, N4RankInput, etc.)
├── pipeline.py         # Scoring, dynamic weighting, and normalization logic
├── schemas.py          # Validation schemas (Input/Output contracts)
└── requirements.txt    # Local dependencies
```

---

## Quick Start

You can import and execute the module directly:

```python
from backend.modules.n4_location_ranking import rank_locations, N4RankInput

payload_dict = {
    "text_k": 2,
    "tags_k": 3,
    "user_vectors": {
        "text": [0.1, 0.2, 0.3],
        "aug_text": [0.1, 0.2, 0.3],
        "aug_tags": [0.4, 0.5, 0.6],
        "img_desc": None
    },
    "locations": [
        {
            "location_id": "loc_1",
            "name": "Bãi biển Mỹ Khê",
            "location_vectors": {
                "text": [0.11, 0.21, 0.31],
                "aug_tags": [0.41, 0.51, 0.61]
            }
        }
    ],
    "top_k": 5
}

# Run ranking using a dictionary input
result = rank_locations(payload_dict)
print(result)
# Output:
# {
#     "locations": [
#         {
#             "location_id": "loc_1",
#             "score": 1.0,
#             "reason": "Phù hợp cao theo từ khóa tìm kiếm (text) và nhãn mô tả địa điểm (aug_tags)."
#         }
#     ],
#     "metadata": {
#         "latency_ms": 1.45
#     }
# }
```

---

## API & Data Contracts

### Public API Signature

```python
def rank_locations(data: Union[N4RankInput, dict[str, Any]]) -> dict[str, Any]
```

### Input Schema (`N4RankInput`)

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `text_k` | `int` | `0` | Text expansion count from N1 (scales `text`/`aug_text` weight). |
| `tags_k` | `int` | `0` | Tag expansion count from N1 (scales `aug_tags` weight). |
| `user_vectors` | `UserVectors` | `{}` | Query-side embedding vectors. |
| `locations` | `list[dict]` | `[]` | List of candidate location dictionaries containing `location_vectors`. |
| `top_k` | `int` | `5` | Maximum number of ranked results to return. |

### Output Schema

The returned dictionary contains the ranked candidate list:

| Field | Type | Description |
| :--- | :--- | :--- |
| `locations` | `list[dict]` | Sorted list of items containing `location_id`, `score`, and `reason`. |
| `metadata` | `dict[str, Any]` | Diagnostic latency metrics. |

*Scores are normalized relative to the top result (where the top-scoring result is set to `1.0`).*

---

## Developer Guidelines

1. **Dynamic Weighting:** Weighting is resolved dynamically using the shared `get_weights` helper based on `text_k` and `tags_k`.
2. **Channel Mapping:** The calling orchestrator is responsible for mapping backend DB vector names to the expected `location_vectors` structure.
3. **Empty Gracefulness:** If the input location candidate list is empty, N4 returns a blank list and a latency of `0.0` ms without raising an exception.
