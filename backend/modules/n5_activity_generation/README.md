# Module N5: Activity Generation

`N5` generates travel activities customized for a list of candidate locations. It uses an LLM generation strategy with a configurable provider chain (primarily Groq) to return a flat list of candidate activity records along with generation diagnostics.

---

## Directory Structure

```text
backend/modules/n5_activity_generation/
├── __init__.py         # Public API exports (generate_activities, N5GenerateInput, etc.)
├── pipeline.py         # Module orchestration (normalize → LLM generation → deduplicate)
├── llm_provider.py     # Prompt templates and LLM response parsing logic
├── config.py           # Local models, temperature, and API configurations
├── schemas.py          # Input contract schemas
└── requirements.txt    # Local dependencies
```

---

## Quick Start

You can import and execute the module directly:

```python
from backend.modules.n5_activity_generation import generate_activities, N5GenerateInput

payload_dict = {
    "user": {
        "text": "Quiet coffee shop with good wifi",
        "tags": ["work", "cafe"],
        "img_desc": ""
    },
    "locations": [
        {
            "location_id": "loc_1",
            "metadata": {
                "name": "Cafe Phố Cổ",
                "description": "Quán cà phê cổ kính tại trung tâm Hà Nội.",
                "tags": ["culture", "cafe"]
            }
        }
    ]
}

# Run generation using a dictionary input
result = generate_activities(payload_dict)
print(result["activities"][0]["metadata"]["name"])
# Output: Thưởng thức cà phê trứng trứng truyền thống
```

---

## API & Data Contracts

### Public API Signature

```python
def generate_activities(data: Union[N5GenerateInput, dict[str, Any]]) -> dict[str, Any]
```

### Input Schema (`N5GenerateInput`)

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `user` | `N5UserInput` | `{}` | User interest context (text, tags, img_desc). |
| `locations` | `list[N5LocationItem]` | `[]` | Locations to generate custom activities for. |

### Output Contract

The returned dictionary is structured as follows:

```python
{
    "activities": [
        {
            "activity_id": str,          # Format: {source}_{location_id}_{hash6}
            "location_id": str,
            "metadata": {
                "name": str,             # Name of the activity
                "description": str,      # Polish Vietnamese description
                "tags": list[str],       # Extracted tags (e.g. food, culture)
                "activity_type": str,    # adventure|relaxation|food|culture|nature|etc.
                "intensity": float,      # Scaled float
                "physical_level": float, # Scaled float
                "social_level": float    # Scaled float
            }
        }
    ],
    "metadata": {
        "per_location": [
            {
                "location_id": str,
                "provider_used": str,
                "model_used": str,
                "latency_ms": int
            }
        ],
        "latency_ms": int
    }
}
```

---

## Developer Guidelines

1. **Deduplication:** The module automatically deduplicates generated activities by name similarity per location before outputting.
2. **Error Isolation:** If the LLM provider fails (e.g. rate limit, bad API key), it records the diagnostic error per location in `metadata.per_location` and continues gracefully instead of crashing the process.
3. **Vietnamese Language:** Generation prompt templates instruct the LLM to output names and descriptions in natural Vietnamese matching the user query's tone.
