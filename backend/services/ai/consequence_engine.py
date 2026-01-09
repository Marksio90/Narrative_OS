"""
Consequence Engine

Analyzes story events and predicts their ripple effects through the narrative.
Uses AI to extract events, predict consequences, and track realization.
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
import anthropic
import os

from core.models.consequences import (
    StoryEvent,
    Consequence,
    EventEntity,
    EventType,
    ConsequenceStatus,
    ConsequenceTimeframe
)
from core.models.canon import Character, Location, Thread


@dataclass
class EventExtraction:
    """Extracted event from a scene"""
    title: str
    description: str
    event_type: str
    magnitude: float
    emotional_impact: float
    affected_characters: List[int]
    affected_locations: List[int]
    affected_threads: List[int]


@dataclass
class ConsequencePrediction:
    """Predicted consequence of an event"""
    description: str
    probability: float
    timeframe: str
    severity: float
    affected_entities: Dict[str, List[int]]
    reasoning: str
    alternative_outcomes: List[str]


@dataclass
class ConsequenceGraph:
    """Complete consequence graph for a project"""
    events: List[Dict[str, Any]]
    consequences: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]  # event -> consequence edges


class ConsequenceEngine:
    """
    AI-powered consequence tracking and prediction

    Features:
    - Event extraction from scenes
    - Consequence prediction
    - Realization tracking
    - Graph building
    - Validation checks
    """

    def __init__(self, db: Session, api_key: Optional[str] = None):
        self.db = db
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None

    # === Event Extraction ===

    async def extract_events_from_scene(
        self,
        project_id: int,
        scene_id: int,
        scene_text: str,
        chapter_number: Optional[int] = None
    ) -> List[StoryEvent]:
        """
        Extract significant events from a scene using AI

        Args:
            project_id: Project ID
            scene_id: Scene ID
            scene_text: Full scene prose
            chapter_number: Chapter number (optional)

        Returns:
            List of extracted StoryEvent objects
        """
        if not self.client:
            # Fallback: manual event creation
            return []

        # Build prompt for AI
        prompt = f"""Analyze this story scene and identify significant events or decisions.

For each event, extract:
1. Title (brief, 3-5 words)
2. Description (detailed, what happened)
3. Event type (decision, revelation, conflict, resolution, discovery, loss, transformation, other)
4. Magnitude (0-1, how impactful this is for the overall story)
5. Emotional impact (0-1, emotional weight)

Scene:
{scene_text}

Return JSON array of events:
[
  {{
    "title": "Sarah discovers secret door",
    "description": "...",
    "event_type": "discovery",
    "magnitude": 0.8,
    "emotional_impact": 0.6
  }}
]

Only include truly significant events (3-5 max). Focus on events that will have consequences."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response (simplified - would need better JSON extraction)
            import json
            import re

            content = response.content[0].text
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                events_data = json.loads(json_match.group(0))

                extracted_events = []
                for event_data in events_data:
                    event = StoryEvent(
                        project_id=project_id,
                        scene_id=scene_id,
                        chapter_number=chapter_number,
                        title=event_data.get('title', 'Untitled Event'),
                        description=event_data.get('description', ''),
                        event_type=EventType(event_data.get('event_type', 'other')),
                        magnitude=float(event_data.get('magnitude', 0.5)),
                        emotional_impact=float(event_data.get('emotional_impact', 0.5)),
                        causes=[],
                        effects=[],
                        extracted_at=datetime.utcnow()
                    )
                    self.db.add(event)
                    extracted_events.append(event)

                if extracted_events:
                    self.db.commit()
                    # Refresh to get IDs
                    for event in extracted_events:
                        self.db.refresh(event)

                return extracted_events

        except Exception as e:
            print(f"Error extracting events: {e}")
            return []

        return []

    # === Consequence Prediction ===

    async def predict_consequences(
        self,
        event: StoryEvent,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Consequence]:
        """
        Predict likely consequences of an event using AI

        Args:
            event: The StoryEvent to analyze
            context: Optional story context (characters, plot threads, etc.)

        Returns:
            List of predicted Consequence objects
        """
        if not self.client:
            return []

        # Build context summary
        context_summary = ""
        if context:
            context_summary = f"""
Story Context:
- Genre: {context.get('genre', 'Unknown')}
- Main characters: {', '.join(context.get('characters', []))}
- Active plot threads: {', '.join(context.get('threads', []))}
"""

        prompt = f"""Analyze this story event and predict its likely consequences.

Event: {event.title}
Description: {event.description}
Type: {event.event_type.value}
Magnitude: {event.magnitude}

{context_summary}

For each consequence, provide:
1. Description (what will happen as a result)
2. Probability (0-1, how likely this is to occur)
3. Timeframe (immediate, short_term, long_term)
4. Severity (0-1, how impactful this consequence is)
5. Reasoning (why this consequence is likely)

Return JSON array of consequences (3-5 max):
[
  {{
    "description": "Sarah's discovery will attract unwanted attention",
    "probability": 0.8,
    "timeframe": "short_term",
    "severity": 0.7,
    "reasoning": "Discovery of secrets typically leads to conflict..."
  }}
]

Focus on narratively interesting consequences that drive the story forward."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            import re

            content = response.content[0].text
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                consequences_data = json.loads(json_match.group(0))

                predicted_consequences = []
                for cons_data in consequences_data:
                    timeframe_str = cons_data.get('timeframe', 'short_term')
                    try:
                        timeframe = ConsequenceTimeframe(timeframe_str)
                    except ValueError:
                        timeframe = ConsequenceTimeframe.SHORT_TERM

                    consequence = Consequence(
                        source_event_id=event.id,
                        description=cons_data.get('description', ''),
                        probability=float(cons_data.get('probability', 0.5)),
                        timeframe=timeframe,
                        severity=float(cons_data.get('severity', 0.5)),
                        status=ConsequenceStatus.POTENTIAL,
                        affected_entities={
                            'character_ids': [],
                            'location_ids': [],
                            'thread_ids': []
                        },
                        ai_prediction={
                            'reasoning': cons_data.get('reasoning', ''),
                            'alternative_outcomes': [],
                            'mitigation_strategies': [],
                            'narrative_potential': 'high'
                        },
                        predicted_at=datetime.utcnow()
                    )
                    self.db.add(consequence)
                    predicted_consequences.append(consequence)

                if predicted_consequences:
                    self.db.commit()
                    for cons in predicted_consequences:
                        self.db.refresh(cons)

                return predicted_consequences

        except Exception as e:
            print(f"Error predicting consequences: {e}")
            return []

        return []

    # === Consequence Tracking ===

    async def check_consequence_realization(
        self,
        consequence: Consequence,
        new_events: List[StoryEvent]
    ) -> bool:
        """
        Check if a predicted consequence has been realized

        Args:
            consequence: The Consequence to check
            new_events: Recently extracted events

        Returns:
            True if consequence was realized
        """
        if not self.client or not new_events:
            return False

        # Build prompt to check if consequence occurred
        events_summary = "\n".join([
            f"- {event.title}: {event.description}"
            for event in new_events
        ])

        prompt = f"""Check if this predicted consequence has occurred in any of the recent events.

