"""
Canon Service

Manages Canon entities with git-like versioning
"""
from typing import List, Optional, Dict, Any, Type
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from core.models import (
    Character,
    Location,
    Faction,
    MagicRule,
    Item,
    Event,
    Promise,
    Thread,
    StyleProfile,
    CanonVersion,
    Project,
)
from core.models.base import CanonEntityMixin


class CanonService:
    """
    Service for managing Canon entities with versioning

    Provides CRUD operations and git-like commit/rollback functionality
    """

    # Map entity types to model classes
    ENTITY_TYPES = {
        "character": Character,
        "location": Location,
        "faction": Faction,
        "magic_rule": MagicRule,
        "item": Item,
        "event": Event,
        "promise": Promise,
        "thread": Thread,
        "style_profile": StyleProfile,
    }

    def __init__(self, db: Session):
        self.db = db

    # ===== CRUD Operations =====

    def create_entity(
        self,
        entity_type: str,
        project_id: int,
        data: Dict[str, Any],
        commit_message: Optional[str] = None,
    ) -> CanonEntityMixin:
        """
        Create a new canon entity

        Args:
            entity_type: Type of entity (character, location, etc.)
            project_id: Project ID
            data: Entity data
            commit_message: Optional commit message for version

        Returns:
            Created entity

        Raises:
            ValueError: If entity_type is invalid
        """
        model_class = self._get_model_class(entity_type)

        # Create entity
        entity = model_class(project_id=project_id, **data)
        self.db.add(entity)
        self.db.flush()

        # Create version if commit message provided
        if commit_message:
            self._create_version(
                project_id=project_id,
                commit_message=commit_message,
                changes={
                    "action": "create",
                    "entity_type": entity_type,
                    "entity_id": entity.id,
                    "data": data,
                },
            )

        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get_entity(
        self,
        entity_type: str,
        entity_id: int,
    ) -> Optional[CanonEntityMixin]:
        """
        Get a canon entity by ID

        Args:
            entity_type: Type of entity
            entity_id: Entity ID

        Returns:
            Entity or None if not found
        """
        model_class = self._get_model_class(entity_type)
        return self.db.query(model_class).filter(model_class.id == entity_id).first()

    def list_entities(
        self,
        entity_type: str,
        project_id: int,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[CanonEntityMixin]:
        """
        List canon entities for a project

        Args:
            entity_type: Type of entity
            project_id: Project ID
            tags: Optional tags to filter by
            limit: Max results
            offset: Pagination offset

        Returns:
            List of entities
        """
        model_class = self._get_model_class(entity_type)

        query = self.db.query(model_class).filter(
            model_class.project_id == project_id
        )

        if tags:
            # Filter by tags (JSON contains)
            for tag in tags:
                query = query.filter(model_class.tags.contains([tag]))

        query = query.order_by(model_class.created_at.desc())
        query = query.limit(limit).offset(offset)

        return query.all()

    def update_entity(
        self,
        entity_type: str,
        entity_id: int,
        data: Dict[str, Any],
        commit_message: Optional[str] = None,
    ) -> CanonEntityMixin:
        """
        Update a canon entity

        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            data: Updated data
            commit_message: Optional commit message

        Returns:
            Updated entity

        Raises:
            ValueError: If entity not found
        """
        entity = self.get_entity(entity_type, entity_id)
        if not entity:
            raise ValueError(f"{entity_type} with id {entity_id} not found")

        # Store old data for version tracking
        old_data = {
            "name": entity.name,
            "description": entity.description,
            "claims": entity.claims,
            "unknowns": entity.unknowns,
        }

        # Update entity
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        self.db.flush()

        # Create version
        if commit_message:
            self._create_version(
                project_id=entity.project_id,
                commit_message=commit_message,
                changes={
                    "action": "update",
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "old_data": old_data,
                    "new_data": data,
                },
            )

        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete_entity(
        self,
        entity_type: str,
        entity_id: int,
        commit_message: Optional[str] = None,
    ) -> bool:
        """
        Delete a canon entity

        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            commit_message: Optional commit message

        Returns:
            True if deleted
        """
        entity = self.get_entity(entity_type, entity_id)
        if not entity:
            return False

        # Store data for version
        if commit_message:
            entity_data = {
                "name": entity.name,
                "description": entity.description,
                "claims": entity.claims,
                "unknowns": entity.unknowns,
            }

            self._create_version(
                project_id=entity.project_id,
                commit_message=commit_message,
                changes={
                    "action": "delete",
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "data": entity_data,
                },
            )

        self.db.delete(entity)
        self.db.commit()
        return True

    # ===== Versioning =====

    def _create_version(
        self,
        project_id: int,
        commit_message: str,
        changes: Dict[str, Any],
        author_id: Optional[int] = None,
    ) -> CanonVersion:
        """
        Create a new canon version (commit)

        Args:
            project_id: Project ID
            commit_message: Description of changes
            changes: Dictionary of what changed
            author_id: User ID who made changes

        Returns:
            Created version
        """
        # Get latest version number
        latest = (
            self.db.query(CanonVersion)
            .filter(CanonVersion.project_id == project_id)
            .order_by(desc(CanonVersion.version_number))
            .first()
        )

        version_number = (latest.version_number + 1) if latest else 1

        # Create version
        version = CanonVersion(
            project_id=project_id,
            version_number=version_number,
            commit_message=commit_message,
            changes=changes,
            parent_version_id=latest.id if latest else None,
            author_id=author_id or 1,  # TODO: Get from auth context
        )

        self.db.add(version)
        self.db.commit()
        return version

    def get_version_history(
        self,
        project_id: int,
        limit: int = 50,
    ) -> List[CanonVersion]:
        """
        Get version history for a project

        Args:
            project_id: Project ID
            limit: Max versions to return

        Returns:
            List of versions (newest first)
        """
        return (
            self.db.query(CanonVersion)
            .filter(CanonVersion.project_id == project_id)
            .order_by(desc(CanonVersion.created_at))
            .limit(limit)
            .all()
        )

    def get_version(
        self,
        version_id: int,
    ) -> Optional[CanonVersion]:
        """
        Get a specific version

        Args:
            version_id: Version ID

        Returns:
            Version or None
        """
        return self.db.query(CanonVersion).filter(CanonVersion.id == version_id).first()

    # TODO: Implement rollback functionality
    # This would require storing full state snapshots or replay capability

    # ===== Validation =====

    def validate_entity(
        self,
        entity_type: str,
        entity_id: int,
    ) -> Dict[str, Any]:
        """
        Validate a canon entity

        Checks for:
        - Missing required fields
        - Broken relationships
        - Inconsistencies

        Args:
            entity_type: Type of entity
            entity_id: Entity ID

        Returns:
            Validation result with issues
        """
        entity = self.get_entity(entity_type, entity_id)
        if not entity:
            return {"valid": False, "errors": ["Entity not found"]}

        issues = []

        # Check required fields
        if not entity.name or not entity.name.strip():
            issues.append("Name is required")

        # Check claims vs unknowns overlap
        if entity.claims and entity.unknowns:
            claim_keys = set(entity.claims.keys()) if isinstance(entity.claims, dict) else set()
            unknown_list = set(entity.unknowns) if isinstance(entity.unknowns, list) else set()
            overlap = claim_keys & unknown_list
            if overlap:
                issues.append(f"Overlap between claims and unknowns: {overlap}")

        # Entity-specific validation
        if entity_type == "character":
            if not entity.goals and not entity.values:
                issues.append("Character should have goals or values defined")

        elif entity_type == "promise":
            if not entity.setup_description:
                issues.append("Promise must have setup description")
            if not entity.payoff_required:
                issues.append("Promise must define required payoff")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }

    # ===== Helpers =====

    def _get_model_class(self, entity_type: str) -> Type[CanonEntityMixin]:
        """
        Get SQLAlchemy model class for entity type

        Args:
            entity_type: Entity type name

        Returns:
            Model class

        Raises:
            ValueError: If entity type is invalid
        """
        if entity_type not in self.ENTITY_TYPES:
            raise ValueError(f"Invalid entity type: {entity_type}")
        return self.ENTITY_TYPES[entity_type]

    def get_entity_stats(self, project_id: int) -> Dict[str, int]:
        """
        Get statistics about canon entities in a project

        Args:
            project_id: Project ID

        Returns:
            Dictionary with counts per entity type
        """
        stats = {}
        for entity_type, model_class in self.ENTITY_TYPES.items():
            count = (
                self.db.query(model_class)
                .filter(model_class.project_id == project_id)
                .count()
            )
            stats[entity_type] = count
        return stats
