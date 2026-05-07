"""
Favorites router for managing user wishlist of laptops and parts.

HTTP layer only - delegates business logic to favorite_service.
"""

from fastapi import APIRouter, Depends

from app.routers.auth import get_current_user
from app.services.favorite_service import (
    add_laptop_favorite,
    remove_laptop_favorite,
    add_part_favorite,
    remove_part_favorite,
)
from app.repositories.user_repo import UserRepository
from app.db.database import get_db

user_repo = UserRepository(get_db().users)

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.post("/laptops/{laptop_id}")
async def add_laptop(
    laptop_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Add a laptop to favorites."""
    user = await add_laptop_favorite(current_user["_id"], laptop_id, user_repo)
    return {"message": "Laptop added to favorites", "count": len(user.get("favorite_laptops", []))}


@router.delete("/laptops/{laptop_id}")
async def remove_laptop(
    laptop_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Remove a laptop from favorites."""
    user = await remove_laptop_favorite(current_user["_id"], laptop_id, user_repo)
    return {"message": "Laptop removed from favorites", "count": len(user.get("favorite_laptops", []))}


@router.post("/parts/{part_id}")
async def add_part(
    part_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Add a part to favorites."""
    user = await add_part_favorite(current_user["_id"], part_id, user_repo)
    return {"message": "Part added to favorites", "count": len(user.get("favorite_parts", []))}


@router.delete("/parts/{part_id}")
async def remove_part(
    part_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Remove a part from favorites."""
    user = await remove_part_favorite(current_user["_id"], part_id, user_repo)
    return {"message": "Part removed from favorites", "count": len(user.get("favorite_parts", []))}