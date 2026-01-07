"""
Modern User Schemas (Pydantic v2 + FastAPI-Users)
Type-safe request/response models
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from fastapi_users import schemas

from core.models.user import SubscriptionTier, CollaboratorRole


# === FastAPI-Users Standard Schemas ===

class UserRead(schemas.BaseUser[int]):
    """
    User response schema (what API returns)
    Excludes sensitive data like hashed_password
    """
    id: int
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    subscription_tier: SubscriptionTier
    subscription_expires_at: Optional[datetime] = None
    is_active: bool
    is_superuser: bool
    is_verified: bool
    llm_calls_this_month: int
    storage_used_bytes: int
    last_login_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(schemas.BaseUserCreate):
    """
    User registration schema
    """
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = Field(None, max_length=100)


class UserUpdate(schemas.BaseUserUpdate):
    """
    User update schema (for profile updates)
    """
    password: Optional[str] = Field(None, min_length=8)
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)


# === Custom Response Models ===

class UserProfile(BaseModel):
    """
    Extended user profile with subscription details
    """
    id: int
    email: EmailStr
    name: Optional[str]
    avatar_url: Optional[str]
    subscription_tier: SubscriptionTier
    subscription_expires_at: Optional[datetime]
    is_verified: bool
    created_at: datetime

    # Usage stats
    llm_calls_this_month: int
    llm_calls_limit: int
    storage_used_mb: float
    storage_limit_mb: int

    # Project counts
    owned_projects_count: int
    collaborated_projects_count: int

    model_config = ConfigDict(from_attributes=True)


class UsageStats(BaseModel):
    """
    Current month usage statistics
    """
    llm_calls: int
    llm_calls_limit: int
    llm_calls_percentage: float
    storage_used_mb: float
    storage_limit_mb: int
    storage_percentage: float
    can_generate: bool
    upgrade_recommended: bool


class SubscriptionUpdate(BaseModel):
    """
    Update subscription tier (admin only)
    """
    user_id: int
    new_tier: SubscriptionTier
    expires_at: Optional[datetime] = None


# === Project Collaboration Schemas ===

class CollaboratorInvite(BaseModel):
    """
    Invite a user to collaborate on a project
    """
    project_id: int
    email: EmailStr
    role: CollaboratorRole = CollaboratorRole.VIEWER
    message: Optional[str] = Field(None, max_length=500)


class CollaboratorResponse(BaseModel):
    """
    Collaborator information
    """
    id: int
    user_id: int
    user_email: str
    user_name: Optional[str]
    user_avatar: Optional[str]
    role: CollaboratorRole
    invited_at: datetime
    accepted_at: Optional[datetime]
    is_pending: bool

    model_config = ConfigDict(from_attributes=True)


class CollaboratorUpdate(BaseModel):
    """
    Update collaborator role
    """
    role: CollaboratorRole


class ProjectAccessCheck(BaseModel):
    """
    Check if user has access to a project
    """
    project_id: int
    user_id: int
    has_access: bool
    role: Optional[CollaboratorRole]
    permissions: list[str]


# === OAuth Schemas ===

class OAuthAccountResponse(BaseModel):
    """
    OAuth account information (sanitized)
    """
    id: int
    oauth_name: str
    account_email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# === Authentication Response ===

class TokenResponse(BaseModel):
    """
    JWT token response (FastAPI-Users format)
    """
    access_token: str
    token_type: str = "bearer"


class AuthenticatedResponse(BaseModel):
    """
    Full authentication response with user data
    """
    access_token: str
    token_type: str = "bearer"
    user: UserRead
