"""
Voice Fingerprinting API Schemas

Pydantic models for voice fingerprinting requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


# === Request Schemas ===

class AnalyzeVoiceRequest(BaseModel):
    """Request to analyze character voice and create fingerprint"""
    character_id: int = Field(..., description="Character ID to analyze")


class ExtractDialogueRequest(BaseModel):
    """Request to extract dialogue from prose"""
    project_id: int = Field(..., description="Project ID")
    scene_id: Optional[int] = Field(None, description="Scene ID if extracting from specific scene")
    prose: str = Field(..., description="Prose text to extract dialogue from")
    character_id: int = Field(..., description="Character ID")
    character_name: str = Field(..., description="Character name for attribution")


class CheckConsistencyRequest(BaseModel):
    """Request to check dialogue consistency"""
    character_id: int = Field(..., description="Character ID")
    dialogue_text: str = Field(..., description="Dialogue to check")
    scene_id: Optional[int] = Field(None, description="Optional scene ID for tracking")


# === Response Schemas ===

class VocabularyProfileResponse(BaseModel):
    """Vocabulary analysis results"""
    word_frequency: Dict[str, int]
    avg_word_length: float
    unique_word_ratio: float
    rarity_score: float
    top_words: List[str]
    avoided_words: List[str]


class SyntaxProfileResponse(BaseModel):
    """Syntax analysis results"""
    avg_sentence_length: float
    sentence_length_variance: float
    complexity_score: float
    question_frequency: float
    exclamation_frequency: float
    subordinate_clause_frequency: float


class LinguisticMarkersResponse(BaseModel):
    """Linguistic quirks and patterns"""
    catchphrases: List[str]
    filler_words: List[str]
    sentence_starters: List[str]
    quirks: List[str]
    contractions_ratio: float
    profanity_frequency: float


class EmotionalBaselineResponse(BaseModel):
    """Emotional tone distribution"""
    joy: float
    anger: float
    sadness: float
    fear: float
    surprise: float
    neutral: float
    dominant_emotion: str


class VoiceFingerprintResponse(BaseModel):
    """Complete voice fingerprint"""
    id: int
    character_id: int
    vocabulary_profile: Dict[str, Any]
    syntax_profile: Dict[str, Any]
    linguistic_markers: Dict[str, Any]
    emotional_baseline: Dict[str, Any]
    formality_score: float = Field(..., description="0-1, casual to formal")
    confidence_score: float = Field(..., description="0-1, fingerprint reliability")
    sample_count: int = Field(..., description="Number of dialogue samples analyzed")
    total_words: int = Field(..., description="Total words analyzed")
    last_analyzed_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConsistencyIssueResponse(BaseModel):
    """A detected consistency issue"""
    type: str = Field(..., description="vocabulary, syntax, formality, emotion")
    severity: str = Field(..., description="low, medium, high")
    description: str
    line_number: int
    problematic_text: str


class ConsistencySuggestionResponse(BaseModel):
    """Suggested fix for an issue"""
    issue_index: int
    original_text: str
    suggested_text: str
    reason: str


class ConsistencyResultResponse(BaseModel):
    """Complete consistency check result"""
    overall_score: float = Field(..., description="0-1, overall consistency")
    vocabulary_score: float = Field(..., description="0-1, word choice consistency")
    syntax_score: float = Field(..., description="0-1, sentence structure consistency")
    formality_score: float = Field(..., description="0-1, formality match")
    emotional_score: float = Field(..., description="0-1, emotional tone match")
    issues: List[ConsistencyIssueResponse]
    suggestions: List[ConsistencySuggestionResponse]


class DialogueLineResponse(BaseModel):
    """Extracted dialogue line"""
    id: int
    project_id: int
    scene_id: Optional[int]
    character_id: int
    text: str
    context: Optional[str]
    word_count: int
    extracted_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExtractDialogueResponse(BaseModel):
    """Result of dialogue extraction"""
    success: bool
    lines_extracted: int
    message: str


class ConsistencyHistoryResponse(BaseModel):
    """Historical consistency scores for a character"""
    character_id: int
    character_name: str
    scores: List[Dict[str, Any]] = Field(..., description="List of {scene_id, overall_score, timestamp}")
    avg_score: float = Field(..., description="Average consistency score")
    total_checks: int


class VoiceFingerprintStatsResponse(BaseModel):
    """Statistics about voice fingerprints"""
    total_fingerprints: int
    characters_analyzed: List[Dict[str, Any]]
    avg_confidence: float
    low_confidence_characters: List[Dict[str, Any]] = Field(..., description="Characters needing more samples")
