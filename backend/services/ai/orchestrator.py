"""
AI Orchestrator - Multi-Agent System for Advanced Prose Generation
Coordinates multiple AI models working together like a writers' room
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import anthropic
import openai
from .config import AIConfig, AIModel, select_best_model


@dataclass
class GenerationResult:
    """Result from AI generation"""
    text: str
    model_used: str
    tokens_used: int
    cost: float
    quality_score: float
    refinement_iterations: int
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class Agent:
    """An AI agent with specific role and personality"""
    name: str
    role: str
    model: AIModel
    system_prompt: str
    temperature: float


class AIOrchestrator:
    """
    Advanced AI orchestration system

    Uses multiple AI agents working together:
    - Planner: Outlines the scene structure
    - Writer: Generates initial prose
    - Critic: Identifies issues and suggests improvements
    - Editor: Polishes and refines
    - Canon Keeper: Ensures consistency with established facts
    """

    def __init__(self, config: AIConfig):
        self.config = config
        self.anthropic_client = None
        self.openai_client = None

        # Initialize API clients
        if config.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(
                api_key=config.anthropic_api_key
            )
        if config.openai_api_key:
            self.openai_client = openai.OpenAI(
                api_key=config.openai_api_key
            )

        # Define specialized agents
        self.agents = self._create_agents()

    def _create_agents(self) -> Dict[str, Agent]:
        """Create specialized AI agents for different tasks"""
        return {
            "planner": Agent(
                name="Story Architect",
                role="scene_planning",
                model=self.config.planning_model,
                temperature=0.7,
                system_prompt="""You are a master story architect. Your role is to:
1. Analyze the scene requirements and story context
2. Identify key story beats that must be hit
3. Determine character motivations and emotional arcs
4. Plan the dramatic structure (setup, conflict, resolution)
5. Identify promises to plant and payoffs to deliver
6. Ensure logical flow and pacing

Think step-by-step and be specific about what needs to happen."""
            ),
            "writer": Agent(
                name="Prose Master",
                role="prose_generation",
                model=self.config.primary_model,
                temperature=self.config.temperature,
                system_prompt="""You are an award-winning fiction writer. Your role is to:
1. Transform story beats into vivid, engaging prose
2. Show, don't tell - use sensory details and action
3. Maintain consistent character voice and personality
4. Create natural, believable dialogue
5. Build tension and emotional resonance
6. Use varied sentence structure and rhythm
7. Avoid clichés and purple prose

Write in a compelling, immersive style that draws readers in."""
            ),
            "critic": Agent(
                name="Story Critic",
                role="quality_assessment",
                model=self.config.critique_model,
                temperature=0.6,
                system_prompt="""You are a sharp-eyed story critic. Your role is to:
1. Identify weaknesses in prose, pacing, and structure
2. Spot inconsistencies with character voice or established facts
3. Flag telling instead of showing
4. Point out weak dialogue or awkward phrasing
5. Assess emotional impact and tension
6. Suggest specific improvements

Be constructive but honest. Focus on what would make the scene better."""
            ),
            "editor": Agent(
                name="Line Editor",
                role="refinement",
                model=select_best_model("expansion", "balanced", 5000),
                temperature=0.5,
                system_prompt="""You are a meticulous line editor. Your role is to:
1. Polish prose for clarity and impact
2. Tighten loose sentences and remove fluff
3. Enhance word choice for precision and beauty
4. Ensure grammatical correctness
5. Improve flow and readability
6. Preserve the author's voice while enhancing quality

Focus on making every word count."""
            ),
            "canon_keeper": Agent(
                name="Canon Guardian",
                role="consistency_check",
                model=AIModel.CLAUDE_HAIKU,  # Fast for facts
                temperature=0.3,  # Low for accuracy
                system_prompt="""You are the guardian of story consistency. Your role is to:
1. Check against established canon (characters, locations, rules)
2. Flag any contradictions or inconsistencies
3. Ensure character behavior matches their personality
4. Verify logical consistency of events
5. Confirm promises are tracked and paid off
6. Maintain continuity of details

