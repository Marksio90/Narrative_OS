"""
Voice Fingerprinting API Routes

REST endpoints for character voice analysis and consistency checking
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from typing import List

from core.database.base import get_db
from services.ai.voice_fingerprint import VoiceFingerprintService
from core.models.canon import (
    Character,
    CharacterVoiceFingerprint,
    DialogueConsistencyScore
)
from api.schemas.voice_fingerprint import (
    AnalyzeVoiceRequest,
    ExtractDialogueRequest,
    CheckConsistencyRequest,
    VoiceFingerprintResponse,
    ConsistencyResultResponse,
    ExtractDialogueResponse,
    ConsistencyHistoryResponse,
    VoiceFingerprintStatsResponse,
)

router = APIRouter()


def get_voice_fingerprint_service(db: Session = Depends(get_db)) -> VoiceFingerprintService:
    """Dependency to get Voice Fingerprint service"""
    return VoiceFingerprintService(db)


# ===== Voice Fingerprint Endpoints =====

@router.post("/character/{character_id}/analyze-voice", response_model=VoiceFingerprintResponse)
async def analyze_character_voice(
    character_id: int,
    service: VoiceFingerprintService = Depends(get_voice_fingerprint_service),
):
    """
    Analyze character's dialogue and create/update voice fingerprint

    Extracts linguistic patterns from all existing dialogue for the character
    and creates a comprehensive voice fingerprint for consistency checking.

    Requires at least a few dialogue samples to work effectively.
    """
    try:
        fingerprint = await service.create_voice_fingerprint(character_id)
        return fingerprint
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/character/{character_id}/voice-fingerprint", response_model=VoiceFingerprintResponse)
async def get_voice_fingerprint(
    character_id: int,
    db: Session = Depends(get_db),
):
    """
    Get existing voice fingerprint for a character

    Returns 404 if no fingerprint exists yet.
    """
    fingerprint = db.execute(
        select(CharacterVoiceFingerprint).where(
            CharacterVoiceFingerprint.character_id == character_id
        )
    ).scalar_one_or_none()

    if not fingerprint:
        raise HTTPException(
            status_code=404,
            detail=f"No voice fingerprint found for character {character_id}. Run /analyze-voice first."
        )

    return fingerprint


@router.post("/character/extract-dialogue", response_model=ExtractDialogueResponse)
async def extract_dialogue(
    data: ExtractDialogueRequest,
    service: VoiceFingerprintService = Depends(get_voice_fingerprint_service),
):
    """
    Extract dialogue from prose and store for later analysis

    This endpoint processes prose text and extracts dialogue lines
    attributed to the specified character. Extracted dialogue is stored
    in the database and can be used to build voice fingerprints.

    Useful for:
    - Building initial fingerprint from existing scenes
    - Adding new dialogue samples to improve fingerprint accuracy
    - Manual dialogue attribution when AI attribution fails
    """
    try:
        count = await service.extract_and_store_dialogue(
            project_id=data.project_id,
            scene_id=data.scene_id,
            prose=data.prose,
            character_id=data.character_id,
            character_name=data.character_name
        )

        return ExtractDialogueResponse(
            success=True,
            lines_extracted=count,
            message=f"Successfully extracted {count} dialogue lines for {data.character_name}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/ai/check-dialogue-consistency", response_model=ConsistencyResultResponse)
async def check_dialogue_consistency(
    data: CheckConsistencyRequest,
    service: VoiceFingerprintService = Depends(get_voice_fingerprint_service),
):
    """
    Check if dialogue is consistent with character's voice fingerprint

    Analyzes new dialogue and scores it against the character's established
    voice fingerprint. Returns detailed scores, issues, and suggestions.

    Use this:
    - Before generating new scenes (to validate AI output)
    - When editing dialogue manually
    - To identify characters whose voice is drifting
    """
    try:
        result = await service.check_dialogue_consistency(
            character_id=data.character_id,
            dialogue_text=data.dialogue_text,
            scene_id=data.scene_id
        )

        return ConsistencyResultResponse(
            overall_score=result.overall_score,
            vocabulary_score=result.vocabulary_score,
            syntax_score=result.syntax_score,
            formality_score=result.formality_score,
            emotional_score=result.emotional_score,
            issues=[{
                'type': issue.type,
                'severity': issue.severity,
                'description': issue.description,
                'line_number': issue.line_number,
                'problematic_text': issue.problematic_text
            } for issue in result.issues],
            suggestions=[{
                'issue_index': sug.issue_index,
                'original_text': sug.original_text,
                'suggested_text': sug.suggested_text,
                'reason': sug.reason
            } for sug in result.suggestions]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consistency check failed: {str(e)}")


@router.get("/character/{character_id}/consistency-history", response_model=ConsistencyHistoryResponse)
async def get_consistency_history(
    character_id: int,
    limit: int = Query(20, ge=1, le=100, description="Number of recent scores to return"),
    db: Session = Depends(get_db),
):
    """
    Get historical consistency scores for a character

    Shows how character voice consistency has evolved over time.
    Useful for identifying when a character's voice started to drift.
    """
    # Get character
    character = db.execute(
        select(Character).where(Character.id == character_id)
    ).scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Get recent consistency scores
    scores = db.execute(
        select(DialogueConsistencyScore)
        .where(DialogueConsistencyScore.character_id == character_id)
        .order_by(desc(DialogueConsistencyScore.created_at))
        .limit(limit)
    ).scalars().all()

    if not scores:
        return ConsistencyHistoryResponse(
            character_id=character_id,
            character_name=character.name,
            scores=[],
            avg_score=0.0,
            total_checks=0
        )

    # Format scores
    scores_data = [
        {
            'scene_id': score.scene_id,
            'overall_score': score.overall_score,
            'timestamp': score.created_at.isoformat(),
            'issues_count': len(score.issues)
        }
        for score in scores
    ]

    # Calculate average
    avg_score = sum(s.overall_score for s in scores) / len(scores)

    return ConsistencyHistoryResponse(
        character_id=character_id,
        character_name=character.name,
        scores=scores_data,
        avg_score=avg_score,
        total_checks=len(scores)
    )


@router.get("/project/{project_id}/voice-fingerprint-stats", response_model=VoiceFingerprintStatsResponse)
async def get_voice_fingerprint_stats(
    project_id: int,
    db: Session = Depends(get_db),
):
    """
    Get statistics about voice fingerprints for all characters in a project

    Shows:
    - Which characters have been analyzed
    - Confidence levels
    - Characters needing more dialogue samples
    """
    # Get all characters with fingerprints
    characters_with_fingerprints = db.execute(
        select(Character, CharacterVoiceFingerprint)
        .join(CharacterVoiceFingerprint, Character.id == CharacterVoiceFingerprint.character_id)
        .where(Character.project_id == project_id)
    ).all()

    if not characters_with_fingerprints:
        return VoiceFingerprintStatsResponse(
            total_fingerprints=0,
            characters_analyzed=[],
            avg_confidence=0.0,
            low_confidence_characters=[]
        )

    characters_analyzed = []
    low_confidence = []
    confidence_scores = []

    for char, fp in characters_with_fingerprints:
        char_data = {
            'character_id': char.id,
            'character_name': char.name,
            'confidence_score': fp.confidence_score,
            'sample_count': fp.sample_count,
            'total_words': fp.total_words,
            'last_analyzed': fp.last_analyzed_at.isoformat()
        }

        characters_analyzed.append(char_data)
        confidence_scores.append(fp.confidence_score)

        if fp.confidence_score < 0.7:  # Low confidence threshold
            low_confidence.append({
                **char_data,
                'needed_samples': max(0, 50 - fp.sample_count)
            })

    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

    return VoiceFingerprintStatsResponse(
        total_fingerprints=len(characters_with_fingerprints),
        characters_analyzed=characters_analyzed,
        avg_confidence=avg_confidence,
        low_confidence_characters=low_confidence
    )
