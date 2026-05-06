"""
Authentication router for user signup, signin, and signout.

HTTP layer only - delegates business logic to auth_service.
"""

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.security import (
    verify_password,
    create_access_token,
    decode_access_token,
    DUMMY_HASH,
)
from app.models.auth import UserSignup, UserSignin, UserResponse, TokenResponse
from app.services.auth_service import create_user, find_user_by_email, get_user_by_id
from app.repositories.user_repo import UserRepository
from app.db.database import get_db

# Repository instance for user operations
user_repo = UserRepository(get_db().users)

router = APIRouter(prefix="/api/auth", tags=["auth"])

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


@router.post("/signin", response_model=TokenResponse)
async def signin(user_data: UserSignin):
    """Authenticate a user and return a JWT access token."""
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

    # User is guaranteed to be non-None here since password_valid would be False otherwise
    assert user is not None
    access_token = create_access_token(
        token_payload={"sub": str(user["_id"])}
    )
    return TokenResponse(access_token=access_token)


@router.post("/signout")
async def signout():
    """Sign out the current user (client-side token discard)."""
    return {"message": "Successfully signed out"}
