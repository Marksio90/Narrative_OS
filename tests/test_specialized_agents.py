"""
Unit tests for Specialized Agent Implementations

Tests PlottingAgent, CharacterAgent, DialogueAgent, ContinuityAgent, QCAgent, and AgentFactory.
"""

import pytest

from backend.services.specialized_agents import (
    AgentFactory, PlottingAgent, CharacterAgent, DialogueAgent,
    ContinuityAgent, QCAgent
)
from backend.core.models import AgentType, StoryEvent, Consequence, CharacterArc


# ==================== AGENT FACTORY ====================

@pytest.mark.unit
@pytest.mark.agent
def test_agent_factory_creates_plotting_agent(db_session, test_agents):
    """Test factory creates PlottingAgent for plotting type"""
    plotting_agent_model = test_agents[0]  # Plotting agent

    agent = AgentFactory.create_agent(plotting_agent_model, db_session)

    assert isinstance(agent, PlottingAgent)
    assert agent.agent == plotting_agent_model


@pytest.mark.unit
@pytest.mark.agent
def test_agent_factory_creates_character_agent(db_session, test_agents):
    """Test factory creates CharacterAgent for character type"""
    character_agent_model = test_agents[1]  # Character agent

    agent = AgentFactory.create_agent(character_agent_model, db_session)

    assert isinstance(agent, CharacterAgent)


@pytest.mark.unit
@pytest.mark.agent
def test_agent_factory_creates_dialogue_agent(db_session, test_agents):
    """Test factory creates DialogueAgent for dialogue type"""
    dialogue_agent_model = test_agents[2]  # Dialogue agent

    agent = AgentFactory.create_agent(dialogue_agent_model, db_session)

    assert isinstance(agent, DialogueAgent)


@pytest.mark.unit
@pytest.mark.agent
def test_agent_factory_invalid_type_raises_error(db_session, test_project):
    """Test that unknown agent type raises error"""
    from backend.core.models import Agent

    invalid_agent = Agent(
        project_id=test_project.id,
        name="Invalid",
        agent_type="invalid_type",  # Invalid type
        role="contributor"
    )

    with pytest.raises(ValueError, match="Unknown agent type"):
        AgentFactory.create_agent(invalid_agent, db_session)


# ==================== PLOTTING AGENT ====================

@pytest.mark.unit
@pytest.mark.agent
def test_plotting_agent_system_prompt(db_session, test_agents):
    """Test PlottingAgent has appropriate system prompt"""
    agent = PlottingAgent(test_agents[0], db_session)

    prompt = agent.get_system_prompt()

    assert "Plot Development Agent" in prompt
    assert "story structure" in prompt.lower()
    assert "plot hole" in prompt.lower()


@pytest.mark.unit
@pytest.mark.agent
def test_plotting_agent_capabilities(db_session, test_agents):
    """Test PlottingAgent capabilities"""
    agent = PlottingAgent(test_agents[0], db_session)

    capabilities = agent.get_capabilities()

    assert "plot_analysis" in capabilities
    assert "pacing_analysis" in capabilities
    assert "plot_hole_detection" in capabilities


@pytest.mark.unit
@pytest.mark.agent
def test_plotting_agent_analyze_plot(db_session, test_agents, test_project):
    """Test PlottingAgent can analyze plot"""
    from backend.core.models import AgentTask

    agent = PlottingAgent(test_agents[0], db_session)

    task = AgentTask(
        project_id=test_project.id,
        title="Analyze plot",
        description="Test",
        task_type="analyze_plot"
    )

    result = agent.execute_task(task)

    assert "analysis" in result
    assert "total_events" in result["analysis"]
    assert "requires_review" in result


@pytest.mark.unit
@pytest.mark.agent
def test_plotting_agent_check_pacing(db_session, test_agents, test_project, test_chapter):
    """Test PlottingAgent pacing analysis"""
    agent = PlottingAgent(test_agents[0], db_session)

    from backend.core.models import AgentTask
    task = AgentTask(
        project_id=test_project.id,
        title="Check pacing",
        description="Test",
        task_type="check_pacing"
    )

    result = agent.execute_task(task)

    assert "pacing_analysis" in result
    assert "total_chapters" in result["pacing_analysis"]


# ==================== CHARACTER AGENT ====================

