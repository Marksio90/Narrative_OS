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

    # ==================== AI-Powered Analysis ====================

    async def analyze_arc_health(self, arc_id: int) -> Dict[str, Any]:
        """
        Use AI to analyze if character arc is well-paced and consistent
        """
        arc = self.get_arc(arc_id)
        if not arc:
            raise ValueError(f"Arc {arc_id} not found")

        character = self.db.query(Character).filter(Character.id == arc.character_id).first()
        milestones = self.get_arc_milestones(arc_id)
        emotional_states = self.get_emotional_journey(arc.character_id, arc.start_chapter, arc.current_chapter)

        # Build analysis prompt
        prompt = f"""Analyze the health of this character arc:

Character: {character.name}
Arc Type: {arc.arc_type.value}
Arc Name: {arc.name}
Description: {arc.description or 'N/A'}

Progress: {arc.completion_percentage}%  (Chapter {arc.current_chapter} of {arc.end_chapter or 'unknown'})

Starting State:
{json.dumps(arc.starting_state, indent=2)}

Target Ending State:
{json.dumps(arc.ending_state, indent=2)}

Milestones Achieved ({len(milestones)}):
{self._format_milestones_for_ai(milestones)}

Emotional Journey:
{self._format_emotional_journey_for_ai(emotional_states)}

Analyze:
1. Is the arc progressing at a good pace? Too fast/slow?
2. Are character changes consistent and believable?
3. Are there missing milestones that should be present?
4. Does the emotional journey support the arc type?
5. What's the arc health score (0-100)?

Return JSON with:
{{
    "pacing_score": 0-1,
    "consistency_score": 0-1,
    "arc_health_score": 0-100,
    "is_on_track": true/false,
    "issues": [str],
    "suggestions": [str],
    "missing_milestones": [str],
    "strengths": [str]
}}
"""

        response = self.client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        analysis_text = response.content[0].text
        analysis = self._extract_json_from_response(analysis_text)

        # Update arc with scores
        arc.pacing_score = analysis.get('pacing_score', 0.5)
        arc.consistency_score = analysis.get('consistency_score', 0.5)
        arc.is_on_track = analysis.get('is_on_track', True)
        arc.validation_notes = analysis.get('issues', []) + analysis.get('suggestions', [])

        self.db.commit()

        return analysis

    async def detect_milestone_from_scene(
        self,
        arc_id: int,
        scene_text: str,
        chapter_number: int,
        story_event_id: Optional[int] = None,
    ) -> Optional[ArcMilestone]:
        """
        Analyze scene text to detect if it contains a character arc milestone
        """
        arc = self.get_arc(arc_id)
        if not arc:
            raise ValueError(f"Arc {arc_id} not found")

        character = self.db.query(Character).filter(Character.id == arc.character_id).first()

        prompt = f"""Analyze this scene for character development milestone:

Character: {character.name}
Arc Type: {arc.arc_type.value}
Arc Progress: {arc.completion_percentage}%

Scene (Chapter {chapter_number}):
{scene_text[:2000]}

Does this scene contain a significant character development milestone for {character.name}?

If YES, identify:
- Milestone type (catalyst, crisis, revelation, turning_point, breakthrough, climax, resolution, etc.)
- Brief title (max 50 chars)
- What changed in the character
- Emotional impact (0-1)
- Significance to overall arc (0-1)

If NO, return: {{"is_milestone": false}}

If YES, return JSON:
{{
    "is_milestone": true,
    "milestone_type": "revelation",
    "title": "Sarah realizes she can trust again",
    "character_change": "Overcame trust issues from past betrayal",
    "emotional_impact": 0.8,
    "significance": 0.9,
    "description": "Longer description of what happened"
}}
"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}]
        )

        result = self._extract_json_from_response(response.content[0].text)

        if not result.get('is_milestone', False):
            return None

        # Create milestone
        try:
            milestone_type = MilestoneType(result['milestone_type'])
        except ValueError:
            milestone_type = MilestoneType.TURNING_POINT  # Default

        milestone = self.add_milestone(
            arc_id=arc_id,
            chapter_number=chapter_number,
            milestone_type=milestone_type,
            title=result.get('title', 'Character Development Moment'),
            description=result.get('description'),
            emotional_impact=result.get('emotional_impact', 0.5),
            character_change=result.get('character_change'),
            story_event_id=story_event_id,
        )

        milestone.ai_analysis = {
            'detected_from_scene': True,
            'confidence': 0.8,
            'full_analysis': result,
        }
        self.db.commit()

        return milestone

    async def extract_emotional_state_from_scene(
        self,
        character_id: int,
        chapter_number: int,
        scene_text: str,
        arc_id: Optional[int] = None,
    ) -> Optional[EmotionalState]:
        """
        Use AI to extract character's emotional state from scene text
        """
        character = self.db.query(Character).filter(Character.id == character_id).first()
        if not character:
            return None

        prompt = f"""Extract {character.name}'s emotional state from this scene:

Scene (Chapter {chapter_number}):
{scene_text[:2000]}

Analyze {character.name}'s emotional state. Return JSON:
{{
    "dominant_emotion": "fear" | "anger" | "joy" | "sadness" | "hope" | etc,
    "secondary_emotions": ["emotion1", "emotion2"],
    "intensity": 0-1 (how intense is the emotion),
    "valence": -1 to 1 (negative to positive),
    "mental_state": "clarity" | "confusion" | "determination" | etc,
    "stress_level": 0-1,
    "confidence_level": 0-1,
    "triggers": [
        {{"event": "what triggered this", "impact": 0-1}}
    ],
    "inner_conflict": "brief description of internal struggle"
}}

