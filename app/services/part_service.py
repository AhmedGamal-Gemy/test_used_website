"""
Part service for CRUD operations.

This module contains business logic for part listings,
separating it from the router layer.
"""

from fastapi import HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone

from app.db.database import get_database
from app.models.parts import PartCreate, PartUpdate

# The name of the MongoDB collection where parts are stored
PARTS_COLLECTION = "parts"


async def create_part(part_data: PartCreate, seller_id: ObjectId) -> dict:
    """
    Create a new part listing.
    
    Args:
        part_data: Pydantic model containing part details
        seller_id: ObjectId of the user creating the listing
        
    Returns:
        dict: The created part document with its new ID and timestamps
    """
    db = await get_database()
    
    now = datetime.now(timezone.utc)
    
    part_doc = {
        "title": part_data.title,
        "category": part_data.category,
        "compatible_models": part_data.compatible_models,
        "condition": part_data.condition,
        "price": part_data.price,
        "description": part_data.description,
        "image_url": None,
        "seller_id": seller_id,
        "created_at": now,
        "updated_at": now,
    }
    
    insert_result = await db[PARTS_COLLECTION].insert_one(part_doc)
    
    created_part = await db[PARTS_COLLECTION].find_one({"_id": insert_result.inserted_id})
    if created_part is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create part listing"
        )
    
    return created_part


async def list_parts(skip: int, limit: int) -> list[dict]:
    """
    List all part listings with pagination.
    
    Args:
        skip: Number of parts to skip (for pagination)
        limit: Maximum number of parts to return
        
    Returns:
        list[dict]: List of part documents
    """
    db = await get_database()
    
    parts_cursor = db[PARTS_COLLECTION].find().skip(skip).limit(limit)
    return await parts_cursor.to_list(length=limit)


async def get_part(part_id: str) -> dict:
    """
    Get a single part listing by its ID.
    
    Args:
        part_id: String representation of the part's ObjectId
        
    Returns:
        dict: Part document
        
    Raises:
        HTTPException 400: If ID format is invalid
        HTTPException 404: If part not found
    """
    db = await get_database()
    
    try:
        obj_id = ObjectId(part_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid part ID format"
        )
    
    part = await db[PARTS_COLLECTION].find_one({"_id": obj_id})
    if part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Part not found"
        )
    
    return part


async def update_part(part_id: str, part_data: PartUpdate, current_user_id: ObjectId) -> dict:
    """
    Update an existing part listing.
    
    Args:
        part_id: String representation of the part's ObjectId
        part_data: Pydantic model with fields to update
        current_user_id: ObjectId of the user attempting the update
        
    Returns:
        dict: Updated part document
        
    Raises:
        HTTPException 400: If ID format is invalid
        HTTPException 403: If user is not the seller
        HTTPException 404: If part not found
    """
    db = await get_database()
    
    try:
        obj_id = ObjectId(part_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid part ID format"
        )
    
    part = await db[PARTS_COLLECTION].find_one({"_id": obj_id})
    if part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Part not found"
        )
    
    # Ownership check
    if str(part["seller_id"]) != str(current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own part listings"
        )
    
    # Build update document with only provided fields
    update_data = {}
    if part_data.title is not None:
        update_data["title"] = part_data.title
    if part_data.category is not None:
        update_data["category"] = part_data.category
    if part_data.compatible_models is not None:
        update_data["compatible_models"] = part_data.compatible_models
    if part_data.condition is not None:
        update_data["condition"] = part_data.condition
    if part_data.price is not None:
        update_data["price"] = part_data.price
    if part_data.description is not None:
        update_data["description"] = part_data.description
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db[PARTS_COLLECTION].update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )
    
    updated_part = await db[PARTS_COLLECTION].find_one({"_id": obj_id})
    if updated_part is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated part"
        )
    
    return updated_part


async def delete_part(part_id: str, current_user_id: ObjectId) -> None:
    """
    Delete a part listing.
    
    Args:
        part_id: String representation of the part's ObjectId
        current_user_id: ObjectId of the user attempting the deletion
        
    Raises:
        HTTPException 400: If ID format is invalid
        HTTPException 403: If user is not the seller
        HTTPException 404: If part not found
    """
    db = await get_database()
    
    try:
        obj_id = ObjectId(part_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid part ID format"
        )
    
    part = await db[PARTS_COLLECTION].find_one({"_id": obj_id})
    if part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Part not found"
        )
    
    # Ownership check
    if str(part["seller_id"]) != str(current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own part listings"
        )
    
    await db[PARTS_COLLECTION].delete_one({"_id": obj_id})
