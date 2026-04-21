# Backend Quick Reference Guide

## Import Cheatsheet

```python
# Settings
from runtime.config.settings import settings

# Database
from runtime.config.database import get_db, get_db_session, init_db
from sqlalchemy.orm import Session

# Dependencies (for FastAPI)
from runtime.core.dependencies import (
    get_db_session,           # Database session dependency
    get_api_key,              # Extract API key from headers
    verify_api_key,           # Verify API key is valid
    get_current_user,         # Get authenticated user
    check_rate_limit,         # Check rate limits
    get_settings,             # Get settings instance
    RateLimiter,              # Rate limiter class
    pagination_params         # Pagination parameters
)

# WebSocket
from runtime.shared.websocket_manager import ConnectionManager, manager

# Utilities
from runtime.shared.utils import (
    # ID Generation
    generate_uuid, generate_short_id,

    # Hashing
    hash_string,

    # JSON
    safe_json_loads, safe_json_dumps,

    # File System
    ensure_dir, get_file_size, format_file_size, sanitize_filename,

    # Date/Time
    timestamp_to_datetime, datetime_to_timestamp, now_timestamp, now_iso,

    # String
    truncate_string, mask_sensitive_data,

    # Validation
    validate_email,

    # Environment
    get_env_bool, get_env_int, get_env_float,

    # Helpers
    merge_dicts, chunk_list, remove_none_values,

    # Timer
    Timer
)
```

## Common Patterns

### 1. FastAPI Endpoint with Database

```python
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from runtime.core.dependencies import get_db_session

router = APIRouter()

@router.get("/items")
def get_items(db: Session = Depends(get_db_session)):
    # Use db to query database
    return {"items": []}
```

### 2. Protected Endpoint with API Key

```python
from fastapi import Depends
from runtime.core.dependencies import verify_api_key

@app.get("/protected")
def protected_endpoint(api_key: str = Depends(verify_api_key)):
    return {"message": "Authenticated"}
```

### 3. Rate Limited Endpoint

```python
from runtime.core.dependencies import RateLimiter

limiter = RateLimiter(max_requests=10, window_seconds=60)

@app.get("/limited")
def limited_endpoint(_: None = Depends(limiter)):
    return {"message": "OK"}
```

### 4. Paginated Endpoint

```python
from runtime.core.dependencies import pagination_params

@app.get("/items")
def get_items(pagination: dict = Depends(pagination_params)):
    skip = pagination["skip"]
    limit = pagination["limit"]
    return {"items": [], "skip": skip, "limit": limit}
```

### 5. WebSocket Endpoint

```python
from fastapi import WebSocket, WebSocketDisconnect
from runtime.shared.websocket_manager import manager

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Echo back
            await manager.send_message(data, client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
```

### 6. Using Settings

```python
from runtime.config.settings import settings

# Access configuration
api_key = settings.ai.api_key
model = settings.ai.model
db_path = settings.database.full_path

# Check if configured
if settings.has_valid_api_key():
    print("API key is configured")

# Update from database
config_dict = {
    "api_key": "sk-...",
    "model": "gpt-4",
    "api_base": "https://api.openai.com/v1"
}
settings.update_ai_config_from_db(config_dict)
```

### 9. Database Operations

```python
from runtime.config.database import get_db_session

# In non-FastAPI code
db = get_db_session()
try:
    # Do database operations
    items = db.query(Item).all()
    db.commit()
finally:
    db.close()
```

### 10. Utility Functions

```python
from runtime.shared.utils import (
    generate_uuid,
    hash_string,
    safe_json_loads,
    sanitize_filename,
    mask_sensitive_data,
    Timer
)

# Generate ID
id = generate_uuid()

# Hash password
hashed = hash_string("password")

# Parse JSON safely
data = safe_json_loads('{"key": "value"}', default={})

# Sanitize filename
safe_name = sanitize_filename("my<file>.txt")  # "my_file_.txt"

# Mask API key
masked = mask_sensitive_data("sk-1234567890", 4)  # "sk-1*********"

# Time code execution
with Timer("Database query"):
    # code here
    pass
```

## Configuration

### Environment Variables

```bash
# AI Configuration
OPENAI_API_KEY=sk-...
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=1.0
OPENAI_MAX_TOKENS=4096

# Server
HOST=0.0.0.0
PORT=8788
DEBUG=false
RELOAD=false
CORS_ORIGINS=*

# Database
DATABASE_URL=/path/to/data
DATABASE_NAME=db.sqlite

# Security
SECRET_KEY=your-secret-key
API_KEY_EXPIRE_DAYS=365

# Rate Limiting
RATE_LIMIT=100
RATE_LIMIT_WINDOW=60

# Storage
UPLOAD_DIR=/path/to/uploads
MAX_UPLOAD_SIZE=52428800
```

## Testing

```bash
# Run all tests
python3 backend/test_backend.py

# Run with pytest (if installed)
pytest backend/test_backend.py -v

# Test specific component
python3 -c "
from runtime.config.settings import settings
print('Settings OK:', settings.has_valid_api_key())
"
```

## File Locations

```
/mnt/c/dev/agi-ev/ai-sns-el/runtime/
├── config/
│   ├── settings.py           # Application settings
│   └── database.py           # Database configuration
├── core/
│   └── dependencies.py       # FastAPI dependencies
├── shared/
│   ├── websocket_manager.py  # WebSocket manager
│   └── utils.py              # Utility functions
├── README.md                 # Documentation
├── IMPLEMENTATION_SUMMARY.md # Implementation details
└── test_backend.py           # Component tests
```

## Quick Tips

1. **Always use settings**: Don't hardcode configuration
2. **Use dependencies**: Leverage FastAPI's dependency injection
3. **Use the AI client**: Don't make raw API calls
4. **Use utilities**: Don't reinvent common functions
5. **Check settings validity**: Use `settings.has_valid_api_key()`
6. **Close database sessions**: Use FastAPI dependencies or try/finally
7. **Handle WebSocket disconnects**: Always use try/except with WebSocketDisconnect
8. **Use Timer for profiling**: Wrap slow code with Timer context manager
9. **Mask sensitive data**: Use `mask_sensitive_data()` for logging
10. **Validate user input**: Use utility functions for validation

## Common Issues

### Issue: "API key not configured"
**Solution**: Configure a default LLM in Settings, or set OPENAI_API_KEY environment variable

### Issue: "Database locked"
**Solution**: Check that database sessions are properly closed

### Issue: "WebSocket already disconnected"
**Solution**: Use try/except around WebSocket operations

### Issue: "Import error"
**Solution**: Make sure you're importing from runtime.* modules

### Issue: "Settings not updating"
**Solution**: Settings are loaded once at startup; restart for changes

## Getting Help

1. Check `backend/README.md` for detailed documentation
2. Review `backend/IMPLEMENTATION_SUMMARY.md` for architecture details
3. Run tests: `python3 backend/test_backend.py`
4. Check example usage in the documentation
5. Look at existing code in `api_server.py` for integration examples
