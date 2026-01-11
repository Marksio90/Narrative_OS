"""
Draft Service

Scene-by-scene prose generation pipeline with quality gates

Pipeline:
1. Input: Scene Card + Canon Context
2. Generate: Prose from scene requirements
3. Extract: New canon facts from generated prose
4. Update: Canon DB with new facts
5. Validate: QC + Contracts + Promises
6. Output: Validated prose OR regeneration needed
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from enum import Enum

from core.llm import get_llm, LLMMessage, LLMConfig
from core.models.planner import Scene, ChapterPlan
from services.qc.service import QCService
from services.canon.promise_ledger import PromiseLedgerService


class DraftStatus(str, Enum):
    """Draft status"""
    GENERATING = "generating"
    VALIDATING = "validating"
    PASSED = "passed"
    FAILED = "failed"
    NEEDS_REGENERATION = "needs_regeneration"


class DraftResult:
    """
    Result of draft generation
    """
    def __init__(
        self,
        status: DraftStatus,
        prose: str,
        word_count: int,
        qc_report: Optional[Dict[str, Any]] = None,
        extracted_facts: Optional[Dict[str, Any]] = None,
        detected_promises: Optional[List[Dict[str, Any]]] = None,
        suggestions: Optional[List[str]] = None,
    ):
        self.status = status
        self.prose = prose
        self.word_count = word_count
        self.qc_report = qc_report
        self.extracted_facts = extracted_facts
        self.detected_promises = detected_promises
        self.suggestions = suggestions or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "prose": self.prose,
            "word_count": self.word_count,
            "qc_report": self.qc_report,
            "extracted_facts": self.extracted_facts,
            "detected_promises": self.detected_promises,
            "suggestions": self.suggestions,
        }


class DraftService:
    """
    Service for generating prose from scene cards

    Implements deterministic scene-by-scene pipeline
    """

    def __init__(self, db: Session):
        self.db = db
        self.qc_service = QCService(db)
        self.promise_service = PromiseLedgerService(db)

    # ===== Scene Generation =====

    async def generate_scene(
        self,
        scene_id: int,
        canon_context: Dict[str, Any],
        style_profile: Optional[Dict[str, Any]] = None,
        auto_validate: bool = True,
    ) -> DraftResult:
        """
        Generate prose for a single scene

        Args:
            scene_id: Scene ID
            canon_context: Relevant canon (characters, locations, rules)
            style_profile: Optional style overrides
            auto_validate: Run QC validation automatically

        Returns:
            DraftResult with prose and validation
        """
        # Get scene
        scene = self.db.query(Scene).filter(Scene.id == scene_id).first()
        if not scene:
            raise ValueError(f"Scene {scene_id} not found")

        # Get chapter for context
        chapter = self.db.query(ChapterPlan).filter(ChapterPlan.id == scene.chapter_id).first()

        # Stage 1: Generate prose
        prose = await self._generate_prose(scene, chapter, canon_context, style_profile)

        # Stage 2: Extract facts
        extracted_facts = await self._extract_facts(prose, scene, canon_context)

        # Stage 3: Detect promises
        detected_promises = await self.promise_service.detect_promises(
            text=prose,
            chapter=chapter.chapter_number if chapter else 1,
            scene=scene.scene_number,
        )

        # Stage 4: QC validation (if requested)
        qc_report = None
        status = DraftStatus.PASSED

        if auto_validate:
            qc_report = await self.qc_service.validate_chapter(
                project_id=scene.project_id,
                chapter_content=prose,
                chapter_metadata={
                    "chapter_number": chapter.chapter_number if chapter else 1,
                    "scene_number": scene.scene_number,
                    "goal": scene.goal,
                },
                canon_context=canon_context,
            )

            # Determine status based on QC
            if not qc_report["passed"]:
                status = DraftStatus.NEEDS_REGENERATION
            elif qc_report["score"] < 70:
                status = DraftStatus.NEEDS_REGENERATION

        # Calculate word count
        word_count = len(prose.split())

        # Generate suggestions
        suggestions = self._generate_suggestions(prose, scene, qc_report)

        return DraftResult(
            status=status,
            prose=prose,
            word_count=word_count,
            qc_report=qc_report,
            extracted_facts=extracted_facts,
            detected_promises=[p.to_dict() for p in detected_promises],
            suggestions=suggestions,
        )

    async def _generate_prose(
        self,
        scene: Scene,
        chapter: Optional[ChapterPlan],
        canon_context: Dict[str, Any],
        style_profile: Optional[Dict[str, Any]],
    ) -> str:
        """
        Generate prose from scene card

        Uses scene card as detailed prompt
        """
        # Build generation prompt
        messages = [
            LLMMessage(
                role="system",
                content=self._build_generation_system_prompt(style_profile),
            ),
            LLMMessage(
                role="user",
                content=self._build_generation_request(scene, chapter, canon_context),
            ),
        ]

        # Call LLM
        llm = get_llm()
        config = LLMConfig(
            model="gpt-4",
            temperature=0.7,  # Creative but controlled
            max_tokens=2000,  # ~1500 words max per scene
        )

        response = await llm.complete(messages, config)
        return response.content.strip()

    def _build_generation_system_prompt(
        self,
        style_profile: Optional[Dict[str, Any]],
    ) -> str:
        """Build system prompt for prose generation"""
        prompt = """You are a professional fiction writer.

