"""
Agent Memory Service

Manages agent learning and knowledge:
- Memory storage and retrieval
- Vector embeddings for semantic search
- Memory decay and expiration
- Learning from user feedback
- Knowledge organization
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from core.models import (
    Agent, AgentMemory, AgentTask, AgentConversation,
    MemoryType, TaskStatus
)


class AgentMemoryService:
    """
    Manages agent memory and learning

    Handles storage, retrieval, and organization of agent knowledge
    including vector embeddings for semantic search.
    """

    def __init__(self, db: Session):
        self.db = db

    # ==================== MEMORY CREATION ====================

    def create_memory(
        self,
        agent_id: int,
        project_id: int,
        content: str,
        memory_type: MemoryType,
        importance: float = 0.5,
        source_type: Optional[str] = None,
        source_id: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        create_embedding: bool = True
    ) -> AgentMemory:
        """
        Create new memory for agent

        Args:
            agent_id: Agent ID
            project_id: Project ID
            content: Memory content
            memory_type: Type of memory
            importance: Importance score (0-1)
            source_type: Where memory came from (task, conversation, etc.)
            source_id: ID of source entity
            context: Additional context
            create_embedding: Generate vector embedding

        Returns:
            Created AgentMemory
        """
        memory = AgentMemory(
            agent_id=agent_id,
            project_id=project_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            source_type=source_type,
            source_id=source_id,
            context=context or {}
        )

        # Generate embedding if requested
        if create_embedding:
            embedding = self._generate_embedding(content)
            memory.embedding = embedding

        # Set expiration for episodic memories
        if memory_type == MemoryType.EPISODIC:
            # Episodic memories expire after 30 days by default
            memory.expires_at = datetime.utcnow() + timedelta(days=30)

        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)

        return memory

    def create_memory_from_task(
        self,
        agent_id: int,
        task: AgentTask,
        include_result: bool = True
    ) -> AgentMemory:
        """
        Create memory from completed task

        Args:
            agent_id: Agent ID
            task: Completed AgentTask
            include_result: Include task result in memory

        Returns:
            Created AgentMemory
        """
        # Build memory content
        content_parts = [
            f"Task: {task.title}",
            f"Description: {task.description}"
        ]

        if include_result and task.result:
            content_parts.append(f"Result: {json.dumps(task.result)}")

        if task.user_feedback:
            content_parts.append(f"User Feedback: {task.user_feedback}")

        content = "\n".join(content_parts)

        # Determine memory type
        memory_type = MemoryType.EPISODIC
        if task.user_rating and task.user_rating >= 4.0:
            # Good tasks become procedural knowledge
            memory_type = MemoryType.PROCEDURAL

        # Calculate importance
        importance = 0.5
        if task.priority:
            priority_importance = {
                "low": 0.3,
                "medium": 0.5,
                "high": 0.7,
                "critical": 0.9
            }
            importance = priority_importance.get(task.priority.value, 0.5)

        # Boost importance if user rated highly
        if task.user_rating:
            importance = max(importance, task.user_rating / 5.0)

        return self.create_memory(
            agent_id=agent_id,
            project_id=task.project_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            source_type="task",
            source_id=task.id,
            context={
                "task_type": task.task_type,
                "user_rating": task.user_rating,
                "chapter_id": task.context.get("chapter_id") if task.context else None
            }
        )

    def create_memory_from_feedback(
        self,
        agent_id: int,
        project_id: int,
        feedback_content: str,
        rating: Optional[float] = None
    ) -> AgentMemory:
        """
        Create memory from user feedback

        Args:
            agent_id: Agent ID
            project_id: Project ID
            feedback_content: Feedback text
            rating: Optional rating (0-5)

        Returns:
            Created AgentMemory
        """
        importance = 0.7  # Feedback is important
        if rating:
            importance = max(importance, rating / 5.0)

        return self.create_memory(
            agent_id=agent_id,
            project_id=project_id,
            content=feedback_content,
            memory_type=MemoryType.FEEDBACK,
            importance=importance,
            source_type="user_feedback"
        )

    # ==================== MEMORY RETRIEVAL ====================

    def get_memories(
        self,
        agent_id: int,
        memory_type: Optional[MemoryType] = None,
        min_importance: float = 0.0,
        limit: int = 50
    ) -> List[AgentMemory]:
        """
        Get memories for agent

        Args:
            agent_id: Agent ID
            memory_type: Filter by type (optional)
            min_importance: Minimum importance threshold
            limit: Max memories to return

        Returns:
            List of AgentMemory objects
        """
        query = self.db.query(AgentMemory).filter(
            AgentMemory.agent_id == agent_id,
            AgentMemory.importance >= min_importance
        )

        if memory_type:
            query = query.filter(AgentMemory.memory_type == memory_type)

        # Filter out expired memories
        query = query.filter(
            or_(
                AgentMemory.expires_at.is_(None),
                AgentMemory.expires_at > datetime.utcnow()
            )
        )

        # Sort by importance and recency
        memories = query.order_by(
            desc(AgentMemory.importance),
            desc(AgentMemory.created_at)
        ).limit(limit).all()

        # Update access counts
        for memory in memories:
            memory.access_count += 1
            memory.last_accessed_at = datetime.utcnow()

        self.db.commit()

        return memories

    def search_memories(
        self,
        agent_id: int,
        query: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10
    ) -> List[Tuple[AgentMemory, float]]:
        """
        Search memories using semantic similarity

        Args:
            agent_id: Agent ID
            query: Search query
            memory_type: Filter by type (optional)
            limit: Max results to return

        Returns:
            List of (AgentMemory, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = self._generate_embedding(query)

        # Get candidate memories
        query_obj = self.db.query(AgentMemory).filter(
            AgentMemory.agent_id == agent_id,
            AgentMemory.embedding.isnot(None)
        )

        if memory_type:
            query_obj = query_obj.filter(AgentMemory.memory_type == memory_type)

        # Filter out expired
        query_obj = query_obj.filter(
            or_(
                AgentMemory.expires_at.is_(None),
                AgentMemory.expires_at > datetime.utcnow()
            )
        )

        memories = query_obj.all()

        # Calculate cosine similarity
        results = []
        for memory in memories:
            if memory.embedding:
                similarity = self._cosine_similarity(query_embedding, memory.embedding)
                results.append((memory, similarity))

        # Sort by similarity (highest first)
        results.sort(key=lambda x: x[1], reverse=True)

        # Update access counts
        for memory, _ in results[:limit]:
            memory.access_count += 1
            memory.last_accessed_at = datetime.utcnow()

        self.db.commit()

        return results[:limit]

    def get_relevant_context(
        self,
        agent_id: int,
        context_query: str,
        max_memories: int = 5
    ) -> str:
        """
        Get relevant memories as context string

        Args:
            agent_id: Agent ID
            context_query: Query describing needed context
            max_memories: Max memories to include

        Returns:
            Formatted context string
        """
        # Search for relevant memories
        results = self.search_memories(
            agent_id=agent_id,
            query=context_query,
            limit=max_memories
        )

        if not results:
            return ""

        # Format as context
        context_parts = ["## Relevant Past Experience:\n"]
        for i, (memory, similarity) in enumerate(results, 1):
            context_parts.append(
                f"{i}. [{memory.memory_type.value.upper()}] "
                f"(relevance: {similarity:.2f})\n{memory.content}\n"
            )

        return "\n".join(context_parts)

    # ==================== MEMORY MANAGEMENT ====================

    def update_memory_importance(
        self,
        memory_id: int,
        new_importance: float
    ) -> AgentMemory:
        """
        Update memory importance

        Args:
            memory_id: Memory ID
            new_importance: New importance score (0-1)

        Returns:
            Updated AgentMemory
        """
        memory = self.db.query(AgentMemory).filter(
            AgentMemory.id == memory_id
        ).first()

        if not memory:
            raise ValueError(f"Memory {memory_id} not found")

        memory.importance = max(0.0, min(1.0, new_importance))
        self.db.commit()
        self.db.refresh(memory)

        return memory

    def decay_memories(self, agent_id: int):
        """
        Apply decay to episodic memories

        Reduces importance of old, rarely accessed memories.

        Args:
            agent_id: Agent ID
        """
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return

        # Get episodic memories
        memories = self.db.query(AgentMemory).filter(
            AgentMemory.agent_id == agent_id,
            AgentMemory.memory_type == MemoryType.EPISODIC
        ).all()

        now = datetime.utcnow()

        for memory in memories:
            # Calculate age in days
            age_days = (now - memory.created_at).days

            # Calculate decay factor
            # Memories decay faster if rarely accessed
            access_factor = 1.0 / (1.0 + memory.access_count)
            age_factor = age_days / 30.0  # 30 days = full decay cycle

            decay_amount = memory.decay_rate * age_factor * access_factor

            # Apply decay
            new_importance = max(0.0, memory.importance - decay_amount)
            memory.importance = new_importance

            # Delete if importance drops too low
            if new_importance < 0.1:
                self.db.delete(memory)

        self.db.commit()

    def cleanup_expired_memories(self, agent_id: Optional[int] = None):
        """
        Delete expired memories

        Args:
            agent_id: Agent ID (optional, if None cleans all agents)
        """
        query = self.db.query(AgentMemory).filter(
            AgentMemory.expires_at < datetime.utcnow()
        )

        if agent_id:
            query = query.filter(AgentMemory.agent_id == agent_id)

        expired_memories = query.all()

        for memory in expired_memories:
            self.db.delete(memory)

        self.db.commit()

    def consolidate_memories(self, agent_id: int):
        """
        Consolidate similar memories

        Finds similar memories and merges them to reduce redundancy.

        Args:
            agent_id: Agent ID
        """
        # Get all memories with embeddings
        memories = self.db.query(AgentMemory).filter(
            AgentMemory.agent_id == agent_id,
            AgentMemory.embedding.isnot(None)
        ).all()

        if len(memories) < 2:
            return

        # Find similar pairs (similarity > 0.9)
        to_merge = []
        for i, mem1 in enumerate(memories):
            for mem2 in memories[i+1:]:
                similarity = self._cosine_similarity(mem1.embedding, mem2.embedding)
                if similarity > 0.9:
                    to_merge.append((mem1, mem2, similarity))

        # Merge similar memories
        for mem1, mem2, similarity in to_merge:
            # Keep the more important one
            if mem1.importance >= mem2.importance:
                keeper, delete = mem1, mem2
            else:
                keeper, delete = mem2, mem1

            # Boost keeper's importance
            keeper.importance = min(1.0, keeper.importance + delete.importance * 0.3)
            keeper.access_count += delete.access_count

            # Merge context
            keeper.context = {**keeper.context, **delete.context}

            # Delete redundant memory
            self.db.delete(delete)

        self.db.commit()

    # ==================== STATISTICS ====================

    def get_memory_statistics(self, agent_id: int) -> Dict[str, Any]:
        """
        Get memory statistics for agent

        Args:
            agent_id: Agent ID

        Returns:
            Statistics dictionary
        """
        total_memories = self.db.query(func.count(AgentMemory.id)).filter(
            AgentMemory.agent_id == agent_id
        ).scalar()

        # Count by type
        type_counts = {}
        for memory_type in MemoryType:
            count = self.db.query(func.count(AgentMemory.id)).filter(
                AgentMemory.agent_id == agent_id,
                AgentMemory.memory_type == memory_type
            ).scalar()
            type_counts[memory_type.value] = count

        # Average importance
        avg_importance = self.db.query(func.avg(AgentMemory.importance)).filter(
            AgentMemory.agent_id == agent_id
        ).scalar()

        # Most accessed
        most_accessed = self.db.query(AgentMemory).filter(
            AgentMemory.agent_id == agent_id
        ).order_by(desc(AgentMemory.access_count)).limit(5).all()

        return {
            "total_memories": total_memories,
            "type_counts": type_counts,
            "average_importance": float(avg_importance) if avg_importance else 0.0,
            "most_accessed": [
                {
                    "id": m.id,
                    "content": m.content[:100] + "..." if len(m.content) > 100 else m.content,
                    "access_count": m.access_count,
                    "importance": m.importance
                }
                for m in most_accessed
            ]
        }

    # ==================== EMBEDDING UTILITIES ====================

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for text

        In production, this would use OpenAI's embedding API or similar.
        For now, using a simple hash-based placeholder.

        Args:
            text: Text to embed

        Returns:
            Vector embedding (list of floats)
        """
        # TODO: Integrate with actual embedding service (OpenAI, Cohere, etc.)
        # This is a placeholder that generates deterministic fake embeddings

        # Use hash for deterministic "embedding"
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert to list of floats (normalized to [-1, 1])
        embedding = [
            (byte - 128) / 128.0
            for byte in hash_bytes[:128]  # 128-dimensional embedding
        ]

        # Pad to 128 dimensions if needed
        while len(embedding) < 128:
            embedding.append(0.0)

        return embedding

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score (0-1)
        """
        if len(vec1) != len(vec2):
            return 0.0

        # Dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))

        # Magnitudes
        mag1 = sum(a * a for a in vec1) ** 0.5
        mag2 = sum(b * b for b in vec2) ** 0.5

        if mag1 == 0 or mag2 == 0:
            return 0.0

        # Cosine similarity
        similarity = dot_product / (mag1 * mag2)

        # Normalize to [0, 1]
        return (similarity + 1.0) / 2.0
