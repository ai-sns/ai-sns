# Backend Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                         AI-SNS Backend                              │
│                          Architecture                               │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                        Application Layer                            │
│                         (api_server.py)                             │
│                                                                      │
│  FastAPI App, Routes, Endpoints, Request/Response Handling         │
└────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ uses
                                  ▼
┌────────────────────────────────────────────────────────────────────┐
│                         Backend Layers                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    Config Layer                               │ │
│  │                  (backend/config/)                            │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │                                                               │ │
│  │  settings.py (259 lines)                                     │ │
│  │  ├─ Multi-source configuration loading                      │ │
│  │  ├─ Priority: Env > Database > YAML > Defaults             │ │
│  │  ├─ AIConfig, DatabaseConfig, ServerConfig                  │ │
│  │  ├─ SecurityConfig, RateLimitConfig, etc.                   │ │
│  │  └─ Singleton settings instance                             │ │
│  │                                                               │ │
│  │  database.py (86 lines)                                      │ │
│  │  ├─ SQLAlchemy engine and session factory                   │ │
│  │  ├─ FastAPI dependency: get_db()                            │ │
│  │  ├─ Database initialization                                 │ │
│  │  └─ Connection management                                   │ │
│  │                                                               │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                     Core Layer                                │ │
│  │                   (backend/core/)                             │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │                                                               │ │
│  │  dependencies.py (167 lines)                                 │ │
│  │  ├─ FastAPI dependency injection                            │ │
│  │  ├─ get_db_session() - Database session                     │ │
│  │  ├─ verify_api_key() - API key auth                         │ │
│  │  ├─ get_current_user() - User authentication                │ │
│  │  ├─ RateLimiter - Rate limiting                             │ │
│  │  ├─ pagination_params() - Pagination                        │ │
│  │  └─ get_settings() - Settings access                        │ │
│  │                                                               │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    Shared Layer                               │ │
│  │                  (backend/shared/)                            │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │                                                               │ │
│  │  websocket_manager.py (210 lines)                            │ │
│  │  ├─ ConnectionManager class                                 │ │
│  │  ├─ connect() / disconnect()                                │ │
│  │  ├─ send_message() / broadcast()                            │ │
│  │  ├─ Room-based messaging                                    │ │
│  │  └─ Client metadata tracking                                │ │
│  │                                                               │ │
│  │  ai_client.py (293 lines)                                    │ │
│  │  ├─ AIClient wrapper for OpenAI API                         │ │
│  │  ├─ chat_completion() - Non-streaming                       │ │
│  │  ├─ chat_completion_stream() - Streaming                    │ │
│  │  ├─ simple_chat() - Simplified interface                    │ │
│  │  └─ Configuration management                                │ │
│  │                                                               │ │
│  │  utils.py (386 lines)                                        │ │
│  │  ├─ UUID/ID generation                                      │ │
│  │  ├─ Hashing functions                                       │ │
│  │  ├─ JSON utilities                                          │ │
│  │  ├─ File system helpers                                     │ │
│  │  ├─ Date/time utilities                                     │ │
│  │  ├─ String manipulation                                     │ │
│  │  ├─ Validation functions                                    │ │
│  │  └─ Timer context manager                                   │ │
│  │                                                               │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ uses
                                  ▼
┌────────────────────────────────────────────────────────────────────┐
│                      External Services                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   Database   │  │   OpenAI     │  │  WebSocket   │            │
│  │   (SQLite)   │  │     API      │  │   Clients    │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘


┌────────────────────────────────────────────────────────────────────┐
│                    Configuration Sources                            │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Priority Order (Highest to Lowest):                              │
│                                                                      │
│   1. Default LLM Config (Database)                                  │
│      └─ Runtime config stored in SQLite (llm_config table)         │
│                                                                      │
│   2. Environment Variables                                          │
│      └─ OPENAI_API_KEY, HOST, PORT, etc.                          │
│                                                                      │
│   3. Default Values                                                 │
│      └─ Hardcoded defaults in code                                 │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘


┌────────────────────────────────────────────────────────────────────┐
│                      Request Flow Example                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Client Request                                                     │
│       │                                                              │
│       ▼                                                              │
│  FastAPI Endpoint                                                   │
│       │                                                              │
│       ├─► Dependency: verify_api_key()     [core/dependencies]     │
│       │      └─► Check API key validity                            │
│       │                                                              │
│       ├─► Dependency: get_db_session()     [config/database]       │
│       │      └─► Get database session                              │
│       │                                                              │
│       ├─► Dependency: pagination_params()  [core/dependencies]     │
│       │      └─► Parse skip/limit                                  │
│       │                                                              │
│       ▼                                                              │
│  Business Logic                                                     │
│       │                                                              │
│       ├─► Use AIClient                     [shared/ai_client]      │
│       │      └─► Call OpenAI API                                   │
│       │                                                              │
│       ├─► Use WebSocket Manager           [shared/websocket_mgr]  │
│       │      └─► Send real-time updates                            │
│       │                                                              │
│       ├─► Use Utilities                    [shared/utils]          │
│       │      └─► Format data, validate, etc.                       │
│       │                                                              │
│       ▼                                                              │
│  Response                                                           │
│       │                                                              │
│       ▼                                                              │
│  Client                                                             │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘


┌────────────────────────────────────────────────────────────────────┐
│                        File Statistics                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Total Files Created:      14                                      │
│  Total Python Code:        1,401 lines                             │
│  Documentation:            3 files (26K)                           │
│  Test Coverage:            All components tested                   │
│                                                                      │
│  Breakdown by Layer:                                               │
│    Config Layer:          345 lines (24.6%)                        │
│    Core Layer:            167 lines (11.9%)                        │
│    Shared Layer:          889 lines (63.5%)                        │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘


┌────────────────────────────────────────────────────────────────────┐
│                         Key Benefits                                │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ✓ Separation of Concerns                                          │
│    Each layer has a specific responsibility                        │
│                                                                      │
│  ✓ Reusability                                                     │
│    Components can be imported and used independently               │
│                                                                      │
│  ✓ Testability                                                     │
│    Each component can be tested in isolation                       │
│                                                                      │
│  ✓ Maintainability                                                 │
│    Easy to locate and modify specific functionality                │
│                                                                      │
│  ✓ Type Safety                                                     │
│    Dataclasses and type hints throughout                           │
│                                                                      │
│  ✓ Configuration Flexibility                                       │
│    Multiple configuration sources with clear priorities            │
│                                                                      │
│  ✓ Production Ready                                                │
│    Error handling, logging, and best practices                     │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘
```

## Component Relationships

```
settings.py ──┐
              ├──► Used by ──► dependencies.py
database.py ──┘                     │
                                    │
                                    ├──► Used by ──► FastAPI Routes
                                    │
ai_client.py ────► Uses ──────┐    │
                              │    │
websocket_manager.py ─────────┼────┤
                              │    │
utils.py ─────────────────────┘    │
                                    │
                                    ▼
                               Application
```

## Import Dependencies

```
backend/
├── config/
│   ├── settings.py
│   │   └── imports: os, yaml, pathlib, logging
│   │
│   └── database.py
│       └── imports: sqlalchemy, settings
│
├── core/
│   └── dependencies.py
│       └── imports: fastapi, database, settings
│
└── shared/
    ├── websocket_manager.py
    │   └── imports: fastapi, logging
    │
    ├── ai_client.py
    │   └── imports: httpx, settings, logging
    │
    └── utils.py
        └── imports: os, json, hashlib, uuid, datetime, pathlib
```
