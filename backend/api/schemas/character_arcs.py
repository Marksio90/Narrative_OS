"""
Character Arc Tracker API Schemas

Pydantic models for character arc requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


# ==================== Request Schemas ====================

class CreateArcRequest(BaseModel):
    """Request to create a new character arc"""
    project_id: int = Field(..., description="Project ID")
    character_id: int = Field(..., description="Character ID")
    arc_type: str = Field(..., description="Arc type (positive_change, redemption, etc.)")
    name: Optional[str] = Field(None, description="Arc name")
    description: Optional[str] = Field(None, description="Arc description")
    start_chapter: Optional[int] = Field(1, description="Starting chapter")
    end_chapter: Optional[int] = Field(None, description="Target end chapter")
    starting_state: Optional[Dict[str, Any]] = Field(None, description="Character's starting state")
    ending_state: Optional[Dict[str, Any]] = Field(None, description="Target ending state")


class UpdateArcProgressRequest(BaseModel):
    """Update arc progress"""
    current_chapter: int = Field(..., description="Current chapter")
    completion_percentage: Optional[float] = Field(None, description="0-100%")


class AddMilestoneRequest(BaseModel):
    """Add milestone to arc"""
    arc_id: int = Field(..., description="Arc ID")
    chapter_number: int = Field(..., description="Chapter where milestone occurs")
    milestone_type: str = Field(..., description="catalyst, crisis, revelation, etc.")
    title: str = Field(..., min_length=3, max_length=255, description="Milestone title")
    description: Optional[str] = Field(None, description="Detailed description")
    emotional_impact: Optional[float] = Field(None, ge=0.0, le=1.0)
    character_change: Optional[str] = Field(None, description="What changed in character")
    story_event_id: Optional[int] = Field(None, description="Link to story event")


class TrackEmotionalStateRequest(BaseModel):
    """Track emotional state"""
    character_id: int = Field(..., description="Character ID")
    chapter_number: int = Field(..., description="Chapter number")
    dominant_emotion: str = Field(..., description="Primary emotion")
    intensity: float = Field(..., ge=0.0, le=1.0, description="Emotion intensity")
    valence: float = Field(..., ge=-1.0, le=1.0, description="Negative to positive")
    arc_id: Optional[int] = Field(None, description="Associated arc ID")
    secondary_emotions: Optional[List[str]] = Field(default_factory=list)
    triggers: Optional[List[Dict]] = Field(default_factory=list)
    mental_state: Optional[str] = Field(None)
    stress_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_level: Optional[float] = Field(None, ge=0.0, le=1.0)


class CreateGoalRequest(BaseModel):
    """Create character goal"""
    character_id: int = Field(..., description="Character ID")
    goal_description: str = Field(..., min_length=10, description="What character wants")
    chapter_number: int = Field(1, description="Chapter where goal starts")
    goal_type: Optional[str] = Field(None, description="external, internal, relationship")
    priority: int = Field(1, ge=1, le=10, description="1=highest priority")
    stakes: Optional[str] = Field(None, description="What happens if they fail")
    arc_id: Optional[int] = Field(None, description="Associated arc")


class UpdateGoalProgressRequest(BaseModel):
    """Update goal progress"""
    chapter_number: int = Field(..., description="Current chapter")
    progress_percentage: float = Field(..., ge=0.0, le=100.0, description="0-100%")
    obstacle: Optional[Dict] = Field(None, description="New obstacle encountered")
    victory: Optional[Dict] = Field(None, description="Small win")
    setback: Optional[Dict] = Field(None, description="Major setback")


class TrackRelationshipChangeRequest(BaseModel):
    """Track relationship evolution"""
    character_id: int = Field(..., description="Character ID")
    related_character_id: int = Field(..., description="Other character ID")
    chapter_number: int = Field(..., description="Chapter number")
    relationship_type: str = Field(..., description="friend, enemy, lover, etc.")
    relationship_strength: float = Field(..., ge=-1.0, le=1.0, description="-1 hostile, +1 close")
    trust_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    affection_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    respect_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    conflict_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    key_moment: Optional[Dict] = Field(None, description="What caused this change")


class AnalyzeSceneForMilestoneRequest(BaseModel):
    """Analyze scene for character milestone"""
    arc_id: int = Field(..., description="Arc ID")
    scene_text: str = Field(..., min_length=50, description="Scene prose")
    chapter_number: int = Field(..., description="Chapter number")
    story_event_id: Optional[int] = Field(None, description="Associated story event")


class ExtractEmotionalStateRequest(BaseModel):
    """Extract emotional state from scene"""
    character_id: int = Field(..., description="Character ID")
    chapter_number: int = Field(..., description="Chapter number")
    scene_text: str = Field(..., min_length=50, description="Scene prose")
    arc_id: Optional[int] = Field(None, description="Associated arc")


# ==================== Response Schemas ====================

class ArcResponse(BaseModel):
    """Character arc response"""
    id: int
    project_id: int
    character_id: int
    arc_type: str
    name: str
    description: Optional[str]
    starting_state: Dict[str, Any]
    ending_state: Dict[str, Any]
    start_chapter: Optional[int]
    end_chapter: Optional[int]
    current_chapter: Optional[int]
    completion_percentage: float
    is_on_track: bool
    pacing_score: Optional[float]
    consistency_score: Optional[float]
    is_complete: bool
    validation_notes: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MilestoneResponse(BaseModel):
    """Arc milestone response"""
    id: int
    arc_id: int
    project_id: int
    chapter_number: int
    milestone_type: str
    title: str
    description: Optional[str]
    emotional_impact: Optional[float]
    character_change: Optional[str]
    significance: float
    is_achieved: bool
    expected_chapter: Optional[int]
    actual_chapter: Optional[int]
    ai_analysis: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmotionalStateResponse(BaseModel):
    """Emotional state response"""
    id: int
    project_id: int
    character_id: int
    character_arc_id: Optional[int]
    chapter_number: int
    dominant_emotion: Optional[str]
    secondary_emotions: List[str]
    intensity: Optional[float]
    valence: Optional[float]
    triggers: List[Dict]
    inner_conflict: Optional[str]
    mental_state: Optional[str]
    stress_level: Optional[float]
    confidence_level: Optional[float]
    detected_from_text: bool
    ai_confidence: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GoalProgressResponse(BaseModel):
    """Goal progress response"""
    id: int
    project_id: int
    character_id: int
    character_arc_id: Optional[int]
    goal_description: str
    goal_type: Optional[str]
    priority: int
    chapter_number: int
    progress_percentage: float
    status: str
    obstacles_faced: List[Dict]
    victories: List[Dict]
    setbacks: List[Dict]
    motivation_strength: Optional[float]
    stakes: Optional[str]
    achieved_chapter: Optional[int]
    failed_chapter: Optional[int]
    abandonment_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RelationshipEvolutionResponse(BaseModel):
    """Relationship evolution response"""
    id: int
    project_id: int
    character_id: int
    related_character_id: int
    chapter_number: int
    relationship_type: Optional[str]
    trust_level: Optional[float]
    affection_level: Optional[float]
    respect_level: Optional[float]
    conflict_level: Optional[float]
    relationship_strength: Optional[float]
    key_moments: List[Dict]
    current_status: Optional[str]
    trajectory: Optional[str]
    last_interaction_chapter: Optional[int]
    last_interaction_type: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArcWithMilestonesResponse(BaseModel):
    """Arc with its milestones"""
    arc: ArcResponse
    milestones: List[MilestoneResponse]
    milestone_count: int
    achieved_count: int


class CharacterArcSummaryResponse(BaseModel):
    """Summary of character's arcs"""
    character_id: int
    character_name: str
    total_arcs: int
    active_arcs: int
    completed_arcs: int
    arcs: List[ArcResponse]


