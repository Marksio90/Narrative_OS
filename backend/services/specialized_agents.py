"""
Specialized Agent Implementations

Concrete implementations of AI agents with specialized capabilities:
- PlottingAgent: Story structure and plot analysis
- CharacterAgent: Character development and arcs
- DialogueAgent: Dialogue writing and refinement
- ContinuityAgent: Consistency checking
- QCAgent: Quality control and review
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from backend.core.models import (
    Agent, AgentTask, AgentType, Character, Chapter,
    BookArc, CharacterArc, StoryEvent, Consequence
)


# ==================== BASE AGENT ====================

class BaseAgent(ABC):
    """
    Base class for specialized agents

    Defines common interface and utilities for all agent types.
    """

    def __init__(self, agent: Agent, db: Session):
        self.agent = agent
        self.db = db
        self.project_id = agent.project_id

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get agent-specific system prompt"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        pass

    @abstractmethod
    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute task and return result"""
        pass

    def get_context(self, task: AgentTask) -> Dict[str, Any]:
        """
        Build context for task execution

        Args:
            task: AgentTask to execute

        Returns:
            Context dictionary with relevant data
        """
        context = task.context.copy() if task.context else {}

        # Add project info
        context["project_id"] = self.project_id

        # Add chapter info if available
        if "chapter_id" in context:
            chapter = self.db.query(Chapter).filter(
                Chapter.id == context["chapter_id"]
            ).first()
            if chapter:
                context["chapter"] = {
                    "id": chapter.id,
                    "number": chapter.chapter_number,
                    "title": chapter.title,
                    "content": chapter.content
                }

        # Add character info if available
        if "character_ids" in context:
            characters = self.db.query(Character).filter(
                Character.id.in_(context["character_ids"])
            ).all()
            context["characters"] = [
                {
                    "id": char.id,
                    "name": char.name,
                    "description": char.description,
                    "traits": char.traits
                }
                for char in characters
            ]

        return context


# ==================== PLOTTING AGENT ====================

