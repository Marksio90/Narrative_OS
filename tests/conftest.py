"""
Pytest configuration and fixtures for Agent Collaboration tests
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.core.database import Base
from backend.core.models import (
    Project, Agent, AgentTask, AgentConversation, AgentMessage,
    AgentMemory, AgentVote, Character, Chapter,
    AgentType, AgentRole, TaskStatus, TaskPriority, MemoryType
)
from backend.main import app


# ==================== DATABASE FIXTURES ====================

@pytest.fixture(scope="function")
def db_engine():
    """Create test database engine"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create test database session"""
    TestingSessionLocal = sessionmaker(bind=db_engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    """Create FastAPI test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    from backend.core.database import get_db
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


# ==================== MODEL FIXTURES ====================

@pytest.fixture
def test_project(db_session):
    """Create test project"""
    project = Project(
        id=1,
        name="Test Novel",
        description="A test writing project",
        created_at=datetime.utcnow()
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def test_agents(db_session, test_project):
    """Create test agents"""
    agents = [
        Agent(
            project_id=test_project.id,
            name="Plot Master",
            agent_type=AgentType.PLOTTING,
            role=AgentRole.CONTRIBUTOR,
            description="Plot analysis agent",
            is_active=True,
            is_busy=False,
            tasks_completed=10,
            tasks_failed=1,
            user_satisfaction_score=0.85
        ),
        Agent(
            project_id=test_project.id,
            name="Character Developer",
            agent_type=AgentType.CHARACTER,
            role=AgentRole.CONTRIBUTOR,
            description="Character development agent",
            is_active=True,
            is_busy=False,
            tasks_completed=8,
            tasks_failed=0,
            user_satisfaction_score=0.92
        ),
        Agent(
            project_id=test_project.id,
            name="Dialogue Specialist",
            agent_type=AgentType.DIALOGUE,
            role=AgentRole.REVIEWER,
            description="Dialogue review agent",
            is_active=False,  # Inactive agent for testing
            is_busy=False
        ),
    ]

    for agent in agents:
        db_session.add(agent)

    db_session.commit()

    for agent in agents:
        db_session.refresh(agent)

    return agents


@pytest.fixture
def test_tasks(db_session, test_project, test_agents):
    """Create test tasks"""
    tasks = [
        AgentTask(
            project_id=test_project.id,
            agent_id=test_agents[0].id,
            title="Analyze plot structure",
            description="Review chapters 1-5 for coherence",
            task_type="analyze_plot",
            status=TaskStatus.ASSIGNED,
            priority=TaskPriority.HIGH,
            context={"chapter_ids": [1, 2, 3, 4, 5]},
            depends_on=[],
        ),
        AgentTask(
            project_id=test_project.id,
            agent_id=test_agents[1].id,
            title="Develop character arc",
            description="Enhance protagonist motivation",
            task_type="develop_character",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.MEDIUM,
            started_at=datetime.utcnow()
        ),
        AgentTask(
            project_id=test_project.id,
            agent_id=None,
            title="Review dialogue naturalness",
            description="Check dialogue in chapter 3",
            task_type="review_dialogue",
            status=TaskStatus.PENDING,
            priority=TaskPriority.LOW
        ),
        AgentTask(
            project_id=test_project.id,
            agent_id=test_agents[0].id,
            title="Check continuity",
            description="Verify timeline consistency",
            task_type="check_continuity",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.HIGH,
            completed_at=datetime.utcnow(),
            result={"issues_found": 2, "suggestions": ["Fix timeline"]},
            user_rating=4.5
        ),
    ]

    for task in tasks:
        db_session.add(task)

    db_session.commit()

    for task in tasks:
        db_session.refresh(task)

    return tasks


@pytest.fixture
def test_conversation(db_session, test_project, test_agents):
    """Create test conversation"""
    conversation = AgentConversation(
        project_id=test_project.id,
        title="Plot vs Character Priority",
        topic="priority_discussion",
        participant_agent_ids=[test_agents[0].id, test_agents[1].id],
        moderator_agent_id=test_agents[0].id,
        is_active=True,
        is_resolved=False
    )

    db_session.add(conversation)
    db_session.commit()
    db_session.refresh(conversation)

    return conversation


@pytest.fixture
def test_messages(db_session, test_conversation, test_agents):
    """Create test messages"""
    messages = [
        AgentMessage(
            conversation_id=test_conversation.id,
            agent_id=test_agents[0].id,
            content="I think we should focus on plot structure first.",
            message_type="comment",
            is_suggestion=True
        ),
        AgentMessage(
            conversation_id=test_conversation.id,
            agent_id=test_agents[1].id,
            content="Character motivation is more important at this stage.",
            message_type="comment",
            is_suggestion=True
        ),
    ]

    for message in messages:
        db_session.add(message)

    db_session.commit()

    for message in messages:
        db_session.refresh(message)

    return messages


@pytest.fixture
def test_memories(db_session, test_project, test_agents):
    """Create test memories"""
    memories = [
        AgentMemory(
            project_id=test_project.id,
            agent_id=test_agents[0].id,
            memory_type=MemoryType.EPISODIC,
            content="User prefers three-act structure",
            importance=0.8,
            embedding=[0.1] * 128,  # Dummy embedding
            source_type="task",
            source_id=1
        ),
        AgentMemory(
            project_id=test_project.id,
            agent_id=test_agents[0].id,
            memory_type=MemoryType.FEEDBACK,
            content="User wants more foreshadowing",
            importance=0.9,
            embedding=[0.2] * 128,
            source_type="user_feedback"
        ),
        AgentMemory(
            project_id=test_project.id,
            agent_id=test_agents[1].id,
            memory_type=MemoryType.PROCEDURAL,
            content="Character arcs should span 5+ chapters",
            importance=0.7,
            embedding=[0.3] * 128,
            source_type="task",
            source_id=2
        ),
    ]

    for memory in memories:
        db_session.add(memory)

    db_session.commit()

    for memory in memories:
        db_session.refresh(memory)

    return memories


@pytest.fixture
def test_character(db_session, test_project):
    """Create test character"""
    character = Character(
        project_id=test_project.id,
        name="John Doe",
        description="Protagonist",
        traits={"brave": True, "intelligent": True}
    )

    db_session.add(character)
    db_session.commit()
    db_session.refresh(character)

    return character


@pytest.fixture
def test_chapter(db_session, test_project):
    """Create test chapter"""
    chapter = Chapter(
        project_id=test_project.id,
        chapter_number=1,
        title="The Beginning",
        content="Once upon a time..." * 100  # Some content
    )

    db_session.add(chapter)
    db_session.commit()
    db_session.refresh(chapter)

    return chapter


# ==================== SERVICE FIXTURES ====================

@pytest.fixture
def orchestration_service(db_session):
    """Create AgentOrchestrationService instance"""
    from backend.services.agent_orchestration_service import AgentOrchestrationService
    return AgentOrchestrationService(db_session)


@pytest.fixture
def memory_service(db_session):
    """Create AgentMemoryService instance"""
    from backend.services.agent_memory_service import AgentMemoryService
    return AgentMemoryService(db_session)


# ==================== HELPER FIXTURES ====================

@pytest.fixture
def sample_task_data():
    """Sample task creation data"""
    return {
        "title": "Test Task",
        "description": "Test task description",
        "task_type": "analyze_plot",
        "priority": TaskPriority.MEDIUM,
        "context": {"chapter_id": 1},
        "depends_on": [],
        "auto_assign": True
    }


@pytest.fixture
def sample_agent_data():
    """Sample agent creation data"""
    return {
        "name": "Test Agent",
        "agent_type": AgentType.PLOTTING,
        "role": AgentRole.CONTRIBUTOR,
        "description": "Test agent",
        "model_name": "claude-sonnet-4",
        "temperature": 0.7,
        "max_tokens": 4000,
        "capabilities": ["test_capability"]
    }


@pytest.fixture
def sample_memory_data():
    """Sample memory creation data"""
    return {
        "content": "Test memory content",
        "memory_type": MemoryType.EPISODIC,
        "importance": 0.5,
        "source_type": "test",
        "context": {"test": True}
    }
