"""
Unit tests for AgentOrchestrationService

Tests task routing, delegation, and coordination logic.
"""

import pytest
from datetime import datetime, timedelta

from backend.core.models import AgentTask, TaskStatus, TaskPriority, Agent


# ==================== TASK CREATION ====================

@pytest.mark.unit
@pytest.mark.task
def test_create_task_basic(orchestration_service, test_project, test_agents):
    """Test basic task creation"""
    task = orchestration_service.create_task(
        project_id=test_project.id,
        title="Test Task",
        description="Test description",
        task_type="analyze_plot",
        priority=TaskPriority.HIGH,
        auto_assign=False
    )

    assert task.id is not None
    assert task.title == "Test Task"
    assert task.description == "Test description"
    assert task.task_type == "analyze_plot"
    assert task.priority == TaskPriority.HIGH
    assert task.status == TaskStatus.PENDING
    assert task.agent_id is None  # auto_assign=False


@pytest.mark.unit
@pytest.mark.task
def test_create_task_with_auto_assign(orchestration_service, test_project, test_agents):
    """Test task creation with automatic assignment"""
    task = orchestration_service.create_task(
        project_id=test_project.id,
        title="Plot Analysis",
        description="Analyze plot structure",
        task_type="analyze_plot",
        priority=TaskPriority.MEDIUM,
        auto_assign=True
    )

    assert task.agent_id is not None
    assert task.status == TaskStatus.ASSIGNED


@pytest.mark.unit
@pytest.mark.task
def test_create_task_with_dependencies(orchestration_service, test_project, test_tasks):
    """Test task creation with dependencies"""
    task = orchestration_service.create_task(
        project_id=test_project.id,
        title="Dependent Task",
        description="Task that depends on others",
        depends_on=[test_tasks[0].id, test_tasks[1].id],
        auto_assign=False
    )

    assert task.depends_on == [test_tasks[0].id, test_tasks[1].id]
    assert task.status == TaskStatus.PENDING


@pytest.mark.unit
@pytest.mark.task
def test_create_batch_tasks(orchestration_service, test_project):
    """Test batch task creation"""
    tasks_data = [
        {
            "title": f"Task {i}",
            "description": f"Description {i}",
            "task_type": "analyze_plot",
            "priority": TaskPriority.MEDIUM
        }
        for i in range(5)
    ]

    created_tasks = orchestration_service.create_batch_tasks(
        project_id=test_project.id,
        tasks_data=tasks_data,
        auto_assign=False
    )

    assert len(created_tasks) == 5
    for i, task in enumerate(created_tasks):
        assert task.title == f"Task {i}"
        assert task.status == TaskStatus.PENDING


# ==================== TASK ASSIGNMENT ====================

@pytest.mark.unit
@pytest.mark.task
def test_assign_task_to_agent(orchestration_service, test_tasks, test_agents):
    """Test manual task assignment"""
    task = test_tasks[2]  # Pending task
    agent = test_agents[0]  # Active plotting agent

    assigned_task = orchestration_service.assign_task(task.id, agent.id)

    assert assigned_task.agent_id == agent.id
    assert assigned_task.status == TaskStatus.ASSIGNED
    assert assigned_task.assigned_at is not None


@pytest.mark.unit
@pytest.mark.task
def test_assign_task_to_inactive_agent_fails(orchestration_service, test_tasks, test_agents):
    """Test that assignment to inactive agent fails"""
    task = test_tasks[2]
    inactive_agent = test_agents[2]  # Inactive agent

    with pytest.raises(ValueError, match="is not active"):
        orchestration_service.assign_task(task.id, inactive_agent.id)


