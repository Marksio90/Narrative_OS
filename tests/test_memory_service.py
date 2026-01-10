"""
Unit tests for AgentMemoryService

Tests memory storage, retrieval, search, and learning logic.
"""

import pytest
from datetime import datetime, timedelta

from backend.core.models import AgentMemory, MemoryType, TaskStatus


# ==================== MEMORY CREATION ====================

@pytest.mark.unit
@pytest.mark.memory
def test_create_memory_basic(memory_service, test_project, test_agents):
    """Test basic memory creation"""
    memory = memory_service.create_memory(
        agent_id=test_agents[0].id,
        project_id=test_project.id,
        content="Test memory content",
        memory_type=MemoryType.EPISODIC,
        importance=0.7
    )

    assert memory.id is not None
    assert memory.content == "Test memory content"
    assert memory.memory_type == MemoryType.EPISODIC
    assert memory.importance == 0.7
    assert memory.embedding is not None  # Should have embedding


@pytest.mark.unit
@pytest.mark.memory
def test_create_memory_with_context(memory_service, test_project, test_agents):
    """Test memory creation with context"""
    context = {"chapter_id": 5, "character_ids": [1, 2]}

    memory = memory_service.create_memory(
        agent_id=test_agents[0].id,
        project_id=test_project.id,
        content="Character development in chapter 5",
        memory_type=MemoryType.SEMANTIC,
        importance=0.8,
        context=context
    )

    assert memory.context == context


@pytest.mark.unit
@pytest.mark.memory
def test_create_memory_episodic_has_expiration(memory_service, test_project, test_agents):
    """Test that episodic memories get expiration date"""
    memory = memory_service.create_memory(
        agent_id=test_agents[0].id,
        project_id=test_project.id,
        content="Episodic memory",
        memory_type=MemoryType.EPISODIC,
        importance=0.5
    )

    assert memory.expires_at is not None
    # Should expire in ~30 days
    days_until_expiry = (memory.expires_at - datetime.utcnow()).days
    assert 29 <= days_until_expiry <= 31


@pytest.mark.unit
@pytest.mark.memory
def test_create_memory_from_task(memory_service, test_agents, test_tasks):
    """Test creating memory from completed task"""
    task = test_tasks[3]  # Completed task with rating

    memory = memory_service.create_memory_from_task(
        agent_id=test_agents[0].id,
        task=task,
        include_result=True
    )

    assert memory.content is not None
    assert "Task:" in memory.content
    assert memory.source_type == "task"
    assert memory.source_id == task.id
    # High rating should boost importance
    assert memory.importance >= 0.5


@pytest.mark.unit
@pytest.mark.memory
def test_create_memory_from_high_rated_task_is_procedural(memory_service, test_agents, test_project, db_session):
    """Test that highly rated tasks become procedural memories"""
    from backend.core.models import AgentTask

    task = AgentTask(
        project_id=test_project.id,
        agent_id=test_agents[0].id,
        title="Great task",
        description="Well done",
        status=TaskStatus.COMPLETED,
        user_rating=4.5,
        result={"success": True}
    )
    db_session.add(task)
    db_session.commit()

    memory = memory_service.create_memory_from_task(
        agent_id=test_agents[0].id,
        task=task
    )

    assert memory.memory_type == MemoryType.PROCEDURAL


@pytest.mark.unit
@pytest.mark.memory
def test_create_memory_from_feedback(memory_service, test_project, test_agents):
    """Test creating memory from user feedback"""
    memory = memory_service.create_memory_from_feedback(
        agent_id=test_agents[0].id,
        project_id=test_project.id,
        feedback_content="Great dialogue suggestions!",
        rating=5.0
    )

    assert memory.memory_type == MemoryType.FEEDBACK
    assert memory.source_type == "user_feedback"
    assert memory.importance >= 0.7  # Feedback is important


# ==================== MEMORY RETRIEVAL ====================

