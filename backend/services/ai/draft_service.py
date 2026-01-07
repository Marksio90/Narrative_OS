"""
Advanced Draft Service
High-level API for AI-powered prose generation with full canon integration
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from datetime import datetime

from .config import AIConfig, GENERATION_PRESETS
from .orchestrator import AIOrchestrator, GenerationResult
from .rag_engine import RAGEngine, CanonFact


class DraftService:
    """
    Main service for AI-powered draft generation

    Features:
    - Multi-agent AI collaboration
    - Canon-aware generation (RAG)
    - Character voice consistency
    - Iterative refinement
    - Promise/payoff tracking
    - Style matching
    """

    def __init__(
        self,
        db: Session,
        config: Optional[AIConfig] = None
    ):
        self.db = db

        # Use default balanced config if not provided
        self.config = config or GENERATION_PRESETS["balanced"]

        # Initialize AI systems
        self.orchestrator = AIOrchestrator(self.config)

        # Initialize RAG if enabled
        self.rag_engine = None
        if self.config.use_rag and self.config.openai_api_key:
            self.rag_engine = RAGEngine(self.config.openai_api_key)

    async def generate_scene(
        self,
        project_id: int,
        scene_description: str,
        act_number: Optional[int] = None,
        chapter_number: Optional[int] = None,
        pov_character_id: Optional[int] = None,
        previous_scene_ids: Optional[List[int]] = None,
        target_word_count: int = 1000,
        style_reference: Optional[str] = None
    ) -> GenerationResult:
        """
        Generate a complete scene with AI

        Args:
            project_id: Project ID
            scene_description: What should happen ("Sarah discovers the hidden door")
            act_number: Which act (for pacing)
            chapter_number: Which chapter
            pov_character_id: POV character ID (for voice consistency)
            previous_scene_ids: Recent scenes for continuity
            target_word_count: Approximate length
            style_reference: Sample text to match style

        Returns:
            GenerationResult with the generated prose
        """
        # Build story context
        story_context = await self._build_story_context(
            project_id=project_id,
            act_number=act_number,
            chapter_number=chapter_number,
            pov_character_id=pov_character_id
        )

        # Retrieve relevant canon using RAG
        canon_facts = None
        if self.rag_engine:
            canon_facts = await self.rag_engine.retrieve_relevant_canon(
                query=scene_description,
                project_id=project_id,
                db=self.db,
                top_k=15
            )

            # Add canon summary to story context
            story_context['canon_summary'] = await self.rag_engine.build_context_summary(
                canon_facts
            )

        # Get previous scenes for continuity
        previous_scenes = None
        if previous_scene_ids:
            previous_scenes = await self._load_previous_scenes(previous_scene_ids)

        # Add style reference if provided
        if style_reference:
            story_context['style_reference'] = style_reference

        # Add target word count
        story_context['target_word_count'] = target_word_count

        # Generate the scene using multi-agent orchestration
        result = await self.orchestrator.generate_scene(
            scene_description=scene_description,
            story_context=story_context,
            canon_context=[self._fact_to_dict(f) for f in canon_facts] if canon_facts else None,
            previous_scenes=previous_scenes
        )

        return result

    async def expand_beats(
        self,
        project_id: int,
        beats: List[str],
        pov_character_id: Optional[int] = None,
        words_per_beat: int = 200
    ) -> List[GenerationResult]:
        """
        Expand story beats into full prose

        Args:
            project_id: Project ID
            beats: List of beat descriptions ["Beat 1", "Beat 2", ...]
            pov_character_id: POV character
            words_per_beat: Target words per beat

        Returns:
            List of GenerationResult objects, one per beat
        """
        results = []

        for i, beat in enumerate(beats):
            # Previous beats provide context
            previous_results = [r.text for r in results[-2:]] if results else None

            result = await self.generate_scene(
                project_id=project_id,
                scene_description=beat,
                pov_character_id=pov_character_id,
                previous_scene_ids=None,  # Using previous results instead
                target_word_count=words_per_beat
            )

            results.append(result)

        return results

    async def continue_from_text(
        self,
        project_id: int,
        existing_text: str,
        continuation_prompt: str,
        target_word_count: int = 500
    ) -> GenerationResult:
        """
        Continue from existing prose

        Args:
            project_id: Project ID
            existing_text: Text to continue from (last 1000 words)
            continuation_prompt: What should happen next
            target_word_count: How much to generate

        Returns:
            GenerationResult with continuation
        """
        # Extract style from existing text
        style_analysis = await self._analyze_style(existing_text[-2000:])

        story_context = {
            'existing_text': existing_text[-1000:],  # Last 1000 words
            'style_notes': style_analysis,
            'target_word_count': target_word_count,
            'continuation': True
        }

        # Get relevant canon
        canon_facts = None
        if self.rag_engine:
            canon_facts = await self.rag_engine.retrieve_relevant_canon(
                query=continuation_prompt + " " + existing_text[-500:],
                project_id=project_id,
                db=self.db,
                top_k=10
            )

        result = await self.orchestrator.generate_scene(
            scene_description=continuation_prompt,
            story_context=story_context,
            canon_context=[self._fact_to_dict(f) for f in canon_facts] if canon_facts else None,
            previous_scenes=[existing_text[-1000:]]
        )

        return result

    async def refine_prose(
        self,
        project_id: int,
        prose: str,
        refinement_goals: List[str],
        preserve_length: bool = True
    ) -> GenerationResult:
        """
        Refine existing prose based on specific goals

        Args:
            project_id: Project ID
            prose: Prose to refine
            refinement_goals: What to improve ["More sensory details", "Tighter pacing"]
            preserve_length: Keep similar word count

        Returns:
            GenerationResult with refined prose
        """
        goals_text = "\n".join([f"- {goal}" for goal in refinement_goals])

        story_context = {
            'refinement_mode': True,
            'original_prose': prose,
            'goals': goals_text,
            'preserve_length': preserve_length,
            'target_word_count': len(prose.split()) if preserve_length else None
        }

        # Get canon for consistency check
        canon_facts = None
        if self.rag_engine:
            canon_facts = await self.rag_engine.retrieve_relevant_canon(
                query=prose[:500],  # Use beginning of prose
                project_id=project_id,
                db=self.db,
                top_k=10
            )

        result = await self.orchestrator.generate_scene(
            scene_description=f"Refine this prose with these goals:\n{goals_text}\n\nOriginal:\n{prose}",
            story_context=story_context,
            canon_context=[self._fact_to_dict(f) for f in canon_facts] if canon_facts else None,
            previous_scenes=None
        )

        return result

    async def _build_story_context(
        self,
        project_id: int,
        act_number: Optional[int],
        chapter_number: Optional[int],
        pov_character_id: Optional[int]
    ) -> Dict[str, Any]:
        """Build comprehensive story context"""
        context: Dict[str, Any] = {}

        # Get project info
        from core.models.base import Project
        project = self.db.execute(
            select(Project).where(Project.id == project_id)
        ).scalar_one_or_none()

        if project:
            context['title'] = project.title
            context['genre'] = project.genre
            context['target_word_count'] = project.target_word_count

        # Act/chapter info
        if act_number:
            context['act'] = act_number
            context['act_phase'] = self._get_act_phase(act_number)

        if chapter_number:
            context['chapter'] = chapter_number

        # POV character info
        if pov_character_id:
            from core.models.characters import Character
            pov_char = self.db.execute(
                select(Character).where(Character.id == pov_character_id)
            ).scalar_one_or_none()

            if pov_char:
                context['pov_character'] = {
                    'name': pov_char.name,
                    'personality': pov_char.psychological_profile.get('personality', {}),
                    'voice': pov_char.voice_profile,
                    'goals': pov_char.psychological_profile.get('core_desires', []),
                    'fears': pov_char.psychological_profile.get('fears', [])
                }

        return context

    def _get_act_phase(self, act_number: int) -> str:
        """Get dramatic phase for act number"""
        phases = {
            1: "Setup - Establish characters, world, and conflict",
            2: "Rising Action - Escalate conflict, raise stakes",
            3: "Climax - Maximum tension, decisive confrontation",
            4: "Falling Action - Resolve conflicts, show consequences",
            5: "Resolution - Conclude arcs, new equilibrium"
        }
        return phases.get(act_number, "Development")

    async def _load_previous_scenes(
        self,
        scene_ids: List[int]
    ) -> List[str]:
        """Load previous scene prose"""
        # TODO: Implement when Scene model is created
        # For now, return empty
        return []

    async def _analyze_style(self, text: str) -> str:
        """
        Analyze writing style from sample text

        Returns style notes for the AI to match
        """
        # Quick heuristic analysis
        words = text.split()
        sentences = text.split('.')
        avg_sentence_length = len(words) / max(len(sentences), 1)

        # Sentence variety
        short_sentences = sum(1 for s in sentences if len(s.split()) < 10)
        long_sentences = sum(1 for s in sentences if len(s.split()) > 25)

        # Dialog ratio
        dialog_markers = text.count('"') + text.count("'")
        dialog_heavy = dialog_markers > len(words) / 20

        notes = []

        if avg_sentence_length < 12:
            notes.append("Short, punchy sentences (Hemingway-esque)")
        elif avg_sentence_length > 20:
            notes.append("Longer, flowing sentences (literary)")
        else:
            notes.append("Balanced sentence length")

        if short_sentences > len(sentences) * 0.3:
            notes.append("Frequent sentence variety with short beats")

        if long_sentences > len(sentences) * 0.2:
            notes.append("Some complex, layered sentences")

        if dialog_heavy:
            notes.append("Dialog-heavy, conversational")
        else:
            notes.append("More narrative/descriptive than dialog")

        # Tense check
        if ' was ' in text or ' were ' in text:
            notes.append("Past tense")
        elif ' is ' in text or ' are ' in text:
            notes.append("Present tense")

        return ". ".join(notes)

    def _fact_to_dict(self, fact: CanonFact) -> Dict[str, Any]:
        """Convert CanonFact to dict for prompts"""
        return {
            'type': fact.entity_type,
            'name': fact.name,
            'summary': fact.summary,
            'relevance': fact.relevance_score
        }
