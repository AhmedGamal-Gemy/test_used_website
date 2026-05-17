"""
Pydantic models for authentication (signup, signin, responses).

For junior developers:
- Pydantic models (BaseModel) are used to define the shape of request bodies and response data
- EmailStr validates that the email field is actually a valid email format
- These models provide automatic request validation and API documentation (OpenAPI/Swagger)
- UserResponse is what we send back to the client (never include password hash in responses!)
"""

from pydantic import BaseModel, EmailStr


# ------------------------------------------------------------------------------
# Request Schemas (what clients send to our API)
# ------------------------------------------------------------------------------

class UserSignup(BaseModel):
    """
    Schema for user registration requests.
    
    This is the data a client sends when they want to create a new account.
    FastAPI automatically validates:
    - email is a valid email format (thanks to EmailStr)
    - password is present and will be a string
    """
    email: EmailStr
    password: str


class UserSignin(BaseModel):
    """
    Schema for user login requests.
    
    This is the data a client sends when they want to log in.
    We use the same structure as signup (email + password).
    """
    email: EmailStr
    password: str


# ------------------------------------------------------------------------------
# Response Schemas (what our API sends back to clients)
# ------------------------------------------------------------------------------

class UserResponse(BaseModel):
    """
    Schema for user data returned to clients.
    
    IMPORTANT: We NEVER return the password hash to the client!
    This is a security best practice - the hash should stay in the database only.
    
    We return the user's email and their unique ID from MongoDB (_id).
    """
    email: EmailStr
    id: str  # MongoDB's _id field converted to string


class TokenResponse(BaseModel):
    """
    Schema for the response after successful login/signup.
    
    Returns the JWT access token that the client will use for authenticated requests.
    The client should include this token in the Authorization header as:
        Authorization: Bearer <access_token>
    """
    access_token: str
    token_type: str = "bearer"  # Default to "bearer" - standard for JWT


# ------------------------------------------------------------------------------
# Profile Schemas (user profile management)
# ------------------------------------------------------------------------------


class UserProfileResponse(BaseModel):
    """Public user profile data."""
    id: str
    email: str
    full_name: str | None = None
    phone: str | None = None
    location: str | None = None
    avatar_url: str | None = None
    role: str = "user"
    favorite_laptops: list[str] = []
    favorite_parts: list[str] = []


class UserProfileUpdate(BaseModel):
    """Fields a user can update on their own profile."""
    full_name: str | None = None
    phone: str | None = None
    location: str | None = None
    avatar_url: str | None = None


class RefreshTokenResponse(BaseModel):
    """Response containing access token and refresh token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
