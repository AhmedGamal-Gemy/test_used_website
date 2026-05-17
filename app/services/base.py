"""
Abstract base service with common business logic.

Provides ownership checks, ID validation, and partial update building
so that entity-specific services can focus on their unique logic.
"""

from abc import ABC, abstractmethod
from bson import ObjectId
from bson.errors import InvalidId

from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.repositories.base import BaseRepository
from app.db.database import get_db


class BaseService(ABC):
    """Abstract base class for all entity services."""

    def __init__(
        self, repository: BaseRepository, owner_field: str = "seller_id"
    ) -> None:
        self._repo = repository
        self._owner_field = owner_field

    def _parse_id(self, entity_id: str) -> ObjectId:
        """Parse a string ID into ObjectId, raising ValidationError on failure."""
        try:
            return ObjectId(entity_id)
        except (InvalidId, TypeError, ValueError):
            raise ValidationError("Invalid ID format")

    async def _require_ownership(
        self, entity: dict, user_id: ObjectId
    ) -> None:
        """Raise ForbiddenError if the entity does not belong to the user."""
        if str(entity.get(self._owner_field, "")) != str(user_id):
            raise ForbiddenError("You can only modify your own listings")

    async def _require_admin(self, user_id: ObjectId) -> None:
        """Raise ForbiddenError if the user is not an admin."""
        db = get_db()
        user = await db.users.find_one({"_id": user_id})
        if not user or user.get("role") != "admin":
            raise ForbiddenError("Admin access required")

    def _build_partial_update(
        self, update_model: object, field_names: list[str]
    ) -> dict[str, object]:
        """Build a dict of only the fields that were explicitly set."""
        return {
            field: getattr(update_model, field)
            for field in field_names
            if getattr(update_model, field) is not None
        }

    @abstractmethod
    async def create(self, data, seller_id: ObjectId) -> dict:
        """Create a new entity. Must be implemented by subclasses."""
        ...

    @abstractmethod
    async def get(self, entity_id: str) -> dict:
        """Get an entity by ID. Must be implemented by subclasses."""
        ...

    @abstractmethod
    async def update(
        self, entity_id: str, data, user_id: ObjectId
    ) -> dict:
        """Update an entity. Must be implemented by subclasses."""
        ...

    @abstractmethod
    async def delete(self, entity_id: str, user_id: ObjectId) -> None:
        """Delete an entity. Must be implemented by subclasses."""
        ...

    async def bulk_delete(self, entity_ids: list[str], user_id: ObjectId) -> dict:
        """Delete multiple entities by IDs (admin only). Returns {deleted, errors}."""
        await self._require_admin(user_id)
        valid_ids = []
        errors = []
        for eid in entity_ids:
            try:
                self._parse_id(eid)
                valid_ids.append(eid)
            except ValidationError:
                errors.append({"id": eid, "error": "Invalid ID format"})
        if not valid_ids:
            return {"deleted": 0, "errors": errors}
        deleted_count = await self._repo.delete_many(valid_ids)
        return {"deleted": deleted_count, "errors": errors}
