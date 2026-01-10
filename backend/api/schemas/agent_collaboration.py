"""
Agent Collaboration API Schemas

Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== ENUMS ====================

class AgentTypeEnum(str, Enum):
    PLOTTING = "plotting"
    CHARACTER = "character"
    DIALOGUE = "dialogue"
    CONTINUITY = "continuity"
    QC = "qc"
    PACING = "pacing"
    THEME = "theme"
    WORLDBUILDING = "worldbuilding"
    CUSTOM = "custom"


class AgentRoleEnum(str, Enum):
    LEADER = "leader"
    CONTRIBUTOR = "contributor"
    REVIEWER = "reviewer"
    OBSERVER = "observer"


class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class TaskPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MemoryTypeEnum(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    FEEDBACK = "feedback"


class ConflictResolutionStrategyEnum(str, Enum):
    VOTING = "voting"
    HIERARCHY = "hierarchy"
    USER_CHOICE = "user_choice"
    CONSENSUS = "consensus"
    AI_JUDGE = "ai_judge"


# ==================== AGENT SCHEMAS ====================

class CreateAgentRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Agent name")
    agent_type: AgentTypeEnum = Field(..., description="Type of agent")
    role: AgentRoleEnum = Field(AgentRoleEnum.CONTRIBUTOR, description="Agent role")
    description: Optional[str] = Field(None, description="Agent description")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt")
    model_name: str = Field("claude-sonnet-4", description="AI model to use")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature")
    max_tokens: int = Field(4000, ge=100, le=100000, description="Max tokens")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    config: Dict[str, Any] = Field(default_factory=dict, description="Additional config")


class UpdateAgentRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    is_active: Optional[bool] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=100, le=100000)
    config: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    id: int
    project_id: int
    name: str
    agent_type: str
    role: str
    description: Optional[str]
    is_active: bool
    is_busy: bool
    tasks_completed: int
    tasks_failed: int
    user_satisfaction_score: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentDetailResponse(AgentResponse):
    system_prompt: Optional[str]
    model_name: str
    temperature: float
    max_tokens: int
    capabilities: List[str]
    current_task_id: Optional[int]
    average_completion_time: Optional[float]
    enable_memory: bool
    memory_window: int
    config: Dict[str, Any]


# ==================== TASK SCHEMAS ====================

class CreateTaskRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: str = Field(..., min_length=1, description="Task description")
    task_type: Optional[str] = Field(None, max_length=100, description="Task type")
    priority: TaskPriorityEnum = Field(TaskPriorityEnum.MEDIUM, description="Priority")
    context: Dict[str, Any] = Field(default_factory=dict, description="Task context")
    depends_on: List[int] = Field(default_factory=list, description="Dependency task IDs")
    deadline: Optional[datetime] = Field(None, description="Task deadline")
    auto_assign: bool = Field(True, description="Auto-assign to best agent")


class UpdateTaskRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=1)
    priority: Optional[TaskPriorityEnum] = None
    deadline: Optional[datetime] = None
    context: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    id: int
    project_id: int
    agent_id: Optional[int]
    title: str
    description: str
    task_type: Optional[str]
    status: str
    priority: str
    assigned_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    deadline: Optional[datetime]
    user_approved: Optional[bool]
    user_rating: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskDetailResponse(TaskResponse):
    context: Dict[str, Any]
    depends_on: List[int]
    blocks_tasks: List[int]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    retry_count: int
    max_retries: int
    user_feedback: Optional[str]
    metadata: Dict[str, Any]


class AssignTaskRequest(BaseModel):
    agent_id: int = Field(..., description="Agent ID to assign task to")


class CompleteTaskRequest(BaseModel):
    result: Optional[Dict[str, Any]] = Field(None, description="Task result")
    user_feedback: Optional[str] = Field(None, description="User feedback")
    user_rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Rating (0-5)")


class FailTaskRequest(BaseModel):
    error_message: str = Field(..., min_length=1, description="Error description")
    auto_retry: bool = Field(True, description="Automatically retry")


class TaskQueueResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    pending_count: int
    in_progress_count: int
    completed_count: int


# ==================== CONVERSATION SCHEMAS ====================

class CreateConversationRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="Conversation title")
    topic: Optional[str] = Field(None, max_length=200, description="Topic")
    participant_agent_ids: List[int] = Field(..., min_items=2, description="Participating agent IDs")
    moderator_agent_id: Optional[int] = Field(None, description="Moderator agent ID")
    related_task_id: Optional[int] = Field(None, description="Related task ID")
    related_chapter_id: Optional[int] = Field(None, description="Related chapter ID")
    related_character_ids: List[int] = Field(default_factory=list, description="Related character IDs")


class AddMessageRequest(BaseModel):
    agent_id: int = Field(..., description="Agent sending message")
    content: str = Field(..., min_length=1, description="Message content")
    message_type: str = Field("comment", description="Message type")
    is_suggestion: bool = Field(False, description="Is this a suggestion")
    suggestion_data: Optional[Dict[str, Any]] = Field(None, description="Suggestion data")
    reply_to_message_id: Optional[int] = Field(None, description="Reply to message ID")


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    agent_id: Optional[int]
    content: str
    message_type: str
    is_suggestion: bool
    suggestion_data: Optional[Dict[str, Any]]
    reply_to_message_id: Optional[int]
    reactions: Dict[str, List[int]]
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    project_id: int
    title: str
    topic: Optional[str]
    participant_agent_ids: List[int]
    moderator_agent_id: Optional[int]
    is_active: bool
    is_resolved: bool
    has_conflict: bool
    started_at: datetime
    ended_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageResponse]
    resolution_summary: Optional[str]
    conflict_type: Optional[str]
    resolution_strategy: Optional[str]
    voting_options: Optional[List[Dict[str, Any]]]


class InitiateVotingRequest(BaseModel):
    voting_options: List[Dict[str, Any]] = Field(..., min_items=2, description="Voting options")
    voting_deadline: Optional[datetime] = Field(None, description="Voting deadline")
    resolution_strategy: ConflictResolutionStrategyEnum = Field(
        ConflictResolutionStrategyEnum.VOTING,
        description="Resolution strategy"
    )


class CastVoteRequest(BaseModel):
    agent_id: int = Field(..., description="Agent casting vote")
    option_id: int = Field(..., description="Option ID")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence")
    reasoning: Optional[str] = Field(None, description="Reasoning")


class VoteResponse(BaseModel):
    id: int
    conversation_id: int
    agent_id: int
    option_id: int
    confidence: Optional[float]
    reasoning: Optional[str]
    vote_weight: float
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== MEMORY SCHEMAS ====================

class CreateMemoryRequest(BaseModel):
    content: str = Field(..., min_length=1, description="Memory content")
    memory_type: MemoryTypeEnum = Field(..., description="Memory type")
    importance: float = Field(0.5, ge=0.0, le=1.0, description="Importance (0-1)")
    source_type: Optional[str] = Field(None, max_length=100, description="Source type")
    source_id: Optional[int] = Field(None, description="Source ID")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context")


class SearchMemoriesRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    memory_type: Optional[MemoryTypeEnum] = Field(None, description="Filter by type")
    limit: int = Field(10, ge=1, le=100, description="Max results")


class MemoryResponse(BaseModel):
    id: int
    agent_id: int
    project_id: int
    memory_type: str
    content: str
    importance: float
    access_count: int
    last_accessed_at: Optional[datetime]
    source_type: Optional[str]
    source_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class MemorySearchResult(BaseModel):
    memory: MemoryResponse
    similarity_score: float


class MemorySearchResponse(BaseModel):
    results: List[MemorySearchResult]
    total: int


# ==================== STATISTICS SCHEMAS ====================

class TaskStatisticsResponse(BaseModel):
    total_tasks: int
    status_counts: Dict[str, int]
    priority_counts: Dict[str, int]
    average_completion_time: Optional[float]
    overdue_tasks: int


class AgentStatisticsResponse(BaseModel):
    agent_name: str
    agent_type: str
    is_active: bool
    is_busy: bool
    tasks_completed: int
    tasks_failed: int
    active_tasks: int
    average_completion_time: Optional[float]
    user_satisfaction_score: Optional[float]
    success_rate: float


class ProjectAgentStatisticsResponse(BaseModel):
    total_agents: int
    active_agents: int
    busy_agents: int
    agents_by_type: Dict[str, int]
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    average_satisfaction: Optional[float]


class MemoryStatisticsResponse(BaseModel):
    total_memories: int
    type_counts: Dict[str, int]
    average_importance: float
    most_accessed: List[Dict[str, Any]]


# ==================== BATCH OPERATIONS ====================

class CreateBatchTasksRequest(BaseModel):
    tasks: List[CreateTaskRequest] = Field(..., min_items=1, max_items=50, description="Tasks to create")
    auto_assign: bool = Field(True, description="Auto-assign tasks")


class BatchTasksResponse(BaseModel):
    tasks: List[TaskResponse]
    total_created: int
    total_assigned: int


# ==================== WORKFLOW SCHEMAS ====================

class CreateWorkflowRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Workflow name")
    description: Optional[str] = Field(None, description="Description")
    tasks: List[CreateTaskRequest] = Field(..., min_items=1, description="Workflow tasks")


class WorkflowResponse(BaseModel):
    workflow_name: str
    total_tasks: int
    tasks: List[TaskResponse]