class EmotionalJourneyResponse(BaseModel):
    """Emotional journey data"""
    character_id: int
    character_name: str
    start_chapter: int
    end_chapter: int
    states: List[EmotionalStateResponse]
    dominant_emotions: Dict[str, int]
    intensity_average: float
    valence_trend: str


class ArcHealthAnalysisResponse(BaseModel):
    """AI analysis of arc health"""
    arc_id: int
    pacing_score: float
    consistency_score: float
    arc_health_score: float
    is_on_track: bool
    issues: List[str]
    suggestions: List[str]
    missing_milestones: List[str]
    strengths: List[str]


class ArcReportResponse(BaseModel):
    """Comprehensive arc report"""
    arc: Dict[str, Any]
    character: Dict[str, Any]
    health: ArcHealthAnalysisResponse
    milestones: Dict[str, Any]
    emotional_journey: Dict[str, Any]
    goals: Dict[str, Any]


class GoalSummaryResponse(BaseModel):
    """Character goals summary"""
    character_id: int
    character_name: str
    total_goals: int
    active_goals: int
    achieved_goals: int
    failed_goals: int
    goals: List[GoalProgressResponse]


class RelationshipTimelineResponse(BaseModel):
    """Relationship evolution timeline"""
    character_id: int
    related_character_id: int
    character_name: str
    related_character_name: str
    evolution: List[RelationshipEvolutionResponse]
    start_state: Optional[RelationshipEvolutionResponse]
    current_state: Optional[RelationshipEvolutionResponse]
    trajectory: str
    key_turning_points: List[Dict]