**Your task:** Write a scene based on the scene card provided.

**Requirements:**
1. Follow the scene card exactly:
   - Achieve the stated goal
   - Show the conflict
   - Deliver the specified change
   - Include all required participants

2. Show, don't tell:
   - Use action and dialogue
   - Avoid exposition dumps
   - Ground in sensory details

3. Scene structure:
   - Opening: Establish situation
   - Middle: Develop conflict
   - Ending: Deliver change (value shift)

4. Canon compliance:
   - Stay true to character voices
   - Respect world rules
   - Maintain continuity

5. Pacing:
   - Keep it tight
   - Every paragraph serves the goal
   - Cut anything that doesn't contribute

"""

        # Add style profile if provided
        if style_profile:
            prompt += "\n**Style requirements:**\n"
            if "tone" in style_profile:
                prompt += f"Tone: {style_profile['tone']}\n"
            if "pacing" in style_profile:
                prompt += f"Pacing: {style_profile['pacing']}\n"
            if "sentence_length" in style_profile:
                prompt += f"Sentence length: {style_profile['sentence_length']}\n"

        prompt += "\n**Output:** Just the scene prose. No explanations or meta-commentary."

        return prompt

    def _build_generation_request(
        self,
        scene: Scene,
        chapter: Optional[ChapterPlan],
        canon_context: Dict[str, Any],
    ) -> str:
        """Build generation request from scene card"""
        request = "**SCENE CARD:**\n\n"

        # Scene requirements
        request += f"**Goal:** {scene.goal}\n"
        if scene.conflict:
            request += f"**Conflict:** {scene.conflict}\n"
        request += f"**What changes:** {scene.what_changes}\n\n"

        # Value shift
        if scene.entering_value and scene.exiting_value:
            request += f"**Value shift:** {scene.entering_value} → {scene.exiting_value}\n\n"

        # Participants
        if scene.participants and "characters" in canon_context:
            request += "**Characters present:**\n"
            char_map = {c["id"]: c for c in canon_context.get("characters", [])}
            for char_id in scene.participants:
                if char_id in char_map:
                    char = char_map[char_id]
                    request += f"- {char.get('name', 'Unknown')}\n"
                    if char.get("goals"):
                        request += f"  Goals: {', '.join(char['goals'][:2])}\n"
            request += "\n"

        # Location
        if scene.location_id and "locations" in canon_context:
            loc_map = {l["id"]: l for l in canon_context.get("locations", [])}
            if scene.location_id in loc_map:
                loc = loc_map[scene.location_id]
                request += f"**Location:** {loc.get('name', 'Unknown')}\n"
                if loc.get("atmosphere"):
                    request += f"Atmosphere: {loc['atmosphere']}\n"
                request += "\n"

        # Timing
        if scene.time_of_day:
            request += f"**Time:** {scene.time_of_day}\n"
        if scene.duration:
            request += f"**Duration:** {scene.duration}\n"

        # Generation hints
        if scene.tone:
            request += f"\n**Tone:** {scene.tone}\n"
        if scene.pacing:
            request += f"**Pacing:** {scene.pacing}\n"
        if scene.focus:
            request += f"**Focus:** {scene.focus}\n"

        request += "\n**Write this scene now.**"

        return request

    # ===== Fact Extraction =====

    async def _extract_facts(
        self,
        prose: str,
        scene: Scene,
        canon_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract new canon facts from generated prose

        Returns facts that should be added to canon
        """
        messages = [
            LLMMessage(
                role="system",
                content=self._build_extraction_prompt(),
            ),
            LLMMessage(
                role="user",
                content=self._build_extraction_request(prose, scene),
            ),
        ]

        llm = get_llm()
        config = LLMConfig(model="gpt-4", temperature=0.2, max_tokens=500)

        try:
            response = await llm.complete(messages, config)
            facts = self._parse_extracted_facts(response.content)
            return facts
        except Exception as e:
            print(f"Fact extraction error: {e}")
            return {}

    def _build_extraction_prompt(self) -> str:
        """Build prompt for fact extraction"""
        return """You are a fact extractor for narrative canon.

**Your task:** Extract new canon facts from prose.

**What to extract:**
- Physical details (scars, tattoos, clothing)
- Character revelations (secrets, backstory)
- Object details (items mentioned, their properties)
- Location details (new places, features)
- Relationship changes (trust, tension)

**What NOT to extract:**
- Temporary states (tired, hungry)
- Generic actions (walked, talked)
- Already established facts

**Output format:**

CATEGORY: character|location|item|relationship
ENTITY: [name or ID]
FACT: [specific fact]
---

Only extract facts that are NEW and SPECIFIC.
"""

    def _build_extraction_request(
        self,
        prose: str,
        scene: Scene,
    ) -> str:
        """Build extraction request"""
        return f"**Prose:**\n\n{prose}\n\n**Extract new canon facts.**"

    def _parse_extracted_facts(self, response: str) -> Dict[str, Any]:
        """Parse extracted facts from LLM response"""
        facts = {
            "character": [],
            "location": [],
            "item": [],
            "relationship": [],
        }

        current_fact = {}
        lines = response.strip().split("\n")

        for line in lines:
            line = line.strip()

            if line.startswith("CATEGORY:"):
                current_fact["category"] = line.split(":", 1)[1].strip().lower()

            elif line.startswith("ENTITY:"):
                current_fact["entity"] = line.split(":", 1)[1].strip()

            elif line.startswith("FACT:"):
                current_fact["fact"] = line.split(":", 1)[1].strip()

            elif line == "---" and current_fact:
                category = current_fact.get("category", "character")
                if category in facts:
                    facts[category].append({
                        "entity": current_fact.get("entity"),
                        "fact": current_fact.get("fact"),
                    })
                current_fact = {}

        return facts

    # ===== ChapterPlan Generation =====

    async def generate_chapter(
        self,
        chapter_id: int,
        canon_context: Dict[str, Any],
        style_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate prose for entire chapter (scene by scene)

        Args:
            chapter_id: ChapterPlan ID
            canon_context: Canon context
            style_profile: Style overrides

        Returns:
            Complete chapter result with all scenes
        """
        # Get chapter and scenes
        chapter = self.db.query(ChapterPlan).filter(ChapterPlan.id == chapter_id).first()
        if not chapter:
            raise ValueError(f"ChapterPlan {chapter_id} not found")

        scenes = (
            self.db.query(Scene)
            .filter(Scene.chapter_id == chapter_id)
            .order_by(Scene.scene_number)
            .all()
        )

        if not scenes:
            raise ValueError(f"No scenes found for chapter {chapter_id}")

        # Generate each scene
        scene_results = []
        accumulated_prose = []
        all_facts = {}
        all_promises = []

        for scene in scenes:
            result = await self.generate_scene(
                scene_id=scene.id,
                canon_context=canon_context,
                style_profile=style_profile,
                auto_validate=False,  # We'll validate complete chapter
            )

            scene_results.append({
                "scene_number": scene.scene_number,
                "result": result.to_dict(),
            })

            accumulated_prose.append(result.prose)

            # Accumulate facts
            if result.extracted_facts:
                for category, facts in result.extracted_facts.items():
                    if category not in all_facts:
                        all_facts[category] = []
                    all_facts[category].extend(facts)

            # Accumulate promises
            if result.detected_promises:
                all_promises.extend(result.detected_promises)

        # Combine prose
        full_chapter = "\n\n".join(accumulated_prose)

        # Validate complete chapter
        qc_report = await self.qc_service.validate_chapter(
            project_id=chapter.project_id,
            chapter_content=full_chapter,
            chapter_metadata={
                "chapter_number": chapter.chapter_number,
                "goal": chapter.goal,
                "stakes": chapter.stakes,
            },
            canon_context=canon_context,
        )

        # Update chapter content
        chapter.content = full_chapter
        chapter.word_count = len(full_chapter.split())
        chapter.status = "drafted" if qc_report["passed"] else "planned"
        self.db.commit()

        return {
            "chapter_id": chapter_id,
            "chapter_number": chapter.chapter_number,
            "prose": full_chapter,
            "word_count": chapter.word_count,
            "scene_count": len(scenes),
            "scene_results": scene_results,
            "qc_report": qc_report,
            "extracted_facts": all_facts,
            "detected_promises": all_promises,
            "status": "passed" if qc_report["passed"] else "needs_revision",
        }

    # ===== Suggestions =====

    def _generate_suggestions(
        self,
        prose: str,
        scene: Scene,
        qc_report: Optional[Dict[str, Any]],
    ) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []

        # Word count check
        word_count = len(prose.split())
        if word_count < 200:
            suggestions.append("Scene is very short - consider adding more detail")
        elif word_count > 1500:
            suggestions.append("Scene is quite long - consider tightening")

        # QC-based suggestions
        if qc_report:
            if qc_report["warnings"] > 0:
                suggestions.append(f"{qc_report['warnings']} warnings found - review for improvements")

            if qc_report["score"] < 80:
                suggestions.append("Quality score below 80 - consider addressing issues")

        return suggestions
