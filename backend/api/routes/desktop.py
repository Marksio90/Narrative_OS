"""
Desktop API Routes

Narrative OS Desktop - central hub endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from core.database.base import get_db
from core.auth.config import current_active_user
from core.models.user import User

router = APIRouter()


# ===== Schemas =====

class WritingStats(BaseModel):
    """Writing statistics"""
    today_words: int = 0
    week_words: int = 0
    month_words: int = 0
    year_words: int = 0
    streak_days: int = 0
    total_words: int = 0
    chapters_completed: int = 0
    avg_words_per_day: float = 0.0
    best_day_words: int = 0
    total_sessions: int = 0


class DailyActivity(BaseModel):
    """Daily writing activity"""
    date: str
    words_written: int
    minutes_spent: int
    chapters_worked: int
    ai_generations: int


class ProjectSummary(BaseModel):
    """Project summary"""
    id: int
    name: str
    description: Optional[str]
    genre: Optional[str]
    target_words: int
    current_words: int
    progress_percent: float
    last_updated: datetime
    chapters_count: int
    characters_count: int
    locations_count: int
    status: str  # planning, drafting, editing, complete


class RecentActivity(BaseModel):
    """Recent activity item"""
    id: int
    type: str  # chapter_created, character_added, ai_generation, export, etc.
    description: str
    timestamp: datetime
    project_id: int
    metadata: dict


class QuickAction(BaseModel):
    """Quick action definition"""
    id: str
    label: str
    description: str
    icon: str
    route: str
    shortcut: str
    category: str  # writing, canon, ai, analysis


class DashboardResponse(BaseModel):
    """Full dashboard data"""
    stats: WritingStats
    projects: List[ProjectSummary]
    recent_activity: List[RecentActivity]
    daily_activity: List[DailyActivity]
    quick_actions: List[QuickAction]


# ===== Endpoints =====

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get full dashboard data

    Returns everything needed for Desktop view:
    - Writing statistics (today, week, month, streak)
    - All user projects with progress
    - Recent activity feed
    - Daily activity chart data
    - Quick actions list
    """
    # Mock data for now - replace with real database queries

    stats = WritingStats(
        today_words=1250,
        week_words=7890,
        month_words=28450,
        year_words=145230,
        streak_days=12,
        total_words=245830,
        chapters_completed=8,
        avg_words_per_day=982,
        best_day_words=3450,
        total_sessions=156
    )

    projects = [
        ProjectSummary(
            id=1,
            name="Mroczna Forteca",
            description="Epicka fantasy o magicznej twierdzy",
            genre="Fantasy",
            target_words=100000,
            current_words=45230,
            progress_percent=45.23,
            last_updated=datetime.now(),
            chapters_count=12,
            characters_count=15,
            locations_count=8,
            status="drafting"
        )
    ]

    recent_activity = [
        RecentActivity(
            id=1,
            type="character_added",
            description='Dodano postać "Elara Shadowblade"',
            timestamp=datetime.now() - timedelta(hours=2),
            project_id=1,
            metadata={"character_id": 42, "character_name": "Elara Shadowblade"}
        ),
        RecentActivity(
            id=2,
            type="chapter_completed",
            description="Ukończono rozdział 8: Bitwa o Cytadelę",
            timestamp=datetime.now() - timedelta(hours=5),
            project_id=1,
            metadata={"chapter_id": 8, "words": 3450}
        ),
        RecentActivity(
            id=3,
            type="ai_consistency_check",
            description="AI sprawdził spójność fabuły - 3 ostrzeżenia",
            timestamp=datetime.now() - timedelta(days=1),
            project_id=1,
            metadata={"issues_count": 3, "score": 92}
        ),
        RecentActivity(
            id=4,
            type="canon_export",
            description="Eksport biblii fabuły do JSON",
            timestamp=datetime.now() - timedelta(days=2),
            project_id=1,
            metadata={"format": "json", "entities": 45}
        )
    ]

    # Generate daily activity for past 7 days
    daily_activity = []
    for i in range(7):
        date = datetime.now() - timedelta(days=6-i)
        daily_activity.append(
            DailyActivity(
                date=date.strftime("%Y-%m-%d"),
                words_written=int(500 + (i * 200) + (i % 2) * 300),
                minutes_spent=int(45 + (i * 15)),
                chapters_worked=1 if i > 2 else 0,
                ai_generations=i % 3
            )
        )

    quick_actions = [
        QuickAction(
            id="new_chapter",
            label="Nowy Rozdział",
            description="Rozpocznij pisanie nowego rozdziału",
            icon="FileText",
            route="/chapters/new",
            shortcut="Ctrl+N",
            category="writing"
        ),
        QuickAction(
            id="story_bible",
            label="Biblia Fabuły",
            description="Zarządzaj kanonem i postaciami",
            icon="Book",
            route="/story-bible",
            shortcut="Ctrl+B",
            category="canon"
        ),
        QuickAction(
            id="ai_assistant",
            label="AI Asystent",
            description="Generuj tekst i sprawdzaj spójność",
            icon="Sparkles",
            route="/ai-tools",
            shortcut="Ctrl+K",
            category="ai"
        ),
        QuickAction(
            id="analytics",
            label="Statystyki",
            description="Analizuj postępy i produktywność",
            icon="BarChart3",
            route="/analytics",
            shortcut="Ctrl+A",
            category="analysis"
        ),
        QuickAction(
            id="relationships",
            label="Graf Relacji",
            description="Wizualizuj relacje między postaciami",
            icon="Network",
            route="/story-bible?tab=graph",
            shortcut="Ctrl+R",
            category="canon"
        ),
        QuickAction(
            id="timeline",
            label="Oś Czasu",
            description="Zarządzaj chronologią wydarzeń",
            icon="Clock",
            route="/story-bible?tab=timeline",
            shortcut="Ctrl+T",
            category="canon"
        )
    ]

    return DashboardResponse(
        stats=stats,
        projects=projects,
        recent_activity=recent_activity,
        daily_activity=daily_activity,
        quick_actions=quick_actions
    )


