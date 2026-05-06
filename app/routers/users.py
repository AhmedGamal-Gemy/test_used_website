"""
User profile router for viewing and updating user profiles.

HTTP layer only - delegates business logic to user_service.
"""

from fastapi import APIRouter, Depends

from app.models.auth import UserProfileResponse, UserProfileUpdate
from app.routers.auth import get_current_user
from app.services.user_service import get_user_profile, update_user_profile
from app.repositories.user_repo import UserRepository
from app.db.database import get_db

user_repo = UserRepository(get_db().users)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Get the authenticated user's own profile."""
    user = await get_user_profile(current_user["_id"], user_repo)
    return UserProfileResponse(
        id=str(user["_id"]),
        email=user["email"],
        full_name=user.get("full_name"),
        phone=user.get("phone"),
        location=user.get("location"),
        avatar_url=user.get("avatar_url"),
    )


@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update the authenticated user's own profile."""
    update_dict = profile_data.model_dump(exclude_unset=True)
    user = await update_user_profile(current_user["_id"], update_dict, user_repo)
    return UserProfileResponse(
        id=str(user["_id"]),
        email=user["email"],
        full_name=user.get("full_name"),
        phone=user.get("phone"),
        location=user.get("location"),
        avatar_url=user.get("avatar_url"),
    )