Be thorough and precise. Canon is sacred."""
            )
        }

    async def generate_scene(
        self,
        scene_description: str,
        story_context: Dict[str, Any],
        canon_context: Optional[List[Dict[str, Any]]] = None,
        previous_scenes: Optional[List[str]] = None
    ) -> GenerationResult:
        """
        Generate a complete scene using multi-agent collaboration

        Args:
            scene_description: What should happen in this scene
            story_context: Broader story context (plot, themes, etc.)
            canon_context: Established canon facts (characters, locations, etc.)
            previous_scenes: Recent scenes for continuity

        Returns:
            GenerationResult with the final prose and metadata
        """
        total_tokens = 0
        total_cost = 0.0
        iterations = 0

        # Step 1: PLANNING
        plan = await self._agent_task(
            agent=self.agents["planner"],
            prompt=self._build_planning_prompt(
                scene_description,
                story_context,
                canon_context
            )
        )
        total_tokens += plan['tokens']
        total_cost += plan['cost']

        # Step 2: INITIAL GENERATION
        draft = await self._agent_task(
            agent=self.agents["writer"],
            prompt=self._build_writing_prompt(
                scene_description,
                plan['response'],
                story_context,
                canon_context,
                previous_scenes
            )
        )
        total_tokens += draft['tokens']
        total_cost += draft['cost']
        current_prose = draft['response']

        # Step 3: ITERATIVE REFINEMENT
        if self.config.use_self_critique:
            for iteration in range(self.config.max_refinement_iterations):
                iterations += 1

                # Critique
                critique = await self._agent_task(
                    agent=self.agents["critic"],
                    prompt=self._build_critique_prompt(
                        current_prose,
                        scene_description,
                        story_context
                    )
                )
                total_tokens += critique['tokens']
                total_cost += critique['cost']

                # If quality is good enough, stop
                if self._extract_quality_score(critique['response']) >= 8.5:
                    break

                # Canon check
                if self.config.use_rag and canon_context:
                    canon_check = await self._agent_task(
                        agent=self.agents["canon_keeper"],
                        prompt=self._build_canon_check_prompt(
                            current_prose,
                            canon_context
                        )
                    )
                    total_tokens += canon_check['tokens']
                    total_cost += canon_check['cost']

                # Refine based on feedback
                refined = await self._agent_task(
                    agent=self.agents["editor"],
                    prompt=self._build_refinement_prompt(
                        current_prose,
                        critique['response'],
                        canon_check['response'] if canon_context else None
                    )
                )
                total_tokens += refined['tokens']
                total_cost += refined['cost']
                current_prose = refined['response']

        # Final quality assessment
        final_critique = await self._agent_task(
            agent=self.agents["critic"],
            prompt=f"Rate this scene from 1-10 and provide brief assessment:\n\n{current_prose}"
        )
        quality_score = self._extract_quality_score(final_critique['response'])

        return GenerationResult(
            text=current_prose,
            model_used=str(self.config.primary_model),
            tokens_used=total_tokens,
            cost=total_cost,
            quality_score=quality_score,
            refinement_iterations=iterations,
            metadata={
                "plan": plan['response'],
                "initial_draft_length": len(draft['response']),
                "final_length": len(current_prose),
                "models_used": list(set(
                    agent.model.value for agent in self.agents.values()
                ))
            },
            timestamp=datetime.utcnow()
        )

    async def _agent_task(
        self,
        agent: Agent,
        prompt: str
    ) -> Dict[str, Any]:
        """Execute a task with a specific agent"""
        # Choose API based on model
        if agent.model.value.startswith("claude"):
            return await self._call_anthropic(agent, prompt)
        elif agent.model.value.startswith("gpt"):
            return await self._call_openai(agent, prompt)
        else:
            raise ValueError(f"Unsupported model: {agent.model}")

    async def _call_anthropic(
        self,
        agent: Agent,
        prompt: str
    ) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")

        response = self.anthropic_client.messages.create(
            model=agent.model.value,
            max_tokens=self.config.max_tokens,
            temperature=agent.temperature,
            system=agent.system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )

        # Calculate cost (example prices from config)
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        # Simplified cost calculation
        cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000

        return {
            "response": response.content[0].text,
            "tokens": input_tokens + output_tokens,
            "cost": cost
        }

    async def _call_openai(
        self,
        agent: Agent,
        prompt: str
    ) -> Dict[str, Any]:
        """Call OpenAI GPT API"""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")

        response = self.openai_client.chat.completions.create(
            model=agent.model.value,
            max_tokens=self.config.max_tokens,
            temperature=agent.temperature,
            messages=[
                {"role": "system", "content": agent.system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        tokens = response.usage.total_tokens
        cost = (tokens * 0.005) / 1000  # Simplified

        return {
            "response": response.choices[0].message.content,
            "tokens": tokens,
            "cost": cost
        }

    def _build_planning_prompt(
        self,
        scene_description: str,
        story_context: Dict[str, Any],
        canon_context: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Build prompt for the planning agent"""
        prompt = f"""Plan a scene with the following requirements:

SCENE GOAL:
{scene_description}

STORY CONTEXT:
Genre: {story_context.get('genre', 'Unknown')}
Act: {story_context.get('act', 'Unknown')}
Previous Scene Summary: {story_context.get('previous_summary', 'N/A')}

"""
        if canon_context:
            prompt += "RELEVANT CANON:\n"
            for fact in canon_context[:10]:  # Top 10 most relevant
                prompt += f"- {fact.get('summary', str(fact))}\n"

        prompt += """
OUTPUT FORMAT:
1. Key Story Beats (3-5 beats this scene must hit)
2. Character Motivations (what each character wants)
3. Emotional Arc (how emotions evolve through the scene)
4. Dramatic Structure (setup → conflict → climax → resolution)
5. Promises & Payoffs (what to plant/deliver)
6. Pacing Notes (where to slow down or speed up)
"""
        return prompt

    def _build_writing_prompt(
        self,
        scene_description: str,
        plan: str,
        story_context: Dict[str, Any],
        canon_context: Optional[List[Dict[str, Any]]],
        previous_scenes: Optional[List[str]]
    ) -> str:
        """Build prompt for the writing agent"""
        prompt = f"""Write a compelling scene based on this plan:

PLAN:
{plan}

SCENE GOAL:
{scene_description}

"""
        if previous_scenes:
            prompt += f"PREVIOUS SCENE ENDING:\n{previous_scenes[-1][-500:]}\n\n"

        if canon_context:
            prompt += "CHARACTER DETAILS:\n"
            for fact in canon_context:
                if fact.get('type') == 'character':
                    prompt += f"- {fact.get('summary', '')}\n"

        prompt += """
WRITING GUIDELINES:
- Show, don't tell (use action, dialogue, sensory details)
- Stay in the established POV and tense
- Create vivid imagery and emotional resonance
- Use natural, character-appropriate dialogue
- Vary sentence structure and rhythm
- Build tension through conflict
- End on a compelling note

Write the scene now (800-1500 words):
"""
        return prompt

    def _build_critique_prompt(
        self,
        prose: str,
        scene_description: str,
        story_context: Dict[str, Any]
    ) -> str:
        """Build prompt for the critic agent"""
        return f"""Critique this scene draft:

DRAFT:
{prose}

SCENE GOAL:
{scene_description}

Assess the following (be specific):
1. STRENGTH (1-10): Overall quality and impact
2. SHOWING: How well does it show vs tell?
3. CHARACTER: Are character voices consistent and believable?
4. DIALOGUE: Is dialogue natural and purposeful?
5. PACING: Does the scene drag or rush?
6. TENSION: Does it maintain engagement?
7. PROSE: Is the writing clear, vivid, and varied?
8. GOAL: Does it achieve the scene's purpose?

Then provide 3-5 specific, actionable improvements.

Format:
RATING: [1-10]
STRENGTHS: ...
WEAKNESSES: ...
IMPROVEMENTS:
1. ...
2. ...
"""

    def _build_canon_check_prompt(
        self,
        prose: str,
        canon_context: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for canon checking"""
        canon_summary = "\n".join([
            f"- {fact.get('summary', str(fact))}"
            for fact in canon_context[:20]
        ])

        return f"""Check this scene for canon consistency:

SCENE:
{prose}

ESTABLISHED CANON:
{canon_summary}

Report any:
1. Direct contradictions
2. Character behavior inconsistencies
3. Factual errors
4. Missed opportunities to reference canon

If consistent, say "CANON VERIFIED".
If issues found, list them specifically.
"""

    def _build_refinement_prompt(
        self,
        prose: str,
        critique: str,
        canon_feedback: Optional[str]
    ) -> str:
        """Build prompt for refinement"""
        prompt = f"""Improve this scene based on feedback:

CURRENT VERSION:
{prose}

FEEDBACK:
{critique}

"""
        if canon_feedback and "CANON VERIFIED" not in canon_feedback:
            prompt += f"CANON ISSUES:\n{canon_feedback}\n\n"

        prompt += """
Revise the scene to address the feedback while:
- Preserving what works well
- Fixing specific issues mentioned
- Maintaining the original intent and tone
- Ensuring canon consistency

Provide the complete improved scene:
"""
        return prompt

    def _extract_quality_score(self, critique: str) -> float:
        """Extract numeric quality score from critique"""
        import re
        match = re.search(r'RATING:\s*(\d+(?:\.\d+)?)', critique)
        if match:
            return float(match.group(1))

        match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*10', critique)
        if match:
            return float(match.group(1))

        # Default to mid-range if can't extract
        return 7.0
