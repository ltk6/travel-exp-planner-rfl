# N1 Embedding Service

`N1` is the semantic entry point for the retrieval pipeline. It runs as a standalone FastAPI microservice that processes text descriptions, augments category tags across four semantic channels, and returns normalized vector embeddings.

---

## Directory Structure

```text
backend/services/n1_embedding/
├── app.py              # FastAPI service entrypoint & API routes
├── pipeline.py         # Multi-channel orchestration logic
├── embedder.py         # SentenceTransformer wrapper and singleton model instances
├── preprocessor.py     # Text cleaning and tag ontology expansion logic
├── schemas.py          # Validation schemas (Input/Output contracts)
├── config.py           # Service configuration & env overrides
└── requirements.txt    # Local service dependencies
```

---

## Quick Start

### 1. Boot Service
Start the Uvicorn web server locally on port 8001:
```bash
python -m uvicorn backend.services.n1_embedding.app:app --host 127.0.0.1 --port 8001
```

### 2. Invoke via HTTP
Make a request to generate embeddings using `curl`:
```bash
curl -X POST http://127.0.0.1:8001/light-embed \
  -H "Content-Type: application/json" \
  -d '{"text": "Quiet coffee shop with wifi", "tags": ["work", "cafe"], "img_desc": ""}'
```

---

## API Endpoints

- **`POST /embed`** — Generate 1024-dimensional BGE-M3 embeddings (heavy model).
- **`POST /light-embed`** — Generate 1024-dimensional Multilingual-E5-Small embeddings (light model).
- **`POST /embed-batch`** — Batch process multiple items with BGE-M3.
- **`POST /light-embed-batch`** — Batch process multiple items with Multilingual-E5-Small.
- **`GET /health`** — Liveness probe returning status and model preloading state.

---

## Data Contracts

### Input Schema (`N1EmbedInput`)
| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `text` | `str` | `""` | Free-form user queries or location description text. |
| `tags` | `list[str]` | `[]` | List of category tags (e.g., `["nature", "romantic"]`). |
| `img_desc` | `str` | `""` | Optional descriptive text generated from images. |

### Output Schema (`N1EmbedOutput`)
Returns preprocessed signals, channel weights, semantic vectors, and metadata:
```json
{
  "text_k": 2,
  "tags_k": 3,
  "preprocessed": {
    "text": "...",
    "img_desc": "...",
    "aug_text": "...",
    "aug_tags": "..."
  },
  "vectors": {
    "text": [0.015, -0.043, ...],
    "aug_text": [...],
    "aug_tags": [...],
    "img_desc": null
  },
  "metadata": {
    "model": "intfloat/multilingual-e5-small",
    "device": "cpu",
    "latency_ms": 12
  }
}
```