@router.get("/stats", response_model=WritingStats)
async def get_writing_stats(
    project_id: Optional[int] = Query(None, description="Filter by project"),
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed writing statistics

    Optionally filter by project_id
    """
    # Mock data - replace with real calculations from database
    return WritingStats(
        today_words=1250,
        week_words=7890,
        month_words=28450,
        year_words=145230,
        streak_days=12,
        total_words=245830,
        chapters_completed=8,
        avg_words_per_day=982,
        best_day_words=3450,
        total_sessions=156
    )


@router.get("/activity", response_model=List[RecentActivity])
async def get_recent_activity(
    project_id: Optional[int] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get recent activity feed

    Returns chronological list of user actions
    """
    # Mock data - replace with real activity log
    return [
        RecentActivity(
            id=1,
            type="character_added",
            description='Dodano postać "Elara Shadowblade"',
            timestamp=datetime.now() - timedelta(hours=2),
            project_id=1,
            metadata={"character_id": 42}
        ),
        RecentActivity(
            id=2,
            type="chapter_completed",
            description="Ukończono rozdział 8",
            timestamp=datetime.now() - timedelta(hours=5),
            project_id=1,
            metadata={"chapter_id": 8, "words": 3450}
        )
    ]


@router.get("/projects", response_model=List[ProjectSummary])
async def get_user_projects(
    status: Optional[str] = Query(None, description="Filter by status"),
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all user projects with summary info
    """
    # Mock data - replace with real project queries
    return [
        ProjectSummary(
            id=1,
            name="Mroczna Forteca",
            description="Epicka fantasy o magicznej twierdzy",
            genre="Fantasy",
            target_words=100000,
            current_words=45230,
            progress_percent=45.23,
            last_updated=datetime.now(),
            chapters_count=12,
            characters_count=15,
            locations_count=8,
            status="drafting"
        )
    ]


@router.post("/track-session")
async def track_writing_session(
    words_written: int,
    minutes_spent: int,
    chapter_id: Optional[int] = None,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """
    Track a writing session

    Updates daily statistics and streak calculation
    """
    # In real implementation:
    # 1. Update daily_stats table
    # 2. Recalculate streak
    # 3. Update chapter word count if chapter_id provided
    # 4. Log activity

    return {
        "success": True,
        "message": f"Sesja zapisana: {words_written} słów w {minutes_spent} minut",
        "new_streak": 12
    }
