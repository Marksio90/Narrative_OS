"""
Project Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import datetime

from core.database.base import get_db
from core.auth.config import current_active_user
from core.models.user import User
from core.models.base import Project
from core.models.canon import Character, Location, Thread, Promise, Event, MagicRule
from api.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectStats,
    ProjectDuplicateRequest,
    ProjectArchiveRequest,
    ProjectTransferRequest,
)

router = APIRouter()


def get_project_stats(db: Session, project_id: int) -> ProjectStats:
    """Calculate project statistics"""

    # Count entities
    characters_count = db.query(func.count(Character.id)).filter(
        Character.project_id == project_id
    ).scalar() or 0

    locations_count = db.query(func.count(Location.id)).filter(
        Location.project_id == project_id
    ).scalar() or 0

    threads_count = db.query(func.count(Thread.id)).filter(
        Thread.project_id == project_id
    ).scalar() or 0

    promises_count = db.query(func.count(Promise.id)).filter(
        Promise.project_id == project_id
    ).scalar() or 0

    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        return ProjectStats()

    # Calculate word count from metadata (mock for now)
    current_word_count = project.metadata.get("current_word_count", 0)

    # Calculate completion
    completion_percent = 0.0
    if project.target_word_count > 0:
        completion_percent = min(100.0, (current_word_count / project.target_word_count) * 100)

    return ProjectStats(
        current_word_count=current_word_count,
        chapters_count=project.metadata.get("chapters_count", 0),
        characters_count=characters_count,
        locations_count=locations_count,
        threads_count=threads_count,
        promises_count=promises_count,
        last_edited=project.updated_at,
        completion_percent=round(completion_percent, 2),
    )


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    status: Optional[str] = Query(None, description="Filter by status"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    search: Optional[str] = Query(None, description="Search in title"),
    include_archived: bool = Query(False, description="Include archived projects"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    List all user's projects

    Returns projects with statistics and filtering options
    """
    query = db.query(Project).filter(Project.owner_id == user.id)

    # Filters
    if status:
        query = query.filter(Project.status == status)

    if genre:
        query = query.filter(Project.genre == genre)

    if search:
        query = query.filter(Project.title.ilike(f"%{search}%"))

    if not include_archived:
        query = query.filter(Project.status != "archived")

    # Order by last updated
    query = query.order_by(Project.updated_at.desc())

    # Get total count
    total = query.count()

    # Paginate
    projects = query.offset(offset).limit(limit).all()

    # Add stats to each project
    project_responses = []
    for project in projects:
        stats = get_project_stats(db, project.id)
        project_dict = {
            "id": project.id,
            "title": project.title,
            "genre": project.genre,
            "target_word_count": project.target_word_count,
            "status": project.status,
            "metadata": project.metadata,
            "owner_id": project.owner_id,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "stats": stats,
        }
        project_responses.append(ProjectResponse(**project_dict))

    return ProjectListResponse(
        projects=project_responses,
        total=total,
    )


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new project

    Initializes empty project with default settings
    """
    # Create project
    new_project = Project(
        title=project_data.title,
        genre=project_data.genre,
        target_word_count=project_data.target_word_count,
        status=project_data.status,
        owner_id=user.id,
        metadata={
            "description": project_data.description or "",
            "current_word_count": 0,
            "chapters_count": 0,
            "created_via": "api",
        },
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # Get stats
    stats = get_project_stats(db, new_project.id)

    return ProjectResponse(
        id=new_project.id,
        title=new_project.title,
        genre=new_project.genre,
        target_word_count=new_project.target_word_count,
        status=new_project.status,
        metadata=new_project.metadata,
        owner_id=new_project.owner_id,
        created_at=new_project.created_at,
        updated_at=new_project.updated_at,
        stats=stats,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get single project by ID

    Includes full statistics
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id,
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stats = get_project_stats(db, project.id)

    return ProjectResponse(
        id=project.id,
        title=project.title,
        genre=project.genre,
        target_word_count=project.target_word_count,
        status=project.status,
        metadata=project.metadata,
        owner_id=project.owner_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        stats=stats,
    )


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update project details

    All fields are optional - only provided fields will be updated
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id,
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update fields
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    project.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(project)

    stats = get_project_stats(db, project.id)

    return ProjectResponse(
        id=project.id,
        title=project.title,
        genre=project.genre,
        target_word_count=project.target_word_count,
        status=project.status,
        metadata=project.metadata,
        owner_id=project.owner_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        stats=stats,
    )


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    permanent: bool = Query(False, description="Permanently delete (vs archive)"),
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete or archive project

    By default, archives the project. Use permanent=true to permanently delete.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id,
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if permanent:
        # Permanently delete project and all related entities
        # WARNING: This cascades to all canon entities
        db.delete(project)
    else:
        # Just archive
        project.status = "archived"
        project.updated_at = datetime.utcnow()

    db.commit()
    return None


@router.post("/{project_id}/duplicate", response_model=ProjectResponse, status_code=201)
async def duplicate_project(
    project_id: int,
    duplicate_data: ProjectDuplicateRequest,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Duplicate an existing project

    Creates a copy with optional canon entities and structure
    Useful for templates or starting new books in same universe
    """
    # Get source project
    source_project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id,
    ).first()

    if not source_project:
        raise HTTPException(status_code=404, detail="Source project not found")

    # Create new project
    new_project = Project(
        title=duplicate_data.new_title,
        genre=source_project.genre,
        target_word_count=source_project.target_word_count,
        status="draft",
        owner_id=user.id,
        metadata={
            **source_project.metadata,
            "duplicated_from": project_id,
            "duplicated_at": datetime.utcnow().isoformat(),
            "current_word_count": 0,
            "chapters_count": 0,
        } if duplicate_data.include_settings else {"current_word_count": 0, "chapters_count": 0},
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # Duplicate canon entities if requested
    if duplicate_data.include_canon:
        # Copy characters
        characters = db.query(Character).filter(Character.project_id == project_id).all()
        for char in characters:
            new_char = Character(
                name=char.name,
                description=char.description,
                claims=char.claims,
                unknowns=char.unknowns,
                tags=char.tags,
                goals=char.goals,
                values=char.values,
                fears=char.fears,
                secrets=char.secrets,
                behavioral_limits=char.behavioral_limits,
                behavioral_patterns=char.behavioral_patterns,
                voice_profile=char.voice_profile,
                relationships=char.relationships,
                appearance=char.appearance,
                background=char.background,
                arc=char.arc,
                project_id=new_project.id,
            )
            db.add(new_char)

        # Copy locations
        locations = db.query(Location).filter(Location.project_id == project_id).all()
        for loc in locations:
            new_loc = Location(
                name=loc.name,
                description=loc.description,
                claims=loc.claims,
                unknowns=loc.unknowns,
                tags=loc.tags,
                geography=loc.geography,
                climate=loc.climate,
                social_rules=loc.social_rules,
                power_structure=loc.power_structure,
                restrictions=loc.restrictions,
                access_control=loc.access_control,
                atmosphere=loc.atmosphere,
                connected_to=loc.connected_to,
                project_id=new_project.id,
            )
            db.add(new_loc)

        # Copy magic rules
        magic_rules = db.query(MagicRule).filter(MagicRule.project_id == project_id).all()
        for rule in magic_rules:
            new_rule = MagicRule(
                name=rule.name,
                description=rule.description,
                claims=rule.claims,
                unknowns=rule.unknowns,
                tags=rule.tags,
                rule_type=rule.rule_type,
                laws=rule.laws,
                costs=rule.costs,
                limitations=rule.limitations,
                exceptions=rule.exceptions,
                prohibitions=rule.prohibitions,
                mechanics=rule.mechanics,
                manifestation=rule.manifestation,
                project_id=new_project.id,
            )
            db.add(new_rule)

        db.commit()

    # Get stats
    stats = get_project_stats(db, new_project.id)

    return ProjectResponse(
        id=new_project.id,
        title=new_project.title,
        genre=new_project.genre,
        target_word_count=new_project.target_word_count,
        status=new_project.status,
        metadata=new_project.metadata,
        owner_id=new_project.owner_id,
        created_at=new_project.created_at,
        updated_at=new_project.updated_at,
        stats=stats,
    )


@router.post("/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(
    project_id: int,
    archive_data: ProjectArchiveRequest,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Archive or unarchive a project

    Archived projects are hidden from default views but can be restored
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id,
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if archive_data.archive:
        project.status = "archived"
    else:
        # Restore to draft if was archived
        if project.status == "archived":
            project.status = "draft"

    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)

    stats = get_project_stats(db, project.id)

    return ProjectResponse(
        id=project.id,
        title=project.title,
        genre=project.genre,
        target_word_count=project.target_word_count,
        status=project.status,
        metadata=project.metadata,
        owner_id=project.owner_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        stats=stats,
    )


@router.get("/{project_id}/stats", response_model=ProjectStats)
async def get_project_statistics(
    project_id: int,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed project statistics

    Returns entity counts, word counts, and completion metrics
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id,
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return get_project_stats(db, project.id)
