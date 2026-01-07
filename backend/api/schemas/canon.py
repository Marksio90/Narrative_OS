"""
Pydantic schemas for Canon API

Request/response validation for all Canon entities
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ===== Base Schemas =====

class CanonEntityBase(BaseModel):
    """Base schema for all canon entities"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    claims: Dict[str, Any] = Field(default_factory=dict)
    unknowns: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class CanonEntityCreate(CanonEntityBase):
    """Schema for creating canon entities"""
    project_id: int


class CanonEntityUpdate(BaseModel):
    """Schema for updating canon entities (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    claims: Optional[Dict[str, Any]] = None
    unknowns: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class CanonEntityResponse(CanonEntityBase):
    """Base response schema"""
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    canon_version_id: Optional[int] = None

    class Config:
        from_attributes = True


# ===== Character Schemas =====

class CharacterCreate(CanonEntityCreate):
    """Create character request"""
    goals: List[str] = Field(default_factory=list)
    values: List[str] = Field(default_factory=list)
    fears: List[str] = Field(default_factory=list)
    secrets: List[str] = Field(default_factory=list)
    behavioral_limits: List[str] = Field(default_factory=list)
    behavioral_patterns: List[str] = Field(default_factory=list)
    voice_profile: Dict[str, Any] = Field(default_factory=dict)
    relationships: Dict[str, Any] = Field(default_factory=dict)
    appearance: Dict[str, Any] = Field(default_factory=dict)
    background: Optional[str] = None
    arc: Dict[str, Any] = Field(default_factory=dict)


class CharacterUpdate(CanonEntityUpdate):
    """Update character request"""
    goals: Optional[List[str]] = None
    values: Optional[List[str]] = None
    fears: Optional[List[str]] = None
    secrets: Optional[List[str]] = None
    behavioral_limits: Optional[List[str]] = None
    behavioral_patterns: Optional[List[str]] = None
    voice_profile: Optional[Dict[str, Any]] = None
    relationships: Optional[Dict[str, Any]] = None
    appearance: Optional[Dict[str, Any]] = None
    background: Optional[str] = None
    arc: Optional[Dict[str, Any]] = None


class CharacterResponse(CanonEntityResponse):
    """Character response"""
    goals: List[str]
    values: List[str]
    fears: List[str]
    secrets: List[str]
    behavioral_limits: List[str]
    behavioral_patterns: List[str]
    voice_profile: Dict[str, Any]
    relationships: Dict[str, Any]
    appearance: Dict[str, Any]
    background: Optional[str]
    arc: Dict[str, Any]


# ===== Location Schemas =====

class LocationCreate(CanonEntityCreate):
    """Create location request"""
    geography: Dict[str, Any] = Field(default_factory=dict)
    climate: Optional[str] = None
    social_rules: List[str] = Field(default_factory=list)
    power_structure: Dict[str, Any] = Field(default_factory=dict)
    restrictions: List[str] = Field(default_factory=list)
    access_control: Dict[str, Any] = Field(default_factory=dict)
    atmosphere: Optional[str] = None
    connected_to: List[Dict[str, Any]] = Field(default_factory=list)


class LocationUpdate(CanonEntityUpdate):
    """Update location request"""
    geography: Optional[Dict[str, Any]] = None
    climate: Optional[str] = None
    social_rules: Optional[List[str]] = None
    power_structure: Optional[Dict[str, Any]] = None
    restrictions: Optional[List[str]] = None
    access_control: Optional[Dict[str, Any]] = None
    atmosphere: Optional[str] = None
    connected_to: Optional[List[Dict[str, Any]]] = None


class LocationResponse(CanonEntityResponse):
    """Location response"""
    geography: Dict[str, Any]
    climate: Optional[str]
    social_rules: List[str]
    power_structure: Dict[str, Any]
    restrictions: List[str]
    access_control: Dict[str, Any]
    atmosphere: Optional[str]
    connected_to: List[Dict[str, Any]]


# ===== Promise Schemas =====

class PromiseCreate(CanonEntityCreate):
    """Create promise request"""
    setup_chapter: int = Field(..., ge=1)
    setup_scene: Optional[int] = None
    setup_description: str = Field(..., min_length=1)
    payoff_required: str = Field(..., min_length=1)
    payoff_deadline: Optional[int] = Field(None, ge=1)


class PromiseUpdate(CanonEntityUpdate):
    """Update promise request"""
    setup_chapter: Optional[int] = Field(None, ge=1)
    setup_scene: Optional[int] = None
    setup_description: Optional[str] = None
    payoff_required: Optional[str] = None
    payoff_deadline: Optional[int] = Field(None, ge=1)
    status: Optional[str] = None
    payoff_chapter: Optional[int] = None
    payoff_scene: Optional[int] = None
    payoff_description: Optional[str] = None


class PromiseResponse(CanonEntityResponse):
    """Promise response"""
    setup_chapter: int
    setup_scene: Optional[int]
    setup_description: str
    payoff_required: str
    payoff_deadline: Optional[int]
    status: str
    payoff_chapter: Optional[int]
    payoff_scene: Optional[int]
    payoff_description: Optional[str]
    validated: Dict[str, Any]


# ===== Thread Schemas =====

class ThreadCreate(CanonEntityCreate):
    """Create thread request"""
    thread_type: str
    start_chapter: int = Field(..., ge=1)
    end_chapter: Optional[int] = Field(None, ge=1)
    stakes: Optional[str] = None
    deadline: Optional[int] = Field(None, ge=1)
    related_characters: List[int] = Field(default_factory=list)
    related_promises: List[int] = Field(default_factory=list)


class ThreadUpdate(CanonEntityUpdate):
    """Update thread request"""
    thread_type: Optional[str] = None
    start_chapter: Optional[int] = Field(None, ge=1)
    end_chapter: Optional[int] = Field(None, ge=1)
    status: Optional[str] = None
    current_chapter: Optional[int] = None
    tension_level: Optional[int] = Field(None, ge=0, le=100)
    stakes: Optional[str] = None
    deadline: Optional[int] = Field(None, ge=1)
    related_characters: Optional[List[int]] = None
    related_promises: Optional[List[int]] = None


class ThreadResponse(CanonEntityResponse):
    """Thread response"""
    thread_type: str
    start_chapter: int
    end_chapter: Optional[int]
    status: str
    current_chapter: Optional[int]
    tension_level: int
    stakes: Optional[str]
    deadline: Optional[int]
    milestones: List[Dict[str, Any]]
    related_characters: List[int]
    related_promises: List[int]


# ===== Version Schemas =====

class CanonVersionResponse(BaseModel):
    """Canon version response"""
    id: int
    project_id: int
    version_number: int
    commit_message: Optional[str]
    changes: Dict[str, Any]
    parent_version_id: Optional[int]
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Validation Schemas =====

class ValidationResult(BaseModel):
    """Entity validation result"""
    valid: bool
    issues: List[str] = Field(default_factory=list)


# ===== Bulk Operations =====

class BulkCreateRequest(BaseModel):
    """Bulk create entities"""
    entities: List[Dict[str, Any]]
    commit_message: Optional[str] = None


class EntityStatsResponse(BaseModel):
    """Canon entity statistics"""
    character: int = 0
    location: int = 0
    faction: int = 0
    magic_rule: int = 0
    item: int = 0
    event: int = 0
    promise: int = 0
    thread: int = 0
    style_profile: int = 0
    total: int = 0


# ===== Generic Response =====

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    details: Optional[Dict[str, Any]] = None
