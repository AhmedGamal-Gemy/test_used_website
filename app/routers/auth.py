"""
Authentication router for user signup, signin, and signout.

For junior developers:
- FastAPI routers group related endpoints together (like auth endpoints)
- OAuth2PasswordBearer is a FastAPI security scheme that tells FastAPI to expect a Bearer token
  in the Authorization header. It also configures the "tokenUrl" for the OpenAPI docs.
- JWT tokens are stateless - we don't store them in the database (as per requirements)
- Signout is essentially a client-side operation since we don't track tokens server-side
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from bson.errors import InvalidId

from app.db.database import get_database
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    DUMMY_HASH,
)
from app.models.auth import UserSignup, UserSignin, UserResponse, TokenResponse

# ------------------------------------------------------------------------------
# Router Configuration
# ------------------------------------------------------------------------------

router = APIRouter(prefix="/api/auth", tags=["auth"])

# OAuth2PasswordBearer tells FastAPI that this API uses OAuth2 with password (and bearer tokens)
# tokenUrl is the endpoint clients use to get a token (our signin endpoint)
# This is used for the OpenAPI documentation and the "Authorize" button in Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/signin")


# ------------------------------------------------------------------------------
# Authentication Dependencies
# ------------------------------------------------------------------------------

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    FastAPI dependency that extracts and validates the current user from the JWT token.
    
    Flow for junior developers:
    1. FastAPI sees this dependency needs a `token` parameter
    2. It uses `oauth2_scheme` to extract the token from the Authorization header
    3. We decode the token to get the user ID (stored in the "sub" claim)
    4. We look up the user in the database
    5. If valid, we return the user; if not, we raise a 401 error
    
    This dependency can be used in any protected endpoint like:
        @app.get("/api/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"message": f"Hello {user['email']}"}
    """
    # Decode the JWT token (this will raise an exception if token is invalid/expired)
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract the user ID from the "sub" (subject) claim
    # payload.get() may return None, so we handle that case
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Convert to string to ensure proper type
    user_id = str(user_id)
    
    # Look up the user in the database
    db = await get_database()
    try:
        # Convert string ID back to ObjectId for MongoDB query
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    except InvalidId:
        # If the ID in the token is not a valid ObjectId
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# ------------------------------------------------------------------------------
# Auth Endpoints
# ------------------------------------------------------------------------------

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup):
    """
    Register a new user.
    
    Flow for junior developers:
    1. Client sends email + password in the request body
    2. FastAPI validates the request using the UserSignup model (validates email format)
    3. We check if a user with this email already exists in the database
    4. If yes → return 409 Conflict (email already registered)
    5. If no → hash the password, save the user to database, return 201 Created
    
    Note: We do NOT return a token here. The user needs to signin after signup.
    (Some APIs return a token here too, but we're keeping it simple.)
    """
    db = await get_database()
    
    # Check if user with this email already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Hash the password before storing it (NEVER store plain-text passwords!)
    hashed_password = get_password_hash(user_data.password)
    
    # Create the user document
    # We let MongoDB generate the _id automatically
    user_doc = {
        "email": user_data.email,
        "hashed_password": hashed_password,
    }
    
    # Insert the user into the users collection
    insert_result = await db.users.insert_one(user_doc)
    
    # Return the user response (without the password hash!)
    return UserResponse(
        email=user_data.email,
        id=str(insert_result.inserted_id)  # Convert ObjectId to string for the response
    )


@router.post("/signin", response_model=TokenResponse)
async def signin(user_data: UserSignin):
    """
    Authenticate a user and return a JWT access token.
    
    Flow for junior developers:
    1. Client sends email + password in the request body
    2. We look up the user by email in the database
    3. If user not found → still run password verification against DUMMY_HASH for timing attack protection
    4. If user found, verify the password using verify_password()
    5. If password doesn't match → return 401 Unauthorized
    6. If password matches → create a JWT token with the user's ID as the subject
    7. Return the token in the response
    
    The client then includes this token in future requests:
        Authorization: Bearer <token>
    
    Timing Attack Protection:
    We always call verify_password() even if the user doesn't exist.
    If the user doesn't exist, we verify against DUMMY_HASH to ensure the response
    time is consistent whether the user exists or not.
    """
    db = await get_database()
    
    # Look up the user by email
    user = await db.users.find_one({"email": user_data.email})
    
    # For timing attack protection:
    # - If user exists, verify against their hashed_password
    # - If user doesn't exist, verify against DUMMY_HASH
    # This ensures the function takes the same time regardless of whether the user exists
    if user:
        # Use type assertion since we know user has hashed_password if user exists
        hashed_password = user.get("hashed_password", "")
        password_valid = verify_password(user_data.password, hashed_password)
    else:
        # User doesn't exist - still run verification against dummy hash
        # This ensures consistent timing whether the email exists or not
        verify_password(user_data.password, DUMMY_HASH)
        password_valid = False
    
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create the access token
    # We use the user's MongoDB _id as the subject (sub) claim
    # This is what get_current_user() will use to look up the user
    # We know user is not None here because password_valid is True
    assert user is not None  # For type checker - user must exist if password is valid
    access_token = create_access_token(token_payload={"sub": str(user["_id"])})
    
    return TokenResponse(access_token=access_token)


@router.post("/signout")
async def signout():
    """
    Sign out the current user.
    
    IMPORTANT FOR JUNIOR DEVELOPERS:
    Since we're using JWT tokens (stateless), we don't actually "invalidate" the token here.
    JWT tokens are valid until they expire, regardless of calling signout.
    
    This endpoint exists for API completeness, but the real "signout" happens client-side:
    the client simply discards the token.
    
    In a production app with refresh tokens or token blacklisting, this would be more involved.
    But per requirements, we're not implementing refresh tokens or storing tokens in the database.
    
    Returns a simple success message.
    """
    return {"message": "Successfully signed out"}
