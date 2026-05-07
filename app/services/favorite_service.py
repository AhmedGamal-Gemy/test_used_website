"""
Favorites service for managing user wishlist of laptops and parts.

Business logic for adding, removing, and listing favorites.
HTTP concerns are handled in the router layer.
"""

from __future__ import annotations

from bson import ObjectId
from bson.errors import InvalidId

from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.user_repo import UserRepository


async def _validate_and_get_user(user_id: str, user_repo: UserRepository) -> tuple[str, dict]:
    """Validate user ID and fetch user document."""
    try:
        obj_id = ObjectId(user_id)
    except (InvalidId, TypeError, ValueError):
        raise ValidationError("Invalid user ID format")

    user = await user_repo.find_by_id(user_id)
    if user is None:
        raise NotFoundError("User not found")

    return str(obj_id), user


async def add_laptop_favorite(user_id: str, laptop_id: str, user_repo: UserRepository) -> dict:
    """Add a laptop to user's favorites."""
    obj_id, user = await _validate_and_get_user(user_id, user_repo)

    try:
        laptop_oid = ObjectId(laptop_id)
    except (InvalidId, TypeError, ValueError):
        raise ValidationError("Invalid laptop ID format")

    favorites = user.get("favorite_laptops", [])
    if laptop_oid in favorites:
        raise ValidationError("Laptop already in favorites")

    favorites.append(laptop_oid)
    await user_repo.update(user_id, {"favorite_laptops": favorites})

    updated = await user_repo.find_by_id(user_id)
    assert updated is not None
    return updated


async def remove_laptop_favorite(user_id: str, laptop_id: str, user_repo: UserRepository) -> dict:
    """Remove a laptop from user's favorites."""
    obj_id, user = await _validate_and_get_user(user_id, user_repo)

    try:
        laptop_oid = ObjectId(laptop_id)
    except (InvalidId, TypeError, ValueError):
        raise ValidationError("Invalid laptop ID format")

    favorites = user.get("favorite_laptops", [])
    if laptop_oid not in favorites:
        raise NotFoundError("Laptop not in favorites")

    favorites.remove(laptop_oid)
    await user_repo.update(user_id, {"favorite_laptops": favorites})

    updated = await user_repo.find_by_id(user_id)
    assert updated is not None
    return updated


async def add_part_favorite(user_id: str, part_id: str, user_repo: UserRepository) -> dict:
    """Add a part to user's favorites."""
    obj_id, user = await _validate_and_get_user(user_id, user_repo)

    try:
        part_oid = ObjectId(part_id)
    except (InvalidId, TypeError, ValueError):
        raise ValidationError("Invalid part ID format")

    favorites = user.get("favorite_parts", [])
    if part_oid in favorites:
        raise ValidationError("Part already in favorites")

    favorites.append(part_oid)
    await user_repo.update(user_id, {"favorite_parts": favorites})

    updated = await user_repo.find_by_id(user_id)
    assert updated is not None
    return updated


async def remove_part_favorite(user_id: str, part_id: str, user_repo: UserRepository) -> dict:
    """Remove a part from user's favorites."""
    obj_id, user = await _validate_and_get_user(user_id, user_repo)

    try:
        part_oid = ObjectId(part_id)
    except (InvalidId, TypeError, ValueError):
        raise ValidationError("Invalid part ID format")

    favorites = user.get("favorite_parts", [])
    if part_oid not in favorites:
        raise NotFoundError("Part not in favorites")

    favorites.remove(part_oid)
    await user_repo.update(user_id, {"favorite_parts": favorites})

    updated = await user_repo.find_by_id(user_id)
    assert updated is not None
    return updated