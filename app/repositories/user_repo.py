"""
User-specific repository operations.

Extends BaseRepository with user-specific queries
like finding a user by email address.
"""

from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """Repository for user documents with email-based lookup."""

    async def find_by_email(self, email: str) -> dict | None:
        """Find a user by their email address. Returns None if not found."""
        return await self._collection.find_one({"email": email})