@pytest.mark.unit
@pytest.mark.task
def test_find_best_agent_for_plot_task(orchestration_service, test_project, test_agents, db_session):
    """Test that plotting task gets assigned to plotting agent"""
    task = AgentTask(
        project_id=test_project.id,
        title="Plot Task",
        description="Test",
        task_type="analyze_plot",
        status=TaskStatus.PENDING
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    best_agent = orchestration_service._find_best_agent_for_task(task)

    assert best_agent is not None
    assert best_agent.agent_type.value == "plotting"


@pytest.mark.unit
@pytest.mark.task
def test_agent_scoring_algorithm(orchestration_service, test_project, test_agents, db_session):
    """Test agent scoring considers multiple factors"""
    task = AgentTask(
        project_id=test_project.id,
        title="Test",
        description="Test",
        task_type="analyze_plot",
        status=TaskStatus.PENDING,
        priority=TaskPriority.HIGH
    )
    db_session.add(task)
    db_session.commit()

    # Score active plotting agent with good satisfaction
    score1 = orchestration_service._calculate_agent_score(test_agents[0], task)

    # Score inactive agent
    score2 = orchestration_service._calculate_agent_score(test_agents[2], task)

    # Active agent should score higher than inactive
    assert score1 > score2


# ==================== TASK LIFECYCLE ====================

@pytest.mark.unit
@pytest.mark.task
def test_start_task(orchestration_service, test_tasks, test_agents, db_session):
    """Test starting a task"""
    task = test_tasks[0]  # Assigned task
    agent = test_agents[0]

    started_task = orchestration_service.start_task(task.id)

    assert started_task.status == TaskStatus.IN_PROGRESS
    assert started_task.started_at is not None

    # Check agent is marked as busy
    db_session.refresh(agent)
    assert agent.is_busy is True
    assert agent.current_task_id == task.id


@pytest.mark.unit
@pytest.mark.task
def test_complete_task(orchestration_service, test_tasks, test_agents, db_session):
    """Test completing a task"""
    task = test_tasks[1]  # In-progress task
    agent = test_agents[1]

    result = {"analysis": "test result"}
    completed_task = orchestration_service.complete_task(
        task_id=task.id,
        result=result,
        user_rating=4.5
    )

    assert completed_task.status == TaskStatus.COMPLETED
    assert completed_task.completed_at is not None
    assert completed_task.result == result
    assert completed_task.user_rating == 4.5

    # Check agent stats updated
    db_session.refresh(agent)
    assert agent.is_busy is False
    assert agent.current_task_id is None
    assert agent.tasks_completed == 9  # Was 8, now 9


@pytest.mark.unit
@pytest.mark.task
def test_complete_task_updates_satisfaction_score(orchestration_service, test_agents, db_session):
    """Test that user rating updates agent satisfaction"""
    agent = test_agents[1]
    initial_score = agent.user_satisfaction_score  # 0.92

    # Create and complete task with high rating
    task = orchestration_service.create_task(
        project_id=1,
        title="Test",
        description="Test",
        auto_assign=False
    )
    task.agent_id = agent.id
    task.status = TaskStatus.IN_PROGRESS
    db_session.commit()

    orchestration_service.complete_task(
        task_id=task.id,
        user_rating=5.0
    )

    db_session.refresh(agent)
    # Score should increase (running average)
    assert agent.user_satisfaction_score > initial_score


@pytest.mark.unit
@pytest.mark.task
def test_fail_task_with_retry(orchestration_service, test_tasks, test_agents, db_session):
    """Test task failure with auto-retry"""
    task = test_tasks[1]  # In-progress task
    agent = test_agents[1]

    failed_task = orchestration_service.fail_task(
        task_id=task.id,
        error_message="Test error",
        auto_retry=True
    )

    assert failed_task.retry_count == 1
    assert failed_task.error_message == "Test error"
    assert failed_task.status == TaskStatus.PENDING  # Retrying

    # Check agent stats
    db_session.refresh(agent)
    assert agent.is_busy is False
    assert agent.tasks_failed == 1  # Was 0, now 1


@pytest.mark.unit
@pytest.mark.task
def test_fail_task_max_retries_reached(orchestration_service, test_project, db_session):
    """Test task failure when max retries reached"""
    task = AgentTask(
        project_id=test_project.id,
        title="Test",
        description="Test",
        status=TaskStatus.IN_PROGRESS,
        retry_count=2,
        max_retries=3
    )
    db_session.add(task)
    db_session.commit()

    # Fail 2 more times to reach max
    orchestration_service.fail_task(task.id, "Error 1", auto_retry=True)
    db_session.refresh(task)
    assert task.status == TaskStatus.PENDING  # Still retrying (3/3)

    orchestration_service.fail_task(task.id, "Error 2", auto_retry=True)
    db_session.refresh(task)
    assert task.status == TaskStatus.FAILED  # Max reached


# ==================== DEPENDENCY MANAGEMENT ====================

@pytest.mark.unit
@pytest.mark.task
def test_check_dependencies_complete(orchestration_service, test_project, db_session):
    """Test checking if task dependencies are completed"""
    # Create completed task
    task1 = AgentTask(
        project_id=test_project.id,
        title="Task 1",
        description="First task",
        status=TaskStatus.COMPLETED
    )
    db_session.add(task1)
    db_session.commit()
    db_session.refresh(task1)

    # Create dependent task
    task2 = AgentTask(
        project_id=test_project.id,
        title="Task 2",
        description="Depends on task 1",
        depends_on=[task1.id],
        status=TaskStatus.BLOCKED
    )
    db_session.add(task2)
    db_session.commit()
    db_session.refresh(task2)

    # Check dependencies
    assert orchestration_service._check_dependencies_complete(task2) is True


@pytest.mark.unit
@pytest.mark.task
def test_check_dependencies_incomplete(orchestration_service, test_project, db_session):
    """Test that incomplete dependencies are detected"""
    task1 = AgentTask(
        project_id=test_project.id,
        title="Task 1",
        description="Not completed",
        status=TaskStatus.PENDING
    )
    db_session.add(task1)
    db_session.commit()
    db_session.refresh(task1)

    task2 = AgentTask(
        project_id=test_project.id,
        title="Task 2",
        description="Depends on pending task",
        depends_on=[task1.id],
        status=TaskStatus.BLOCKED
    )
    db_session.add(task2)
    db_session.commit()

    assert orchestration_service._check_dependencies_complete(task2) is False


@pytest.mark.unit
@pytest.mark.task
def test_unblock_dependent_tasks(orchestration_service, test_project, test_agents, db_session):
    """Test that completing a task unblocks dependent tasks"""
    # Create first task
    task1 = AgentTask(
        project_id=test_project.id,
        title="Task 1",
        description="Blocker task",
        status=TaskStatus.IN_PROGRESS,
        agent_id=test_agents[0].id
    )
    db_session.add(task1)
    db_session.commit()
    db_session.refresh(task1)

    # Create blocked task
    task2 = AgentTask(
        project_id=test_project.id,
        title="Task 2",
        description="Blocked task",
        depends_on=[task1.id],
        status=TaskStatus.BLOCKED
    )
    db_session.add(task2)
    db_session.commit()
    db_session.refresh(task2)

    # Complete blocker task
    orchestration_service.complete_task(task1.id)

    # Check that task2 is unblocked
    db_session.refresh(task2)
    assert task2.status == TaskStatus.PENDING


# ==================== QUEUE MANAGEMENT ====================

@pytest.mark.unit
@pytest.mark.task
def test_get_task_queue_all(orchestration_service, test_project, test_tasks):
    """Test getting all tasks in queue"""
    queue = orchestration_service.get_task_queue(
        project_id=test_project.id,
        limit=50
    )

    assert len(queue) == len(test_tasks)


@pytest.mark.unit
@pytest.mark.task
def test_get_task_queue_by_agent(orchestration_service, test_project, test_agents, test_tasks):
    """Test filtering queue by agent"""
    agent = test_agents[0]

    queue = orchestration_service.get_task_queue(
        project_id=test_project.id,
        agent_id=agent.id
    )

    # All tasks should belong to this agent
    for task in queue:
        assert task.agent_id == agent.id


@pytest.mark.unit
@pytest.mark.task
def test_get_task_queue_by_status(orchestration_service, test_project):
    """Test filtering queue by status"""
    queue = orchestration_service.get_task_queue(
        project_id=test_project.id,
        status=TaskStatus.PENDING
    )

    for task in queue:
        assert task.status == TaskStatus.PENDING


@pytest.mark.unit
@pytest.mark.task
def test_get_task_queue_priority_sorting(orchestration_service, test_project, db_session):
    """Test that queue is sorted by priority"""
    # Create tasks with different priorities
    for priority in [TaskPriority.LOW, TaskPriority.CRITICAL, TaskPriority.MEDIUM]:
        task = AgentTask(
            project_id=test_project.id,
            title=f"Task {priority.value}",
            description="Test",
            priority=priority,
            status=TaskStatus.PENDING
        )
        db_session.add(task)
    db_session.commit()

    queue = orchestration_service.get_task_queue(test_project.id)

    # First task should be CRITICAL
    assert queue[0].priority == TaskPriority.CRITICAL


@pytest.mark.unit
@pytest.mark.task
def test_get_next_task(orchestration_service, test_agents):
    """Test getting next task for agent"""
    agent = test_agents[0]

    next_task = orchestration_service.get_next_task(agent.id)

    # Should return assigned task with satisfied dependencies
    assert next_task is not None
    assert next_task.agent_id == agent.id
    assert next_task.status == TaskStatus.ASSIGNED


# ==================== STATISTICS ====================

@pytest.mark.unit
@pytest.mark.task
def test_get_task_statistics(orchestration_service, test_project, test_tasks):
    """Test getting task statistics"""
    stats = orchestration_service.get_task_statistics(test_project.id)

    assert stats["total_tasks"] == len(test_tasks)
    assert "status_counts" in stats
    assert "priority_counts" in stats
    assert stats["status_counts"]["completed"] >= 1
    assert stats["status_counts"]["pending"] >= 1


@pytest.mark.unit
@pytest.mark.task
def test_get_agent_statistics(orchestration_service, test_agents):
    """Test getting agent statistics"""
    agent = test_agents[0]

    stats = orchestration_service.get_agent_statistics(agent.id)

    assert stats["agent_name"] == agent.name
    assert stats["agent_type"] == agent.agent_type.value
    assert stats["tasks_completed"] == agent.tasks_completed
    assert stats["tasks_failed"] == agent.tasks_failed
    assert "success_rate" in stats


@pytest.mark.unit
@pytest.mark.task
def test_agent_statistics_success_rate_calculation(orchestration_service, test_agents):
    """Test success rate calculation in statistics"""
    agent = test_agents[0]  # 10 completed, 1 failed

    stats = orchestration_service.get_agent_statistics(agent.id)

    expected_rate = 10 / (10 + 1)
    assert abs(stats["success_rate"] - expected_rate) < 0.01
