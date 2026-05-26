"""
FastAPI Dependencies

Provides reusable dependencies for FastAPI endpoints.
"""

from typing import Optional, Generator
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
import logging

from db.database import get_db
from runtime.config.settings import get_settings as get_app_settings
from runtime.shared import debug_info

logger = logging.getLogger(__name__)

# Get settings instance
_settings = get_app_settings()


def get_db_session() -> Generator[Session, None, None]:
    """
    Database session dependency

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db_session)):
            return db.query(Item).all()
    """
    return get_db()


async def get_api_key(x_api_key: Optional[str] = Header(None)) -> Optional[str]:
    """
    Extract API key from request headers

    Usage:
        @app.get("/protected")
        def protected_route(api_key: str = Depends(get_api_key)):
            return {"message": "Authenticated"}
    """
    return x_api_key


async def verify_api_key(api_key: Optional[str] = Depends(get_api_key)) -> str:
    """
    Verify API key is valid

    Usage:
        @app.get("/protected")
        def protected_route(api_key: str = Depends(verify_api_key)):
            return {"message": "Authenticated"}
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # TODO: Verify API key against database
    # For now, just check it's not empty
    if not api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key


async def get_current_user(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db_session)
) -> dict:
    """
    Get current authenticated user

    Usage:
        @app.get("/me")
        def get_me(user: dict = Depends(get_current_user)):
            return user
    """
    # TODO: Implement user lookup from database using API key
    # For now, return a mock user
    return {
        "id": 1,
        "username": "user",
        "email": "user@example.com",
        "api_key": api_key
    }


async def check_rate_limit(
    api_key: Optional[str] = Depends(get_api_key)
) -> bool:
    """
    Check rate limit for request

    Usage:
        @app.get("/limited")
        def limited_route(rate_ok: bool = Depends(check_rate_limit)):
            return {"message": "OK"}
    """
    # TODO: Implement rate limiting logic
    # For now, always allow
    return True


async def get_settings_dependency():
    """
    Settings dependency for FastAPI endpoints

    Usage:
        @app.get("/config")
        def get_config(app_settings = Depends(get_settings_dependency)):
            return {"version": app_settings.app_version}
    """
    return _settings


class RateLimiter:
    """
    Rate limiter dependency class

    Usage:
        limiter = RateLimiter(max_requests=10, window_seconds=60)

        @app.get("/limited")
        def limited_route(_: None = Depends(limiter)):
            return {"message": "OK"}
    """

    def __init__(self, max_requests: int = None, window_seconds: int = None):
        self.max_requests = max_requests or _settings.rate_limit.default_limit
        self.window_seconds = window_seconds or _settings.rate_limit.window_seconds
        self.requests = {}  # TODO: Use Redis for distributed rate limiting

    async def __call__(
        self,
        api_key: Optional[str] = Depends(get_api_key)
    ):
        """Check rate limit for the request"""
        # TODO: Implement actual rate limiting with sliding window
        # For now, always allow
        return None


def pagination_params(
    skip: int = 0,
    limit: int = 100
) -> dict:
    """
    Pagination parameters

    Usage:
        @app.get("/items")
        def get_items(
            pagination: dict = Depends(pagination_params),
            db: Session = Depends(get_db_session)
        ):
            return db.query(Item).offset(pagination['skip']).limit(pagination['limit']).all()
    """
    if limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit cannot exceed 1000"
        )
    return {"skip": skip, "limit": limit}