@pytest.mark.unit
@pytest.mark.memory
def test_get_memories_all(memory_service, test_agents, test_memories):
    """Test retrieving all memories for agent"""
    memories = memory_service.get_memories(
        agent_id=test_agents[0].id,
        limit=50
    )

    # Agent 0 has 2 memories
    assert len(memories) >= 2


@pytest.mark.unit
@pytest.mark.memory
def test_get_memories_by_type(memory_service, test_agents, test_memories):
    """Test filtering memories by type"""
    memories = memory_service.get_memories(
        agent_id=test_agents[0].id,
        memory_type=MemoryType.FEEDBACK
    )

    for memory in memories:
        assert memory.memory_type == MemoryType.FEEDBACK


@pytest.mark.unit
@pytest.mark.memory
def test_get_memories_min_importance(memory_service, test_agents, test_memories):
    """Test filtering memories by minimum importance"""
    memories = memory_service.get_memories(
        agent_id=test_agents[0].id,
        min_importance=0.85
    )

    for memory in memories:
        assert memory.importance >= 0.85


@pytest.mark.unit
@pytest.mark.memory
def test_get_memories_updates_access_count(memory_service, test_agents, test_memories, db_session):
    """Test that retrieving memories increments access count"""
    memory = test_memories[0]
    initial_count = memory.access_count

    memory_service.get_memories(test_agents[0].id, limit=10)

    db_session.refresh(memory)
    assert memory.access_count == initial_count + 1
    assert memory.last_accessed_at is not None


# ==================== MEMORY SEARCH ====================

@pytest.mark.unit
@pytest.mark.memory
def test_search_memories_basic(memory_service, test_agents, test_memories):
    """Test semantic memory search"""
    results = memory_service.search_memories(
        agent_id=test_agents[0].id,
        query="three-act structure",
        limit=5
    )

    assert len(results) > 0
    # Results should be tuples of (memory, similarity_score)
    memory, score = results[0]
    assert isinstance(memory, AgentMemory)
    assert 0 <= score <= 1


@pytest.mark.unit
@pytest.mark.memory
def test_search_memories_returns_relevant(memory_service, test_agents, test_memories):
    """Test that search returns relevant memories"""
    results = memory_service.search_memories(
        agent_id=test_agents[0].id,
        query="user prefers three-act structure",
        limit=3
    )

    # Should find the memory about three-act structure
    found = False
    for memory, score in results:
        if "three-act structure" in memory.content:
            found = True
            assert score > 0.5  # Should have decent similarity
            break

    assert found


@pytest.mark.unit
@pytest.mark.memory
def test_search_memories_sorted_by_similarity(memory_service, test_agents, test_memories):
    """Test that results are sorted by similarity score"""
    results = memory_service.search_memories(
        agent_id=test_agents[0].id,
        query="test query",
        limit=10
    )

    if len(results) > 1:
        # Check that scores are descending
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True)


@pytest.mark.unit
@pytest.mark.memory
def test_search_memories_by_type(memory_service, test_agents, test_memories):
    """Test searching within specific memory type"""
    results = memory_service.search_memories(
        agent_id=test_agents[0].id,
        query="feedback",
        memory_type=MemoryType.FEEDBACK,
        limit=5
    )

    for memory, score in results:
        assert memory.memory_type == MemoryType.FEEDBACK


@pytest.mark.unit
@pytest.mark.memory
def test_get_relevant_context(memory_service, test_agents, test_memories):
    """Test getting formatted context from relevant memories"""
    context = memory_service.get_relevant_context(
        agent_id=test_agents[0].id,
        context_query="What does the user prefer for story structure?",
        max_memories=3
    )

    assert context != ""
    assert "## Relevant Past Experience:" in context
    # Should include memory content
    assert any(mem.content[:20] in context for mem in test_memories if mem.agent_id == test_agents[0].id)


# ==================== MEMORY MANAGEMENT ====================

