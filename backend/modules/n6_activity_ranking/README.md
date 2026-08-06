# Module N6: Activity Ranking

`N6` ranks candidate activities by combining semantic similarity with rule-based attribute fit. It compares query-side vector channels against activity vectors, infers user preference axes from raw input text and tags, and returns a sorted result list with normalized scores and explanation strings.

---

## Directory Structure

```text
backend/modules/n6_activity_ranking/
├── __init__.py         # Public API exports (rank_activities, N6RankInput, etc.)
├── pipeline.py         # Scoring, blending, and ranking orchestrator
├── preferences.py      # Rule-based user preference inference (intensity, physical effort, social style)
├── schemas.py          # Validation schemas (Input/Output contracts)
└── requirements.txt    # Local dependencies
```

---

## Quick Start

You can import and execute the module directly:

```python
from backend.modules.n6_activity_ranking import rank_activities, N6RankInput

payload_dict = {
    "text_k": 2,
    "tags_k": 3,
    "user_input": {
        "text": "Quiet coffee shop with good wifi",
        "tags": ["work", "cafe"],
        "img_desc": ""
    },
    "user_vectors": {
        "text": [0.1, 0.2, 0.3],
        "aug_tags": [0.4, 0.5, 0.6]
    },
    "activities": [
        {
            "activity_id": "act_1",
            "location_id": "loc_1",
            "vectors": {
                "text": [0.11, 0.21, 0.31],
                "aug_tags": [0.41, 0.51, 0.61]
            },
            "metadata": {
                "name": "Quiet Work Station",
                "activity_type": "relaxation",
                "intensity": 0.2,
                "physical_level": 0.1,
                "social_level": 0.1
            }
        }
    ],
    "top_k": 5
}

# Run ranking using a dictionary input
result = rank_activities(payload_dict)
print(result)
# Output:
# {
#     "activities": [
#         {
#             "activity_id": "act_1",
#             "location_id": "loc_1",
#             "score": 0.92,
#             "reason": "Hoàn hảo cho thư giãn (relaxation) với độ tải nhẹ nhàng."
#         }
#     ],
#     "metadata": {
#         "latency_ms": 2.1
#     }
# }
```

---

## API & Data Contracts

### Public API Signature

```python
def rank_activities(data: Union[N6RankInput, dict[str, Any]]) -> dict[str, Any]
```

### Input Schema (`N6RankInput`)

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `text_k` | `int` | `0` | Text expansion count from N1. |
| `tags_k` | `int` | `0` | Tag expansion count from N1. |
| `user_input` | `UserInput` | `{}` | Raw text, tags, and image description. |
| `user_vectors` | `UserVectors` | `{}` | Query-side embedding vectors. |
| `activities` | `list[dict]` | `[]` | List of candidate activity dictionaries to rank. |
| `top_k` | `int` | `5` | Maximum number of ranked results to return. |

### Output Schema

The returned dictionary contains the ranked activities list:

| Field | Type | Description |
| :--- | :--- | :--- |
| `activities` | `list[dict]` | Sorted list of items containing `activity_id`, `location_id`, `score`, and `reason`. |
| `metadata` | `dict[str, Any]` | Diagnostic metrics containing execution latency. |

---

## Developer Guidelines

1. **Scoring Mixture:** The scoring blends semantic match (50%) and attribute fit (50%) to sort activities.
2. **Preference Inference:** The `preferences.py` helper infers three core axes from the raw `user_input.text`:
   * **Intensity:** Energy level requirements.
   * **Physical Effort:** Physical strength/mobility needed.
   * **Social Style:** Solo vs. group/public environment.
3. **Graceful Defaults:** If the candidate activities list is empty, N6 returns an empty list without raising errors.
