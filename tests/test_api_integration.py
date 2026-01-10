"""
Integration tests for Agent Collaboration API

Tests full request-response cycle through FastAPI endpoints.
"""

import pytest
from datetime import datetime


# ==================== AGENT MANAGEMENT API ====================

@pytest.mark.integration
@pytest.mark.agent
def test_create_agent_endpoint(test_client, test_project):
    """Test POST /api/projects/{id}/agents"""
    response = test_client.post(
        f"/api/projects/{test_project.id}/agents",
        json={
            "name": "New Agent",
            "agent_type": "plotting",
            "role": "contributor",
            "description": "Test agent",
            "model_name": "claude-sonnet-4",
            "temperature": 0.7,
            "max_tokens": 4000,
            "capabilities": ["plot_analysis"]
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Agent"
    assert data["agent_type"] == "plotting"
    assert data["is_active"] is True


@pytest.mark.integration
@pytest.mark.agent
def test_list_agents_endpoint(test_client, test_project, test_agents):
    """Test GET /api/projects/{id}/agents"""
    response = test_client.get(f"/api/projects/{test_project.id}/agents")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= len(test_agents)


@pytest.mark.integration
@pytest.mark.agent
def test_list_agents_filter_by_type(test_client, test_project, test_agents):
    """Test GET /api/projects/{id}/agents with type filter"""
    response = test_client.get(
        f"/api/projects/{test_project.id}/agents?agent_type=plotting"
    )

    assert response.status_code == 200
    data = response.json()
    for agent in data:
        assert agent["agent_type"] == "plotting"


@pytest.mark.integration
@pytest.mark.agent
def test_get_agent_details_endpoint(test_client, test_project, test_agents):
    """Test GET /api/projects/{id}/agents/{agent_id}"""
    agent = test_agents[0]

    response = test_client.get(
        f"/api/projects/{test_project.id}/agents/{agent.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == agent.id
    assert data["name"] == agent.name


@pytest.mark.integration
@pytest.mark.agent
def test_update_agent_endpoint(test_client, test_project, test_agents):
    """Test PATCH /api/projects/{id}/agents/{agent_id}"""
    agent = test_agents[0]

    response = test_client.patch(
        f"/api/projects/{test_project.id}/agents/{agent.id}",
        json={
            "name": "Updated Name",
            "is_active": False
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["is_active"] is False


@pytest.mark.integration
@pytest.mark.agent
def test_delete_agent_endpoint(test_client, test_project):
    """Test DELETE /api/projects/{id}/agents/{agent_id}"""
    # Create agent to delete
    create_response = test_client.post(
        f"/api/projects/{test_project.id}/agents",
        json={
            "name": "To Delete",
            "agent_type": "plotting",
            "role": "contributor"
        }
    )
    agent_id = create_response.json()["id"]

    # Delete agent
    delete_response = test_client.delete(
        f"/api/projects/{test_project.id}/agents/{agent_id}"
    )

    assert delete_response.status_code == 204

    # Verify deleted
    get_response = test_client.get(
        f"/api/projects/{test_project.id}/agents/{agent_id}"
    )
    assert get_response.status_code == 404


@pytest.mark.integration
@pytest.mark.agent
def test_initialize_default_agents_endpoint(test_client, test_project):
    """Test POST /api/projects/{id}/agents/initialize"""
    response = test_client.post(
        f"/api/projects/{test_project.id}/agents/initialize"
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5  # Should create 5 default agents


@pytest.mark.integration
@pytest.mark.agent
def test_get_agent_statistics_endpoint(test_client, test_project, test_agents):
    """Test GET /api/projects/{id}/agents/{agent_id}/statistics"""
    agent = test_agents[0]

    response = test_client.get(
        f"/api/projects/{test_project.id}/agents/{agent.id}/statistics"
    )

    assert response.status_code == 200
    data = response.json()
    assert "agent_name" in data
    assert "tasks_completed" in data
    assert "success_rate" in data


# ==================== TASK MANAGEMENT API ====================

@pytest.mark.integration
@pytest.mark.task
def test_create_task_endpoint(test_client, test_project):
    """Test POST /api/projects/{id}/tasks"""
    response = test_client.post(
        f"/api/projects/{test_project.id}/tasks",
        json={
            "title": "New Task",
            "description": "Task description",
            "task_type": "analyze_plot",
            "priority": "high",
            "context": {},
            "depends_on": [],
            "auto_assign": False
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Task"
    assert data["priority"] == "high"
    assert data["status"] == "pending"


@pytest.mark.integration
@pytest.mark.task
def test_create_batch_tasks_endpoint(test_client, test_project):
    """Test POST /api/projects/{id}/tasks/batch"""
    response = test_client.post(
        f"/api/projects/{test_project.id}/tasks/batch",
        json={
            "tasks": [
                {
                    "title": f"Task {i}",
                    "description": "Test",
                    "task_type": "analyze_plot",
                    "priority": "medium",
                    "context": {},
                    "depends_on": []
                }
                for i in range(3)
            ],
            "auto_assign": False
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_created"] == 3
    assert len(data["tasks"]) == 3


@pytest.mark.integration
@pytest.mark.task
def test_get_task_queue_endpoint(test_client, test_project, test_tasks):
    """Test GET /api/projects/{id}/tasks"""
    response = test_client.get(f"/api/projects/{test_project.id}/tasks")

    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "total" in data
    assert "pending_count" in data


@pytest.mark.integration
@pytest.mark.task
def test_get_task_details_endpoint(test_client, test_project, test_tasks):
    """Test GET /api/projects/{id}/tasks/{task_id}"""
    task = test_tasks[0]

    response = test_client.get(
        f"/api/projects/{test_project.id}/tasks/{task.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task.id
    assert data["title"] == task.title


@pytest.mark.integration
@pytest.mark.task
def test_update_task_endpoint(test_client, test_project, test_tasks):
    """Test PATCH /api/projects/{id}/tasks/{task_id}"""
    task = test_tasks[2]  # Pending task

    response = test_client.patch(
        f"/api/projects/{test_project.id}/tasks/{task.id}",
        json={
            "title": "Updated Title",
            "priority": "critical"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["priority"] == "critical"


@pytest.mark.integration
@pytest.mark.task
def test_assign_task_endpoint(test_client, test_project, test_tasks, test_agents):
    """Test POST /api/projects/{id}/tasks/{task_id}/assign"""
    task = test_tasks[2]  # Pending task
    agent = test_agents[0]

    response = test_client.post(
        f"/api/projects/{test_project.id}/tasks/{task.id}/assign",
        json={"agent_id": agent.id}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == agent.id
    assert data["status"] == "assigned"


@pytest.mark.integration
@pytest.mark.task
def test_start_task_endpoint(test_client, test_project, test_tasks):
    """Test POST /api/projects/{id}/tasks/{task_id}/start"""
    task = test_tasks[0]  # Assigned task

    response = test_client.post(
        f"/api/projects/{test_project.id}/tasks/{task.id}/start"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["started_at"] is not None


@pytest.mark.integration
@pytest.mark.task
def test_complete_task_endpoint(test_client, test_project, test_tasks):
    """Test POST /api/projects/{id}/tasks/{task_id}/complete"""
    task = test_tasks[1]  # In-progress task

    response = test_client.post(
        f"/api/projects/{test_project.id}/tasks/{task.id}/complete",
        json={
            "result": {"analysis": "Complete"},
            "user_rating": 4.5
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["user_rating"] == 4.5


@pytest.mark.integration
@pytest.mark.task
def test_get_task_statistics_endpoint(test_client, test_project, test_tasks):
    """Test GET /api/projects/{id}/tasks/statistics"""
    response = test_client.get(
        f"/api/projects/{test_project.id}/tasks/statistics"
    )

    assert response.status_code == 200
    data = response.json()
    assert "total_tasks" in data
    assert "status_counts" in data
    assert "priority_counts" in data


# ==================== CONVERSATION API ====================

@pytest.mark.integration
@pytest.mark.conversation
def test_create_conversation_endpoint(test_client, test_project, test_agents):
    """Test POST /api/projects/{id}/conversations"""
    response = test_client.post(
        f"/api/projects/{test_project.id}/conversations",
        json={
            "title": "Test Discussion",
            "topic": "plot_development",
            "participant_agent_ids": [test_agents[0].id, test_agents[1].id],
            "moderator_agent_id": test_agents[0].id
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Discussion"
    assert len(data["participant_agent_ids"]) == 2


@pytest.mark.integration
@pytest.mark.conversation
def test_list_conversations_endpoint(test_client, test_project, test_conversation):
    """Test GET /api/projects/{id}/conversations"""
    response = test_client.get(
        f"/api/projects/{test_project.id}/conversations"
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.integration
@pytest.mark.conversation
def test_get_conversation_details_endpoint(test_client, test_project, test_conversation, test_messages):
    """Test GET /api/projects/{id}/conversations/{id}"""
    response = test_client.get(
        f"/api/projects/{test_project.id}/conversations/{test_conversation.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_conversation.id
    assert "messages" in data
    assert len(data["messages"]) >= len(test_messages)


@pytest.mark.integration
@pytest.mark.conversation
def test_add_message_endpoint(test_client, test_project, test_conversation, test_agents):
    """Test POST /api/projects/{id}/conversations/{id}/messages"""
    response = test_client.post(
        f"/api/projects/{test_project.id}/conversations/{test_conversation.id}/messages",
        json={
            "agent_id": test_agents[0].id,
            "content": "New message",
            "message_type": "comment",
            "is_suggestion": False
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "New message"
    assert data["agent_id"] == test_agents[0].id


@pytest.mark.integration
@pytest.mark.conversation
def test_initiate_voting_endpoint(test_client, test_project, test_conversation, test_agents):
    """Test POST /api/projects/{id}/conversations/{id}/vote"""
    response = test_client.post(
        f"/api/projects/{test_project.id}/conversations/{test_conversation.id}/vote",
        json={
            "voting_options": [
                {"id": 1, "description": "Option A", "proposed_by_agent_id": test_agents[0].id},
                {"id": 2, "description": "Option B", "proposed_by_agent_id": test_agents[1].id}
            ],
            "resolution_strategy": "voting"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["has_conflict"] is True
    assert data["voting_options"] is not None


@pytest.mark.integration
@pytest.mark.conversation
def test_cast_vote_endpoint(test_client, test_project, test_conversation, test_agents):
    """Test POST /api/projects/{id}/conversations/{id}/cast-vote"""
    # First initiate voting
    test_client.post(
        f"/api/projects/{test_project.id}/conversations/{test_conversation.id}/vote",
        json={
            "voting_options": [
                {"id": 1, "description": "Option A", "proposed_by_agent_id": test_agents[0].id},
                {"id": 2, "description": "Option B", "proposed_by_agent_id": test_agents[1].id}
            ],
            "resolution_strategy": "voting"
        }
    )

    # Cast vote
    response = test_client.post(
        f"/api/projects/{test_project.id}/conversations/{test_conversation.id}/cast-vote",
        json={
            "agent_id": test_agents[0].id,
            "option_id": 1,
            "confidence": 0.9
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == test_agents[0].id
    assert data["option_id"] == 1


# ==================== MEMORY API ====================

@pytest.mark.integration
@pytest.mark.memory
def test_create_memory_endpoint(test_client, test_project, test_agents):
    """Test POST /api/projects/{id}/agents/{id}/memories"""
    response = test_client.post(
        f"/api/projects/{test_project.id}/agents/{test_agents[0].id}/memories",
        json={
            "content": "New memory",
            "memory_type": "episodic",
            "importance": 0.7,
            "context": {}
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "New memory"
    assert data["memory_type"] == "episodic"
    assert data["importance"] == 0.7


@pytest.mark.integration
@pytest.mark.memory
def test_list_memories_endpoint(test_client, test_project, test_agents, test_memories):
    """Test GET /api/projects/{id}/agents/{id}/memories"""
    response = test_client.get(
        f"/api/projects/{test_project.id}/agents/{test_agents[0].id}/memories"
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # Agent 0 has 2+ memories


@pytest.mark.integration
@pytest.mark.memory
def test_list_memories_filter_by_type(test_client, test_project, test_agents, test_memories):
    """Test GET /api/projects/{id}/agents/{id}/memories with type filter"""
    response = test_client.get(
        f"/api/projects/{test_project.id}/agents/{test_agents[0].id}/memories?memory_type=feedback"
    )

    assert response.status_code == 200
    data = response.json()
    for memory in data:
        assert memory["memory_type"] == "feedback"


@pytest.mark.integration
@pytest.mark.memory
def test_search_memories_endpoint(test_client, test_project, test_agents, test_memories):
    """Test POST /api/projects/{id}/agents/{id}/memories/search"""
    response = test_client.post(
        f"/api/projects/{test_project.id}/agents/{test_agents[0].id}/memories/search",
        json={
            "query": "three-act structure",
            "limit": 5
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data
    # Results should have memory and similarity_score
    if data["results"]:
        assert "memory" in data["results"][0]
        assert "similarity_score" in data["results"][0]


@pytest.mark.integration
@pytest.mark.memory
def test_get_memory_statistics_endpoint(test_client, test_project, test_agents, test_memories):
    """Test GET /api/projects/{id}/agents/{id}/memories/statistics"""
    response = test_client.get(
        f"/api/projects/{test_project.id}/agents/{test_agents[0].id}/memories/statistics"
    )

    assert response.status_code == 200
    data = response.json()
    assert "total_memories" in data
    assert "type_counts" in data
    assert "average_importance" in data


# ==================== PROJECT STATISTICS API ====================

@pytest.mark.integration
def test_get_project_statistics_endpoint(test_client, test_project, test_agents, test_tasks):
    """Test GET /api/projects/{id}/agent-collaboration/statistics"""
    response = test_client.get(
        f"/api/projects/{test_project.id}/agent-collaboration/statistics"
    )

    assert response.status_code == 200
    data = response.json()
    assert "total_agents" in data
    assert "active_agents" in data
    assert "total_tasks" in data
    assert "agents_by_type" in data
    assert data["total_agents"] >= len(test_agents)