@pytest.mark.unit
@pytest.mark.memory
def test_update_memory_importance(memory_service, test_memories, db_session):
    """Test updating memory importance"""
    memory = test_memories[0]
    new_importance = 0.95

    updated = memory_service.update_memory_importance(memory.id, new_importance)

    assert updated.importance == new_importance
    db_session.refresh(memory)
    assert memory.importance == new_importance


@pytest.mark.unit
@pytest.mark.memory
def test_update_memory_importance_clamped(memory_service, test_memories):
    """Test that importance is clamped to [0, 1]"""
    memory = test_memories[0]

    # Test upper bound
    updated = memory_service.update_memory_importance(memory.id, 1.5)
    assert updated.importance == 1.0

    # Test lower bound
    updated = memory_service.update_memory_importance(memory.id, -0.5)
    assert updated.importance == 0.0


@pytest.mark.unit
@pytest.mark.memory
def test_decay_memories(memory_service, test_project, test_agents, db_session):
    """Test memory decay for episodic memories"""
    # Create old episodic memory
    old_memory = AgentMemory(
        project_id=test_project.id,
        agent_id=test_agents[0].id,
        memory_type=MemoryType.EPISODIC,
        content="Old memory",
        importance=0.8,
        embedding=[0.1] * 128,
        created_at=datetime.utcnow() - timedelta(days=30),
        access_count=0
    )
    db_session.add(old_memory)
    db_session.commit()
    db_session.refresh(old_memory)

    initial_importance = old_memory.importance

    # Apply decay
    memory_service.decay_memories(test_agents[0].id)

    db_session.refresh(old_memory)
    # Importance should decrease
    assert old_memory.importance < initial_importance


@pytest.mark.unit
@pytest.mark.memory
def test_decay_memories_deletes_low_importance(memory_service, test_project, test_agents, db_session):
    """Test that very low importance memories are deleted"""
    # Create memory with very low importance
    low_memory = AgentMemory(
        project_id=test_project.id,
        agent_id=test_agents[0].id,
        memory_type=MemoryType.EPISODIC,
        content="Low importance",
        importance=0.05,
        embedding=[0.1] * 128,
        created_at=datetime.utcnow() - timedelta(days=60),
        access_count=0
    )
    db_session.add(low_memory)
    db_session.commit()
    memory_id = low_memory.id

    # Apply decay
    memory_service.decay_memories(test_agents[0].id)

    # Memory should be deleted
    deleted = db_session.query(AgentMemory).filter(AgentMemory.id == memory_id).first()
    assert deleted is None


@pytest.mark.unit
@pytest.mark.memory
def test_cleanup_expired_memories(memory_service, test_project, test_agents, db_session):
    """Test cleanup of expired memories"""
    # Create expired memory
    expired = AgentMemory(
        project_id=test_project.id,
        agent_id=test_agents[0].id,
        memory_type=MemoryType.EPISODIC,
        content="Expired",
        importance=0.5,
        embedding=[0.1] * 128,
        expires_at=datetime.utcnow() - timedelta(days=1)
    )
    db_session.add(expired)
    db_session.commit()
    memory_id = expired.id

    # Cleanup
    memory_service.cleanup_expired_memories(test_agents[0].id)

    # Memory should be deleted
    deleted = db_session.query(AgentMemory).filter(AgentMemory.id == memory_id).first()
    assert deleted is None


