"""
Authentication router for user signup, signin, signout, and token refresh.

HTTP layer only - delegates business logic to auth_service.
"""

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.security import (
    verify_password,
    create_access_token,
    decode_access_token,
    DUMMY_HASH,
    generate_refresh_token,
    hash_refresh_token,
)
from app.models.auth import UserSignup, UserSignin, UserResponse, RefreshTokenResponse
from app.services.auth_service import create_user, find_user_by_email, get_user_by_id, refresh_tokens
from app.repositories.user_repo import UserRepository
from app.db.database import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])

user_repo = UserRepository(get_db().users)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/signin")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """FastAPI dependency that extracts and validates the current user from JWT token."""
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_by_id(str(user_id), user_repo)
    return user


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup):
    """Register a new user."""
    user_doc = await create_user(
        user_data.email, user_data.password, user_repo
    )
    return UserResponse(
        email=user_data.email,
        id=str(user_doc["_id"]),
    )


@router.post("/signin", response_model=RefreshTokenResponse)
async def signin(user_data: UserSignin):
    """Authenticate a user and return JWT access token + refresh token."""
    user = await find_user_by_email(user_data.email, user_repo)

    if user:
        hashed_password = user.get("hashed_password", "")
        password_valid = verify_password(user_data.password, hashed_password)
    else:
        verify_password(user_data.password, DUMMY_HASH)
        password_valid = False

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    assert user is not None
    access_token = create_access_token(token_payload={"sub": str(user["_id"])})

    refresh_token = generate_refresh_token()
    refresh_hash = hash_refresh_token(refresh_token)
    await user_repo.update_refresh_token(str(user["_id"]), refresh_hash)

    return RefreshTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh(body: dict):
    """Exchange a valid refresh token for a new access token and refresh token."""
    token = body.get("refresh_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="refresh_token is required",
        )

    payload, new_refresh_token = await refresh_tokens(token, user_repo)
    access_token = create_access_token(token_payload=payload)
    return RefreshTokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.post("/signout")
async def signout(current_user: dict = Depends(get_current_user)):
    """Sign out the current user and invalidate refresh token."""
    await user_repo.update_refresh_token(current_user["_id"], "")
    return {"message": "Successfully signed out"}
