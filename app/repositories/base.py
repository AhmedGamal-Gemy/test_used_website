"""
Generic MongoDB repository with CRUD operations.

This base class is used by all entity-specific repositories
to avoid code duplication and provide a consistent interface.
"""

from __future__ import annotations

from typing import Any
from bson import ObjectId
from pymongo import AsyncMongoClient


class BaseRepository:
    """Generic repository for MongoDB CRUD operations."""

    def __init__(self, collection) -> None:  # type: ignore[no-any-unimported] - async MongoDB collection
        self._collection = collection

    async def create(self, document: dict[str, Any]) -> ObjectId:
        """Insert a document and return its new ObjectId."""
        result = await self._collection.insert_one(document)
        return result.inserted_id

    async def find_by_id(self, entity_id: str) -> dict[str, Any] | None:
        """Find a document by its string ID. Returns None if not found."""
        try:
            obj_id = ObjectId(entity_id)
        except Exception:
            return None
        return await self._collection.find_one({"_id": obj_id})

    async def list(self, skip: int, limit: int) -> list[dict[str, Any]]:
        """List documents with pagination (skip + limit)."""
        cursor = self._collection.find().skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def find_with_filters(
        self, filters: dict[str, Any], skip: int, limit: int
    ) -> list[dict[str, Any]]:
        """Find documents matching filters with pagination."""
        cursor = self._collection.find(filters).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def update(self, entity_id: str, update_data: dict[str, Any]) -> None:
        """Update a document by ID with the given fields."""
        obj_id = ObjectId(entity_id)
        await self._collection.update_one(
            {"_id": obj_id},
            {"$set": update_data},
        )

    async def delete(self, entity_id: str) -> None:
        """Delete a document by ID."""
        obj_id = ObjectId(entity_id)
        await self._collection.delete_one({"_id": obj_id})
