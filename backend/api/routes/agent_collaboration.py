"""
Agent Collaboration API Routes

REST endpoints for multi-agent collaboration system
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.database import get_db
from backend.core.models import (
    Agent, AgentTask, AgentConversation, AgentMessage,
    AgentMemory, AgentVote, AgentType, TaskStatus
)
from backend.services.agent_orchestration_service import AgentOrchestrationService
from backend.services.agent_memory_service import AgentMemoryService
from backend.services.specialized_agents import AgentFactory
from backend.api.schemas.agent_collaboration import *


router = APIRouter()


# ==================== DEPENDENCY INJECTION ====================

def get_orchestration_service(db: Session = Depends(get_db)) -> AgentOrchestrationService:
    return AgentOrchestrationService(db)


def get_memory_service(db: Session = Depends(get_db)) -> AgentMemoryService:
    return AgentMemoryService(db)


# ==================== AGENT MANAGEMENT ====================

@router.post("/projects/{project_id}/agents", response_model=AgentDetailResponse, status_code=201)
async def create_agent(
    project_id: int,
    request: CreateAgentRequest,
    db: Session = Depends(get_db)
):
    """
    Create new AI agent

    Creates a specialized AI agent with configured capabilities.
    """
    agent = Agent(
        project_id=project_id,
        name=request.name,
        agent_type=request.agent_type.value,
        role=request.role.value,
        description=request.description,
        system_prompt=request.system_prompt,
        model_name=request.model_name,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        capabilities=request.capabilities,
        config=request.config
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return agent


@router.get("/projects/{project_id}/agents", response_model=List[AgentResponse])
async def list_agents(
    project_id: int,
    agent_type: Optional[AgentTypeEnum] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    List all agents for project

    Filter by agent type and active status.
    """
    query = db.query(Agent).filter(Agent.project_id == project_id)

    if agent_type:
        query = query.filter(Agent.agent_type == agent_type.value)

    if is_active is not None:
        query = query.filter(Agent.is_active == is_active)

    agents = query.all()
    return agents


@router.get("/projects/{project_id}/agents/{agent_id}", response_model=AgentDetailResponse)
async def get_agent(
    project_id: int,
    agent_id: int,
    db: Session = Depends(get_db)
):
    """Get agent details"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.project_id == project_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent


@router.patch("/projects/{project_id}/agents/{agent_id}", response_model=AgentDetailResponse)
async def update_agent(
    project_id: int,
    agent_id: int,
    request: UpdateAgentRequest,
    db: Session = Depends(get_db)
):
    """Update agent configuration"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.project_id == project_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Update fields
    if request.name is not None:
        agent.name = request.name
    if request.description is not None:
        agent.description = request.description
    if request.system_prompt is not None:
        agent.system_prompt = request.system_prompt
    if request.is_active is not None:
        agent.is_active = request.is_active
    if request.temperature is not None:
        agent.temperature = request.temperature
    if request.max_tokens is not None:
        agent.max_tokens = request.max_tokens
    if request.config is not None:
        agent.config = request.config

    db.commit()
    db.refresh(agent)

    return agent


