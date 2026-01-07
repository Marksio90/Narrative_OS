"""
Project permissions and collaborator management API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from core.database.base import get_async_db
from core.models.user import User, ProjectCollaborator, CollaboratorRole
from core.models.base import Project
from core.auth.config import current_active_user
from core.auth.permissions import (
    require_owner,
    require_project_access,
    get_user_project_role
)
from api.schemas.permissions import (
    CollaboratorInvite,
    CollaboratorResponse,
    UserProjectRole,
    CollaboratorUpdate
)

router = APIRouter()


@router.get("/projects/{project_id}/role", response_model=UserProjectRole)
async def get_my_project_role(
    project_id: int,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get current user's role for a project
    Used by frontend to show/hide UI elements based on permissions
    """
    role = await get_user_project_role(user.id, project_id, db)

    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project"
        )

    return UserProjectRole(
        project_id=project_id,
        user_id=user.id,
        role=role.value,
        can_view=True,
        can_edit=role in [CollaboratorRole.EDITOR, CollaboratorRole.OWNER],
        can_write=role in [CollaboratorRole.WRITER, CollaboratorRole.EDITOR, CollaboratorRole.OWNER],
        can_manage=role == CollaboratorRole.OWNER,
    )


@router.get("/projects/{project_id}/collaborators", response_model=List[CollaboratorResponse])
async def list_collaborators(
    project_id: int,
    user: User = Depends(require_project_access()),
    db: AsyncSession = Depends(get_async_db)
):
    """
    List all collaborators for a project
    Anyone with access can view collaborators
    """
    result = await db.execute(
        select(ProjectCollaborator, User)
        .join(User, ProjectCollaborator.user_id == User.id)
        .where(ProjectCollaborator.project_id == project_id)
        .order_by(ProjectCollaborator.invited_at.desc())
    )

    collaborators = []
    for collab, collab_user in result.all():
        collaborators.append(CollaboratorResponse(
            id=collab.id,
            project_id=collab.project_id,
            user_id=collab.user_id,
            user_name=collab_user.name or collab_user.email,
            user_email=collab_user.email,
            user_avatar=collab_user.avatar_url,
            role=collab.role.value,
            invited_at=collab.invited_at,
            accepted_at=collab.accepted_at,
            is_pending=collab.accepted_at is None,
        ))

    return collaborators


@router.post("/projects/{project_id}/collaborators", response_model=CollaboratorResponse)
async def invite_collaborator(
    project_id: int,
    invite: CollaboratorInvite,
    user: User = Depends(require_owner()),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Invite a user to collaborate on a project
    Only project owner can invite collaborators
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == invite.email)
    )
    invited_user = result.scalar_one_or_none()

    if not invited_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{invite.email}' not found"
        )

    # Check if already collaborator
    result = await db.execute(
        select(ProjectCollaborator).where(
            and_(
                ProjectCollaborator.project_id == project_id,
                ProjectCollaborator.user_id == invited_user.id
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a collaborator"
        )

    # Create invitation
    collaboration = ProjectCollaborator(
        project_id=project_id,
        user_id=invited_user.id,
        role=CollaboratorRole[invite.role.upper()],
        invited_by=user.id,
        invited_at=datetime.utcnow(),
        accepted_at=datetime.utcnow() if invite.auto_accept else None
    )

    db.add(collaboration)
    await db.commit()
    await db.refresh(collaboration)

    # TODO: Send invitation email to invited_user.email

    return CollaboratorResponse(
        id=collaboration.id,
        project_id=collaboration.project_id,
        user_id=invited_user.id,
        user_name=invited_user.name or invited_user.email,
        user_email=invited_user.email,
        user_avatar=invited_user.avatar_url,
        role=collaboration.role.value,
        invited_at=collaboration.invited_at,
        accepted_at=collaboration.accepted_at,
        is_pending=collaboration.accepted_at is None,
    )


@router.patch("/projects/{project_id}/collaborators/{collaborator_id}")
async def update_collaborator(
    project_id: int,
    collaborator_id: int,
    update: CollaboratorUpdate,
    user: User = Depends(require_owner()),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Update collaborator role
    Only project owner can update roles
    """
    result = await db.execute(
        select(ProjectCollaborator).where(
            and_(
                ProjectCollaborator.id == collaborator_id,
                ProjectCollaborator.project_id == project_id
            )
        )
    )
    collab = result.scalar_one_or_none()

    if not collab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaborator not found"
        )

    if update.role:
        collab.role = CollaboratorRole[update.role.upper()]

    await db.commit()

    return {"message": "Collaborator updated successfully"}


@router.delete("/projects/{project_id}/collaborators/{collaborator_id}")
async def remove_collaborator(
    project_id: int,
    collaborator_id: int,
    user: User = Depends(require_owner()),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Remove a collaborator from a project
    Only project owner can remove collaborators
    """
    result = await db.execute(
        select(ProjectCollaborator).where(
            and_(
                ProjectCollaborator.id == collaborator_id,
                ProjectCollaborator.project_id == project_id
            )
        )
    )
    collab = result.scalar_one_or_none()

    if not collab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaborator not found"
        )

    await db.delete(collab)
    await db.commit()

    return {"message": "Collaborator removed successfully"}


@router.post("/collaborations/{collaboration_id}/accept")
async def accept_invitation(
    collaboration_id: int,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Accept a collaboration invitation
    User must be the invited user
    """
    result = await db.execute(
        select(ProjectCollaborator).where(
            and_(
                ProjectCollaborator.id == collaboration_id,
                ProjectCollaborator.user_id == user.id,
                ProjectCollaborator.accepted_at.is_(None)
            )
        )
    )
    collab = result.scalar_one_or_none()

    if not collab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or already accepted"
        )

    collab.accepted_at = datetime.utcnow()
    await db.commit()

    return {"message": "Invitation accepted successfully"}


@router.get("/me/invitations", response_model=List[CollaboratorResponse])
async def list_my_invitations(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    List pending invitations for current user
    """
    result = await db.execute(
        select(ProjectCollaborator, Project)
        .join(Project, ProjectCollaborator.project_id == Project.id)
        .where(
            and_(
                ProjectCollaborator.user_id == user.id,
                ProjectCollaborator.accepted_at.is_(None)
            )
        )
        .order_by(ProjectCollaborator.invited_at.desc())
    )

    invitations = []
    for collab, project in result.all():
        invitations.append(CollaboratorResponse(
            id=collab.id,
            project_id=collab.project_id,
            user_id=collab.user_id,
            user_name=user.name or user.email,
            user_email=user.email,
            user_avatar=user.avatar_url,
            role=collab.role.value,
            invited_at=collab.invited_at,
            accepted_at=collab.accepted_at,
            is_pending=True,
            project_title=project.title,
        ))

    return invitations
