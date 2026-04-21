# Backend Architecture

This directory contains the refactored backend layers for the AI-SNS application.

## Directory Structure

```
backend/
├── __init__.py
├── config/                    # Configuration layer
│   ├── __init__.py
│   ├── settings.py           # Application settings (env vars, yaml, database)
│   └── database.py           # Database configuration and session management
├── core/                      # Core application components
│   ├── __init__.py
│   └── dependencies.py       # FastAPI dependency injection
└── shared/                    # Shared utilities
    ├── __init__.py
    ├── websocket_manager.py  # WebSocket connection management
    └── utils.py              # Common utility functions
```

## Configuration Priority

The settings system follows this priority order (highest to lowest):

1. **Default LLM Config (Database)** - Runtime configuration stored in database
2. **Environment Variables** - Override everything
3. **Default Values** - Fallback defaults

## Usage Examples

### 1. Using Settings

```python
from runtime.config.settings import settings

# Access AI configuration
print(settings.ai.api_key)
print(settings.ai.model)

# Access database configuration
print(settings.database.full_path)

# Access server configuration
print(f"{settings.server.host}:{settings.server.port}")

# Check if API key is configured
if settings.has_valid_api_key():
    print("API key is configured")
```

### 2. Using Database Session

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from runtime.core.dependencies import get_db_session

@app.get("/items")
def get_items(db: Session = Depends(get_db_session)):
    return db.query(Item).all()
```

### 3. Using WebSocket Manager

```python
from runtime.shared.websocket_manager import manager

# In WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast({"message": data})
    except WebSocketDisconnect:
        manager.disconnect(client_id)
```

### 4. Using Dependencies

```python
from fastapi import Depends
from runtime.core.dependencies import (
    get_db_session,
    verify_api_key,
    pagination_params,
    RateLimiter
)

# Rate limiting
limiter = RateLimiter(max_requests=10, window_seconds=60)

@app.get("/limited")
def limited_route(_: None = Depends(limiter)):
    return {"message": "OK"}

# API key authentication
@app.get("/protected")
def protected_route(api_key: str = Depends(verify_api_key)):
    return {"message": "Authenticated"}

# Pagination
@app.get("/items")
def get_items(
    pagination: dict = Depends(pagination_params),
    db: Session = Depends(get_db_session)
):
    skip, limit = pagination["skip"], pagination["limit"]
    return db.query(Item).offset(skip).limit(limit).all()
```

## Configuration Files

### Environment Variables

Create a `.env` file in the project root:

```bash
# AI Configuration
OPENAI_API_KEY=sk-...
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=1.0
OPENAI_MAX_TOKENS=4096

# Server Configuration
HOST=0.0.0.0
PORT=8788
DEBUG=false
RELOAD=false

# Security
SECRET_KEY=your-secret-key-here
API_KEY_EXPIRE_DAYS=365

# Database
DATABASE_URL=/path/to/data
DATABASE_NAME=db.sqlite

# Rate Limiting
RATE_LIMIT=100
RATE_LIMIT_WINDOW=60

# Blockchain
BLOCKCHAIN_NETWORK=sepolia
INFURA_API_KEY=...
BLOCKCHAIN_PRIVATE_KEY=...
ESCROW_CONTRACT_ADDRESS=0x...

# Storage
UPLOAD_DIR=/path/to/uploads
MAX_UPLOAD_SIZE=52428800
KM_BASE_DIR=/path/to/km
```

## Migrating from api_server.py

The backend layer extracts and organizes code from `api_server.py`:

| Old Code | New Location |
|----------|--------------|
| `get_ai_config()` | `runtime.config.settings.Settings._load_ai_config()` |
| `ConnectionManager` | `runtime.shared.websocket_manager.ConnectionManager` |
| Database session | `runtime.config.database.get_db()` |
| Utility functions | `runtime.shared.utils` |

## Benefits

1. **Separation of Concerns** - Clear separation between config, core, and shared utilities
2. **Reusability** - Components can be imported and used across different modules
3. **Testability** - Each component can be tested independently
4. **Maintainability** - Easier to locate and modify specific functionality
5. **Configuration Management** - Unified configuration system with clear priorities
6. **Type Safety** - Better type hints and IDE support

## Testing

```python
# Test settings
from runtime.config.settings import settings
assert settings.has_valid_api_key()

# Test database
from runtime.config.database import get_db_session
db = get_db_session()
assert db is not None

# Test WebSocket manager
from runtime.shared.websocket_manager import manager
assert manager.get_client_count() == 0
```

## Next Steps

1. Update `api_server.py` to import from `runtime.*` modules
2. Remove duplicated code from `api_server.py`
3. Add unit tests for each backend component
4. Add integration tests
5. Create API documentation using FastAPI's auto-generated docs
