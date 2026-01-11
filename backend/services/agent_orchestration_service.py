"""
Agent Orchestration Service

Coordinates multi-agent workflows:
- Task routing and delegation
- Dependency management
- Priority queue management
- Agent selection and assignment
- Task lifecycle management
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from core.models import (
    Agent, AgentTask, AgentType, AgentRole,
    TaskStatus, TaskPriority
)


class AgentOrchestrationService:
    """
    Orchestrates multi-agent collaboration workflows

    Handles task creation, routing, delegation, and coordination
    across multiple AI agents.
    """

    def __init__(self, db: Session):
        self.db = db

    # ==================== TASK CREATION ====================

    def create_task(
        self,
        project_id: int,
        title: str,
        description: str,
        task_type: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        depends_on: Optional[List[int]] = None,
        deadline: Optional[datetime] = None,
        auto_assign: bool = True
    ) -> AgentTask:
        """
        Create a new agent task

        Args:
            project_id: Project ID
            title: Task title
            description: Task description
            task_type: Type of task (e.g., "analyze_plot", "develop_character")
            priority: Task priority
            context: Additional context for the task
            depends_on: List of task IDs this task depends on
            deadline: Task deadline
            auto_assign: Automatically assign to best agent

        Returns:
            Created AgentTask
        """
        task = AgentTask(
            project_id=project_id,
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            context=context or {},
            depends_on=depends_on or [],
            deadline=deadline,
            status=TaskStatus.PENDING
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        # Auto-assign to best agent
        if auto_assign:
            best_agent = self._find_best_agent_for_task(task)
            if best_agent:
                self.assign_task(task.id, best_agent.id)

        return task

    def create_batch_tasks(
        self,
        project_id: int,
        tasks_data: List[Dict[str, Any]],
        auto_assign: bool = True
    ) -> List[AgentTask]:
        """
        Create multiple tasks in batch

        Args:
            project_id: Project ID
            tasks_data: List of task data dictionaries
            auto_assign: Automatically assign to best agents

        Returns:
            List of created AgentTasks
        """
        created_tasks = []

        for task_data in tasks_data:
            task = self.create_task(
                project_id=project_id,
                title=task_data["title"],
                description=task_data["description"],
                task_type=task_data.get("task_type"),
                priority=task_data.get("priority", TaskPriority.MEDIUM),
                context=task_data.get("context"),
                depends_on=task_data.get("depends_on"),
                deadline=task_data.get("deadline"),
                auto_assign=auto_assign
            )
            created_tasks.append(task)

        return created_tasks

    # ==================== TASK ASSIGNMENT ====================

    def assign_task(self, task_id: int, agent_id: int) -> AgentTask:
        """
        Assign task to specific agent

        Args:
            task_id: Task ID
            agent_id: Agent ID

        Returns:
            Updated AgentTask
        """
        task = self.db.query(AgentTask).filter(AgentTask.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")

        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        if not agent.is_active:
            raise ValueError(f"Agent {agent_id} is not active")

        # Update task
        task.agent_id = agent_id
        task.status = TaskStatus.ASSIGNED
        task.assigned_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(task)

        return task

    def _find_best_agent_for_task(self, task: AgentTask) -> Optional[Agent]:
        """
        Find best agent for a task based on:
        - Agent type matching task type
        - Agent availability
        - Agent performance history
        - Agent current workload

        Args:
            task: AgentTask to assign

        Returns:
            Best matching Agent or None
        """
        # Map task types to agent types
        task_type_to_agent_type = {
            "analyze_plot": AgentType.PLOTTING,
            "develop_plot": AgentType.PLOTTING,
            "analyze_character": AgentType.CHARACTER,
            "develop_character": AgentType.CHARACTER,
            "write_dialogue": AgentType.DIALOGUE,
            "review_dialogue": AgentType.DIALOGUE,
            "check_continuity": AgentType.CONTINUITY,
            "quality_check": AgentType.QC,
            "analyze_pacing": AgentType.PACING,
            "analyze_theme": AgentType.THEME,
            "check_worldbuilding": AgentType.WORLDBUILDING,
        }

        # Determine required agent type
        required_agent_type = None
        if task.task_type:
            required_agent_type = task_type_to_agent_type.get(task.task_type)

        # Build query
        query = self.db.query(Agent).filter(
            Agent.project_id == task.project_id,
            Agent.is_active == True
        )

        if required_agent_type:
            query = query.filter(Agent.agent_type == required_agent_type)

        # Get all candidate agents
        candidates = query.all()

        if not candidates:
            return None

        # Score each agent
        scored_agents = []
        for agent in candidates:
            score = self._calculate_agent_score(agent, task)
            scored_agents.append((agent, score))

        # Sort by score (highest first)
        scored_agents.sort(key=lambda x: x[1], reverse=True)

        # Return best agent
        return scored_agents[0][0] if scored_agents else None

    def _calculate_agent_score(self, agent: Agent, task: AgentTask) -> float:
        """
        Calculate suitability score for agent-task pairing

        Factors:
        - Agent is busy (-50 points)
        - Agent performance (0-20 points)
        - Agent workload (0-20 points)
        - Task priority match (0-10 points)

        Args:
            agent: Agent to score
            task: Task to assign

        Returns:
            Score (higher is better)
        """
        score = 100.0

        # Penalty if agent is currently busy
        if agent.is_busy:
            score -= 50

        # Bonus for good performance
        if agent.user_satisfaction_score:
            score += agent.user_satisfaction_score * 20

        # Penalty for high workload
        active_tasks = self.db.query(func.count(AgentTask.id)).filter(
            AgentTask.agent_id == agent.id,
            AgentTask.status.in_([TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS])
        ).scalar()

        if active_tasks == 0:
            score += 20  # Bonus for no active tasks
        elif active_tasks <= 2:
            score += 10  # Small bonus for low workload
        elif active_tasks >= 5:
            score -= 20  # Penalty for high workload

        # Bonus for high-priority tasks assigned to leaders
        if task.priority == TaskPriority.CRITICAL and agent.role == AgentRole.LEADER:
            score += 10

        return score

    # ==================== TASK EXECUTION ====================

    def start_task(self, task_id: int) -> AgentTask:
        """
        Mark task as in progress

        Args:
            task_id: Task ID

        Returns:
            Updated AgentTask
        """
        task = self.db.query(AgentTask).filter(AgentTask.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Check dependencies
        if not self._check_dependencies_complete(task):
            raise ValueError(f"Task {task_id} has incomplete dependencies")

        # Update task status
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()

        # Mark agent as busy
        if task.agent_id:
            agent = self.db.query(Agent).filter(Agent.id == task.agent_id).first()
            if agent:
                agent.is_busy = True
                agent.current_task_id = task.id

        self.db.commit()
        self.db.refresh(task)

        return task

    def complete_task(
        self,
        task_id: int,
        result: Optional[Dict[str, Any]] = None,
        user_feedback: Optional[str] = None,
        user_rating: Optional[float] = None
    ) -> AgentTask:
        """
        Mark task as completed

        Args:
            task_id: Task ID
            result: Task result data
            user_feedback: Optional user feedback
            user_rating: Optional user rating (0-5)

        Returns:
            Updated AgentTask
        """
        task = self.db.query(AgentTask).filter(AgentTask.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Update task
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.result = result
        task.user_feedback = user_feedback
        task.user_rating = user_rating

        # Update agent stats
        if task.agent_id:
            agent = self.db.query(Agent).filter(Agent.id == task.agent_id).first()
            if agent:
                agent.is_busy = False
                agent.current_task_id = None
                agent.tasks_completed += 1

                # Update average completion time
                if task.completion_time:
                    if agent.average_completion_time:
                        # Running average
                        agent.average_completion_time = (
                            agent.average_completion_time * 0.8 + task.completion_time * 0.2
                        )
                    else:
                        agent.average_completion_time = task.completion_time

                # Update satisfaction score
                if user_rating is not None:
                    if agent.user_satisfaction_score:
                        # Running average (normalize rating from 0-5 to 0-1)
                        agent.user_satisfaction_score = (
                            agent.user_satisfaction_score * 0.8 + (user_rating / 5.0) * 0.2
                        )
                    else:
                        agent.user_satisfaction_score = user_rating / 5.0

        self.db.commit()
        self.db.refresh(task)

        # Check if any blocked tasks can now start
        self._unblock_dependent_tasks(task_id)

        return task

    def fail_task(
        self,
        task_id: int,
        error_message: str,
        auto_retry: bool = True
    ) -> AgentTask:
        """
        Mark task as failed

        Args:
            task_id: Task ID
            error_message: Error description
            auto_retry: Automatically retry if under max_retries

        Returns:
            Updated AgentTask
        """
        task = self.db.query(AgentTask).filter(AgentTask.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.error_message = error_message
        task.retry_count += 1

        # Update agent stats
        if task.agent_id:
            agent = self.db.query(Agent).filter(Agent.id == task.agent_id).first()
            if agent:
                agent.is_busy = False
                agent.current_task_id = None
                agent.tasks_failed += 1

        # Retry if under limit
        if auto_retry and task.retry_count < task.max_retries:
            task.status = TaskStatus.PENDING
            task.agent_id = None  # Will be reassigned
            task.assigned_at = None

            # Find new agent (avoid previous one)
            best_agent = self._find_best_agent_for_task(task)
            if best_agent and best_agent.id != task.agent_id:
                self.assign_task(task.id, best_agent.id)
        else:
            task.status = TaskStatus.FAILED

        self.db.commit()
        self.db.refresh(task)

        return task

    # ==================== DEPENDENCY MANAGEMENT ====================

    def _check_dependencies_complete(self, task: AgentTask) -> bool:
        """
        Check if all task dependencies are completed

        Args:
            task: AgentTask to check

        Returns:
            True if all dependencies are completed
        """
        if not task.depends_on:
            return True

        completed_count = self.db.query(func.count(AgentTask.id)).filter(
            AgentTask.id.in_(task.depends_on),
            AgentTask.status == TaskStatus.COMPLETED
        ).scalar()

        return completed_count == len(task.depends_on)

    def _unblock_dependent_tasks(self, completed_task_id: int):
        """
        Unblock tasks that were waiting for this task

        Args:
            completed_task_id: ID of completed task
        """
        # Find all tasks that depend on this one
        blocked_tasks = self.db.query(AgentTask).filter(
            AgentTask.status == TaskStatus.BLOCKED
        ).all()

        for task in blocked_tasks:
            if completed_task_id in task.depends_on:
                # Check if all dependencies are now complete
                if self._check_dependencies_complete(task):
                    task.status = TaskStatus.PENDING

                    # Auto-assign if possible
                    best_agent = self._find_best_agent_for_task(task)
                    if best_agent:
                        self.assign_task(task.id, best_agent.id)

        self.db.commit()

    # ==================== QUEUE MANAGEMENT ====================

    def get_task_queue(
        self,
        project_id: int,
        agent_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        limit: int = 50
    ) -> List[AgentTask]:
        """
        Get task queue with optional filtering

        Args:
            project_id: Project ID
            agent_id: Filter by agent (optional)
            status: Filter by status (optional)
            priority: Filter by priority (optional)
            limit: Max tasks to return

        Returns:
            List of AgentTasks sorted by priority and deadline
        """
        query = self.db.query(AgentTask).filter(
            AgentTask.project_id == project_id
        )

        if agent_id:
            query = query.filter(AgentTask.agent_id == agent_id)

        if status:
            query = query.filter(AgentTask.status == status)

        if priority:
            query = query.filter(AgentTask.priority == priority)

        # Sort by priority (critical first) then deadline
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }

        tasks = query.limit(limit).all()

        # Sort in Python for complex sorting
        tasks.sort(key=lambda t: (
            priority_order.get(t.priority, 999),
            t.deadline if t.deadline else datetime.max,
            t.created_at
        ))

        return tasks

    def get_next_task(self, agent_id: int) -> Optional[AgentTask]:
        """
        Get next task for agent to work on

        Args:
            agent_id: Agent ID

        Returns:
            Next AgentTask or None
        """
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return None

        # Get assigned tasks for this agent
        tasks = self.get_task_queue(
            project_id=agent.project_id,
            agent_id=agent_id,
            status=TaskStatus.ASSIGNED,
            limit=10
        )

        # Return highest priority task with satisfied dependencies
        for task in tasks:
            if self._check_dependencies_complete(task):
                return task

        return None

    # ==================== STATISTICS ====================

    def get_task_statistics(self, project_id: int) -> Dict[str, Any]:
        """
        Get task statistics for project

        Args:
            project_id: Project ID

        Returns:
            Statistics dictionary
        """
        total_tasks = self.db.query(func.count(AgentTask.id)).filter(
            AgentTask.project_id == project_id
        ).scalar()

        # Count by status
        status_counts = {}
        for status in TaskStatus:
            count = self.db.query(func.count(AgentTask.id)).filter(
                AgentTask.project_id == project_id,
                AgentTask.status == status
            ).scalar()
            status_counts[status.value] = count

        # Count by priority
        priority_counts = {}
        for priority in TaskPriority:
            count = self.db.query(func.count(AgentTask.id)).filter(
                AgentTask.project_id == project_id,
                AgentTask.priority == priority
            ).scalar()
            priority_counts[priority.value] = count

        # Average completion time
        avg_completion = self.db.query(func.avg(
            func.extract('epoch', AgentTask.completed_at - AgentTask.started_at)
        )).filter(
            AgentTask.project_id == project_id,
            AgentTask.status == TaskStatus.COMPLETED,
            AgentTask.started_at.isnot(None),
            AgentTask.completed_at.isnot(None)
        ).scalar()

        # Overdue tasks
        overdue_count = self.db.query(func.count(AgentTask.id)).filter(
            AgentTask.project_id == project_id,
            AgentTask.status.in_([TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]),
            AgentTask.deadline < datetime.utcnow()
        ).scalar()

        return {
            "total_tasks": total_tasks,
            "status_counts": status_counts,
            "priority_counts": priority_counts,
            "average_completion_time": avg_completion,
            "overdue_tasks": overdue_count
        }

    def get_agent_statistics(self, agent_id: int) -> Dict[str, Any]:
        """
        Get statistics for specific agent

        Args:
            agent_id: Agent ID

        Returns:
            Agent statistics dictionary
        """
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return {}

        active_tasks = self.db.query(func.count(AgentTask.id)).filter(
            AgentTask.agent_id == agent_id,
            AgentTask.status.in_([TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS])
        ).scalar()

        return {
            "agent_name": agent.name,
            "agent_type": agent.agent_type.value,
            "is_active": agent.is_active,
            "is_busy": agent.is_busy,
            "tasks_completed": agent.tasks_completed,
            "tasks_failed": agent.tasks_failed,
            "active_tasks": active_tasks,
            "average_completion_time": agent.average_completion_time,
            "user_satisfaction_score": agent.user_satisfaction_score,
            "success_rate": (
                agent.tasks_completed / (agent.tasks_completed + agent.tasks_failed)
                if (agent.tasks_completed + agent.tasks_failed) > 0 else 0
            )
        }