@router.delete("/projects/{project_id}/agents/{agent_id}", status_code=204)
async def delete_agent(
    project_id: int,
    agent_id: int,
    db: Session = Depends(get_db)
):
    """Delete agent"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.project_id == project_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    db.delete(agent)
    db.commit()


@router.get("/projects/{project_id}/agents/{agent_id}/statistics", response_model=AgentStatisticsResponse)
async def get_agent_statistics(
    project_id: int,
    agent_id: int,
    service: AgentOrchestrationService = Depends(get_orchestration_service)
):
    """Get agent performance statistics"""
    stats = service.get_agent_statistics(agent_id)

    if not stats:
        raise HTTPException(status_code=404, detail="Agent not found")

    return stats


@router.post("/projects/{project_id}/agents/initialize", response_model=List[AgentResponse])
async def initialize_default_agents(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Initialize default agent team

    Creates a standard set of agents for the project:
    - Plotting Agent
    - Character Agent
    - Dialogue Agent
    - Continuity Agent
    - QC Agent
    """
    default_agents = [
        {
            "name": "Plot Master",
            "agent_type": AgentType.PLOTTING,
            "description": "Analyzes and develops plot structure"
        },
        {
            "name": "Character Developer",
            "agent_type": AgentType.CHARACTER,
            "description": "Develops character arcs and motivations"
        },
        {
            "name": "Dialogue Specialist",
            "agent_type": AgentType.DIALOGUE,
            "description": "Reviews and writes dialogue"
        },
        {
            "name": "Continuity Checker",
            "agent_type": AgentType.CONTINUITY,
            "description": "Ensures story consistency"
        },
        {
            "name": "Quality Controller",
            "agent_type": AgentType.QC,
            "description": "Reviews overall quality"
        }
    ]

    created_agents = []
    for agent_data in default_agents:
        agent = Agent(
            project_id=project_id,
            name=agent_data["name"],
            agent_type=agent_data["agent_type"],
            description=agent_data["description"]
        )
        db.add(agent)
        created_agents.append(agent)

    db.commit()

    for agent in created_agents:
        db.refresh(agent)

    return created_agents


# ==================== TASK MANAGEMENT ====================

@router.post("/projects/{project_id}/tasks", response_model=TaskDetailResponse, status_code=201)
async def create_task(
    project_id: int,
    request: CreateTaskRequest,
    service: AgentOrchestrationService = Depends(get_orchestration_service)
):
    """Create new task for agents"""
    task = service.create_task(
        project_id=project_id,
        title=request.title,
        description=request.description,
        task_type=request.task_type,
        priority=request.priority,
        context=request.context,
        depends_on=request.depends_on,
        deadline=request.deadline,
        auto_assign=request.auto_assign
    )

    return task


@router.post("/projects/{project_id}/tasks/batch", response_model=BatchTasksResponse)
async def create_batch_tasks(
    project_id: int,
    request: CreateBatchTasksRequest,
    service: AgentOrchestrationService = Depends(get_orchestration_service)
):
    """Create multiple tasks in batch"""
    tasks_data = [
        {
            "title": task.title,
            "description": task.description,
            "task_type": task.task_type,
            "priority": task.priority,
            "context": task.context,
            "depends_on": task.depends_on,
            "deadline": task.deadline
        }
        for task in request.tasks
    ]

    created_tasks = service.create_batch_tasks(
        project_id=project_id,
        tasks_data=tasks_data,
        auto_assign=request.auto_assign
    )

    total_assigned = sum(1 for task in created_tasks if task.agent_id is not None)

    return {
        "tasks": created_tasks,
        "total_created": len(created_tasks),
        "total_assigned": total_assigned
    }


@router.get("/projects/{project_id}/tasks", response_model=TaskQueueResponse)
async def get_task_queue(
    project_id: int,
    agent_id: Optional[int] = None,
    status: Optional[TaskStatusEnum] = None,
    priority: Optional[TaskPriorityEnum] = None,
    limit: int = Query(50, ge=1, le=200),
    service: AgentOrchestrationService = Depends(get_orchestration_service),
    db: Session = Depends(get_db)
):
    """Get task queue with optional filtering"""
    tasks = service.get_task_queue(
        project_id=project_id,
        agent_id=agent_id,
        status=status.value if status else None,
        priority=priority.value if priority else None,
        limit=limit
    )

    # Count by status
    pending_count = db.query(AgentTask).filter(
        AgentTask.project_id == project_id,
        AgentTask.status == TaskStatus.PENDING
    ).count()

    in_progress_count = db.query(AgentTask).filter(
        AgentTask.project_id == project_id,
        AgentTask.status == TaskStatus.IN_PROGRESS
    ).count()

    completed_count = db.query(AgentTask).filter(
        AgentTask.project_id == project_id,
        AgentTask.status == TaskStatus.COMPLETED
    ).count()

    return {
        "tasks": tasks,
        "total": len(tasks),
        "pending_count": pending_count,
        "in_progress_count": in_progress_count,
        "completed_count": completed_count
    }