@pytest.mark.unit
@pytest.mark.agent
def test_character_agent_system_prompt(db_session, test_agents):
    """Test CharacterAgent system prompt"""
    agent = CharacterAgent(test_agents[1], db_session)

    prompt = agent.get_system_prompt()

    assert "Character Development Agent" in prompt
    assert "character arc" in prompt.lower()
    assert "motivation" in prompt.lower()


@pytest.mark.unit
@pytest.mark.agent
def test_character_agent_capabilities(db_session, test_agents):
    """Test CharacterAgent capabilities"""
    agent = CharacterAgent(test_agents[1], db_session)

    capabilities = agent.get_capabilities()

    assert "character_analysis" in capabilities
    assert "arc_development" in capabilities
    assert "motivation_tracking" in capabilities


@pytest.mark.unit
@pytest.mark.agent
def test_character_agent_analyze_character(db_session, test_agents, test_project, test_character):
    """Test CharacterAgent analysis"""
    from backend.core.models import AgentTask

    agent = CharacterAgent(test_agents[1], db_session)

    task = AgentTask(
        project_id=test_project.id,
        title="Analyze character",
        description="Test",
        task_type="analyze_character",
        context={"character_ids": [test_character.id]}
    )

    result = agent.execute_task(task)

    assert "analysis" in result
    assert "character_id" in result["analysis"]
    assert "character_name" in result["analysis"]


@pytest.mark.unit
@pytest.mark.agent
def test_character_agent_consistency_check(db_session, test_agents, test_project, test_character):
    """Test CharacterAgent consistency checking"""
    from backend.core.models import AgentTask

    agent = CharacterAgent(test_agents[1], db_session)

    task = AgentTask(
        project_id=test_project.id,
        title="Check consistency",
        description="Test",
        task_type="check_consistency",
        context={"character_ids": [test_character.id]}
    )

    result = agent.execute_task(task)

    assert "consistency_check" in result
    assert "issues" in result["consistency_check"]


# ==================== DIALOGUE AGENT ====================

@pytest.mark.unit
@pytest.mark.agent
def test_dialogue_agent_system_prompt(db_session, test_agents):
    """Test DialogueAgent system prompt"""
    agent = DialogueAgent(test_agents[2], db_session)

    prompt = agent.get_system_prompt()

    assert "Dialogue Specialist" in prompt
    assert "natural" in prompt.lower() or "dialogue" in prompt.lower()


@pytest.mark.unit
@pytest.mark.agent
def test_dialogue_agent_capabilities(db_session, test_agents):
    """Test DialogueAgent capabilities"""
    agent = DialogueAgent(test_agents[2], db_session)

    capabilities = agent.get_capabilities()

    assert "dialogue_analysis" in capabilities
    assert "dialogue_writing" in capabilities
    assert "voice_consistency" in capabilities


@pytest.mark.unit
@pytest.mark.agent
def test_dialogue_agent_review_dialogue(db_session, test_agents, test_project, test_chapter):
    """Test DialogueAgent review"""
    from backend.core.models import AgentTask

    agent = DialogueAgent(test_agents[2], db_session)

    task = AgentTask(
        project_id=test_project.id,
        title="Review dialogue",
        description="Test",
        task_type="review_dialogue",
        context={"chapter_id": test_chapter.id}
    )

    result = agent.execute_task(task)

    assert "review" in result
    assert "chapter_id" in result["review"]


# ==================== CONTINUITY AGENT ====================

@pytest.mark.unit
@pytest.mark.agent
def test_continuity_agent_system_prompt(db_session, test_agents):
    """Test ContinuityAgent system prompt"""
    # Create continuity agent
    from backend.core.models import Agent
    continuity_agent_model = Agent(
        project_id=1,
        name="Continuity Checker",
        agent_type=AgentType.CONTINUITY,
        role="reviewer"
    )

    agent = ContinuityAgent(continuity_agent_model, db_session)

    prompt = agent.get_system_prompt()

    assert "Continuity Agent" in prompt
    assert "consistency" in prompt.lower()


@pytest.mark.unit
@pytest.mark.agent
def test_continuity_agent_capabilities(db_session, test_agents):
    """Test ContinuityAgent capabilities"""
    from backend.core.models import Agent
    continuity_agent_model = Agent(
        project_id=1,
        name="Test",
        agent_type=AgentType.CONTINUITY,
        role="reviewer"
    )

    agent = ContinuityAgent(continuity_agent_model, db_session)

    capabilities = agent.get_capabilities()

    assert "continuity_checking" in capabilities
    assert "timeline_verification" in capabilities
    assert "canon_compliance" in capabilities


