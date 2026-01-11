"""
Chapter Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from core.database.base import get_db
from core.auth.config import current_active_user
from core.models.user import User
from core.models.base import Project
from core.models.chapter import Chapter, ChapterVersion, WritingSession
from api.schemas.chapter import (
    ChapterCreate,
    ChapterUpdate,
    ChapterResponse,
    ChapterListItem,
    ChapterListResponse,
    ChapterVersionResponse,
    WritingSessionCreate,
    WritingSessionUpdate,
    WritingSessionEnd,
    WritingSessionResponse,
    ChapterAutoSaveRequest,
    ChapterReorderRequest,
)

router = APIRouter()


def verify_project_access(db: Session, project_id: int, user_id: int) -> Project:
    """Verify user has access to project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


def calculate_word_count(text: str) -> int:
    """Calculate word count from text"""
    if not text:
        return 0
    return len(text.split())


@router.get("/projects/{project_id}/chapters", response_model=ChapterListResponse)
async def list_chapters(
    project_id: int,
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    List all chapters in a project

    Returns chapters ordered by chapter_number
    """
    verify_project_access(db, project_id, user.id)

    query = db.query(Chapter).filter(Chapter.project_id == project_id)

    if status:
        query = query.filter(Chapter.status == status)

    query = query.order_by(Chapter.chapter_number, Chapter.scene_number)

    total = query.count()
    chapters = query.offset(offset).limit(limit).all()

    chapter_items = [
        ChapterListItem(
            id=c.id,
            project_id=c.project_id,
            chapter_number=c.chapter_number,
            scene_number=c.scene_number,
            title=c.title,
            word_count=c.word_count,
            status=c.status,
            last_edited_at=c.last_edited_at,
        )
        for c in chapters
    ]

    return ChapterListResponse(chapters=chapter_items, total=total)


@router.post("/projects/{project_id}/chapters", response_model=ChapterResponse, status_code=201)
async def create_chapter(
    project_id: int,
    chapter_data: ChapterCreate,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new chapter

    Initializes with empty content and draft status
    """
    verify_project_access(db, project_id, user.id)

    # Check if chapter number already exists
    existing = db.query(Chapter).filter(
        Chapter.project_id == project_id,
        Chapter.chapter_number == chapter_data.chapter_number,
        Chapter.scene_number == chapter_data.scene_number
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Chapter {chapter_data.chapter_number}" +
                   (f" Scene {chapter_data.scene_number}" if chapter_data.scene_number else "") +
                   " already exists"
        )

    # Calculate word count
    word_count = calculate_word_count(chapter_data.content)

    # Create chapter
    new_chapter = Chapter(
        project_id=project_id,
        chapter_number=chapter_data.chapter_number,
        scene_number=chapter_data.scene_number,
        title=chapter_data.title,
        content=chapter_data.content,
        summary=chapter_data.summary,
        pov_character_id=chapter_data.pov_character_id,
        narrator_type=chapter_data.narrator_type,
        target_word_count=chapter_data.target_word_count,
        status=chapter_data.status,
        notes=chapter_data.notes,
        tags=chapter_data.tags,
        metadata=chapter_data.metadata,
        word_count=word_count,
        started_at=datetime.utcnow() if word_count > 0 else None,
    )

    db.add(new_chapter)
    db.commit()
    db.refresh(new_chapter)

    # Create initial version
    initial_version = ChapterVersion(
        chapter_id=new_chapter.id,
        version_number=1,
        commit_message="Initial version",
        content_snapshot=chapter_data.content,
        word_count_snapshot=word_count,
        metadata_snapshot=chapter_data.metadata,
        author_id=user.id,
        is_autosave=False,
    )
    db.add(initial_version)
    db.commit()

    return ChapterResponse(**new_chapter.__dict__)


@router.get("/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    chapter_id: int,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get single chapter by ID

    Includes full content
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()

    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Verify access
    verify_project_access(db, chapter.project_id, user.id)

    return ChapterResponse(**chapter.__dict__)


@router.patch("/chapters/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    chapter_id: int,
    chapter_data: ChapterUpdate,
    create_version: bool = Query(False, description="Create version snapshot"),
    commit_message: Optional[str] = Query(None, description="Version commit message"),
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update chapter

    Optionally creates a version snapshot
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()

    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    verify_project_access(db, chapter.project_id, user.id)

    # Update fields
    update_data = chapter_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(chapter, field, value)

    # Recalculate word count if content changed
    if "content" in update_data:
        chapter.word_count = calculate_word_count(update_data["content"])

        # Set started_at if first content
        if chapter.word_count > 0 and not chapter.started_at:
            chapter.started_at = datetime.utcnow()

        # Set completed_at if status changed to complete
        if chapter.status == "complete" and not chapter.completed_at:
            chapter.completed_at = datetime.utcnow()

    chapter.last_edited_at = datetime.utcnow()

    # Create version snapshot if requested
    if create_version:
        chapter.version += 1

        version = ChapterVersion(
            chapter_id=chapter.id,
            version_number=chapter.version,
            commit_message=commit_message or f"Version {chapter.version}",
            content_snapshot=chapter.content,
            word_count_snapshot=chapter.word_count,
            metadata_snapshot=chapter.chapter_metadata,
            author_id=user.id,
            is_autosave=False,
        )
        db.add(version)

    db.commit()
    db.refresh(chapter)

    return ChapterResponse(**chapter.__dict__)


@router.post("/chapters/{chapter_id}/autosave")
async def autosave_chapter(
    chapter_id: int,
    autosave_data: ChapterAutoSaveRequest,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Auto-save chapter content

    Creates autosave version every N saves
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()

    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    verify_project_access(db, chapter.project_id, user.id)

    # Update content
    chapter.content = autosave_data.content
    chapter.word_count = autosave_data.word_count
    chapter.last_edited_at = datetime.utcnow()

    # Create autosave version every 10th autosave
    autosave_count = db.query(func.count(ChapterVersion.id)).filter(
        ChapterVersion.chapter_id == chapter_id,
        ChapterVersion.is_autosave == True
    ).scalar()

    if autosave_count % 10 == 0:
        version = ChapterVersion(
            chapter_id=chapter.id,
            version_number=chapter.version,
            commit_message=f"Autosave {autosave_count + 1}",
            content_snapshot=autosave_data.content,
            word_count_snapshot=autosave_data.word_count,
            metadata_snapshot=chapter.chapter_metadata,
            author_id=user.id,
            is_autosave=True,
        )
        db.add(version)

    db.commit()

    return {
        "success": True,
        "word_count": chapter.word_count,
        "last_edited_at": chapter.last_edited_at,
    }


@router.delete("/chapters/{chapter_id}", status_code=204)
async def delete_chapter(
    chapter_id: int,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a chapter

    Also deletes all versions
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()

    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    verify_project_access(db, chapter.project_id, user.id)

    db.delete(chapter)
    db.commit()

    return None


@router.get("/chapters/{chapter_id}/versions", response_model=List[ChapterVersionResponse])
async def list_chapter_versions(
    chapter_id: int,
    include_autosaves: bool = Query(False, description="Include autosave versions"),
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get chapter version history

    Returns all saved versions for rollback
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()

    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    verify_project_access(db, chapter.project_id, user.id)

    query = db.query(ChapterVersion).filter(ChapterVersion.chapter_id == chapter_id)

    if not include_autosaves:
        query = query.filter(ChapterVersion.is_autosave == False)

    query = query.order_by(ChapterVersion.created_at.desc())

    versions = query.all()

    return [ChapterVersionResponse(**v.__dict__) for v in versions]


@router.post("/chapters/{chapter_id}/versions/{version_id}/restore", response_model=ChapterResponse)
async def restore_chapter_version(
    chapter_id: int,
    version_id: int,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Restore chapter to a previous version

    Creates a new version with the old content
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()

    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    verify_project_access(db, chapter.project_id, user.id)

    version = db.query(ChapterVersion).filter(
        ChapterVersion.id == version_id,
        ChapterVersion.chapter_id == chapter_id
    ).first()

    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    # Restore content
    chapter.content = version.content_snapshot
    chapter.word_count = version.word_count_snapshot
    chapter.chapter_metadata = version.metadata_snapshot
    chapter.version += 1
    chapter.last_edited_at = datetime.utcnow()

    # Create new version
    restore_version = ChapterVersion(
        chapter_id=chapter.id,
        version_number=chapter.version,
        commit_message=f"Restored from version {version.version_number}",
        content_snapshot=version.content_snapshot,
        word_count_snapshot=version.word_count_snapshot,
        metadata_snapshot=version.metadata_snapshot,
        author_id=user.id,
        is_autosave=False,
    )
    db.add(restore_version)

    db.commit()
    db.refresh(chapter)

    return ChapterResponse(**chapter.__dict__)


# ===== Writing Sessions =====

@router.post("/projects/{project_id}/writing-sessions", response_model=WritingSessionResponse, status_code=201)
async def start_writing_session(
    project_id: int,
    session_data: WritingSessionCreate,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Start a new writing session

    Tracks time and productivity
    """
    verify_project_access(db, project_id, user.id)

    session = WritingSession(
        user_id=user.id,
        project_id=project_id,
        chapter_id=session_data.chapter_id,
        started_at=datetime.utcnow(),
        session_metadata=session_data.metadata,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return WritingSessionResponse(**session.__dict__)


@router.patch("/writing-sessions/{session_id}", response_model=WritingSessionResponse)
async def update_writing_session(
    session_id: int,
    session_data: WritingSessionUpdate,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update active writing session

    Updates word counts and activity
    """
    session = db.query(WritingSession).filter(
        WritingSession.id == session_id,
        WritingSession.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    update_data = session_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(session, field, value)

    # Recalculate net words
    session.net_words = session.words_added - session.words_deleted

    db.commit()
    db.refresh(session)

    return WritingSessionResponse(**session.__dict__)


@router.post("/writing-sessions/{session_id}/end", response_model=WritingSessionResponse)
async def end_writing_session(
    session_id: int,
    session_data: WritingSessionEnd,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    End a writing session

    Finalizes metrics and calculates duration
    """
    session = db.query(WritingSession).filter(
        WritingSession.id == session_id,
        WritingSession.user_id == user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Update final metrics
    session.ended_at = datetime.utcnow()
    session.words_added = session_data.words_added
    session.words_deleted = session_data.words_deleted
    session.net_words = session_data.words_added - session_data.words_deleted
    session.keystrokes = session_data.keystrokes
    session.ai_generations = session_data.ai_generations

    # Calculate duration
    duration = (session.ended_at - session.started_at).total_seconds()
    session.duration_seconds = int(duration)

    # Add session notes
    if session_data.session_notes:
        session.session_metadata = {
            **session.session_metadata,
            "session_notes": session_data.session_notes
        }

    db.commit()
    db.refresh(session)

    return WritingSessionResponse(**session.__dict__)


@router.post("/projects/{project_id}/chapters/reorder")
async def reorder_chapters(
    project_id: int,
    reorder_data: ChapterReorderRequest,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_db),
):
    """
    Reorder chapters

    Updates chapter_number for multiple chapters
    """
    verify_project_access(db, project_id, user.id)

    for item in reorder_data.chapter_orders:
        chapter_id = item.get("chapter_id")
        new_number = item.get("new_number")

        if chapter_id and new_number:
            chapter = db.query(Chapter).filter(
                Chapter.id == chapter_id,
                Chapter.project_id == project_id
            ).first()

            if chapter:
                chapter.chapter_number = new_number

    db.commit()

    return {"success": True, "message": "Chapters reordered successfully"}
