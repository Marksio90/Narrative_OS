"""
Modern Authentication Routes (FastAPI-Users)
Production-ready auth endpoints with best practices 2026
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.auth.config import (
    fastapi_users,
    auth_backend,
    current_active_user,
    current_superuser,
)
from core.models.user import User, SubscriptionTier
from core.database.base import get_async_db
from api.schemas.user import (
    UserRead,
    UserCreate,
    UserUpdate,
    UserProfile,
    UsageStats,
    SubscriptionUpdate,
)


# === FastAPI-Users Standard Routes ===

# Authentication router (login, logout)
auth_router = fastapi_users.get_auth_router(auth_backend)

# Registration router
register_router = fastapi_users.get_register_router(UserRead, UserCreate)

# User management router (get, update, delete self)
users_router = fastapi_users.get_users_router(UserRead, UserUpdate)

# Password reset router
reset_password_router = fastapi_users.get_reset_password_router()

# Email verification router
verify_router = fastapi_users.get_verify_router(UserRead)


# === Custom Routes ===

custom_router = APIRouter(prefix="/auth", tags=["Authentication"])


@custom_router.get("/me/profile", response_model=UserProfile)
async def get_current_user_profile(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get current user's extended profile with stats
    """
    # Get project counts
    from core.models.base import Project
    from core.models.user import ProjectCollaborator

    owned_count_query = select(func.count(Project.id)).where(
        Project.owner_id == user.id,
        Project.deleted_at.is_(None)
    )
    owned_count = await db.scalar(owned_count_query) or 0

    collab_count_query = select(func.count(ProjectCollaborator.id)).where(
        ProjectCollaborator.user_id == user.id
    )
    collab_count = await db.scalar(collab_count_query) or 0

    # Calculate limits based on tier
    limits = {
        SubscriptionTier.FREE: {"llm_calls": 100, "storage_mb": 100},
        SubscriptionTier.PRO: {"llm_calls": 1000, "storage_mb": 1000},
        SubscriptionTier.STUDIO: {"llm_calls": 10000, "storage_mb": 10000},
    }

    tier_limits = limits[user.subscription_tier]

    return UserProfile(
        **user.__dict__,
        llm_calls_limit=tier_limits["llm_calls"],
        storage_used_mb=user.storage_used_bytes / (1024 * 1024),
        storage_limit_mb=tier_limits["storage_mb"],
        owned_projects_count=owned_count,
        collaborated_projects_count=collab_count,
    )


@custom_router.get("/me/usage", response_model=UsageStats)
async def get_current_user_usage(user: User = Depends(current_active_user)):
    """
    Get current month's usage statistics
    """
    limits = {
        SubscriptionTier.FREE: {"llm_calls": 100, "storage_mb": 100},
        SubscriptionTier.PRO: {"llm_calls": 1000, "storage_mb": 1000},
        SubscriptionTier.STUDIO: {"llm_calls": 10000, "storage_mb": 10000},
    }

    tier_limits = limits[user.subscription_tier]
    storage_used_mb = user.storage_used_bytes / (1024 * 1024)

    llm_percentage = (user.llm_calls_this_month / tier_limits["llm_calls"]) * 100
    storage_percentage = (storage_used_mb / tier_limits["storage_mb"]) * 100

    return UsageStats(
        llm_calls=user.llm_calls_this_month,
        llm_calls_limit=tier_limits["llm_calls"],
        llm_calls_percentage=round(llm_percentage, 2),
        storage_used_mb=round(storage_used_mb, 2),
        storage_limit_mb=tier_limits["storage_mb"],
        storage_percentage=round(storage_percentage, 2),
        can_generate=user.llm_calls_this_month < tier_limits["llm_calls"],
        upgrade_recommended=llm_percentage > 80 or storage_percentage > 80,
    )


@custom_router.post("/admin/update-subscription", response_model=UserRead)
async def update_user_subscription(
    data: SubscriptionUpdate,
    admin: User = Depends(current_superuser),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Update user's subscription (admin only)
    """
    # Get user
    user_query = select(User).where(User.id == data.user_id)
    result = await db.execute(user_query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update subscription
    user.subscription_tier = data.new_tier
    user.subscription_expires_at = data.expires_at

    await db.commit()
    await db.refresh(user)

    return user


@custom_router.post("/me/reset-usage", response_model=UserRead)
async def reset_monthly_usage(
    admin: User = Depends(current_superuser),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Reset all users' monthly usage counters (admin only, called by cron)
    """
    from sqlalchemy import update

    await db.execute(
        update(User).values(llm_calls_this_month=0)
    )
    await db.commit()

    return {"message": "Monthly usage reset for all users"}


# === Helper Functions ===

async def increment_user_llm_calls(user_id: int, db: AsyncSession):
    """
    Increment user's LLM call counter (call this after each LLM request)
    """
    user_query = select(User).where(User.id == user_id)
    result = await db.execute(user_query)
    user = result.scalar_one_or_none()

    if user:
        user.llm_calls_this_month += 1
        await db.commit()


async def update_user_storage(user_id: int, bytes_delta: int, db: AsyncSession):
    """
    Update user's storage usage (call when projects/prose changes)
    """
    user_query = select(User).where(User.id == user_id)
    result = await db.execute(user_query)
    user = result.scalar_one_or_none()

    if user:
        user.storage_used_bytes = max(0, user.storage_used_bytes + bytes_delta)
        await db.commit()