@router.get("/projects/{project_id}/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db)
):
    """Get task details"""
    task = db.query(AgentTask).filter(
        AgentTask.id == task_id,
        AgentTask.project_id == project_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.patch("/projects/{project_id}/tasks/{task_id}", response_model=TaskDetailResponse)
async def update_task(
    project_id: int,
    task_id: int,
    request: UpdateTaskRequest,
    db: Session = Depends(get_db)
):
    """Update task"""
    task = db.query(AgentTask).filter(
        AgentTask.id == task_id,
        AgentTask.project_id == project_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if request.title is not None:
        task.title = request.title
    if request.description is not None:
        task.description = request.description
    if request.priority is not None:
        task.priority = request.priority
    if request.deadline is not None:
        task.deadline = request.deadline
    if request.context is not None:
        task.context = request.context

    db.commit()
    db.refresh(task)

    return task


@router.delete("/projects/{project_id}/tasks/{task_id}", status_code=204)
async def delete_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db)
):
    """Delete task"""
    task = db.query(AgentTask).filter(
        AgentTask.id == task_id,
        AgentTask.project_id == project_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()


@router.post("/projects/{project_id}/tasks/{task_id}/assign", response_model=TaskDetailResponse)
async def assign_task(
    project_id: int,
    task_id: int,
    request: AssignTaskRequest,
    service: AgentOrchestrationService = Depends(get_orchestration_service)
):
    """Assign task to specific agent"""
    try:
        task = service.assign_task(task_id, request.agent_id)
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/projects/{project_id}/tasks/{task_id}/start", response_model=TaskDetailResponse)
async def start_task(
    project_id: int,
    task_id: int,
    service: AgentOrchestrationService = Depends(get_orchestration_service)
):
    """Start task execution"""
    try:
        task = service.start_task(task_id)
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/projects/{project_id}/tasks/{task_id}/complete", response_model=TaskDetailResponse)
async def complete_task(
    project_id: int,
    task_id: int,
    request: CompleteTaskRequest,
    service: AgentOrchestrationService = Depends(get_orchestration_service)
):
    """Mark task as completed"""
    try:
        task = service.complete_task(
            task_id=task_id,
            result=request.result,
            user_feedback=request.user_feedback,
            user_rating=request.user_rating
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/projects/{project_id}/tasks/{task_id}/fail", response_model=TaskDetailResponse)
async def fail_task(
    project_id: int,
    task_id: int,
    request: FailTaskRequest,
    service: AgentOrchestrationService = Depends(get_orchestration_service)
):
    """Mark task as failed"""
    try:
        task = service.fail_task(
            task_id=task_id,
            error_message=request.error_message,
            auto_retry=request.auto_retry
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects/{project_id}/agents/{agent_id}/next-task", response_model=Optional[TaskDetailResponse])
async def get_next_task(
    project_id: int,
    agent_id: int,
    service: AgentOrchestrationService = Depends(get_orchestration_service)
):
    """Get next task for agent to work on"""
    task = service.get_next_task(agent_id)
    return task


@router.get("/projects/{project_id}/tasks/statistics", response_model=TaskStatisticsResponse)
async def get_task_statistics(
    project_id: int,
    service: AgentOrchestrationService = Depends(get_orchestration_service)
):
    """Get task statistics for project"""
    stats = service.get_task_statistics(project_id)
    return stats


# ==================== CONVERSATION MANAGEMENT ====================

@router.post("/projects/{project_id}/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    project_id: int,
    request: CreateConversationRequest,
    db: Session = Depends(get_db)
):
    """Create multi-agent conversation"""
    conversation = AgentConversation(
        project_id=project_id,
        title=request.title,
        topic=request.topic,
        participant_agent_ids=request.participant_agent_ids,
        moderator_agent_id=request.moderator_agent_id,
        related_task_id=request.related_task_id,
        related_chapter_id=request.related_chapter_id,
        related_character_ids=request.related_character_ids
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.get("/projects/{project_id}/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    project_id: int,
    is_active: Optional[bool] = None,
    is_resolved: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List conversations for project"""
    query = db.query(AgentConversation).filter(
        AgentConversation.project_id == project_id
    )

    if is_active is not None:
        query = query.filter(AgentConversation.is_active == is_active)

    if is_resolved is not None:
        query = query.filter(AgentConversation.is_resolved == is_resolved)

    conversations = query.all()
    return conversations


@router.get("/projects/{project_id}/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    project_id: int,
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get conversation details with messages"""
    conversation = db.query(AgentConversation).filter(
        AgentConversation.id == conversation_id,
        AgentConversation.project_id == project_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


@router.post("/projects/{project_id}/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def add_message(
    project_id: int,
    conversation_id: int,
    request: AddMessageRequest,
    db: Session = Depends(get_db)
):
    """Add message to conversation"""
    conversation = db.query(AgentConversation).filter(
        AgentConversation.id == conversation_id,
        AgentConversation.project_id == project_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    message = AgentMessage(
        conversation_id=conversation_id,
        agent_id=request.agent_id,
        content=request.content,
        message_type=request.message_type,
        is_suggestion=request.is_suggestion,
        suggestion_data=request.suggestion_data,
        reply_to_message_id=request.reply_to_message_id
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


@router.post("/projects/{project_id}/conversations/{conversation_id}/vote", response_model=ConversationDetailResponse)
async def initiate_voting(
    project_id: int,
    conversation_id: int,
    request: InitiateVotingRequest,
    db: Session = Depends(get_db)
):
    """Initiate voting on conflicting suggestions"""
    conversation = db.query(AgentConversation).filter(
        AgentConversation.id == conversation_id,
        AgentConversation.project_id == project_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation.has_conflict = True
    conversation.voting_options = request.voting_options
    conversation.voting_deadline = request.voting_deadline
    conversation.resolution_strategy = request.resolution_strategy

    db.commit()
    db.refresh(conversation)

    return conversation


@router.post("/projects/{project_id}/conversations/{conversation_id}/cast-vote", response_model=VoteResponse)
async def cast_vote(
    project_id: int,
    conversation_id: int,
    request: CastVoteRequest,
    db: Session = Depends(get_db)
):
    """Cast vote on voting option"""
    conversation = db.query(AgentConversation).filter(
        AgentConversation.id == conversation_id,
        AgentConversation.project_id == project_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    vote = AgentVote(
        conversation_id=conversation_id,
        agent_id=request.agent_id,
        option_id=request.option_id,
        confidence=request.confidence,
        reasoning=request.reasoning
    )

    db.add(vote)
    db.commit()
    db.refresh(vote)

    return vote


@router.post("/projects/{project_id}/conversations/{conversation_id}/resolve", response_model=ConversationDetailResponse)
async def resolve_conversation(
    project_id: int,
    conversation_id: int,
    resolution_summary: str,
    db: Session = Depends(get_db)
):
    """Mark conversation as resolved"""
    conversation = db.query(AgentConversation).filter(
        AgentConversation.id == conversation_id,
        AgentConversation.project_id == project_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation.is_resolved = True
    conversation.is_active = False
    conversation.resolution_summary = resolution_summary
    conversation.ended_at = datetime.utcnow()

    db.commit()
    db.refresh(conversation)

    return conversation


# ==================== MEMORY MANAGEMENT ====================

@router.post("/projects/{project_id}/agents/{agent_id}/memories", response_model=MemoryResponse)
async def create_memory(
    project_id: int,
    agent_id: int,
    request: CreateMemoryRequest,
    service: AgentMemoryService = Depends(get_memory_service)
):
    """Create new memory for agent"""
    memory = service.create_memory(
        agent_id=agent_id,
        project_id=project_id,
        content=request.content,
        memory_type=request.memory_type,
        importance=request.importance,
        source_type=request.source_type,
        source_id=request.source_id,
        context=request.context
    )

    return memory


@router.get("/projects/{project_id}/agents/{agent_id}/memories", response_model=List[MemoryResponse])
async def get_memories(
    project_id: int,
    agent_id: int,
    memory_type: Optional[MemoryTypeEnum] = None,
    min_importance: float = Query(0.0, ge=0.0, le=1.0),
    limit: int = Query(50, ge=1, le=200),
    service: AgentMemoryService = Depends(get_memory_service)
):
    """Get memories for agent"""
    memories = service.get_memories(
        agent_id=agent_id,
        memory_type=memory_type,
        min_importance=min_importance,
        limit=limit
    )

    return memories


@router.post("/projects/{project_id}/agents/{agent_id}/memories/search", response_model=MemorySearchResponse)
async def search_memories(
    project_id: int,
    agent_id: int,
    request: SearchMemoriesRequest,
    service: AgentMemoryService = Depends(get_memory_service)
):
    """Search agent memories using semantic similarity"""
    results = service.search_memories(
        agent_id=agent_id,
        query=request.query,
        memory_type=request.memory_type,
        limit=request.limit
    )

    return {
        "results": [
            {"memory": memory, "similarity_score": score}
            for memory, score in results
        ],
        "total": len(results)
    }


@router.get("/projects/{project_id}/agents/{agent_id}/memories/statistics", response_model=MemoryStatisticsResponse)
async def get_memory_statistics(
    project_id: int,
    agent_id: int,
    service: AgentMemoryService = Depends(get_memory_service)
):
    """Get memory statistics for agent"""
    stats = service.get_memory_statistics(agent_id)
    return stats


@router.post("/projects/{project_id}/agents/{agent_id}/memories/cleanup", status_code=204)
async def cleanup_expired_memories(
    project_id: int,
    agent_id: int,
    service: AgentMemoryService = Depends(get_memory_service)
):
    """Delete expired memories for agent"""
    service.cleanup_expired_memories(agent_id)


@router.post("/projects/{project_id}/agents/{agent_id}/memories/consolidate", status_code=204)
async def consolidate_memories(
    project_id: int,
    agent_id: int,
    service: AgentMemoryService = Depends(get_memory_service)
):
    """Consolidate similar memories for agent"""
    service.consolidate_memories(agent_id)


# ==================== PROJECT STATISTICS ====================

@router.get("/projects/{project_id}/agent-collaboration/statistics", response_model=ProjectAgentStatisticsResponse)
async def get_project_statistics(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get overall agent collaboration statistics for project"""
    total_agents = db.query(Agent).filter(Agent.project_id == project_id).count()
    active_agents = db.query(Agent).filter(
        Agent.project_id == project_id,
        Agent.is_active == True
    ).count()
    busy_agents = db.query(Agent).filter(
        Agent.project_id == project_id,
        Agent.is_busy == True
    ).count()

    # Count by type
    agents_by_type = {}
    for agent_type in AgentType:
        count = db.query(Agent).filter(
            Agent.project_id == project_id,
            Agent.agent_type == agent_type
        ).count()
        agents_by_type[agent_type.value] = count

    # Task counts
    total_tasks = db.query(AgentTask).filter(AgentTask.project_id == project_id).count()
    completed_tasks = db.query(AgentTask).filter(
        AgentTask.project_id == project_id,
        AgentTask.status == TaskStatus.COMPLETED
    ).count()
    failed_tasks = db.query(AgentTask).filter(
        AgentTask.project_id == project_id,
        AgentTask.status == TaskStatus.FAILED
    ).count()

    # Average satisfaction
    from sqlalchemy import func
    avg_satisfaction = db.query(func.avg(Agent.user_satisfaction_score)).filter(
        Agent.project_id == project_id,
        Agent.user_satisfaction_score.isnot(None)
    ).scalar()

    return {
        "total_agents": total_agents,
        "active_agents": active_agents,
        "busy_agents": busy_agents,
        "agents_by_type": agents_by_type,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks,
        "average_satisfaction": float(avg_satisfaction) if avg_satisfaction else None
    }