class PlottingAgent(BaseAgent):
    """
    Plot development and analysis agent

    Specializes in:
    - Story structure analysis
    - Plot hole detection
    - Pacing recommendations
    - Arc development
    """

    def get_system_prompt(self) -> str:
        return """You are a Plot Development Agent specialized in story structure and narrative design.

Your expertise includes:
- Three-act structure and story beats
- Plot hole detection and resolution
- Pacing analysis and recommendations
- Character arc integration with plot
- Foreshadowing and payoff tracking
- Conflict escalation and resolution

When analyzing plot:
1. Consider overall story structure
2. Identify key turning points
3. Check for logical consistency
4. Evaluate pacing and tension
5. Suggest improvements clearly

Always provide actionable suggestions with specific chapter/scene references."""

    def get_capabilities(self) -> List[str]:
        return [
            "plot_analysis",
            "structure_evaluation",
            "pacing_analysis",
            "plot_hole_detection",
            "arc_development",
            "conflict_analysis"
        ]

    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute plotting task"""
        context = self.get_context(task)

        if task.task_type == "analyze_plot":
            return self._analyze_plot(context)
        elif task.task_type == "develop_plot":
            return self._develop_plot(context)
        elif task.task_type == "check_pacing":
            return self._check_pacing(context)
        else:
            return {"error": f"Unknown task type: {task.task_type}"}

    def _analyze_plot(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze plot structure"""
        # Get all story events and arcs
        events = self.db.query(StoryEvent).filter(
            StoryEvent.project_id == self.project_id
        ).order_by(StoryEvent.chapter_number).all()

        arcs = self.db.query(BookArc).filter(
            BookArc.project_id == self.project_id
        ).all()

        # Analyze structure
        analysis = {
            "total_events": len(events),
            "total_arcs": len(arcs),
            "issues": [],
            "suggestions": []
        }

        # Check for plot holes (events without clear connections)
        isolated_events = [
            event for event in events
            if not event.consequences or len(event.consequences) == 0
        ]

        if isolated_events:
            analysis["issues"].append({
                "type": "isolated_events",
                "severity": "warning",
                "description": f"Found {len(isolated_events)} events with no consequences",
                "events": [e.id for e in isolated_events[:5]]
            })

        # Check arc completion
        incomplete_arcs = [arc for arc in arcs if arc.status != "completed"]
        if incomplete_arcs:
            analysis["suggestions"].append({
                "type": "complete_arcs",
                "description": f"{len(incomplete_arcs)} arcs are incomplete",
                "arc_ids": [arc.id for arc in incomplete_arcs]
            })

        return {
            "analysis": analysis,
            "confidence": 0.85,
            "requires_review": len(analysis["issues"]) > 0
        }

    def _develop_plot(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Develop plot suggestions"""
        suggestions = []

        # Get current chapter if specified
        if "chapter" in context:
            chapter = context["chapter"]
            suggestions.append({
                "type": "chapter_development",
                "chapter_id": chapter["id"],
                "suggestion": f"Consider adding a turning point in Chapter {chapter['number']} "
                             f"to increase tension and drive character development."
            })

        return {
            "suggestions": suggestions,
            "confidence": 0.75,
            "requires_review": True
        }

    def _check_pacing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check story pacing"""
        chapters = self.db.query(Chapter).filter(
            Chapter.project_id == self.project_id
        ).order_by(Chapter.chapter_number).all()

        pacing_analysis = {
            "total_chapters": len(chapters),
            "pacing_issues": [],
            "recommendations": []
        }

        # Check chapter length variance
        word_counts = [len(ch.content.split()) if ch.content else 0 for ch in chapters]
        if word_counts:
            avg_length = sum(word_counts) / len(word_counts)

            for i, (chapter, word_count) in enumerate(zip(chapters, word_counts)):
                if word_count > avg_length * 1.5:
                    pacing_analysis["pacing_issues"].append({
                        "chapter_id": chapter.id,
                        "chapter_number": chapter.chapter_number,
                        "issue": "too_long",
                        "word_count": word_count,
                        "suggestion": "Consider splitting into multiple chapters"
                    })
                elif word_count < avg_length * 0.5 and word_count > 0:
                    pacing_analysis["pacing_issues"].append({
                        "chapter_id": chapter.id,
                        "chapter_number": chapter.chapter_number,
                        "issue": "too_short",
                        "word_count": word_count,
                        "suggestion": "Consider expanding or merging with adjacent chapter"
                    })

        return {
            "pacing_analysis": pacing_analysis,
            "confidence": 0.8,
            "requires_review": len(pacing_analysis["pacing_issues"]) > 0
        }


# ==================== CHARACTER AGENT ====================

class CharacterAgent(BaseAgent):
    """
    Character development agent

    Specializes in:
    - Character arc analysis
    - Motivation tracking
    - Character consistency
    - Relationship dynamics
    """

    def get_system_prompt(self) -> str:
        return """You are a Character Development Agent specialized in character arcs and psychology.

Your expertise includes:
- Character motivation and goals
- Emotional arc development
- Character consistency and voice
- Relationship dynamics
- Character growth and transformation
- Backstory integration

When analyzing characters:
1. Consider their goals and motivations
2. Track emotional journey
3. Check for consistency in behavior
4. Evaluate relationships with other characters
5. Suggest development opportunities

Always ground suggestions in character psychology and story needs."""

    def get_capabilities(self) -> List[str]:
        return [
            "character_analysis",
            "arc_development",
            "motivation_tracking",
            "consistency_checking",
            "relationship_analysis",
            "voice_consistency"
        ]

    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute character development task"""
        context = self.get_context(task)

        if task.task_type == "analyze_character":
            return self._analyze_character(context)
        elif task.task_type == "develop_character":
            return self._develop_character(context)
        elif task.task_type == "check_consistency":
            return self._check_consistency(context)
        else:
            return {"error": f"Unknown task type: {task.task_type}"}

    def _analyze_character(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze character development"""
        if "character_ids" not in context or not context["character_ids"]:
            return {"error": "No character IDs provided"}

        character_id = context["character_ids"][0]
        character = self.db.query(Character).filter(Character.id == character_id).first()

        if not character:
            return {"error": f"Character {character_id} not found"}

        # Get character arcs
        arcs = self.db.query(CharacterArc).filter(
            CharacterArc.character_id == character_id
        ).all()

        analysis = {
            "character_id": character_id,
            "character_name": character.name,
            "total_arcs": len(arcs),
            "issues": [],
            "strengths": []
        }

        # Check for arc completion
        if not arcs:
            analysis["issues"].append({
                "type": "no_arcs",
                "severity": "warning",
                "description": "Character has no defined arcs"
            })
        else:
            completed_arcs = [arc for arc in arcs if arc.status == "completed"]
            analysis["strengths"].append({
                "type": "arc_progress",
                "description": f"{len(completed_arcs)}/{len(arcs)} arcs completed"
            })

        return {
            "analysis": analysis,
            "confidence": 0.85,
            "requires_review": len(analysis["issues"]) > 0
        }

    def _develop_character(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Develop character suggestions"""
        suggestions = []

        if "characters" in context:
            for char in context["characters"]:
                suggestions.append({
                    "character_id": char["id"],
                    "suggestion": f"Consider developing {char['name']}'s internal conflict "
                                f"to add depth to their motivations."
                })

        return {
            "suggestions": suggestions,
            "confidence": 0.75,
            "requires_review": True
        }

    def _check_consistency(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check character consistency"""
        issues = []

        if "character_ids" in context:
            for char_id in context["character_ids"]:
                character = self.db.query(Character).filter(Character.id == char_id).first()
                if character:
                    # Check if traits are defined
                    if not character.traits:
                        issues.append({
                            "character_id": char_id,
                            "character_name": character.name,
                            "issue": "no_traits_defined",
                            "severity": "warning"
                        })

        return {
            "consistency_check": {
                "issues": issues
            },
            "confidence": 0.8,
            "requires_review": len(issues) > 0
        }


# ==================== DIALOGUE AGENT ====================

class DialogueAgent(BaseAgent):
    """
    Dialogue writing and analysis agent

    Specializes in:
    - Dialogue naturalness
    - Character voice consistency
    - Subtext and tension
    - Dialogue pacing
    """

    def get_system_prompt(self) -> str:
        return """You are a Dialogue Specialist Agent focused on natural, compelling dialogue.

Your expertise includes:
- Natural speech patterns and rhythm
- Character voice distinctiveness
- Subtext and implied meaning
- Dialogue pacing and beats
- Exposition through dialogue
- Conflict and tension in conversation

When reviewing dialogue:
1. Check for character voice consistency
2. Ensure naturalness and believability
3. Look for "show don't tell" opportunities
4. Evaluate pacing and rhythm
5. Identify areas for improvement

Provide specific line-by-line feedback when needed."""

    def get_capabilities(self) -> List[str]:
        return [
            "dialogue_analysis",
            "voice_consistency",
            "dialogue_writing",
            "subtext_analysis",
            "pacing_review",
            "naturalness_check"
        ]

    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute dialogue task"""
        context = self.get_context(task)

        if task.task_type == "review_dialogue":
            return self._review_dialogue(context)
        elif task.task_type == "write_dialogue":
            return self._write_dialogue(context)
        else:
            return {"error": f"Unknown task type: {task.task_type}"}

    def _review_dialogue(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Review dialogue in chapter"""
        if "chapter" not in context:
            return {"error": "No chapter provided"}

        chapter = context["chapter"]
        content = chapter.get("content", "")

        review = {
            "chapter_id": chapter["id"],
            "issues": [],
            "suggestions": []
        }

        # Simple dialogue detection (lines with quotes)
        dialogue_lines = [line for line in content.split('\n') if '"' in line]

        if not dialogue_lines:
            review["issues"].append({
                "type": "no_dialogue",
                "severity": "info",
                "description": "No dialogue found in chapter"
            })
        else:
            review["suggestions"].append({
                "type": "dialogue_present",
                "description": f"Found {len(dialogue_lines)} dialogue lines"
            })

        return {
            "review": review,
            "confidence": 0.7,
            "requires_review": True
        }

    def _write_dialogue(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dialogue suggestions"""
        suggestions = []

        if "characters" in context and len(context["characters"]) >= 2:
            char1, char2 = context["characters"][:2]
            suggestions.append({
                "type": "dialogue_starter",
                "characters": [char1["name"], char2["name"]],
                "suggestion": f"Consider a scene where {char1['name']} and {char2['name']} "
                            f"discuss their conflicting goals."
            })

        return {
            "suggestions": suggestions,
            "confidence": 0.7,
            "requires_review": True
        }


# ==================== CONTINUITY AGENT ====================

class ContinuityAgent(BaseAgent):
    """
    Continuity and consistency checking agent

    Specializes in:
    - Timeline consistency
    - Canon violations
    - Character behavior consistency
    - World rules adherence
    """

    def get_system_prompt(self) -> str:
        return """You are a Continuity Agent specialized in consistency and canon adherence.

Your expertise includes:
- Timeline and chronology verification
- Canon rule compliance
- Character behavior consistency
- World-building consistency
- Detail tracking (names, dates, locations)
- Cause and effect logic

When checking continuity:
1. Verify timeline consistency
2. Check against established canon
3. Track character knowledge and abilities
4. Ensure world rules are followed
5. Flag contradictions clearly

Provide specific references to conflicting information."""

    def get_capabilities(self) -> List[str]:
        return [
            "continuity_checking",
            "timeline_verification",
            "canon_compliance",
            "consistency_analysis",
            "detail_tracking",
            "logic_verification"
        ]

    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute continuity check"""
        context = self.get_context(task)

        if task.task_type == "check_continuity":
            return self._check_continuity(context)
        else:
            return {"error": f"Unknown task type: {task.task_type}"}

    def _check_continuity(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for continuity issues"""
        issues = []

        # Check timeline consistency
        events = self.db.query(StoryEvent).filter(
            StoryEvent.project_id == self.project_id
        ).order_by(StoryEvent.chapter_number).all()

        # Check for consequences before causes
        for event in events:
            consequences = self.db.query(Consequence).filter(
                Consequence.story_event_id == event.id
            ).all()

            for consequence in consequences:
                if consequence.chapter_number < event.chapter_number:
                    issues.append({
                        "type": "temporal_violation",
                        "severity": "error",
                        "description": f"Consequence in ch.{consequence.chapter_number} "
                                     f"before cause in ch.{event.chapter_number}",
                        "event_id": event.id,
                        "consequence_id": consequence.id
                    })

        return {
            "continuity_check": {
                "issues": issues,
                "total_events_checked": len(events)
            },
            "confidence": 0.9,
            "requires_review": len(issues) > 0
        }


# ==================== QC AGENT ====================

class QCAgent(BaseAgent):
    """
    Quality Control agent

    Specializes in:
    - Overall quality review
    - Grammar and style
    - Story coherence
    - Reader experience
    """

    def get_system_prompt(self) -> str:
        return """You are a Quality Control Agent focused on overall story quality.

Your expertise includes:
- Story coherence and flow
- Grammar and style consistency
- Reader engagement
- Pacing and structure
- Technical quality
- Overall polish

When reviewing quality:
1. Assess overall coherence
2. Check for engagement and pacing
3. Review style consistency
4. Identify major issues
5. Provide holistic feedback

Focus on high-level quality rather than minor details."""

    def get_capabilities(self) -> List[str]:
        return [
            "quality_review",
            "coherence_check",
            "style_analysis",
            "engagement_assessment",
            "technical_review",
            "holistic_feedback"
        ]

    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute QC review"""
        context = self.get_context(task)

        if task.task_type == "quality_check":
            return self._quality_check(context)
        else:
            return {"error": f"Unknown task type: {task.task_type}"}

    def _quality_check(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform quality check"""
        qc_results = {
            "overall_score": 0.0,
            "areas": {},
            "major_issues": [],
            "recommendations": []
        }

        # Check plot completeness
        events = self.db.query(StoryEvent).filter(
            StoryEvent.project_id == self.project_id
        ).count()
        qc_results["areas"]["plot"] = min(1.0, events / 10.0)  # Expect at least 10 events

        # Check character development
        characters = self.db.query(Character).filter(
            Character.project_id == self.project_id
        ).count()
        arcs = self.db.query(CharacterArc).count()
        qc_results["areas"]["characters"] = min(1.0, arcs / max(1, characters))

        # Check chapter count
        chapters = self.db.query(Chapter).filter(
            Chapter.project_id == self.project_id
        ).count()
        qc_results["areas"]["structure"] = min(1.0, chapters / 20.0)  # Expect ~20 chapters

        # Calculate overall score
        qc_results["overall_score"] = sum(qc_results["areas"].values()) / len(qc_results["areas"])

        # Add recommendations
        if qc_results["overall_score"] < 0.7:
            qc_results["major_issues"].append({
                "severity": "warning",
                "description": "Story needs more development before publication"
            })

        return {
            "qc_results": qc_results,
            "confidence": 0.75,
            "requires_review": qc_results["overall_score"] < 0.8
        }


# ==================== AGENT FACTORY ====================

class AgentFactory:
    """Factory for creating specialized agent instances"""

    @staticmethod
    def create_agent(agent: Agent, db: Session) -> BaseAgent:
        """
        Create specialized agent instance

        Args:
            agent: Agent model
            db: Database session

        Returns:
            Specialized agent instance
        """
        agent_classes = {
            AgentType.PLOTTING: PlottingAgent,
            AgentType.CHARACTER: CharacterAgent,
            AgentType.DIALOGUE: DialogueAgent,
            AgentType.CONTINUITY: ContinuityAgent,
            AgentType.QC: QCAgent,
        }

        agent_class = agent_classes.get(agent.agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent.agent_type}")

        return agent_class(agent, db)
