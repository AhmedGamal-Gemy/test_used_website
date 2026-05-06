"""
Authentication service for user signup, signin lookup, and user retrieval.

This module contains business logic for authentication operations,
separating it from the router layer.
"""

from fastapi import HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId

from app.db.database import get_database
from app.core.security import get_password_hash


async def create_user(email: str, password: str) -> dict:
    """
    Create a new user with the given email and password.
    
    Args:
        email: User's email address
        password: Plain-text password (will be hashed before storage)
        
    Returns:
        dict: The created user document with inserted_id
        
    Raises:
        HTTPException 409: If email is already registered
    """
    db = await get_database()
    
    # Check if user with this email already exists
    existing_user = await db.users.find_one({"email": email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Hash the password before storing it
    hashed_password = get_password_hash(password)
    
    # Create the user document
    user_doc = {
        "email": email,
        "hashed_password": hashed_password,
    }
    
    # Insert the user into the users collection
    insert_result = await db.users.insert_one(user_doc)
    
    # Return the user document with the new ID
    user_doc["_id"] = insert_result.inserted_id
    return user_doc


async def find_user_by_email(email: str) -> dict | None:
    """
    Find a user by their email address.
    
    Args:
        email: User's email address
        
    Returns:
        dict | None: User document if found, None otherwise
    """
    db = await get_database()
    return await db.users.find_one({"email": email})


async def get_user_by_id(user_id: str) -> dict:
    """
    Get a user by their ID.
    
    Args:
        user_id: String representation of the user's ObjectId
        
    Returns:
        dict: User document
        
    Raises:
        HTTPException 401: If user not found or invalid ID format
    """
    db = await get_database()
    
    try:
        obj_id = ObjectId(user_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await db.users.find_one({"_id": obj_id})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
