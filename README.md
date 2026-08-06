# Travel Experience Planner Reflourished

Hệ thống lập kế hoạch du lịch sử dụng semantic retrieval, multimodal input và LLM.  
Giao diện người dùng được xây dựng bằng **Next.js**, backend API chạy trên **FastAPI (N18)**.

## Các Tính năng Chính
- **Tìm kiếm Semantic Đa phương thức (Multi-modal Semantic Search)**: Nhận diện sở thích qua văn bản và hình ảnh.
- **Gợi ý Hoạt động Động (Dynamic Activity Generation)**: Sinh hoạt động bằng Groq LLM dựa trên địa điểm thực tế.
- **Tinh chỉnh bằng Phản hồi (Feedback Loop)**: Ghi nhận yêu cầu của người dùng để điều chỉnh lại các gợi ý realtime.

## Công nghệ sử dụng
- **Frontend**: Next.js
- **Backend Orchestrator**: FastAPI (N18)
- **LLM Engine**: Groq (Llama3/Mixtral)
- **Embeddings**: SentenceTransformers (`intfloat/multilingual-e5-small` & `BAAI/bge-m3`)
- **Cơ sở dữ liệu**: PostgreSQL với `pgvector` extension

## Công cụ Hỗ trợ Phát triển
- **Coding & Hỗ trợ chung**: Claude / Gemini (Hỗ trợ viết mã, debug, và pair-programming)
- **Xử lý dữ liệu**: NotebookLM (Tổng hợp thông tin, chuẩn hóa và xử lý bộ dữ liệu địa điểm ban đầu)

## Khởi động nhanh

### Yêu cầu

- Python 3.10+
- Node.js 18+ và npm
- PostgreSQL (với pgvector extension)

### Cấu hình môi trường

```bash
# Cấu hình Backend
cp .env.example .env
# Mở .env và điền các biến: PG_URI, GROQ_API_KEY, INTERNAL_API_KEY

# Cấu hình Frontend
cd frontend/n16_web_ui
cp .env.local.example .env.local
# Mở .env.local và cấu hình INTERNAL_API_KEY
```

### Chạy trên Windows

```bat
run.bat
```

- Tự động tạo và kích hoạt Python venv
- Cài đặt Python dependencies từ `requirements.txt` (bỏ qua nếu đã có)
- Cài đặt Node.js dependencies cho Next.js (bỏ qua nếu đã có)
- Khởi động backend trên `:8000` và frontend trên `:3000`
- Tự động mở trình duyệt tại `http://localhost:3000`

### Sau khi khởi động

| Service | URL |
|---|---|
| **Frontend (Next.js)** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **Health check** | http://localhost:8000/health |

## Quản lý Dữ liệu (Data Pipeline)

Hệ thống cung cấp các công cụ để chuẩn hóa và nạp dữ liệu địa điểm vào cơ sở dữ liệu vector:
- **Cập nhật & Sinh Embeddings**: Chạy `python backend/n3_database/seeds/embed_locations.py` để tự động tạo vector embeddings (hỗ trợ lưu gia tăng - incremental) cho các địa điểm mới trong `locations.json`. Dữ liệu đầu ra được lưu tại `locations_with_vectors.json`.
## Kiến trúc

Hệ thống được chia thành các module độc lập (N0–N17), mỗi module có contract Pydantic V2 riêng xác định input/output tại ranh giới module:

| Module | Chức năng |
|---|---|
| N1 | Embedding (BGE-M3, multi-channel) |
| N2 | Image processing → text description |
| N3 | PostgreSQL persistence (locations, users, history) |
| N4 | Location ranking (cosine similarity) |
| N5 | Activity generation |
| N6 | Activity ranking (semantic + attribute) |
| N7 | Frontend (Streamlit) superseded by N16 |
| N8 | API orchestrator (Flask) superseded by N18 |
| N9-N14 | Activity retrievals (real maps) removed for instability |
| N15 | User profile handling absorbed by N3 |
| N16 | Frontend (Next.js + Zustand) |
| N17 | Feedback processing |
| N18 | API orchestrator (FastAPI) |

---

*Lưu ý: Dự án này là phiên bản được duy trì và tiếp tục phát triển sau khi khóa học Tư duy tính toán HK2 2025-2026 kết thúc. Dự án gốc ban đầu là [`travel-exp-planner`](https://github.com/ltk6/travel-exp-planner). Vui lòng xem [LICENSE](LICENSE) để biết thông tin chi tiết về bản quyền.*