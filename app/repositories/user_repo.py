"""
User-specific repository operations.

Extends BaseRepository with user-specific queries
like finding a user by email address.
"""

from __future__ import annotations

from typing import Any
from bson import ObjectId

from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """Repository for user documents with email-based lookup."""

    async def find_by_email(self, email: str) -> dict[str, Any] | None:
        """Find a user by their email address. Returns None if not found."""
        return await self._collection.find_one({"email": email})

    async def find_by_refresh_token_hash(self, token_hash: str) -> dict[str, Any] | None:
        """Find a user by their refresh token hash."""
        return await self._collection.find_one({"refresh_token_hash": token_hash})

    async def update_refresh_token(self, user_id: str, token_hash: str) -> None:
        """Update the user's refresh token hash."""
        await self._collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"refresh_token_hash": token_hash}},
        )
