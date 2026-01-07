"""
Modern Authentication Configuration (FastAPI-Users)
Production-ready auth with async support
"""
import os
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.user import User
from core.database.base import get_async_db


# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_LIFETIME_SECONDS = 3600  # 1 hour
REFRESH_TOKEN_LIFETIME_SECONDS = 2592000  # 30 days


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """
    User manager with custom business logic
    """
    reset_password_token_secret = SECRET_KEY
    verification_token_secret = SECRET_KEY

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        Hook: After user registration
        - Send welcome email
        - Track analytics
        - Create default project
        """
        print(f"User {user.id} has registered.")
        # TODO: Send welcome email
        # TODO: Create default "My First Novel" project
        # TODO: Track analytics event

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Hook: After password reset request"""
        print(f"User {user.id} has forgotten their password. Reset token: {token}")
        # TODO: Send password reset email

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Hook: After email verification request"""
        print(f"Verification requested for user {user.id}. Verification token: {token}")
        # TODO: Send verification email


async def get_user_db(session: AsyncSession = Depends(get_async_db)):
    """Dependency: Get async user database"""
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """Dependency: Get user manager"""
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    """JWT strategy with configurable lifetime"""
    return JWTStrategy(
        secret=SECRET_KEY,
        lifetime_seconds=ACCESS_TOKEN_LIFETIME_SECONDS,
        algorithm=ALGORITHM,
    )


# Bearer transport (Authorization: Bearer <token>)
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# Authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# FastAPI-Users instance
fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

# Dependencies for route protection
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
current_verified_user = fastapi_users.current_user(active=True, verified=True)


# Usage tracking decorator
async def check_usage_limits(user: User = Depends(current_active_user)) -> User:
    """
    Dependency: Check if user is within usage limits
    Raises HTTPException if limits exceeded
    """
    from fastapi import HTTPException, status

    limits = {
        "free": {"llm_calls": 100, "storage_mb": 100},
        "pro": {"llm_calls": 1000, "storage_mb": 1000},
        "studio": {"llm_calls": 10000, "storage_mb": 10000},
    }

    tier_limits = limits[user.subscription_tier.value]

    if user.llm_calls_this_month >= tier_limits["llm_calls"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Monthly LLM call limit ({tier_limits['llm_calls']}) exceeded. "
                   f"Please upgrade your plan or wait until next month."
        )

    if user.storage_used_bytes > tier_limits["storage_mb"] * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            detail=f"Storage limit ({tier_limits['storage_mb']}MB) exceeded. "
                   f"Please upgrade your plan or delete some projects."
        )

    return user
