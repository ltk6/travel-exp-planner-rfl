# Module N1: Embedding

`N1` is the semantic entry point for the retrieval pipeline. It takes raw user queries or location text data, expands available signals across four semantic channels, and returns normalized embedding vectors along with metadata.

---

## Directory Structure

```text
backend/modules/n1_embedding/
├── __init__.py         # Public API exports (embed, light_embed, N1EmbedInput, etc.)
├── pipeline.py         # Entry points and orchestrating logic
├── embedder.py         # SentenceTransformer wrapper and singleton model instance
├── preprocessor.py     # Text cleaning and tag ontology expansion logic
├── schemas.py          # Validation schemas (Input/Output contracts)
├── config.py           # Local model configurations
└── requirements.txt    # Local dependencies
```

---

## Quick Start

You can import and execute the module directly:

```python
from backend.modules.n1_embedding import light_embed, N1EmbedInput

# Option 1: Execute using a dictionary payload
payload_dict = {
    "text": "Quiet coffee shop with good wifi",
    "tags": ["work", "cafe"],
    "img_desc": "Cozy indoor seating area"
}
result_dict = light_embed(payload_dict, task_type="passage")

# Option 2: Execute using a Pydantic object
payload_obj = N1EmbedInput(
    text="Quiet coffee shop with good wifi",
    tags=["work", "cafe"],
    img_desc="Cozy indoor seating area"
)
result_obj = light_embed(payload_obj, task_type="passage")

print(result_obj["vectors"]["text"][:3])
# Output: [-0.0154, 0.0431, -0.0092]
```

---

## API & Data Contracts

### Public API Signature

```python
# Process a single item
def embed(data: Union[N1EmbedInput, dict[str, Any]]) -> dict[str, Any]
def light_embed(data: Union[N1EmbedInput, dict[str, Any]], task_type: str = "passage") -> dict[str, Any]

# Process multiple items in batch (single model forward pass)
def embed_batch(data_list: list[Union[N1EmbedInput, dict[str, Any]]]) -> list[dict[str, Any]]
def light_embed_batch(data_list: list[Union[N1EmbedInput, dict[str, Any]]], task_type: str = "passage") -> list[dict[str, Any]]
```

### Input Schema (`N1EmbedInput`)

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | `""` | Free-form user queries or location description text. |
| `tags` | `list[str]` | `[]` | List of category tags (e.g. `['romantic', 'nature']`). |
| `img_desc` | `str` | `""` | Descriptive text generated from images (optional). |

### Output Schema

Each output item dictionary conforms to the following structure:

```python
class N1EmbedOutput(BaseModel):
    text_k: int
    tags_k: int
    preprocessed: PreprocessedText
    vectors: EmbedVectors
    metadata: dict[str, Any]
```

#### `preprocessed` Details
* `text` / `img_desc`: Cleaned & trimmed input text.
* `aug_text`: Input text + matched context/mood keyword expansions.
* `aug_tags`: Ontology category expansions generated from input tags.

#### `vectors` Details
* Contains 1024-dimensional float list embeddings for: `text`, `aug_text`, `aug_tags`, and `img_desc`.
* Unused channels (where input was empty) will map to `None`.

#### `metadata` Tracing Details
* `model`: Name of the embedding model used.
* `device`: CPU/CUDA running device.
* `latency_ms`: Execution latency in milliseconds.

---

## Developer Guidelines

1. **Model Choices:** Use `embed` for heavy BGE-M3 embeddings and `light_embed` for multilingual-e5-small embeddings when throughput is critical.
2. **Channel Weighting:** Downstream ranking modules rely on `text_k` and `tags_k` to dynamically scale cosine weights. Do not omit these counters.
3. **Batching:** When processing multiple inputs, always use `embed_batch` or `light_embed_batch` to avoid sequential CPU/GPU overhead.
