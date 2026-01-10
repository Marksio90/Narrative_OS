"""
Timeline Service

Aggregates and manages timeline data from multiple sources
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any, Set
from datetime import datetime
import hashlib
import json

from core.models.timeline import (
    TimelineEvent,
    TimelineConflict,
    TimelineView,
    TimelineBookmark,
    TimelineEventType,
    TimelineLayer,
    ConflictType,
    ConflictSeverity,
)
from core.models.chapter import Chapter
from core.models.consequences import StoryEvent, Consequence
from core.models.character_arcs import CharacterArc, ArcMilestone
from core.models.planner import BookArc


class TimelineService:
    """
    Service for timeline management and visualization

    Handles:
    - Aggregating data from multiple sources
    - Syncing timeline events
    - Conflict detection
    - View management
    """

    def __init__(self, db: Session):
        self.db = db

    # ==================== Aggregation & Sync ====================

    def sync_project_timeline(self, project_id: int) -> Dict[str, int]:
        """
        Sync all timeline events for a project from source tables

        Returns counts of synced events by type
        """
        counts = {
            "chapters": self._sync_chapters(project_id),
            "story_events": self._sync_story_events(project_id),
            "milestones": self._sync_milestones(project_id),
            "beats": self._sync_beats(project_id),
            "consequences": self._sync_consequences(project_id),
        }

        # After sync, detect conflicts
        self.detect_all_conflicts(project_id)

        return counts

    def _sync_chapters(self, project_id: int) -> int:
        """Sync chapters to timeline events"""
        chapters = self.db.query(Chapter).filter(
            Chapter.project_id == project_id
        ).all()

        synced_count = 0
        for chapter in chapters:
            # Calculate hash of source data
            source_hash = self._calculate_hash({
                "title": chapter.title,
                "chapter_number": chapter.chapter_number,
                "status": chapter.status,
                "word_count": chapter.word_count,
            })

            # Check if event exists
            existing = self.db.query(TimelineEvent).filter(
                TimelineEvent.project_id == project_id,
                TimelineEvent.event_type == TimelineEventType.CHAPTER,
                TimelineEvent.source_id == chapter.id
            ).first()

            if existing:
                # Update if hash changed
                if existing.sync_hash != source_hash:
                    existing.chapter_number = chapter.chapter_number
                    existing.title = chapter.title or f"Chapter {chapter.chapter_number}"
                    existing.description = chapter.summary
                    existing.metadata = {
                        "chapter": {
                            "word_count": chapter.word_count,
                            "target_word_count": chapter.target_word_count,
                            "status": chapter.status,
                            "pov_character_id": chapter.pov_character_id,
                            "is_published": chapter.is_published,
                        }
                    }
                    existing.sync_hash = source_hash
                    existing.last_synced_at = datetime.utcnow()
                    synced_count += 1
            else:
                # Create new event
                new_event = TimelineEvent(
                    project_id=project_id,
                    event_type=TimelineEventType.CHAPTER,
                    source_id=chapter.id,
                    source_table="chapters",
                    chapter_number=chapter.chapter_number,
                    title=chapter.title or f"Chapter {chapter.chapter_number}",
                    description=chapter.summary,
                    layer=TimelineLayer.TECHNICAL,
                    color="#6B7280",
                    icon="book",
                    magnitude=0.3,
                    related_characters=[chapter.pov_character_id] if chapter.pov_character_id else [],
                    metadata={
                        "chapter": {
                            "word_count": chapter.word_count,
                            "target_word_count": chapter.target_word_count,
                            "status": chapter.status,
                            "pov_character_id": chapter.pov_character_id,
                            "is_published": chapter.is_published,
                        }
                    },
                    sync_hash=source_hash,
                    last_synced_at=datetime.utcnow(),
                    is_custom=False
                )
                self.db.add(new_event)
                synced_count += 1

        self.db.commit()
        return synced_count

    def _sync_story_events(self, project_id: int) -> int:
        """Sync story events to timeline events"""
        story_events = self.db.query(StoryEvent).filter(
            StoryEvent.project_id == project_id
        ).all()

        synced_count = 0
        for event in story_events:
            if not event.chapter_number:
                continue  # Skip events without chapter position

            source_hash = self._calculate_hash({
                "title": event.title,
                "event_type": event.event_type.value,
                "magnitude": event.magnitude,
                "chapter_number": event.chapter_number,
            })

            existing = self.db.query(TimelineEvent).filter(
                TimelineEvent.project_id == project_id,
                TimelineEvent.event_type == TimelineEventType.STORY_EVENT,
                TimelineEvent.source_id == event.id
            ).first()

            # Determine color based on event type
            event_colors = {
                "decision": "#3B82F6",  # Blue
                "revelation": "#FBBF24",  # Yellow
                "conflict": "#EF4444",  # Red
                "resolution": "#10B981",  # Green
                "discovery": "#8B5CF6",  # Purple
                "loss": "#DC2626",  # Dark red
                "transformation": "#EC4899",  # Pink
            }
            color = event_colors.get(event.event_type.value, "#6B7280")

            if existing:
                if existing.sync_hash != source_hash:
                    existing.chapter_number = event.chapter_number
                    existing.title = event.title
                    existing.description = event.description
                    existing.magnitude = event.magnitude
                    existing.color = color
                    existing.metadata = {
                        "story_event": {
                            "event_type": event.event_type.value,
                            "emotional_impact": event.emotional_impact,
                            "causes": event.causes,
                            "effects": event.effects,
                        }
                    }
                    existing.sync_hash = source_hash
                    existing.last_synced_at = datetime.utcnow()
                    synced_count += 1
            else:
                new_event = TimelineEvent(
                    project_id=project_id,
                    event_type=TimelineEventType.STORY_EVENT,
                    source_id=event.id,
                    source_table="story_events",
                    chapter_number=event.chapter_number,
                    title=event.title,
                    description=event.description,
                    layer=TimelineLayer.PLOT,
                    color=color,
                    icon="zap",
                    magnitude=event.magnitude,
                    is_major_beat=event.magnitude > 0.7,
                    metadata={
                        "story_event": {
                            "event_type": event.event_type.value,
                            "emotional_impact": event.emotional_impact,
                            "causes": event.causes,
                            "effects": event.effects,
                        }
                    },
                    sync_hash=source_hash,
                    last_synced_at=datetime.utcnow(),
                    is_custom=False
                )
                self.db.add(new_event)
                synced_count += 1

        self.db.commit()
        return synced_count

    def _sync_milestones(self, project_id: int) -> int:
        """Sync character arc milestones to timeline events"""
        milestones = self.db.query(ArcMilestone).join(
            CharacterArc
        ).filter(
            CharacterArc.project_id == project_id
        ).all()

        synced_count = 0
        for milestone in milestones:
            source_hash = self._calculate_hash({
                "milestone_type": milestone.milestone_type.value,
                "chapter_number": milestone.chapter_number,
                "description": milestone.description,
                "significance": milestone.significance,
            })

            existing = self.db.query(TimelineEvent).filter(
                TimelineEvent.project_id == project_id,
                TimelineEvent.event_type == TimelineEventType.MILESTONE,
                TimelineEvent.source_id == milestone.id
            ).first()

            # Get character arc to get character_id
            arc = self.db.query(CharacterArc).filter(
                CharacterArc.id == milestone.arc_id
            ).first()

            milestone_colors = {
                "inciting_incident": "#3B82F6",
                "turning_point": "#8B5CF6",
                "crisis": "#F59E0B",
                "climax": "#DC2626",
                "resolution": "#10B981",
                "revelation": "#FBBF24",
                "setback": "#6B7280",
                "triumph": "#059669",
            }
            color = milestone_colors.get(milestone.milestone_type.value, "#6B7280")

            if existing:
                if existing.sync_hash != source_hash:
                    existing.chapter_number = milestone.chapter_number
                    existing.title = f"{milestone.milestone_type.value.replace('_', ' ').title()}"
                    existing.description = milestone.description
                    existing.magnitude = milestone.significance / 5.0  # Convert 1-5 to 0-1
                    existing.color = color
                    existing.related_characters = [arc.character_id] if arc else []
                    existing.metadata = {
                        "milestone": {
                            "arc_id": milestone.arc_id,
                            "milestone_type": milestone.milestone_type.value,
                            "significance": milestone.significance,
                            "notes": milestone.notes,
                        }
                    }
                    existing.sync_hash = source_hash
                    existing.last_synced_at = datetime.utcnow()
                    synced_count += 1
            else:
                new_event = TimelineEvent(
                    project_id=project_id,
                    event_type=TimelineEventType.MILESTONE,
                    source_id=milestone.id,
                    source_table="arc_milestones",
                    chapter_number=milestone.chapter_number,
                    title=f"{milestone.milestone_type.value.replace('_', ' ').title()}",
                    description=milestone.description,
                    layer=TimelineLayer.CHARACTER,
                    color=color,
                    icon="flag",
                    magnitude=milestone.significance / 5.0,
                    is_major_beat=milestone.significance >= 4,
                    related_characters=[arc.character_id] if arc else [],
                    metadata={
                        "milestone": {
                            "arc_id": milestone.arc_id,
                            "milestone_type": milestone.milestone_type.value,
                            "significance": milestone.significance,
                            "notes": milestone.notes,
                        }
                    },
                    sync_hash=source_hash,
                    last_synced_at=datetime.utcnow(),
                    is_custom=False
                )
                self.db.add(new_event)
                synced_count += 1

        self.db.commit()
        return synced_count

    def _sync_beats(self, project_id: int) -> int:
        """Sync book arc story beats to timeline events"""
        book_arc = self.db.query(BookArc).filter(
            BookArc.project_id == project_id
        ).first()

        if not book_arc:
            return 0

        synced_count = 0
        beats = [
            ("inciting_incident", book_arc.inciting_incident, "#F59E0B"),
            ("first_plot_point", book_arc.first_plot_point, "#3B82F6"),
            ("midpoint", book_arc.midpoint, "#8B5CF6"),
            ("all_is_lost", book_arc.all_is_lost, "#DC2626"),
            ("climax", book_arc.climax, "#DC2626"),
            ("resolution", book_arc.resolution, "#10B981"),
        ]

        for beat_name, beat_data, color in beats:
            if not beat_data or not isinstance(beat_data, dict):
                continue

            chapter = beat_data.get("chapter")
            if not chapter:
                continue

            source_hash = self._calculate_hash({
                "beat_type": beat_name,
                "chapter": chapter,
                "description": beat_data.get("description", ""),
            })

            # Use beat_name as unique identifier (source_id will be derived)
            existing = self.db.query(TimelineEvent).filter(
                TimelineEvent.project_id == project_id,
                TimelineEvent.event_type == TimelineEventType.BEAT,
                TimelineEvent.metadata["beat"]["beat_type"].astext == beat_name
            ).first()

            if existing:
                if existing.sync_hash != source_hash:
                    existing.chapter_number = chapter
                    existing.title = beat_name.replace("_", " ").title()
                    existing.description = beat_data.get("description", "")
                    existing.color = color
                    existing.metadata = {
                        "beat": {
                            "beat_type": beat_name,
                            "act": 1 if chapter <= (book_arc.act1_end_chapter or 7) else (
                                2 if chapter <= (book_arc.act2_end_chapter or 20) else 3
                            ),
                            "changes": beat_data.get("changes", ""),
                        }
                    }
                    existing.sync_hash = source_hash
                    existing.last_synced_at = datetime.utcnow()
                    synced_count += 1
            else:
                new_event = TimelineEvent(
                    project_id=project_id,
                    event_type=TimelineEventType.BEAT,
                    source_id=book_arc.id,
                    source_table="book_arcs",
                    chapter_number=chapter,
                    title=beat_name.replace("_", " ").title(),
                    description=beat_data.get("description", ""),
                    layer=TimelineLayer.PLOT,
                    color=color,
                    icon="star",
                    magnitude=0.9,
                    is_major_beat=True,
                    metadata={
                        "beat": {
                            "beat_type": beat_name,
                            "act": 1 if chapter <= (book_arc.act1_end_chapter or 7) else (
                                2 if chapter <= (book_arc.act2_end_chapter or 20) else 3
                            ),
                            "changes": beat_data.get("changes", ""),
                        }
                    },
                    sync_hash=source_hash,
                    last_synced_at=datetime.utcnow(),
                    is_custom=False
                )
                self.db.add(new_event)
                synced_count += 1

        self.db.commit()
        return synced_count

    def _sync_consequences(self, project_id: int) -> int:
        """Sync consequences to timeline events"""
        consequences = self.db.query(Consequence).join(
            StoryEvent
        ).filter(
            StoryEvent.project_id == project_id
        ).all()

        synced_count = 0
        for consequence in consequences:
            # Only sync realized consequences with target events
            if consequence.status.value != "realized" or not consequence.target_event_id:
                continue

            # Get target event to find chapter
            target_event = self.db.query(StoryEvent).filter(
                StoryEvent.id == consequence.target_event_id
            ).first()

            if not target_event or not target_event.chapter_number:
                continue

            source_hash = self._calculate_hash({
                "description": consequence.description,
                "target_chapter": target_event.chapter_number,
                "status": consequence.status.value,
            })

            existing = self.db.query(TimelineEvent).filter(
                TimelineEvent.project_id == project_id,
                TimelineEvent.event_type == TimelineEventType.CONSEQUENCE,
                TimelineEvent.source_id == consequence.id
            ).first()

            if existing:
                if existing.sync_hash != source_hash:
                    existing.chapter_number = target_event.chapter_number
                    existing.title = f"Consequence: {consequence.description[:50]}"
                    existing.description = consequence.description
                    existing.magnitude = consequence.severity
                    existing.metadata = {
                        "consequence": {
                            "timeframe": consequence.timeframe.value,
                            "status": consequence.status.value,
                            "probability": consequence.probability,
                            "severity": consequence.severity,
                            "source_event_id": consequence.source_event_id,
                        }
                    }
                    existing.sync_hash = source_hash
                    existing.last_synced_at = datetime.utcnow()
                    synced_count += 1
            else:
                new_event = TimelineEvent(
                    project_id=project_id,
                    event_type=TimelineEventType.CONSEQUENCE,
                    source_id=consequence.id,
                    source_table="consequences",
                    chapter_number=target_event.chapter_number,
                    title=f"Consequence: {consequence.description[:50]}",
                    description=consequence.description,
                    layer=TimelineLayer.CONSEQUENCE,
                    color="#F59E0B",
                    icon="git-branch",
                    magnitude=consequence.severity,
                    metadata={
                        "consequence": {
                            "timeframe": consequence.timeframe.value,
                            "status": consequence.status.value,
                            "probability": consequence.probability,
                            "severity": consequence.severity,
                            "source_event_id": consequence.source_event_id,
                        }
                    },
                    sync_hash=source_hash,
                    last_synced_at=datetime.utcnow(),
                    is_custom=False
                )
                self.db.add(new_event)
                synced_count += 1

        self.db.commit()
        return synced_count

    # ==================== Helper Methods ====================

    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash of data for change detection"""
        # Convert to JSON string with sorted keys for consistency
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()

    # ==================== CRUD Operations ====================

    def get_timeline_events(
        self,
        project_id: int,
        chapter_start: Optional[int] = None,
        chapter_end: Optional[int] = None,
        event_types: Optional[List[TimelineEventType]] = None,
        layers: Optional[List[TimelineLayer]] = None,
        tags: Optional[List[str]] = None,
        only_visible: bool = True,
        only_major_beats: bool = False,
    ) -> List[TimelineEvent]:
        """
        Get timeline events with filtering

        Args:
            project_id: Project ID
            chapter_start: Filter by chapter range start
            chapter_end: Filter by chapter range end
            event_types: Filter by event types
            layers: Filter by layers
            tags: Filter by tags
            only_visible: Only return visible events
            only_major_beats: Only return major story beats

        Returns:
            List of TimelineEvent objects
        """
        query = self.db.query(TimelineEvent).filter(
            TimelineEvent.project_id == project_id
        )

        if chapter_start is not None:
            query = query.filter(TimelineEvent.chapter_number >= chapter_start)

        if chapter_end is not None:
            query = query.filter(TimelineEvent.chapter_number <= chapter_end)

        if event_types:
            query = query.filter(TimelineEvent.event_type.in_(event_types))

        if layers:
            query = query.filter(TimelineEvent.layer.in_(layers))

        if only_visible:
            query = query.filter(TimelineEvent.is_visible == True)

        if only_major_beats:
            query = query.filter(TimelineEvent.is_major_beat == True)

        # Tag filtering (JSONB contains)
        if tags:
            for tag in tags:
                query = query.filter(TimelineEvent.tags.contains([tag]))

        # Order by chapter, then position weight
        query = query.order_by(
            TimelineEvent.chapter_number,
            TimelineEvent.position_weight,
            TimelineEvent.id
        )

        return query.all()

    def create_custom_event(
        self,
        project_id: int,
        chapter_number: int,
        title: str,
        description: Optional[str] = None,
        layer: TimelineLayer = TimelineLayer.PLOT,
        magnitude: float = 0.5,
        **kwargs
    ) -> TimelineEvent:
        """Create a custom user-defined timeline event"""
        event = TimelineEvent(
            project_id=project_id,
            event_type=TimelineEventType.CUSTOM,
            chapter_number=chapter_number,
            title=title,
            description=description,
            layer=layer,
            magnitude=magnitude,
            is_custom=True,
            **kwargs
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def update_event(
        self,
        event_id: int,
        **updates
    ) -> Optional[TimelineEvent]:
        """Update a timeline event"""
        event = self.db.query(TimelineEvent).filter(
            TimelineEvent.id == event_id
        ).first()

        if not event:
            return None

        # Don't allow updates to locked or non-custom synced events
        if event.is_locked and "is_locked" not in updates:
            return None

        for key, value in updates.items():
            if hasattr(event, key):
                setattr(event, key, value)

        self.db.commit()
        self.db.refresh(event)
        return event

    def delete_event(self, event_id: int) -> bool:
        """Delete a timeline event (custom events only)"""
        event = self.db.query(TimelineEvent).filter(
            TimelineEvent.id == event_id
        ).first()

        if not event or not event.is_custom:
            return False

        self.db.delete(event)
        self.db.commit()
        return True

    def move_event(
        self,
        event_id: int,
        new_chapter: int,
        new_position_weight: Optional[float] = None
    ) -> Optional[TimelineEvent]:
        """Move an event to a different chapter/position"""
        event = self.db.query(TimelineEvent).filter(
            TimelineEvent.id == event_id
        ).first()

        if not event or event.is_locked:
            return None

        event.chapter_number = new_chapter
        if new_position_weight is not None:
            event.position_weight = new_position_weight

        self.db.commit()
        self.db.refresh(event)
        return event
