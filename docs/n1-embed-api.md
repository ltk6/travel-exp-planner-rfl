# N1 Service API Contract (`docs/N1-embed-api.md`)

API specifications and payload contracts for the standalone **N1 Embedding Service**.

---

## 1. Overview
The N1 service exposes endpoints to generate BGE-M3 and Multilingual-E5-Small text vector embeddings. It operates as a containerized FastAPI app inside the local Docker network.

* **Default port:** `8001`
* **Default host:** `http://n1_embedding:8001` (internal Compose network)

---

## 2. API Endpoints

### Health Check
Verify model load state and service availability.
* **Route:** `GET /health`
* **Response `200 OK` (Healthy):**
  ```json
  {
    "status": "healthy",
    "models_loaded": true
  }
  ```
* **Response `503 Service Unavailable` (Loading):**
  ```json
  {
    "status": "unhealthy",
    "models_loaded": false,
    "detail": "Models are loading or failed to load"
  }
  ```

---

### Generate BGE-M3 Embedding
Generates high-dimensional BGE-M3 text and tag vectors.
* **Route:** `POST /embed`
* **Content-Type:** `application/json`
* **Request Body (`N1EmbedInput`):**
  ```json
  {
    "text": "vịnh hạ long quảng ninh",
    "tags": ["beach", "nature"],
    "img_desc": "a beautiful bay with limestone mountains"
  }
  ```
* **Response Body (`N1EmbedOutput`):**
  ```json
  {
    "text_k": 1024,
    "tags_k": 1024,
    "preprocessed": {
      "text": "vinh ha long quang ninh",
      "aug_text": "vịnh hạ long quảng ninh",
      "aug_tags": "beach nature",
      "img_desc": "a beautiful bay with limestone mountains"
    },
    "vectors": {
      "text": [0.0123, -0.0456, "... (1024 dimensions)"],
      "aug_text": [0.0789, -0.0123, "... (1024 dimensions)"],
      "aug_tags": [0.0456, 0.0890, "... (1024 dimensions)"],
      "img_desc": [-0.0123, 0.0567, "... (1024 dimensions)"]
    },
    "metadata": {
      "model": "BAAI/bge-m3",
      "latency_ms": 142
    }
  }
  ```

---

### Generate E5 Embedding (Light)
Generates lower-dimensional, faster E5 vector embeddings.
* **Route:** `POST /light-embed?task_type=passage`
* **Query Parameters:**
  - `task_type` (string, optional, default: `"passage"`): E5 task prompt modifier (e.g. `"query"` or `"passage"`).
* **Request Body (`N1EmbedInput`):**
  *(Same as `/embed` input structure)*
* **Response Body (`N1EmbedOutput`):**
  *Returns vectors of 384 dimensions matching E5-Small model output.*

---

### Batch Generation
Optimized batch requests to process multiple locations in a single model forward pass.
* **Route:** `POST /embed-batch`
* **Route:** `POST /light-embed-batch?task_type=passage`
* **Request Body:** Array of `N1EmbedInput` objects.
* **Response Body:** Array of `N1EmbedOutput` objects.
