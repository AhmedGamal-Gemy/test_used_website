"""
Laptop service inheriting from BaseService.

Business logic for laptop CRUD operations.
HTTP concerns are handled in the router layer.
"""

from datetime import datetime, timezone
from bson import ObjectId

from app.services.base import BaseService
from app.models.laptops import LaptopCreate, LaptopUpdate
from app.core.exceptions import NotFoundError

LAPTOP_FIELDS = ["title", "brand", "model", "condition", "price", "description"]


class LaptopService(BaseService):
    """Service for laptop listing CRUD operations."""

    async def create(self, data: LaptopCreate, seller_id: ObjectId) -> dict:
        now = datetime.now(timezone.utc)
        doc = {
            **{k: getattr(data, k) for k in LAPTOP_FIELDS},
            "image_url": None,
            "seller_id": seller_id,
            "created_at": now,
            "updated_at": now,
        }
        doc_id = await self._repo.create(doc)
        result = await self._repo.find_by_id(str(doc_id))
        if result is None:
            raise NotFoundError("Failed to create laptop")
        return result

    async def list(self, skip: int, limit: int) -> list[dict]:
        return await self._repo.list(skip, limit)

    async def get(self, entity_id: str) -> dict:
        entity = await self._repo.find_by_id(entity_id)
        if entity is None:
            raise NotFoundError("Laptop not found")
        return entity

    async def update(
        self, entity_id: str, data: LaptopUpdate, user_id: ObjectId
    ) -> dict:
        entity = await self.get(entity_id)
        await self._require_ownership(entity, user_id)
        update_data = self._build_partial_update(data, LAPTOP_FIELDS)
        update_data["updated_at"] = datetime.now(timezone.utc)
        await self._repo.update(entity_id, update_data)
        result = await self._repo.find_by_id(entity_id)
        if result is None:
            raise NotFoundError("Failed to update laptop")
        return result

    async def delete(self, entity_id: str, user_id: ObjectId) -> None:
        entity = await self.get(entity_id)
        await self._require_ownership(entity, user_id)
        await self._repo.delete(entity_id)
