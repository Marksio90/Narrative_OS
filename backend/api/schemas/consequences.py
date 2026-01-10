"""
Consequence Simulator API Schemas

Pydantic models for consequence tracking requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


# === Request Schemas ===

class AnalyzeSceneRequest(BaseModel):
    """Request to analyze a scene and extract events"""
    project_id: int = Field(..., description="Project ID")
    scene_id: int = Field(..., description="Scene ID")
    scene_text: str = Field(..., description="Full scene prose")
    chapter_number: Optional[int] = Field(None, description="Chapter number")


class PredictConsequencesRequest(BaseModel):
    """Request to predict consequences for an event"""
    event_id: int = Field(..., description="Story event ID")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional story context")


class MarkConsequenceRequest(BaseModel):
    """Request to mark a consequence status"""
    consequence_id: int = Field(..., description="Consequence ID")
    status: str = Field(..., description="New status: potential, active, realized, invalidated")
    target_event_id: Optional[int] = Field(None, description="Event where consequence was realized")
    invalidation_reason: Optional[str] = Field(None, description="Why consequence was invalidated")


class CreateEventRequest(BaseModel):
    """Request to manually create a story event"""
    project_id: int
    scene_id: Optional[int] = None
    chapter_number: Optional[int] = None
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    event_type: str = Field(..., description="decision, revelation, conflict, etc.")
    magnitude: float = Field(0.5, ge=0.0, le=1.0)
    emotional_impact: Optional[float] = Field(None, ge=0.0, le=1.0)
    affected_character_ids: List[int] = Field(default_factory=list)
    affected_location_ids: List[int] = Field(default_factory=list)
    affected_thread_ids: List[int] = Field(default_factory=list)


# === Response Schemas ===

class StoryEventResponse(BaseModel):
    """Story event response"""
    id: int
    project_id: int
    scene_id: Optional[int]
    chapter_number: Optional[int]
    title: str
    description: str
    event_type: str
    magnitude: float
    emotional_impact: Optional[float]
    causes: List[int]
    effects: List[int]
    ai_analysis: Optional[Dict[str, Any]]
    extracted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConsequenceResponse(BaseModel):
    """Consequence response"""
    id: int
    source_event_id: int
    target_event_id: Optional[int]
    description: str
    probability: float
    timeframe: str
    status: str
    affected_entities: Dict[str, List[int]]
    severity: float
    plot_impact: Optional[str]
    ai_prediction: Optional[Dict[str, Any]]
    predicted_at: Optional[datetime]
    realized_at: Optional[datetime]
    invalidated_at: Optional[datetime]
    invalidation_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EventWithConsequencesResponse(BaseModel):
    """Event with its consequences"""
    event: StoryEventResponse
    consequences: List[ConsequenceResponse]
    consequence_count: int
    active_consequence_count: int


class ConsequenceGraphResponse(BaseModel):
    """Complete consequence graph"""
    events: List[Dict[str, Any]]
    consequences: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
    total_events: int
    total_consequences: int
    active_consequences: int


class ActiveConsequencesResponse(BaseModel):
    """Active consequences for a project/chapter"""
    consequences: List[ConsequenceResponse]
    total_count: int
    high_probability_count: int = Field(..., description="Count with probability > 0.7")
    high_severity_count: int = Field(..., description="Count with severity > 0.7")


class AnalyzeSceneResponse(BaseModel):
    """Result of scene analysis"""
    success: bool
    events_extracted: int
    events: List[StoryEventResponse]
    consequences_predicted: int
    message: str


class ConsequenceStatsResponse(BaseModel):
    """Statistics about consequences for a project"""
    total_events: int
    total_consequences: int
    potential_consequences: int
    active_consequences: int
    realized_consequences: int
    invalidated_consequences: int
    avg_consequences_per_event: float
    events_by_type: Dict[str, int]
    consequences_by_timeframe: Dict[str, int]


class EventEntityResponse(BaseModel):
    """Event entity relationship"""
    id: int
    event_id: int
    entity_type: str
    entity_id: int
    involvement_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
