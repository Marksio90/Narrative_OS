"""
Character Arc Service

Tracks character development across the narrative timeline.
Integrates with AI to detect emotional states, validate consistency, and analyze arc health.
"""
import anthropic
from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime
import json

from core.models.character_arcs import (
    CharacterArc,
    ArcMilestone,
    EmotionalState,
    GoalProgress,
    RelationshipEvolution,
    ArcType,
    MilestoneType,
    GoalStatus,
)
from core.models.canon import Character
from core.models.consequences import StoryEvent
from services.ai.config import get_ai_config


class CharacterArcService:
    """
    Main service for character arc tracking and analysis
    """

    def __init__(self, db: Session, anthropic_client: Optional[anthropic.Anthropic] = None):
        self.db = db
        self.client = anthropic_client or anthropic.Anthropic()
        self.config = get_ai_config()

    # ==================== Arc CRUD ====================

    def create_arc(
        self,
        project_id: int,
        character_id: int,
        arc_type: ArcType,
        name: Optional[str] = None,
        description: Optional[str] = None,
        start_chapter: Optional[int] = None,
        end_chapter: Optional[int] = None,
        starting_state: Optional[Dict] = None,
        ending_state: Optional[Dict] = None,
    ) -> CharacterArc:
        """Create a new character arc"""

        # Get character info for context
        character = self.db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise ValueError(f"Character {character_id} not found")

        # Create arc
        arc = CharacterArc(
            project_id=project_id,
            character_id=character_id,
            arc_type=arc_type,
            name=name or f"{character.name}'s {arc_type.value.replace('_', ' ').title()} Arc",
            description=description,
            start_chapter=start_chapter or 1,
            end_chapter=end_chapter,
            starting_state=starting_state or self._extract_starting_state(character),
            ending_state=ending_state or {},
            current_chapter=start_chapter or 1,
            completion_percentage=0.0,
        )

        self.db.add(arc)
        self.db.commit()
        self.db.refresh(arc)

        return arc

    def get_arc(self, arc_id: int) -> Optional[CharacterArc]:
        """Get arc by ID"""
        return self.db.query(CharacterArc).filter(CharacterArc.id == arc_id).first()

    def get_character_arcs(
        self,
        project_id: int,
        character_id: Optional[int] = None,
        active_only: bool = False,
    ) -> List[CharacterArc]:
        """Get all arcs for a character or project"""
        query = self.db.query(CharacterArc).filter(CharacterArc.project_id == project_id)

        if character_id:
            query = query.filter(CharacterArc.character_id == character_id)

        if active_only:
            query = query.filter(CharacterArc.is_complete == False)

        return query.order_by(CharacterArc.start_chapter).all()

    def update_arc_progress(
        self,
        arc_id: int,
        current_chapter: int,
        completion_percentage: Optional[float] = None,
    ) -> CharacterArc:
        """Update arc progress"""
        arc = self.get_arc(arc_id)
        if not arc:
            raise ValueError(f"Arc {arc_id} not found")

        arc.current_chapter = current_chapter

        if completion_percentage is not None:
            arc.completion_percentage = max(0, min(100, completion_percentage))
        else:
            # Auto-calculate based on chapter progress
            if arc.end_chapter:
                chapter_progress = (current_chapter - arc.start_chapter) / (
                    arc.end_chapter - arc.start_chapter
                )
                arc.completion_percentage = max(0, min(100, chapter_progress * 100))

        # Check if arc is complete
        if arc.completion_percentage >= 100:
            arc.is_complete = True

        self.db.commit()
        self.db.refresh(arc)

        return arc

    # ==================== Milestone Tracking ====================

    def add_milestone(
        self,
        arc_id: int,
        chapter_number: int,
        milestone_type: MilestoneType,
        title: str,
        description: Optional[str] = None,
        emotional_impact: Optional[float] = None,
        character_change: Optional[str] = None,
        story_event_id: Optional[int] = None,
    ) -> ArcMilestone:
        """Add a milestone to an arc"""

        arc = self.get_arc(arc_id)
        if not arc:
            raise ValueError(f"Arc {arc_id} not found")

        milestone = ArcMilestone(
            arc_id=arc_id,
            project_id=arc.project_id,
            chapter_number=chapter_number,
            milestone_type=milestone_type,
            title=title,
            description=description,
            emotional_impact=emotional_impact,
            character_change=character_change,
            story_event_id=story_event_id,
            expected_chapter=chapter_number,
            actual_chapter=chapter_number,
            is_achieved=True,
        )

        self.db.add(milestone)
        self.db.commit()
        self.db.refresh(milestone)

        # Update arc progress
        self._recalculate_arc_progress(arc_id)

        return milestone

    def get_arc_milestones(
        self,
        arc_id: int,
        include_unachieved: bool = True,
    ) -> List[ArcMilestone]:
        """Get milestones for an arc"""
        query = self.db.query(ArcMilestone).filter(ArcMilestone.arc_id == arc_id)

        if not include_unachieved:
            query = query.filter(ArcMilestone.is_achieved == True)

        return query.order_by(ArcMilestone.chapter_number).all()

    # ==================== Emotional State Tracking ====================

    def track_emotional_state(
        self,
        character_id: int,
        chapter_number: int,
        dominant_emotion: str,
        intensity: float,
        valence: float,
        arc_id: Optional[int] = None,
        secondary_emotions: Optional[List[str]] = None,
        triggers: Optional[List[Dict]] = None,
        mental_state: Optional[str] = None,
        stress_level: Optional[float] = None,
        confidence_level: Optional[float] = None,
    ) -> EmotionalState:
        """Track emotional state for a chapter"""

        # Get project_id from character
        character = self.db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise ValueError(f"Character {character_id} not found")

        emotional_state = EmotionalState(
            project_id=character.project_id,
            character_id=character_id,
            character_arc_id=arc_id,
            chapter_number=chapter_number,
            dominant_emotion=dominant_emotion,
            secondary_emotions=secondary_emotions or [],
            intensity=intensity,
            valence=valence,
            triggers=triggers or [],
            mental_state=mental_state,
            stress_level=stress_level,
            confidence_level=confidence_level,
            detected_from_text=False,
        )

        self.db.add(emotional_state)
        self.db.commit()
        self.db.refresh(emotional_state)

        return emotional_state

    def get_emotional_journey(
        self,
        character_id: int,
        start_chapter: Optional[int] = None,
        end_chapter: Optional[int] = None,
    ) -> List[EmotionalState]:
        """Get emotional journey across chapters"""
        query = self.db.query(EmotionalState).filter(
            EmotionalState.character_id == character_id
        )

        if start_chapter:
            query = query.filter(EmotionalState.chapter_number >= start_chapter)
        if end_chapter:
            query = query.filter(EmotionalState.chapter_number <= end_chapter)

        return query.order_by(EmotionalState.chapter_number).all()

    # ==================== Goal Progress Tracking ====================

    def create_goal(
        self,
        character_id: int,
        goal_description: str,
        chapter_number: int = 1,
        goal_type: Optional[str] = None,
        priority: int = 1,
        stakes: Optional[str] = None,
        arc_id: Optional[int] = None,
    ) -> GoalProgress:
        """Create a character goal to track"""

        character = self.db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise ValueError(f"Character {character_id} not found")

        goal = GoalProgress(
            project_id=character.project_id,
            character_id=character_id,
            character_arc_id=arc_id,
            goal_description=goal_description,
            goal_type=goal_type,
            priority=priority,
            chapter_number=chapter_number,
            progress_percentage=0.0,
            status=GoalStatus.ACTIVE,
            stakes=stakes,
            motivation_strength=1.0,
        )

        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)

        return goal

    def update_goal_progress(
        self,
        goal_id: int,
        chapter_number: int,
        progress_percentage: float,
        obstacle: Optional[Dict] = None,
        victory: Optional[Dict] = None,
        setback: Optional[Dict] = None,
    ) -> GoalProgress:
        """Update goal progress"""
        goal = self.db.query(GoalProgress).filter(GoalProgress.id == goal_id).first()
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")

        goal.chapter_number = chapter_number
        goal.progress_percentage = max(0, min(100, progress_percentage))

        # Add journey events
        if obstacle:
            obstacles = goal.obstacles_faced or []
            obstacles.append({**obstacle, 'chapter': chapter_number})
            goal.obstacles_faced = obstacles

        if victory:
            victories = goal.victories or []
            victories.append({**victory, 'chapter': chapter_number})
            goal.victories = victories

        if setback:
            setbacks = goal.setbacks or []
            setbacks.append({**setback, 'chapter': chapter_number})
            goal.setbacks = setbacks

        # Update status based on progress
        if progress_percentage >= 100:
            goal.status = GoalStatus.ACHIEVED
            goal.achieved_chapter = chapter_number
        elif progress_percentage <= 0 and goal.obstacles_faced and len(goal.obstacles_faced) > 3:
            goal.status = GoalStatus.BLOCKED

        self.db.commit()
        self.db.refresh(goal)

        return goal

    def get_character_goals(
        self,
        character_id: int,
        active_only: bool = False,
    ) -> List[GoalProgress]:
        """Get all goals for a character"""
        query = self.db.query(GoalProgress).filter(
            GoalProgress.character_id == character_id
        )

        if active_only:
            query = query.filter(
                GoalProgress.status.in_([GoalStatus.ACTIVE, GoalStatus.IN_PROGRESS])
            )

        return query.order_by(GoalProgress.priority, desc(GoalProgress.created_at)).all()

    # ==================== Relationship Evolution ====================

    def track_relationship_change(
        self,
        character_id: int,
        related_character_id: int,
        chapter_number: int,
        relationship_type: str,
        relationship_strength: float,
        trust_level: Optional[float] = None,
        affection_level: Optional[float] = None,
        respect_level: Optional[float] = None,
        conflict_level: Optional[float] = None,
        key_moment: Optional[Dict] = None,
    ) -> RelationshipEvolution:
        """Track how a relationship changes"""

        character = self.db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise ValueError(f"Character {character_id} not found")

        rel_evolution = RelationshipEvolution(
            project_id=character.project_id,
            character_id=character_id,
            related_character_id=related_character_id,
            chapter_number=chapter_number,
            relationship_type=relationship_type,
            relationship_strength=relationship_strength,
            trust_level=trust_level,
            affection_level=affection_level,
            respect_level=respect_level,
            conflict_level=conflict_level,
            key_moments=[key_moment] if key_moment else [],
        )

        self.db.add(rel_evolution)
        self.db.commit()
        self.db.refresh(rel_evolution)

        # Calculate trajectory
        self._calculate_relationship_trajectory(character_id, related_character_id)

        return rel_evolution

    def get_relationship_evolution(
        self,
        character_id: int,
        related_character_id: int,
        start_chapter: Optional[int] = None,
        end_chapter: Optional[int] = None,
    ) -> List[RelationshipEvolution]:
        """Get relationship evolution over time"""
        query = self.db.query(RelationshipEvolution).filter(
            and_(
                RelationshipEvolution.character_id == character_id,
                RelationshipEvolution.related_character_id == related_character_id,
            )
        )

        if start_chapter:
            query = query.filter(RelationshipEvolution.chapter_number >= start_chapter)
        if end_chapter:
            query = query.filter(RelationshipEvolution.chapter_number <= end_chapter)

        return query.order_by(RelationshipEvolution.chapter_number).all()

    # ==================== Helper Methods ====================

    def _extract_starting_state(self, character: Character) -> Dict:
        """Extract starting state from character canon"""
        return {
            'emotional': 'neutral',
            'beliefs': character.values or [],
            'fears': character.fears or [],
            'goals': character.goals or [],
            'skills': [],
        }

    def _recalculate_arc_progress(self, arc_id: int):
        """Recalculate arc completion based on milestones"""
        arc = self.get_arc(arc_id)
        if not arc:
            return

        milestones = self.get_arc_milestones(arc_id)
        if not milestones:
            return

        achieved_count = sum(1 for m in milestones if m.is_achieved)
        total_count = len(milestones)

        arc.completion_percentage = (achieved_count / total_count) * 100 if total_count > 0 else 0

        self.db.commit()

    def _calculate_relationship_trajectory(
        self,
        character_id: int,
        related_character_id: int,
    ):
        """Calculate if relationship is improving, declining, stable"""
        evolutions = self.get_relationship_evolution(character_id, related_character_id)

        if len(evolutions) < 2:
            return

        # Get last entry
        latest = evolutions[-1]

        # Compare last 3 entries if available
        recent = evolutions[-3:]
        strengths = [e.relationship_strength for e in recent if e.relationship_strength is not None]

        if len(strengths) < 2:
            latest.trajectory = 'stable'
        else:
            # Calculate trend
            trend = strengths[-1] - strengths[0]
            if trend > 0.2:
                latest.trajectory = 'improving'
            elif trend < -0.2:
                latest.trajectory = 'declining'
            elif max(strengths) - min(strengths) > 0.3:
                latest.trajectory = 'volatile'
            else:
                latest.trajectory = 'stable'

        self.db.commit()
