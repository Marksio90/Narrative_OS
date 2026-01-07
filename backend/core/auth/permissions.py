"""
Project-level permissions system
FastAPI dependencies for checking user access to projects
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database.base import get_async_db
from ..models.user import User, ProjectCollaborator, CollaboratorRole
from .config import current_active_user


class PermissionChecker:
    """
    Dependency for checking project permissions

    Usage in routes:
        @app.get("/projects/{project_id}")
        async def get_project(
            project_id: int,
            user: User = Depends(require_project_access(min_role=CollaboratorRole.VIEWER))
        ):
            # user has at least VIEWER access to project_id
    """

    def __init__(self, min_role: CollaboratorRole = CollaboratorRole.VIEWER):
        self.min_role = min_role

    async def __call__(
        self,
        project_id: int,
        user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_db)
    ) -> User:
        """
        Check if user has required access to project
        Returns user if authorized, raises HTTPException otherwise
        """
        # Check if user is project owner (always has full access)
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        # Owner has all permissions
        if project.owner_id == user.id:
            return user

        # Check collaborator role
        result = await db.execute(
            select(ProjectCollaborator).where(
                ProjectCollaborator.project_id == project_id,
                ProjectCollaborator.user_id == user.id,
                ProjectCollaborator.accepted_at.isnot(None)  # Only accepted invitations
            )
        )
        collab = result.scalar_one_or_none()

        if not collab:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project"
            )

        # Check role hierarchy: OWNER > EDITOR > WRITER > VIEWER
        role_hierarchy = {
            CollaboratorRole.OWNER: 4,
            CollaboratorRole.EDITOR: 3,
            CollaboratorRole.WRITER: 2,
            CollaboratorRole.VIEWER: 1,
        }

        if role_hierarchy[collab.role] < role_hierarchy[self.min_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {self.min_role.value}, you have: {collab.role.value}"
            )

        return user


# Convenience functions for common permission checks
def require_project_access(min_role: CollaboratorRole = CollaboratorRole.VIEWER):
    """
    Require at least VIEWER access to a project

    Usage:
        @app.get("/projects/{project_id}")
        async def get_project(
            project_id: int,
            user: User = Depends(require_project_access())
        ):
            ...
    """
    return PermissionChecker(min_role=min_role)


def require_owner():
    """Require OWNER access (only project owner)"""
    return PermissionChecker(min_role=CollaboratorRole.OWNER)


def require_editor():
    """Require EDITOR access (can edit canon + prose)"""
    return PermissionChecker(min_role=CollaboratorRole.EDITOR)


def require_writer():
    """Require WRITER access (can write prose, limited canon)"""
    return PermissionChecker(min_role=CollaboratorRole.WRITER)


def require_viewer():
    """Require VIEWER access (read-only)"""
    return PermissionChecker(min_role=CollaboratorRole.VIEWER)


async def get_user_project_role(
    user_id: int,
    project_id: int,
    db: AsyncSession
) -> Optional[CollaboratorRole]:
    """
    Get user's role for a project (for frontend checks)
    Returns None if user has no access
    """
    # Check if owner
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if project and project.owner_id == user_id:
        return CollaboratorRole.OWNER

    # Check collaborator role
    result = await db.execute(
        select(ProjectCollaborator).where(
            ProjectCollaborator.project_id == project_id,
            ProjectCollaborator.user_id == user_id,
            ProjectCollaborator.accepted_at.isnot(None)
        )
    )
    collab = result.scalar_one_or_none()

    return collab.role if collab else None


# Import Project model (needed for permission checks)
from ..models.base import Project
