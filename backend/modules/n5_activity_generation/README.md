# N5 Activity Generation Module

N5 generates candidate activities for each location in a result set. It uses a pure LLM strategy with a configurable provider chain (primarily Groq), and returns a flat list of activity records plus per-location generation diagnostics.

## Responsibilities

- Accept user preferences and candidate locations
- Normalize and validate incoming user and location payloads
- Generate activities for each location via the configured LLM provider chain
- Deduplicate activities by name within each location
- Return structured activity metadata and per-location generation diagnostics

## Module Structure

```
backend/modules/n5_activity_generation/
├── __init__.py                  # Re-exports generate_activities
├── pipeline.py              # Orchestration: normalize → LLM → dedup
├── llm_provider.py          # LLM prompt construction and response parsing
├── config.py
├── schemas.py
└── requirements.txt
```

## Public API

```python
from modules.n5_activity_generation import generate_activities
from backend.shared.contracts.n5_contracts import N5GenerateInput

generate_activities(data: Union[N5GenerateInput, dict]) -> dict
```

`generate_activities()` enforces Pydantic V2 validation at the module boundary.

---

## Input Contract

```python
class N5UserInput(BaseModel):
    text: Optional[str] = ""
    tags: List[str] = []
    img_desc: Optional[str] = ""

class N5LocationMetadata(BaseModel):
    name: Optional[str] = ""
    description: Optional[str] = ""
    tags: List[str] = []

class N5LocationItem(BaseModel):
    location_id: str
    metadata: Optional[N5LocationMetadata] = None

class N5GenerateInput(BaseModel):
    user: N5UserInput = Field(default_factory=N5UserInput)
    locations: List[N5LocationItem] = Field(default_factory=list)
```

| Field | Description |
|---|---|
| `user` | User preferences: free text, tags, and image description |
| `locations` | Locations to generate activities for |

---

## Output Shape

N5 has no formal Pydantic output model. Malformed LLM items are dropped internally. The returned dict is:

```python
{
    "activities": [
        {
            "activity_id": str,          # {source}_{location_id}_{hash6}
            "location_id": str,
            "metadata": {
                "name": str,
                "description": str,
                "tags": list[str],
                "activity_type": str,    # adventure|relaxation|food|culture|nightlife|nature|shopping
                "intensity": float,
                "physical_level": float | None,
                "social_level": float | None,
            }
        }
    ],
    "metadata": {
        "per_location": [
            {
                "location_id": str,
                "provider_used": str | None,
                "model_used": str | None,
                "usage": dict | None,
                "latency_ms": int,
            }
        ],
        "latency_ms": int,
    }
}
```

- `activities` is a flat list across all input locations
- Malformed or incomplete items are silently dropped by N5's internal JSON parser
- When used in the N18 orchestrator, N5 output is validated against `N3ActivityItem` before merging with DB-backed activities

---

## Generation Flow

For each location:

1. Normalize the user input and location metadata
2. Build a travel-context prompt (location name, tags, user preferences)
3. Try the LLM provider chain in order (Groq exclusively with a fallback chain)
4. Accept LLM output if enough valid activities are returned
5. Deduplicate activities by name within the location
6. Accumulate into the flat output list

---

## LLM Provider Chain

N5 uses a prioritized provider chain managed by `providers/registry.py`:

- **Groq**: fast, free-tier, rate-limited

Groq provider implements retry logic and RPM-limit awareness via `providers/base.py`. The chain is exposed as `get_llm_chain()` and is also used by `processor.py` (activity retrievals) for description enrichment.

---

## Runtime Notes

- The module short-circuits to an empty result when generation count is configured to `0`
- Activity types are drawn from the 9-value enum: `adventure`, `relaxation`, `food`, `culture`, `nightlife`, `nature`, `shopping`, `photography`, `experience`
- Logging covers generation progress and per-location timing via the project logging helper
