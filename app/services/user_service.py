"""
User profile service for reading and updating user data.

Business logic for profile management.
HTTP concerns are handled in the router layer.
"""

from __future__ import annotations

from bson import ObjectId
from bson.errors import InvalidId

from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.user_repo import UserRepository

PROFILE_FIELDS = ["full_name", "phone", "location", "avatar_url"]


async def get_user_profile(user_id: str, user_repo: UserRepository) -> dict:
    """Get a user's profile by ID."""
    try:
        ObjectId(user_id)
    except (InvalidId, TypeError, ValueError):
        raise ValidationError("Invalid user ID format")

    user = await user_repo.find_by_id(user_id)
    if user is None:
        raise NotFoundError("User not found")
    return user


async def update_user_profile(
    user_id: str, data: dict, user_repo: UserRepository
) -> dict:
    """Update a user's profile fields."""
    try:
        ObjectId(user_id)
    except (InvalidId, TypeError, ValueError):
        raise ValidationError("Invalid user ID format")

    update_data = {k: v for k, v in data.items() if k in PROFILE_FIELDS and v is not None}
    if not update_data:
        raise ValidationError("No valid fields to update")

    user = await user_repo.find_by_id(user_id)
    if user is None:
        raise NotFoundError("User not found")

    await user_repo.update(user_id, update_data)
    updated = await user_repo.find_by_id(user_id)
    assert updated is not None
    return updated
