# Module N0: Sample Template

`N0` is a reference template used to bootstrap new backend modules. It defines standard communication patterns and illustrates how to use Pydantic contracts for input/output boundary validation.

---

## Directory Structure

```text
backend/modules/n0_sample/
├── __init__.py         # Public API exports (run_sample, N0SampleInput, etc.)
├── pipeline.py         # Module execution logic
├── config.py           # Local module-specific configurations
├── schemas.py          # Input and output validation schemas
└── requirements.txt    # Local dependencies
```

---

## Quick Start

You can import and execute the module directly:

```python
from backend.modules.n0_sample import run_sample, N0SampleInput

# Option 1: Execute using a dictionary payload
payload_dict = {
    "text": " Hello World! ",
    "tags": ["travel", "  planning  ", ""]
}
result_dict = run_sample(payload_dict)

# Option 2: Execute using a Pydantic object
payload_obj = N0SampleInput(text=" Hello World! ", tags=["travel", "  planning  ", ""])
result_obj = run_sample(payload_obj)

print(result_obj)
# Output:
# {
#     "data": {
#         "text": "Hello World!",
#         "tags": ["travel", "planning"]
#     },
#     "metadata": {
#         "module": "n0_sample",
#         "latency_ms": 0.12
#     }
# }
```

---

## API & Data Contracts

### Public API Signature

```python
def run_sample(data: Union[N0SampleInput, dict[str, Any]]) -> dict[str, Any]
```

### Input Schema (`N0SampleInput`)

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | `""` | Sample input string to be processed/cleaned. |
| `tags` | `list[str]` | `[]` | List of category tags to filter or associate. |

### Output Schema

The return value is a Python `dict` conforming to the standard output envelope:

```python
class N0SampleOutput(BaseModel):
    data: N0SampleData
    metadata: N0SampleMetadata
```

#### `data` Payload Details

| Field | Type | Description |
| :--- | :--- | :--- |
| `text` | `str` | The processed string (whitespace stripped). |
| `tags` | `list[str]` | Cleaned list of non-empty tags. |

#### `metadata` Tracing Details

| Field | Type | Description |
| :--- | :--- | :--- |
| `module` | `str` | Name identifier of the module (`"n0_sample"`). |
| `latency_ms` | `float` | Computation execution latency in milliseconds. |

---

## Developer Guidelines

1. **Isolation:** Keep module logic contained within its subfolder. Always specify local dependencies in `requirements.txt`.
2. **Error Handling:** Modules should catch exceptions internally and return an error payload or status code instead of raising unhandled exceptions to the API orchestrator.
3. **Execution Latency:** Always track and report `latency_ms` within the metadata envelope for performance benchmarking.
