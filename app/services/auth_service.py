"""
Authentication service using UserRepository and domain exceptions.

Business logic for user signup, lookup, and retrieval.
No HTTP concerns here - routers handle HTTP, services raise domain exceptions.
"""

from __future__ import annotations

from bson import ObjectId
from bson.errors import InvalidId

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.security import get_password_hash, generate_refresh_token, hash_refresh_token
from app.repositories.user_repo import UserRepository


async def create_user(
    email: str, password: str, user_repo: UserRepository
) -> dict:
    """Create a new user. Raises ConflictError if email already exists."""
    existing = await user_repo.find_by_email(email)
    if existing:
        raise ConflictError("Email already registered")

    hashed_password = get_password_hash(password)
    user_doc = {
        "email": email,
        "hashed_password": hashed_password,
    }

    doc_id = await user_repo.create(user_doc)
    user = await user_repo.find_by_id(str(doc_id))
    assert user is not None
    return user


async def find_user_by_email(
    email: str, user_repo: UserRepository
) -> dict | None:
    """Find a user by email. Returns None if not found."""
    return await user_repo.find_by_email(email)


async def get_user_by_id(
    user_id: str, user_repo: UserRepository
) -> dict:
    """Get user by ID. Raises ValidationError or NotFoundError."""
    try:
        obj_id = ObjectId(user_id)
    except (InvalidId, TypeError, ValueError):
        raise ValidationError("Invalid user ID format")

    user = await user_repo.find_by_id(user_id)
    if user is None:
        raise ValidationError("User not found")

    return user


async def refresh_tokens(
    refresh_token: str, user_repo: UserRepository
) -> tuple[dict, str]:
    """Validate a refresh token and return new access token payload + new refresh token.

    Raises NotFoundError if token is invalid.
    """
    token_hash = hash_refresh_token(refresh_token)
    user = await user_repo.find_by_refresh_token_hash(token_hash)
    if user is None:
        raise NotFoundError("Invalid refresh token")

    new_refresh_token = generate_refresh_token()
    new_hash = hash_refresh_token(new_refresh_token)
    await user_repo.update_refresh_token(str(user["_id"]), new_hash)

    return {"sub": str(user["_id"])}, new_refresh_token