If {character.name} is not in the scene or emotions are unclear, return: {{"present": false}}
"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            temperature=0.4,
            messages=[{"role": "user", "content": prompt}]
        )

        result = self._extract_json_from_response(response.content[0].text)

        if not result.get('present', True):
            return None

        # Create emotional state
        emotional_state = self.track_emotional_state(
            character_id=character_id,
            chapter_number=chapter_number,
            dominant_emotion=result.get('dominant_emotion', 'neutral'),
            intensity=result.get('intensity', 0.5),
            valence=result.get('valence', 0.0),
            arc_id=arc_id,
            secondary_emotions=result.get('secondary_emotions', []),
            triggers=result.get('triggers', []),
            mental_state=result.get('mental_state'),
            stress_level=result.get('stress_level'),
            confidence_level=result.get('confidence_level'),
        )

        emotional_state.detected_from_text = True
        emotional_state.ai_confidence = 0.8
        self.db.commit()

        return emotional_state

    async def generate_arc_report(self, arc_id: int) -> Dict[str, Any]:
        """
        Generate comprehensive arc analysis report
        """
        arc = self.get_arc(arc_id)
        if not arc:
            raise ValueError(f"Arc {arc_id} not found")

        character = self.db.query(Character).filter(Character.id == arc.character_id).first()
        milestones = self.get_arc_milestones(arc_id)
        emotional_journey = self.get_emotional_journey(arc.character_id, arc.start_chapter, arc.current_chapter)
        goals = self.get_character_goals(arc.character_id, active_only=False)

        # AI-powered health analysis
        health_analysis = await self.analyze_arc_health(arc_id)

        return {
            'arc': {
                'id': arc.id,
                'name': arc.name,
                'type': arc.arc_type.value,
                'progress': arc.completion_percentage,
                'chapter_range': f"{arc.start_chapter}-{arc.end_chapter or '?'}",
                'is_complete': arc.is_complete,
                'is_on_track': arc.is_on_track,
            },
            'character': {
                'id': character.id,
                'name': character.name,
            },
            'health': health_analysis,
            'milestones': {
                'total': len(milestones),
                'achieved': sum(1 for m in milestones if m.is_achieved),
                'list': [
                    {
                        'chapter': m.chapter_number,
                        'type': m.milestone_type.value,
                        'title': m.title,
                        'impact': m.emotional_impact,
                        'achieved': m.is_achieved,
                    }
                    for m in milestones
                ],
            },
            'emotional_journey': {
                'data_points': len(emotional_journey),
                'dominant_emotions': self._analyze_emotion_frequency(emotional_journey),
                'intensity_avg': sum(e.intensity for e in emotional_journey if e.intensity) / len(emotional_journey) if emotional_journey else 0,
                'valence_trend': self._calculate_valence_trend(emotional_journey),
            },
            'goals': {
                'total': len(goals),
                'active': sum(1 for g in goals if g.status in [GoalStatus.ACTIVE, GoalStatus.IN_PROGRESS]),
                'achieved': sum(1 for g in goals if g.status == GoalStatus.ACHIEVED),
                'failed': sum(1 for g in goals if g.status == GoalStatus.FAILED),
            },
        }

    # ==================== Helper Methods for AI ====================

    def _format_milestones_for_ai(self, milestones: List[ArcMilestone]) -> str:
        """Format milestones for AI prompt"""
        if not milestones:
            return "No milestones yet"

        lines = []
        for m in milestones:
            lines.append(
                f"- Ch {m.chapter_number}: {m.milestone_type.value.upper()} - {m.title}"
            )
            if m.character_change:
                lines.append(f"  Change: {m.character_change}")

        return "\n".join(lines)

    def _format_emotional_journey_for_ai(self, states: List[EmotionalState]) -> str:
        """Format emotional states for AI prompt"""
        if not states:
            return "No emotional data yet"

        lines = []
        for state in states:
            lines.append(
                f"- Ch {state.chapter_number}: {state.dominant_emotion} "
                f"(intensity: {state.intensity:.1f}, valence: {state.valence:+.1f})"
            )

        return "\n".join(lines)

    def _extract_json_from_response(self, text: str) -> Dict:
        """Extract JSON from AI response"""
        # Try to find JSON in response
        import re

        # Look for JSON block
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try parsing entire response as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Look for first JSON object
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass

        return {}

    def _analyze_emotion_frequency(self, states: List[EmotionalState]) -> Dict[str, int]:
        """Count frequency of emotions"""
        freq = {}
        for state in states:
            if state.dominant_emotion:
                freq[state.dominant_emotion] = freq.get(state.dominant_emotion, 0) + 1
        return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))

    def _calculate_valence_trend(self, states: List[EmotionalState]) -> str:
        """Calculate if emotions are getting more positive or negative"""
        if len(states) < 3:
            return 'insufficient_data'

        valences = [s.valence for s in states if s.valence is not None]
        if len(valences) < 3:
            return 'insufficient_data'

        # Compare first third vs last third
        first_third = sum(valences[: len(valences) // 3]) / (len(valences) // 3)
        last_third = sum(valences[-(len(valences) // 3) :]) / (len(valences) // 3)

        diff = last_third - first_third

        if diff > 0.2:
            return 'improving'
        elif diff < -0.2:
            return 'declining'
        else:
            return 'stable'