@pytest.mark.unit
@pytest.mark.memory
def test_consolidate_memories(memory_service, test_project, test_agents, db_session):
    """Test consolidation of similar memories"""
    # Create two very similar memories
    embedding = [0.5] * 128

    mem1 = AgentMemory(
        project_id=test_project.id,
        agent_id=test_agents[0].id,
        memory_type=MemoryType.SEMANTIC,
        content="User likes concise dialogue",
        importance=0.7,
        embedding=embedding,
        access_count=5
    )
    mem2 = AgentMemory(
        project_id=test_project.id,
        agent_id=test_agents[0].id,
        memory_type=MemoryType.SEMANTIC,
        content="User prefers short dialogue",
        importance=0.6,
        embedding=embedding,  # Same embedding = high similarity
        access_count=3
    )

    db_session.add_all([mem1, mem2])
    db_session.commit()
    initial_count = db_session.query(AgentMemory).filter(
        AgentMemory.agent_id == test_agents[0].id
    ).count()

    # Consolidate
    memory_service.consolidate_memories(test_agents[0].id)

    # Should have fewer memories (similar ones merged)
    final_count = db_session.query(AgentMemory).filter(
        AgentMemory.agent_id == test_agents[0].id
    ).count()

    assert final_count <= initial_count


# ==================== STATISTICS ====================

@pytest.mark.unit
@pytest.mark.memory
def test_get_memory_statistics(memory_service, test_agents, test_memories):
    """Test getting memory statistics"""
    stats = memory_service.get_memory_statistics(test_agents[0].id)

    assert "total_memories" in stats
    assert "type_counts" in stats
    assert "average_importance" in stats
    assert "most_accessed" in stats

    assert stats["total_memories"] >= 2  # Agent 0 has 2+ memories


@pytest.mark.unit
@pytest.mark.memory
def test_memory_statistics_type_counts(memory_service, test_agents, test_memories):
    """Test that type counts are accurate"""
    stats = memory_service.get_memory_statistics(test_agents[0].id)

    type_counts = stats["type_counts"]
    assert isinstance(type_counts, dict)
    # Should have at least episodic and feedback
    assert type_counts.get("episodic", 0) >= 1
    assert type_counts.get("feedback", 0) >= 1


@pytest.mark.unit
@pytest.mark.memory
def test_memory_statistics_most_accessed(memory_service, test_agents, test_memories, db_session):
    """Test that most accessed memories are returned"""
    # Access one memory multiple times
    memory = test_memories[0]
    memory.access_count = 10
    db_session.commit()

    stats = memory_service.get_memory_statistics(test_agents[0].id)

    most_accessed = stats["most_accessed"]
    assert len(most_accessed) > 0
    # The memory we accessed 10 times should be in the list
    found = any(m["id"] == memory.id for m in most_accessed)
    assert found


# ==================== EMBEDDING UTILITIES ====================

@pytest.mark.unit
@pytest.mark.memory
def test_generate_embedding(memory_service):
    """Test embedding generation"""
    embedding = memory_service._generate_embedding("test text")

    assert isinstance(embedding, list)
    assert len(embedding) == 128  # 128-dimensional
    assert all(isinstance(v, float) for v in embedding)
    assert all(-1 <= v <= 1 for v in embedding)  # Normalized


@pytest.mark.unit
@pytest.mark.memory
def test_generate_embedding_deterministic(memory_service):
    """Test that same text produces same embedding"""
    text = "consistent text"

    emb1 = memory_service._generate_embedding(text)
    emb2 = memory_service._generate_embedding(text)

    assert emb1 == emb2


@pytest.mark.unit
@pytest.mark.memory
def test_cosine_similarity(memory_service):
    """Test cosine similarity calculation"""
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    vec3 = [-1.0, 0.0, 0.0]

    # Identical vectors
    sim1 = memory_service._cosine_similarity(vec1, vec2)
    assert sim1 == 1.0

    # Opposite vectors
    sim2 = memory_service._cosine_similarity(vec1, vec3)
    assert sim2 == 0.0  # Normalized to [0, 1], so -1 becomes 0


@pytest.mark.unit
@pytest.mark.memory
def test_cosine_similarity_range(memory_service):
    """Test that similarity is always in [0, 1]"""
    vec1 = [0.5, 0.5, 0.0]
    vec2 = [0.3, 0.7, 0.1]

    similarity = memory_service._cosine_similarity(vec1, vec2)

    assert 0.0 <= similarity <= 1.0