@pytest.mark.unit
@pytest.mark.agent
def test_continuity_agent_check_continuity(db_session, test_project):
    """Test ContinuityAgent continuity check"""
    from backend.core.models import Agent, AgentTask

    continuity_agent_model = Agent(
        project_id=test_project.id,
        name="Test",
        agent_type=AgentType.CONTINUITY,
        role="reviewer"
    )

    agent = ContinuityAgent(continuity_agent_model, db_session)

    task = AgentTask(
        project_id=test_project.id,
        title="Check continuity",
        description="Test",
        task_type="check_continuity"
    )

    result = agent.execute_task(task)

    assert "continuity_check" in result
    assert "issues" in result["continuity_check"]


# ==================== QC AGENT ====================

@pytest.mark.unit
@pytest.mark.agent
def test_qc_agent_system_prompt(db_session):
    """Test QCAgent system prompt"""
    from backend.core.models import Agent

    qc_agent_model = Agent(
        project_id=1,
        name="QC",
        agent_type=AgentType.QC,
        role="reviewer"
    )

    agent = QCAgent(qc_agent_model, db_session)

    prompt = agent.get_system_prompt()

    assert "Quality Control" in prompt
    assert "quality" in prompt.lower()


@pytest.mark.unit
@pytest.mark.agent
def test_qc_agent_capabilities(db_session):
    """Test QCAgent capabilities"""
    from backend.core.models import Agent

    qc_agent_model = Agent(
        project_id=1,
        name="QC",
        agent_type=AgentType.QC,
        role="reviewer"
    )

    agent = QCAgent(qc_agent_model, db_session)

    capabilities = agent.get_capabilities()

    assert "quality_review" in capabilities
    assert "coherence_check" in capabilities
    assert "holistic_feedback" in capabilities


@pytest.mark.unit
@pytest.mark.agent
def test_qc_agent_quality_check(db_session, test_project):
    """Test QCAgent quality check"""
    from backend.core.models import Agent, AgentTask

    qc_agent_model = Agent(
        project_id=test_project.id,
        name="QC",
        agent_type=AgentType.QC,
        role="reviewer"
    )

    agent = QCAgent(qc_agent_model, db_session)

    task = AgentTask(
        project_id=test_project.id,
        title="Quality check",
        description="Test",
        task_type="quality_check"
    )

    result = agent.execute_task(task)

    assert "qc_results" in result
    assert "overall_score" in result["qc_results"]
    assert "areas" in result["qc_results"]


@pytest.mark.unit
@pytest.mark.agent
def test_qc_agent_calculates_scores(db_session, test_project):
    """Test that QC agent calculates quality scores"""
    from backend.core.models import Agent, AgentTask

    qc_agent_model = Agent(
        project_id=test_project.id,
        name="QC",
        agent_type=AgentType.QC,
        role="reviewer"
    )

    agent = QCAgent(qc_agent_model, db_session)

    task = AgentTask(
        project_id=test_project.id,
        title="Quality check",
        description="Test",
        task_type="quality_check"
    )

    result = agent.execute_task(task)

    overall_score = result["qc_results"]["overall_score"]
    assert 0.0 <= overall_score <= 1.0


# ==================== BASE AGENT CONTEXT ====================

@pytest.mark.unit
@pytest.mark.agent
def test_base_agent_get_context_with_chapter(db_session, test_agents, test_chapter):
    """Test that base agent includes chapter in context"""
    from backend.core.models import AgentTask

    agent = PlottingAgent(test_agents[0], db_session)

    task = AgentTask(
        project_id=1,
        title="Test",
        description="Test",
        context={"chapter_id": test_chapter.id}
    )

    context = agent.get_context(task)

    assert "chapter" in context
    assert context["chapter"]["id"] == test_chapter.id
    assert context["chapter"]["title"] == test_chapter.title


@pytest.mark.unit
@pytest.mark.agent
def test_base_agent_get_context_with_characters(db_session, test_agents, test_character):
    """Test that base agent includes characters in context"""
    from backend.core.models import AgentTask

    agent = CharacterAgent(test_agents[1], db_session)

    task = AgentTask(
        project_id=1,
        title="Test",
        description="Test",
        context={"character_ids": [test_character.id]}
    )

    context = agent.get_context(task)

    assert "characters" in context
    assert len(context["characters"]) == 1
    assert context["characters"][0]["name"] == test_character.name