Predicted Consequence:
{consequence.description}

Recent Events:
{events_summary}

Did the consequence occur? Answer with JSON:
{{
  "occurred": true/false,
  "matching_event_index": 0-based index or null,
  "confidence": 0-1,
  "explanation": "brief explanation"
}}"""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            import re

            content = response.content[0].text
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))

                if result.get('occurred') and result.get('confidence', 0) > 0.7:
                    # Mark consequence as realized
                    consequence.status = ConsequenceStatus.REALIZED
                    consequence.realized_at = datetime.utcnow()

                    # Link to target event if identified
                    event_index = result.get('matching_event_index')
                    if event_index is not None and 0 <= event_index < len(new_events):
                        consequence.target_event_id = new_events[event_index].id

                    self.db.commit()
                    return True

        except Exception as e:
            print(f"Error checking consequence realization: {e}")

        return False

    # === Graph Building ===

    async def build_consequence_graph(
        self,
        project_id: int,
        chapter_range: Optional[Tuple[int, int]] = None
    ) -> ConsequenceGraph:
        """
        Build complete consequence graph for a project

        Args:
            project_id: Project ID
            chapter_range: Optional (start_chapter, end_chapter) tuple

        Returns:
            ConsequenceGraph with events, consequences, and connections
        """
        # Query events
        query = select(StoryEvent).where(StoryEvent.project_id == project_id)
        if chapter_range:
            start, end = chapter_range
            query = query.where(
                and_(
                    StoryEvent.chapter_number >= start,
                    StoryEvent.chapter_number <= end
                )
            )
        query = query.order_by(StoryEvent.chapter_number, StoryEvent.id)

        events = self.db.execute(query).scalars().all()

        # Query consequences for these events
        event_ids = [e.id for e in events]
        consequences = []
        if event_ids:
            cons_query = select(Consequence).where(
                Consequence.source_event_id.in_(event_ids)
            )
            consequences = self.db.execute(cons_query).scalars().all()

        # Build graph structure
        events_data = [
            {
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'type': event.event_type.value,
                'chapter': event.chapter_number,
                'magnitude': event.magnitude,
                'emotional_impact': event.emotional_impact
            }
            for event in events
        ]

        consequences_data = [
            {
                'id': cons.id,
                'source_event_id': cons.source_event_id,
                'target_event_id': cons.target_event_id,
                'description': cons.description,
                'probability': cons.probability,
                'status': cons.status.value,
                'timeframe': cons.timeframe.value,
                'severity': cons.severity
            }
            for cons in consequences
        ]

        connections = [
            {
                'from': cons.source_event_id,
                'to': cons.id,
                'type': 'predicts',
                'probability': cons.probability
            }
            for cons in consequences
        ]

        # Add realized connections
        for cons in consequences:
            if cons.target_event_id:
                connections.append({
                    'from': cons.id,
                    'to': cons.target_event_id,
                    'type': 'realizes',
                    'status': cons.status.value
                })

        return ConsequenceGraph(
            events=events_data,
            consequences=consequences_data,
            connections=connections
        )

    # === Active Consequences ===

    async def get_active_consequences(
        self,
        project_id: int,
        chapter_number: Optional[int] = None
    ) -> List[Consequence]:
        """
        Get active (potential/active status) consequences for a project

        Args:
            project_id: Project ID
            chapter_number: Optional chapter to scope consequences

        Returns:
            List of active Consequence objects
        """
        # Get events for project
        event_query = select(StoryEvent).where(StoryEvent.project_id == project_id)
        if chapter_number:
            # Get consequences from events up to this chapter
            event_query = event_query.where(StoryEvent.chapter_number <= chapter_number)

        events = self.db.execute(event_query).scalars().all()
        event_ids = [e.id for e in events]

        if not event_ids:
            return []

        # Query active consequences
        cons_query = select(Consequence).where(
            and_(
                Consequence.source_event_id.in_(event_ids),
                or_(
                    Consequence.status == ConsequenceStatus.POTENTIAL,
                    Consequence.status == ConsequenceStatus.ACTIVE
                )
            )
        ).order_by(Consequence.probability.desc(), Consequence.severity.desc())

        consequences = self.db.execute(cons_query).scalars().all()
        return consequences
