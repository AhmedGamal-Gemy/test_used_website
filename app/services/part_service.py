"""
Part service inheriting from BaseService.

Business logic for part listing CRUD operations.
HTTP concerns are handled in the router layer.
"""

from datetime import datetime, timezone
from bson import ObjectId

from app.services.base import BaseService
from app.models.parts import PartCreate, PartUpdate
from app.core.exceptions import NotFoundError

PART_FIELDS = [
    "title",
    "category",
    "compatible_models",
    "condition",
    "price",
    "description",
]


class PartService(BaseService):
    """Service for part listing CRUD operations."""

    async def create(self, data: PartCreate, seller_id: ObjectId) -> dict:
        now = datetime.now(timezone.utc)
        doc = {
            **{k: getattr(data, k) for k in PART_FIELDS},
            "image_url": None,
            "seller_id": seller_id,
            "created_at": now,
            "updated_at": now,
        }
        doc_id = await self._repo.create(doc)
        result = await self._repo.find_by_id(str(doc_id))
        if result is None:
            raise NotFoundError("Failed to create part")
        return result

    async def list(self, skip: int, limit: int) -> list[dict]:
        return await self._repo.list(skip, limit)

    async def get(self, entity_id: str) -> dict:
        entity = await self._repo.find_by_id(entity_id)
        if entity is None:
            raise NotFoundError("Part not found")
        return entity

    async def update(
        self, entity_id: str, data: PartUpdate, user_id: ObjectId
    ) -> dict:
        entity = await self.get(entity_id)
        await self._require_ownership(entity, user_id)
        update_data = self._build_partial_update(data, PART_FIELDS)
        update_data["updated_at"] = datetime.now(timezone.utc)
        await self._repo.update(entity_id, update_data)
        result = await self._repo.find_by_id(entity_id)
        if result is None:
            raise NotFoundError("Failed to update part")
        return result

    async def delete(self, entity_id: str, user_id: ObjectId) -> None:
        entity = await self.get(entity_id)
        await self._require_ownership(entity, user_id)
        await self._repo.delete(entity_id)
