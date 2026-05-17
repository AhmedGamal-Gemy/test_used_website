"""
Laptop service inheriting from BaseService.

Business logic for laptop CRUD operations.
HTTP concerns are handled in the router layer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from bson import ObjectId

from app.services.base import BaseService
from app.models.laptops import LaptopCreate, LaptopUpdate
from app.core.exceptions import NotFoundError
from app.db.database import get_db

LAPTOP_FIELDS = ["title", "brand", "model", "condition", "price", "description"]


class LaptopService(BaseService):
    """Service for laptop listing CRUD operations."""

    async def create(self, data: LaptopCreate, seller_id: ObjectId) -> dict:
        # Check if user is admin
        db = get_db()
        user = await db.users.find_one({"_id": seller_id})
        if not user or user.get("role") != "admin":
            from app.core.exceptions import ForbiddenError
            raise ForbiddenError("Only admin users can create listings")
        
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

    async def search(
        self,
        brand: str | None = None,
        condition: str | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[dict]:
        """Search laptops with filters and pagination."""
        from typing import Any
        filters: dict[str, Any] = {}
        if brand:
            filters["brand"] = brand
        if condition:
            filters["condition"] = condition
        if price_min is not None or price_max is not None:
            price_filter: dict[str, Any] = {}
            if price_min is not None:
                price_filter["$gte"] = price_min
            if price_max is not None:
                price_filter["$lte"] = price_max
            filters["price"] = price_filter
        if search:
            filters["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
            ]
        return await self._repo.find_with_filters(filters, skip, limit)

    async def get(self, entity_id: str) -> dict:
        self._parse_id(entity_id)  # validate format -> raises 400 for invalid ObjectId
        entity = await self._repo.find_by_id(entity_id)
        if entity is None:
            raise NotFoundError("Laptop not found")
        return entity

    async def update(
        self, entity_id: str, data: LaptopUpdate, user_id: ObjectId
    ) -> dict:
        entity = await self.get(entity_id)
        # Check if user is admin (admin can update any listing)
        db = get_db()
        user = await db.users.find_one({"_id": user_id})
        if not user or user.get("role") != "admin":
            from app.core.exceptions import ForbiddenError
            raise ForbiddenError("Only admin users can update listings")
        update_data = self._build_partial_update(data, LAPTOP_FIELDS)
        update_data["updated_at"] = datetime.now(timezone.utc)
        await self._repo.update(entity_id, update_data)
        result = await self._repo.find_by_id(entity_id)
        if result is None:
            raise NotFoundError("Failed to update laptop")
        return result

    async def delete(self, entity_id: str, user_id: ObjectId) -> None:
        entity = await self.get(entity_id)
        # Check if user is admin (admin can delete any listing)
        db = get_db()
        user = await db.users.find_one({"_id": user_id})
        if not user or user.get("role") != "admin":
            from app.core.exceptions import ForbiddenError
            raise ForbiddenError("Only admin users can delete listings")
        await self._repo.delete(entity_id)
