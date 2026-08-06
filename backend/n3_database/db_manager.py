import os
import json
import logging
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from pgvector.psycopg2 import register_vector
import base64
import time

from config import setup_logging
logger = setup_logging("N3")

from .schemas import N3GetLocationsOutput


class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.last_state_change = time.time()

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.last_state_change = time.time()
            logger.warning(f"Circuit Breaker OPENED: DB connections will fail-fast for {self.recovery_timeout}s.")

    def record_success(self):
        self.failure_count = 0
        if self.state != "CLOSED":
            logger.info("Circuit Breaker CLOSED: DB connection restored.")
        self.state = "CLOSED"

    def can_attempt(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_state_change > self.recovery_timeout:
                self.state = "HALF-OPEN"
                logger.info("Circuit Breaker HALF-OPEN: testing DB connection...")
                return True
            return False
        return True

_DB_CIRCUIT_BREAKER = CircuitBreaker()

from config import PG_URI
def _get_connection():
    """Tạo kết nối DB với retry + circuit-breaker."""
    if not _DB_CIRCUIT_BREAKER.can_attempt():
        raise psycopg2.OperationalError("Circuit Breaker is OPEN: database is temporarily unreachable.")

    max_retries = 3
    delay = 0.5
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(PG_URI, cursor_factory=RealDictCursor)
            conn.autocommit = True
            try:
                cur = conn.cursor()
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                cur.close()
            except Exception as ex:
                logger.warning(f"Failed to create vector extension: {ex}")
            register_vector(conn)
            _DB_CIRCUIT_BREAKER.record_success()
            return conn
        except Exception as e:
            logger.warning(f"Ket noi DB that bai (Lan {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(delay)
                delay *= 2
            else:
                _DB_CIRCUIT_BREAKER.record_failure()
                raise e

def init_db(drop_existing: bool = False):
    """Khởi tạo cấu trúc Database và ép ngắt các kết nối đang treo để tránh Lock."""
    conn = _get_connection()
    cur = conn.cursor()
    
    try:
        # Chỉ ngắt kết nối của CHÍNH MÌNH (current user) để không cần quyền Superuser
        cur.execute("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = current_database()
              AND usename = current_user
              AND pid <> pg_backend_pid();
        """)
    except Exception as e:
        logger.warning(f"Không thể ngắt các kết nối khác: {e}")

    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    if drop_existing:
        cur.execute("DROP TABLE IF EXISTS locations CASCADE;")
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            location_id VARCHAR(255) PRIMARY KEY,
            text vector(1024),
            aug_text vector(1024),
            aug_tags vector(1024),
            img_desc vector(1024),
            metadata JSONB,
            geo JSONB,
            images BYTEA[], 
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.close()
    conn.close()
    logger.info(f"Khoi tao DB thanh cong (drop_existing={drop_existing}).")

def get_db_fingerprint() -> str:
    """Tạo dấu vân tay duy nhất cho trạng thái hiện tại của DB."""
    try:
        conn = _get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*), MAX(updated_at) FROM locations;")
        row = cur.fetchone()
        conn.close()
        return f"{row['count']}:{row['max']}"
    except Exception as e:
        logger.warning(f"Lỗi lấy Fingerprint: {e}")
        return "fallback_v1"

def _format_vectors(row: Dict[str, Any]) -> Dict[str, Any]:
    def to_list(v):
        if v is None: return None
        return v.tolist() if hasattr(v, "tolist") else list(v)

    return {
        "text": to_list(row.get("text")),
        "aug_text": to_list(row.get("aug_text")),
        "aug_tags": to_list(row.get("aug_tags")),
        "img_desc": to_list(row.get("img_desc"))
    }

def save_location(location_data: Dict[str, Any]) -> Dict[str, Any]:
    """Lưu dữ liệu địa điểm kèm mảng ảnh Binary vào Database."""
    import time
    t0 = time.time()
    try:
        conn = _get_connection()
        cur = conn.cursor()

        vectors = location_data.get("vectors", {})
        images_binary = location_data.get("images_binary", [])

        cur.execute("""
            INSERT INTO locations (
                location_id, text, aug_text, aug_tags, img_desc, metadata, geo, images, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (location_id)
            DO UPDATE SET
                text = EXCLUDED.text,
                aug_text = EXCLUDED.aug_text,
                aug_tags = EXCLUDED.aug_tags,
                img_desc = EXCLUDED.img_desc,
                metadata = EXCLUDED.metadata,
                geo = EXCLUDED.geo,
                images = CASE WHEN array_length(EXCLUDED.images, 1) > 0 THEN EXCLUDED.images ELSE locations.images END,
                updated_at = CURRENT_TIMESTAMP;
        """,
        (
            location_data.get("location_id"),
            vectors.get("text"),
            vectors.get("aug_text"),
            vectors.get("aug_tags"),
            vectors.get("img_desc"),
            json.dumps(location_data.get("metadata", {})),
            json.dumps(location_data.get("geo", {})),
            images_binary if images_binary else None,
        ))

        conn.commit()
        conn.close()
        
        elapsed_ms = int((time.time() - t0) * 1000)
        return {
            "status": "success", 
            "location_id": location_data.get("location_id"),
            "metadata": {"source": "postgresql", "latency_ms": elapsed_ms}
        }
    except Exception as e:
        logger.error(f"Lỗi lưu Location: {e}")
        return {
            "status": "error", 
            "message": str(e),
            "metadata": {"source": "postgresql", "latency_ms": 0}
        }

def get_all_locations(include_images: bool = True) -> Dict[str, Any]:
    """Lấy toàn bộ danh sách địa điểm, giải mã Binary sang Base64 cho Frontend."""
    import time
    t0 = time.time()
    try:
        conn = _get_connection()
        cur = conn.cursor()
        
        query = "SELECT location_id, text, aug_text, aug_tags, img_desc, metadata, geo"
        if include_images:
            query += ", images"
        query += " FROM locations;"
        
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        results = []
        for row in rows:
            row_dict = dict(row)
            formatted = {
                "location_id": row_dict["location_id"],
                "vectors": _format_vectors(row_dict),
                "metadata": row_dict.get("metadata"),
                "geo": row_dict.get("geo"),
            }
            
            if include_images and row_dict.get("images"):
                encoded_images = []
                for img_bytes in row_dict["images"]:
                    if img_bytes:
                        b64_str = base64.b64encode(img_bytes).decode("utf-8")
                        encoded_images.append(f"data:image/jpeg;base64,{b64_str}")
                formatted["images"] = encoded_images
            else:
                formatted["images"] = []
                
            results.append(formatted)

        elapsed_ms = int((time.time() - t0) * 1000)
        raw_response = {
            "status": "success", 
            "total": len(results), 
            "data": results,
            "metadata": {"source": "postgresql", "latency_ms": elapsed_ms}
        }
        validated = N3GetLocationsOutput.model_validate(raw_response)
        return validated.model_dump()

    except Exception as e:
        logger.error(f"Lỗi truy vấn DB: {e}. Fallback to local files...")
        import json, os
        fallback_path = os.path.join(os.path.dirname(__file__), "seeds", "locations_with_vectors.json")
        if os.path.exists(fallback_path):
            try:
                with open(fallback_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                
                results = []
                for item in raw_data:
                    formatted = {
                        "location_id": item.get("location_id"),
                        "vectors": item.get("vectors", {}),
                        "metadata": item.get("metadata", {}),
                        "geo": item.get("geo", {}),
                        "images": []
                    }
                    if include_images and item.get("images_binary"):
                        encoded_images = []
                        for img_str in item.get("images_binary", []):
                            if img_str:
                                if not img_str.startswith("data:image"):
                                    img_str = f"data:image/jpeg;base64,{img_str}"
                                encoded_images.append(img_str)
                        formatted["images"] = encoded_images
                    
                    results.append(formatted)
                
                elapsed_ms = int((time.time() - t0) * 1000)
                raw_response = {
                    "status": "success", 
                    "total": len(results), 
                    "data": results,
                    "metadata": {"source": "fallback_file", "latency_ms": elapsed_ms}
                }
                validated = N3GetLocationsOutput.model_validate(raw_response)
                return validated.model_dump()
            except Exception as inner_e:
                logger.error(f"Lỗi đọc fallback file: {inner_e}")
        
        return {
            "status": "error",
            "message": str(e),
            "data": [],
            "metadata": {"source": "postgresql", "latency_ms": 0}
        }

# ──────────────── USER PROFILE FEATURES ────────────────
# AUTH AND RECOMMENDATION HISTORY FEATURES
from werkzeug.security import generate_password_hash, check_password_hash

def init_profile_db(drop_existing: bool = False):
    """Khoi tao bang nguoi dung va bang luu lich su goi y"""
    conn = _get_connection()
    cur = conn.cursor()
    
    if drop_existing:
        cur.execute("DROP TABLE IF EXISTS rec_history CASCADE;")
        cur.execute("DROP TABLE IF EXISTS users CASCADE;")
    
    # 1. Bang luu tai khoan de dang nhap
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # 2. Bang luu toan bo Input va Output cua moi lan Recommendation
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rec_history (
            history_id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            input_data JSONB,
            output_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 3. Bang luu general feedback cua app
    cur.execute("""
        CREATE TABLE IF NOT EXISTS app_feedback (
            feedback_id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255),
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"users, history and app_feedback tables successfully initialized (drop_existing={drop_existing})")

# PHAN 1: AUTHENTICATION (DANG KY DANG NHAP)

def register_user(username, password) -> Dict[str, Any]:
    try:
        conn = _get_connection()
        cur = conn.cursor()
        hashed_pw = generate_password_hash(password)
        cur.execute("""
            INSERT INTO users (username, password_hash) 
            VALUES (%s, %s) RETURNING user_id;
        """, (username, hashed_pw))
        user_id = cur.fetchone()["user_id"]
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "Dang ky thanh cong", "user_id": user_id}
    except psycopg2.errors.UniqueViolation:
        return {"status": "error", "message": "Ten dang nhap da ton tai"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def login_user(username, password) -> Dict[str, Any]:
    try:
        conn = _get_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id, password_hash FROM users WHERE username = %s;", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            return {"status": "success", "message": "Dang nhap thanh cong", "user_id": user["user_id"]}
        return {"status": "error", "message": "Sai tai khoan va mat khau"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# PART 2: RECOMMENDATION HISTORY PERSISTENCE

def save_rec_turn(user_id: int, input_data: Dict[str, Any], output_data: Dict[str, Any], history_id: Optional[int] = None) -> Dict[str, Any]:
    """Save recommendation turn or update loaded activities in the database."""
    try:
        conn = _get_connection()
        cur = conn.cursor()
        if history_id:
            cur.execute("""
                UPDATE rec_history 
                SET input_data = %s, output_data = %s
                WHERE history_id = %s AND user_id = %s;
            """, (json.dumps(input_data), json.dumps(output_data), history_id, user_id))
            conn.commit()
            cur.close()
            conn.close()
            return {"status": "success", "message": "Successfully updated recommendation history", "history_id": history_id}
        else:
            cur.execute("""
                INSERT INTO rec_history (user_id, input_data, output_data)
                VALUES (%s, %s, %s) RETURNING history_id;
            """, (user_id, json.dumps(input_data), json.dumps(output_data)))
            row = cur.fetchone()
            history_id = row["history_id"] if row else None
            conn.commit()
            cur.close()
            conn.close()
            return {"status": "success", "message": "Successfully saved recommendation history", "history_id": history_id}
    except Exception as e:
        logger.error(f"Error saving/updating recommendation history: {e}")
        return {"status": "error", "message": str(e)}

def get_user_history(user_id: int) -> Dict[str, Any]:
    """Lay toan bo du lieu tat ca cac lan rec cua user sau khi dang nhap thanh cong"""
    try:
        conn = _get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT history_id, input_data, output_data, created_at 
            FROM rec_history WHERE user_id = %s ORDER BY created_at DESC;
        """, (user_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        history_list = []
        for row in rows:
            history_list.append({
                "history_id": row["history_id"],
                "input_data": json.loads(row["input_data"]) if isinstance(row["input_data"], str) else row["input_data"],
                "output_data": json.loads(row["output_data"]) if isinstance(row["output_data"], str) else row["output_data"],
                "created_at": row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            })
        return {"status": "success", "data": history_list}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_location_image_by_index(location_id: str, idx: int) -> Optional[bytes]:
    """Retrieve raw image bytes directly from PostgreSQL for lazy-load."""
    try:
        conn = _get_connection()
        cur = conn.cursor()
        cur.execute("SELECT images FROM locations WHERE location_id = %s;", (location_id,))
        row = cur.fetchone()
        conn.close()
        if row and row.get("images"):
            images = row["images"]
            if 0 <= idx < len(images):
                img_data = images[idx]
                if img_data:
                    return bytes(img_data)
        return None
    except Exception as e:
        logger.error(f"Lỗi lấy ảnh lazy từ DB: {e}")
        return None

def save_app_feedback(name: str, email: str, content: str) -> Dict[str, Any]:
    try:
        conn = _get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO app_feedback (name, email, content)
            VALUES (%s, %s, %s) RETURNING feedback_id;
        """, (name, email, content))
        feedback_id = cur.fetchone()["feedback_id"]
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "Cảm ơn bạn đã gửi feedback!", "feedback_id": feedback_id}
    except Exception as e:
        logger.error(f"Lỗi lưu feedback vào DB: {e}")
        return {"status": "error", "message": str(e)}

