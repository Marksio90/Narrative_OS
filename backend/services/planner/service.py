"""
Planner Service

3-level story planning: Book Arc → Chapters → Scenes
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from core.models.planner import BookArc, Chapter, Scene


class PlannerService:
    """
    Service for managing story structure

    Three levels:
    1. Book Arc: Overall structure, acts, story beats
    2. Chapters: Individual chapters with goals and conflicts
    3. Scenes: Scene cards (building blocks of chapters)
    """

    def __init__(self, db: Session):
        self.db = db

    # ===== Book Arc =====

    def create_book_arc(
        self,
        project_id: int,
        data: Dict[str, Any],
    ) -> BookArc:
        """
        Create book arc (overall story structure)

        Args:
            project_id: Project ID
            data: Arc data (premise, theme, story beats, etc.)

        Returns:
            Created book arc
        """
        arc = BookArc(project_id=project_id, **data)
        self.db.add(arc)
        self.db.commit()
        self.db.refresh(arc)
        return arc

    def get_book_arc(self, project_id: int) -> Optional[BookArc]:
        """Get book arc for project"""
        return self.db.query(BookArc).filter(BookArc.project_id == project_id).first()

    def update_book_arc(
        self,
        arc_id: int,
        data: Dict[str, Any],
    ) -> BookArc:
        """Update book arc"""
        arc = self.db.query(BookArc).filter(BookArc.id == arc_id).first()
        if not arc:
            raise ValueError(f"Book arc {arc_id} not found")

        for key, value in data.items():
            if hasattr(arc, key) and value is not None:
                setattr(arc, key, value)

        self.db.commit()
        self.db.refresh(arc)
        return arc

    def validate_book_arc(self, arc_id: int) -> Dict[str, Any]:
        """
        Validate book arc structure

        Checks:
        - Act breaks are logical
        - Story beats are defined
        - Tension curve is present

        Returns:
            Validation result
        """
        arc = self.db.query(BookArc).filter(BookArc.id == arc_id).first()
        if not arc:
            return {"valid": False, "errors": ["Book arc not found"]}

        issues = []

        # Check premise
        if not arc.premise or len(arc.premise.strip()) < 10:
            issues.append("Premise too short or missing")

        # Check theme
        if not arc.theme:
            issues.append("Theme not defined")

        # Check act structure
        if arc.act1_end_chapter and arc.act2_end_chapter:
            if arc.act1_end_chapter >= arc.act2_end_chapter:
                issues.append("Act 1 end must be before Act 2 end")

        # Check story beats
        required_beats = ["inciting_incident", "climax"]
        for beat in required_beats:
            beat_data = getattr(arc, beat, None)
            if not beat_data or not isinstance(beat_data, dict) or not beat_data.get("description"):
                issues.append(f"{beat.replace('_', ' ').title()} not defined or incomplete")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }

    # ===== Chapters =====

    def create_chapter(
        self,
        project_id: int,
        chapter_number: int,
        data: Dict[str, Any],
    ) -> Chapter:
        """
        Create chapter

        Args:
            project_id: Project ID
            chapter_number: Chapter number
            data: Chapter data (goal, stakes, conflict, etc.)

        Returns:
            Created chapter
        """
        chapter = Chapter(
            project_id=project_id,
            chapter_number=chapter_number,
            **data,
        )
        self.db.add(chapter)
        self.db.commit()
        self.db.refresh(chapter)
        return chapter

    def get_chapter(
        self,
        project_id: int,
        chapter_number: int,
    ) -> Optional[Chapter]:
        """Get chapter by number"""
        return self.db.query(Chapter).filter(
            and_(
                Chapter.project_id == project_id,
                Chapter.chapter_number == chapter_number,
            )
        ).first()

    def get_chapter_by_id(self, chapter_id: int) -> Optional[Chapter]:
        """Get chapter by ID"""
        return self.db.query(Chapter).filter(Chapter.id == chapter_id).first()

    def list_chapters(
        self,
        project_id: int,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Chapter]:
        """
        List chapters for a project

        Args:
            project_id: Project ID
            status: Filter by status (planned, drafted, revised, final)
            limit: Max chapters to return

        Returns:
            List of chapters
        """
        query = self.db.query(Chapter).filter(Chapter.project_id == project_id)

        if status:
            query = query.filter(Chapter.status == status)

        query = query.order_by(Chapter.chapter_number)
        return query.limit(limit).all()

    def update_chapter(
        self,
        chapter_id: int,
        data: Dict[str, Any],
    ) -> Chapter:
        """Update chapter"""
        chapter = self.get_chapter_by_id(chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        for key, value in data.items():
            if hasattr(chapter, key) and value is not None:
                setattr(chapter, key, value)

        self.db.commit()
        self.db.refresh(chapter)
        return chapter

    def delete_chapter(self, chapter_id: int) -> bool:
        """Delete chapter and all its scenes"""
        chapter = self.get_chapter_by_id(chapter_id)
        if not chapter:
            return False

        # Delete scenes first
        self.db.query(Scene).filter(Scene.chapter_id == chapter_id).delete()

        # Delete chapter
        self.db.delete(chapter)
        self.db.commit()
        return True

    def validate_chapter(self, chapter_id: int) -> Dict[str, Any]:
        """
        Validate chapter structure

        Checks:
        - Goal is defined
        - Conflict exists
        - Emotional change specified
        - Word count reasonable

        Returns:
            Validation result
        """
        chapter = self.get_chapter_by_id(chapter_id)
        if not chapter:
            return {"valid": False, "errors": ["Chapter not found"]}

        issues = []

        # Check goal
        if not chapter.goal or len(chapter.goal.strip()) < 10:
            issues.append("Chapter goal too short or missing")

        # Check conflict
        if not chapter.conflict:
            issues.append("Conflict not defined")

        # Check emotional journey
        if not chapter.opening_emotion or not chapter.closing_emotion:
            issues.append("Emotional journey incomplete (opening/closing emotions)")

        # Check word count
        if chapter.word_count > chapter.target_word_count * 1.5:
            issues.append(f"Chapter too long ({chapter.word_count} vs target {chapter.target_word_count})")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }

    # ===== Scenes =====

    def create_scene(
        self,
        chapter_id: int,
        project_id: int,
        scene_number: int,
        data: Dict[str, Any],
    ) -> Scene:
        """
        Create scene card

        Args:
            chapter_id: Parent chapter ID
            project_id: Project ID
            scene_number: Scene number within chapter
            data: Scene data (goal, conflict, what_changes, etc.)

        Returns:
            Created scene
        """
        scene = Scene(
            chapter_id=chapter_id,
            project_id=project_id,
            scene_number=scene_number,
            **data,
        )
        self.db.add(scene)
        self.db.commit()
        self.db.refresh(scene)
        return scene

    def get_scene(self, scene_id: int) -> Optional[Scene]:
        """Get scene by ID"""
        return self.db.query(Scene).filter(Scene.id == scene_id).first()

    def list_scenes(
        self,
        chapter_id: int,
    ) -> List[Scene]:
        """
        List scenes for a chapter

        Args:
            chapter_id: Chapter ID

        Returns:
            List of scenes in order
        """
        return (
            self.db.query(Scene)
            .filter(Scene.chapter_id == chapter_id)
            .order_by(Scene.scene_number)
            .all()
        )

    def update_scene(
        self,
        scene_id: int,
        data: Dict[str, Any],
    ) -> Scene:
        """Update scene"""
        scene = self.get_scene(scene_id)
        if not scene:
            raise ValueError(f"Scene {scene_id} not found")

        for key, value in data.items():
            if hasattr(scene, key) and value is not None:
                setattr(scene, key, value)

        self.db.commit()
        self.db.refresh(scene)
        return scene

    def delete_scene(self, scene_id: int) -> bool:
        """Delete scene"""
        scene = self.get_scene(scene_id)
        if not scene:
            return False

        self.db.delete(scene)
        self.db.commit()
        return True

    def validate_scene(self, scene_id: int) -> Dict[str, Any]:
        """
        Validate scene card

        Checks:
        - Goal defined
        - Change specified
        - Participants present

        Returns:
            Validation result
        """
        scene = self.get_scene(scene_id)
        if not scene:
            return {"valid": False, "errors": ["Scene not found"]}

        issues = []

        # Check goal
        if not scene.goal or len(scene.goal.strip()) < 5:
            issues.append("Scene goal too short or missing")

        # Check change
        if not scene.what_changes or len(scene.what_changes.strip()) < 5:
            issues.append("'What changes' not defined - every scene must change something")

        # Check participants
        if not scene.participants or len(scene.participants) == 0:
            issues.append("No participants - who is in this scene?")

        # Check value shift
        if scene.entering_value and scene.exiting_value:
            if scene.entering_value == scene.exiting_value:
                issues.append("Entering and exiting values are the same - no change")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }

    # ===== Bulk Operations =====

    def get_project_structure(self, project_id: int) -> Dict[str, Any]:
        """
        Get complete project structure

        Returns:
            {
                "arc": BookArc,
                "chapters": [Chapter],
                "total_scenes": int,
                "total_words": int,
            }
        """
        arc = self.get_book_arc(project_id)
        chapters = self.list_chapters(project_id)

        total_scenes = sum(len(self.list_scenes(ch.id)) for ch in chapters)
        total_words = sum(ch.word_count for ch in chapters)

        return {
            "arc": arc,
            "chapters": chapters,
            "total_chapters": len(chapters),
            "total_scenes": total_scenes,
            "total_words": total_words,
            "completion": self._calculate_completion(chapters),
        }

    def _calculate_completion(self, chapters: List[Chapter]) -> Dict[str, Any]:
        """Calculate project completion metrics"""
        if not chapters:
            return {"percent": 0, "by_status": {}}

        status_counts = {}
        for ch in chapters:
            status_counts[ch.status] = status_counts.get(ch.status, 0) + 1

        # Completion based on status weights
        weights = {"planned": 0, "drafted": 50, "revised": 75, "final": 100}
        total_weight = sum(weights.get(ch.status, 0) for ch in chapters)
        avg_completion = total_weight / len(chapters) if chapters else 0

        return {
            "percent": round(avg_completion, 1),
            "by_status": status_counts,
            "total_chapters": len(chapters),
        }

    def reorder_scenes(
        self,
        chapter_id: int,
        scene_order: List[int],
    ) -> List[Scene]:
        """
        Reorder scenes within a chapter

        Args:
            chapter_id: Chapter ID
            scene_order: List of scene IDs in desired order

        Returns:
            Updated scenes
        """
        scenes = self.list_scenes(chapter_id)
        scene_map = {s.id: s for s in scenes}

        # Update scene numbers
        for idx, scene_id in enumerate(scene_order, start=1):
            if scene_id in scene_map:
                scene_map[scene_id].scene_number = idx

        self.db.commit()
        return self.list_scenes(chapter_id)
