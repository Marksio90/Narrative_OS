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

    # ==================== Conflict Detection ====================

    def detect_all_conflicts(self, project_id: int) -> Dict[str, int]:
        """
        Run all conflict detection algorithms

        Returns counts of conflicts detected by type
        """
        counts = {
            "overlap": self._detect_overlap_conflicts(project_id),
            "character_conflicts": self._detect_character_conflicts(project_id),
            "pacing_issues": self._detect_pacing_issues(project_id),
            "continuity_errors": self._detect_continuity_errors(project_id),
        }
        return counts

    def _detect_overlap_conflicts(self, project_id: int) -> int:
        """
        Detect events that overlap in the same chapter

        Creates warnings when multiple high-magnitude events
        occur in the same chapter.
        """
        # Get all events grouped by chapter
        events = self.db.query(TimelineEvent).filter(
            TimelineEvent.project_id == project_id,
            TimelineEvent.is_visible == True
        ).order_by(
            TimelineEvent.chapter_number,
            TimelineEvent.position_weight
        ).all()

        # Group by chapter
        chapters: Dict[int, List[TimelineEvent]] = {}
        for event in events:
            if event.chapter_number not in chapters:
                chapters[event.chapter_number] = []
            chapters[event.chapter_number].append(event)

        conflicts_created = 0

        for chapter_num, chapter_events in chapters.items():
            # Count major beats in this chapter
            major_beats = [e for e in chapter_events if e.is_major_beat]

            if len(major_beats) > 2:
                # Too many major beats in one chapter
                event_ids = [e.id for e in major_beats]

                # Check if conflict already exists
                existing = self.db.query(TimelineConflict).filter(
                    TimelineConflict.project_id == project_id,
                    TimelineConflict.conflict_type == ConflictType.OVERLAP,
                    TimelineConflict.chapter_start == chapter_num,
                    TimelineConflict.status == "open"
                ).first()

                if not existing:
                    conflict = TimelineConflict(
                        project_id=project_id,
                        conflict_type=ConflictType.OVERLAP,
                        severity=ConflictSeverity.WARNING,
                        chapter_start=chapter_num,
                        chapter_end=chapter_num,
                        event_ids=event_ids,
                        title=f"Chapter {chapter_num}: Too Many Major Events",
                        description=f"Chapter {chapter_num} contains {len(major_beats)} major story beats. "
                                  f"This may overwhelm the reader. Consider spreading events across chapters.",
                        suggestions=[
                            {
                                "action": "move_event",
                                "details": "Move one or more events to adjacent chapters for better pacing"
                            }
                        ],
                        detection_method="overlap_detector",
                        confidence=0.8
                    )
                    self.db.add(conflict)
                    conflicts_created += 1

            # Check for milestone clustering
            milestones = [e for e in chapter_events if e.event_type == TimelineEventType.MILESTONE]
            if len(milestones) > 3:
                event_ids = [e.id for e in milestones]

                existing = self.db.query(TimelineConflict).filter(
                    TimelineConflict.project_id == project_id,
                    TimelineConflict.conflict_type == ConflictType.OVERLAP,
                    TimelineConflict.chapter_start == chapter_num,
                    TimelineConflict.description.contains("milestones")
                ).first()

                if not existing:
                    conflict = TimelineConflict(
                        project_id=project_id,
                        conflict_type=ConflictType.OVERLAP,
                        severity=ConflictSeverity.INFO,
                        chapter_start=chapter_num,
                        chapter_end=chapter_num,
                        event_ids=event_ids,
                        title=f"Chapter {chapter_num}: Multiple Character Milestones",
                        description=f"{len(milestones)} character arc milestones occur in this chapter. "
                                  f"This is acceptable but verify it's intentional.",
                        detection_method="overlap_detector",
                        confidence=0.6
                    )
                    self.db.add(conflict)
                    conflicts_created += 1

        self.db.commit()
        return conflicts_created

    def _detect_character_conflicts(self, project_id: int) -> int:
        """
        Detect characters appearing in conflicting locations/events

        Checks if a character has milestones or events that would
        require them to be in multiple places simultaneously.
        """
        events = self.db.query(TimelineEvent).filter(
            TimelineEvent.project_id == project_id,
            TimelineEvent.is_visible == True
        ).all()

        # Group events by chapter and character
        character_chapters: Dict[int, Dict[int, List[TimelineEvent]]] = {}

        for event in events:
            if not event.related_characters:
                continue

            chapter = event.chapter_number
            if chapter not in character_chapters:
                character_chapters[chapter] = {}

            for char_id in event.related_characters:
                if char_id not in character_chapters[chapter]:
                    character_chapters[chapter][char_id] = []
                character_chapters[chapter][char_id].append(event)

        conflicts_created = 0

        # Check for characters with too many concurrent events
        for chapter_num, characters in character_chapters.items():
            for char_id, char_events in characters.items():
                if len(char_events) > 5:
                    # Character is involved in many events this chapter
                    event_ids = [e.id for e in char_events]

                    existing = self.db.query(TimelineConflict).filter(
                        TimelineConflict.project_id == project_id,
                        TimelineConflict.conflict_type == ConflictType.CHARACTER_CONFLICT,
                        TimelineConflict.chapter_start == chapter_num,
                        TimelineConflict.event_ids.contains(event_ids[:1])  # Check if any event matches
                    ).first()

                    if not existing:
                        conflict = TimelineConflict(
                            project_id=project_id,
                            conflict_type=ConflictType.CHARACTER_CONFLICT,
                            severity=ConflictSeverity.WARNING,
                            chapter_start=chapter_num,
                            chapter_end=chapter_num,
                            event_ids=event_ids,
                            title=f"Chapter {chapter_num}: Character Over-Involved",
                            description=f"Character (ID: {char_id}) is involved in {len(char_events)} events in this chapter. "
                                      f"Verify this character can realistically participate in all these events.",
                            suggestions=[
                                {
                                    "action": "review_events",
                                    "details": "Review event timing and character availability"
                                }
                            ],
                            detection_method="character_conflict_detector",
                            confidence=0.7
                        )
                        self.db.add(conflict)
                        conflicts_created += 1

        self.db.commit()
        return conflicts_created

    def _detect_pacing_issues(self, project_id: int) -> int:
        """
        Detect pacing problems in the timeline

        Identifies:
        - Long stretches with no major events
        - Too many events clustered together
        - Uneven distribution of story beats
        """
        events = self.db.query(TimelineEvent).filter(
            TimelineEvent.project_id == project_id,
            TimelineEvent.is_visible == True,
            TimelineEvent.is_major_beat == True
        ).order_by(TimelineEvent.chapter_number).all()

        if len(events) < 2:
            return 0

        conflicts_created = 0

        # Check gaps between major events
        for i in range(len(events) - 1):
            current = events[i]
            next_event = events[i + 1]

            gap = next_event.chapter_number - current.chapter_number

            # Large gap without major beats
            if gap > 7:
                existing = self.db.query(TimelineConflict).filter(
                    TimelineConflict.project_id == project_id,
                    TimelineConflict.conflict_type == ConflictType.PACING_ISSUE,
                    TimelineConflict.chapter_start == current.chapter_number,
                    TimelineConflict.chapter_end == next_event.chapter_number
                ).first()

                if not existing:
                    conflict = TimelineConflict(
                        project_id=project_id,
                        conflict_type=ConflictType.PACING_ISSUE,
                        severity=ConflictSeverity.WARNING,
                        chapter_start=current.chapter_number,
                        chapter_end=next_event.chapter_number,
                        event_ids=[current.id, next_event.id],
                        title=f"Pacing Gap: Chapters {current.chapter_number}-{next_event.chapter_number}",
                        description=f"There's a {gap}-chapter gap between major story beats. "
                                  f"Consider adding tension or conflict to maintain reader engagement.",
                        suggestions=[
                            {
                                "action": "add_event",
                                "details": "Add a plot complication, character development, or rising tension"
                            }
                        ],
                        detection_method="pacing_detector",
                        confidence=0.7
                    )
                    self.db.add(conflict)
                    conflicts_created += 1

        self.db.commit()
        return conflicts_created

    def _detect_continuity_errors(self, project_id: int) -> int:
        """
        Detect timeline continuity issues

        Checks for:
        - Character arcs that end before they begin
        - Consequences that occur before their cause
        - Events that reference future events
        """
        conflicts_created = 0

        # Check character arcs
        arcs = self.db.query(CharacterArc).filter(
            CharacterArc.project_id == project_id
        ).all()

        for arc in arcs:
            if arc.start_chapter and arc.end_chapter:
                if arc.end_chapter < arc.start_chapter:
                    # Arc ends before it begins
                    existing = self.db.query(TimelineConflict).filter(
                        TimelineConflict.project_id == project_id,
                        TimelineConflict.conflict_type == ConflictType.CONTINUITY_ERROR,
                        TimelineConflict.description.contains(f"Arc ID: {arc.id}")
                    ).first()

                    if not existing:
                        conflict = TimelineConflict(
                            project_id=project_id,
                            conflict_type=ConflictType.CONTINUITY_ERROR,
                            severity=ConflictSeverity.ERROR,
                            chapter_start=arc.start_chapter,
                            chapter_end=arc.end_chapter,
                            event_ids=[],
                            title=f"Character Arc Timeline Error",
                            description=f"Character arc (Arc ID: {arc.id}) ends at chapter {arc.end_chapter} "
                                      f"but starts at chapter {arc.start_chapter}. End must come after start.",
                            suggestions=[
                                {
                                    "action": "edit_event",
                                    "details": "Correct the start or end chapter for this arc"
                                }
                            ],
                            detection_method="continuity_detector",
                            confidence=1.0
                        )
                        self.db.add(conflict)
                        conflicts_created += 1

        # Check consequences and their sources
        consequences = self.db.query(TimelineEvent).filter(
            TimelineEvent.project_id == project_id,
            TimelineEvent.event_type == TimelineEventType.CONSEQUENCE
        ).all()

        for consequence in consequences:
            source_event_id = consequence.metadata.get("consequence", {}).get("source_event_id")
            if source_event_id:
                # Find source event in timeline
                source = self.db.query(TimelineEvent).filter(
                    TimelineEvent.project_id == project_id,
                    TimelineEvent.source_id == source_event_id,
                    TimelineEvent.event_type == TimelineEventType.STORY_EVENT
                ).first()

                if source and source.chapter_number > consequence.chapter_number:
                    # Consequence occurs before its cause
                    existing = self.db.query(TimelineConflict).filter(
                        TimelineConflict.project_id == project_id,
                        TimelineConflict.conflict_type == ConflictType.CONTINUITY_ERROR,
                        TimelineConflict.event_ids.contains([consequence.id])
                    ).first()

                    if not existing:
                        conflict = TimelineConflict(
                            project_id=project_id,
                            conflict_type=ConflictType.CONTINUITY_ERROR,
                            severity=ConflictSeverity.CRITICAL,
                            chapter_start=consequence.chapter_number,
                            chapter_end=source.chapter_number,
                            event_ids=[consequence.id, source.id],
                            title=f"Consequence Before Cause",
                            description=f"A consequence occurs in chapter {consequence.chapter_number} "
                                      f"but its source event is in chapter {source.chapter_number}. "
                                      f"Effects cannot precede their causes.",
                            suggestions=[
                                {
                                    "action": "move_event",
                                    "event_id": consequence.id,
                                    "details": f"Move consequence to chapter {source.chapter_number + 1} or later"
                                }
                            ],
                            detection_method="continuity_detector",
                            confidence=1.0
                        )
                        self.db.add(conflict)
                        conflicts_created += 1

        self.db.commit()
        return conflicts_created

    # ==================== Conflict Management ====================

    def get_conflicts(
        self,
        project_id: int,
        conflict_types: Optional[List[ConflictType]] = None,
        severities: Optional[List[ConflictSeverity]] = None,
        status: Optional[str] = None,
        chapter_range: Optional[tuple[int, int]] = None
    ) -> List[TimelineConflict]:
        """Get timeline conflicts with filtering"""
        query = self.db.query(TimelineConflict).filter(
            TimelineConflict.project_id == project_id
        )

        if conflict_types:
            query = query.filter(TimelineConflict.conflict_type.in_(conflict_types))

        if severities:
            query = query.filter(TimelineConflict.severity.in_(severities))

        if status:
            query = query.filter(TimelineConflict.status == status)

        if chapter_range:
            start, end = chapter_range
            query = query.filter(
                or_(
                    and_(
                        TimelineConflict.chapter_start >= start,
                        TimelineConflict.chapter_start <= end
                    ),
                    and_(
                        TimelineConflict.chapter_end >= start,
                        TimelineConflict.chapter_end <= end
                    )
                )
            )

        return query.order_by(
            TimelineConflict.severity.desc(),
            TimelineConflict.chapter_start
        ).all()

    def resolve_conflict(
        self,
        conflict_id: int,
        resolution_note: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Optional[TimelineConflict]:
        """Mark a conflict as resolved"""
        conflict = self.db.query(TimelineConflict).filter(
            TimelineConflict.id == conflict_id
        ).first()

        if not conflict:
            return None

        conflict.status = "resolved"
        conflict.resolution_note = resolution_note
        conflict.resolved_at = datetime.utcnow()
        conflict.resolved_by_user_id = user_id

        self.db.commit()
        self.db.refresh(conflict)
        return conflict

    def ignore_conflict(self, conflict_id: int) -> Optional[TimelineConflict]:
        """Mark a conflict as ignored (user acknowledges but won't fix)"""
        conflict = self.db.query(TimelineConflict).filter(
            TimelineConflict.id == conflict_id
        ).first()

        if not conflict:
            return None

        conflict.status = "ignored"
        self.db.commit()
        self.db.refresh(conflict)
        return conflict

    # ==================== Views & Bookmarks ====================

    def save_view(
        self,
        project_id: int,
        name: str,
        config: Dict[str, Any],
        user_id: Optional[int] = None,
        description: Optional[str] = None,
        is_default: bool = False
    ) -> TimelineView:
        """Save a timeline view configuration"""
        view = TimelineView(
            project_id=project_id,
            user_id=user_id,
            name=name,
            description=description,
            config=config,
            is_default=is_default
        )
        self.db.add(view)
        self.db.commit()
        self.db.refresh(view)
        return view

    def get_views(
        self,
        project_id: int,
        user_id: Optional[int] = None
    ) -> List[TimelineView]:
        """Get saved views for a project"""
        query = self.db.query(TimelineView).filter(
            TimelineView.project_id == project_id
        )

        if user_id:
            query = query.filter(
                or_(
                    TimelineView.user_id == user_id,
                    TimelineView.is_shared == True
                )
            )

        return query.order_by(
            TimelineView.is_default.desc(),
            TimelineView.last_used_at.desc()
        ).all()

    def create_bookmark(
        self,
        project_id: int,
        user_id: int,
        chapter_number: int,
        title: str,
        notes: Optional[str] = None,
        color: str = "#FFD700"
    ) -> TimelineBookmark:
        """Create a bookmark on the timeline"""
        bookmark = TimelineBookmark(
            project_id=project_id,
            user_id=user_id,
            chapter_number=chapter_number,
            title=title,
            notes=notes,
            color=color
        )
        self.db.add(bookmark)
        self.db.commit()
        self.db.refresh(bookmark)
        return bookmark

    def get_bookmarks(
        self,
        project_id: int,
        user_id: int
    ) -> List[TimelineBookmark]:
        """Get user's bookmarks for a project"""
        return self.db.query(TimelineBookmark).filter(
            TimelineBookmark.project_id == project_id,
            TimelineBookmark.user_id == user_id
        ).order_by(
            TimelineBookmark.sort_order,
            TimelineBookmark.chapter_number
        ).all()
