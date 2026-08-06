# N3: Database Management

`N3` is the database persistence layer. It manages three data domains: location records, user authentication, and recommendation history. All data is stored in PostgreSQL using `pgvector` for vector columns and JSONB for flexible payloads.

## Directory Structure

```text
backend/n3_database/
├── __init__.py         # Public API exports (database functions and input schemas)
├── db_manager.py       # Core PostgreSQL interactions, connection pools, and query logic
├── schemas.py          # Input and output validation contracts
├── seeds/              # Database seed scripts and migrations
├── requirements.txt    # Local dependencies
└── README.md           # This documentation
```

## Connection Resilience

N3 wraps database operations in a connection retry-wrapper with exponential backoff and a Circuit Breaker:
- **Breaker Opens:** After 3 consecutive failures, the breaker opens for 30 seconds to fail-fast.
- **Breaker Closes:** Retries occur inside half-open state and close the breaker on success.

## Quick Start

Initialize the database and perform basic authentication operations:

```python
from backend.n3_database import register_user, login_user, N3RegisterInput

# Register a new user
register_payload = N3RegisterInput(username="testuser", password="securepassword123")
reg_result = register_user(register_payload)
print(reg_result)
# Output: {"status": "success", "message": "User registered successfully", "user_id": 1}

# Log in
login_result = login_user({"username": "testuser", "password": "securepassword123"})
print(login_result)
# Output: {"status": "success", "message": "Login successful", "user_id": 1}
```

## API & Data Contracts

### Public API Functions

```python
# Initializations
def init_db(drop_existing: bool = False) -> None
def init_profile_db(drop_existing: bool = False) -> None

# Locations
def save_location(location_data: dict[str, Any]) -> dict[str, Any]
def get_all_locations(include_images: bool = True) -> dict[str, Any]
def get_db_fingerprint() -> str
def get_location_image_by_index(location_id: str, idx: int) -> bytes | None

# Authentication
def register_user(data: Union[N3RegisterInput, dict[str, Any]]) -> dict[str, Any]
def login_user(data: Union[N3LoginInput, dict[str, Any]]) -> dict[str, Any]

# History
def save_rec_turn(data: Union[N3SaveHistoryInput, dict[str, Any]]) -> dict[str, Any]
def get_user_history(user_id: int) -> dict[str, Any]
```

### Input Schemas

#### 1. `N3RegisterInput` / `N3LoginInput`
- `username` (`str`): Unique account username.
- `password` (`str`): Plaintext user password.

#### 2. `N3SaveHistoryInput`
- `user_id` (`int`): ID of the user.
- `input_data` (`dict`): Query parameters, text, tags, and descriptors.
- `output_data` (`dict`): Recommended locations and activities.

## Developer Guidelines

1. **pgvector extension:** All location-query operations require the PostgreSQL server to have the `pgvector` extension installed.
2. **Flexible Payload Storage:** Fields under location `metadata` are stored as a JSONB column, allowing downstream updates to append details without schema migration.
3. **Transaction Safety:** DB pool handles open/close sessions. Keep read/write transactions fast to prevent pool exhaustion.
