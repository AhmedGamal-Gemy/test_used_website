"""
Laptop service for CRUD operations.

This module contains business logic for laptop listings,
separating it from the router layer.
"""

from fastapi import HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone

from app.db.database import get_database
from app.models.laptops import LaptopCreate, LaptopUpdate

# The name of the MongoDB collection where laptops are stored
LAPTOPS_COLLECTION = "laptops"


async def create_laptop(laptop_data: LaptopCreate, seller_id: ObjectId) -> dict:
    """
    Create a new laptop listing.
    
    Args:
        laptop_data: Pydantic model containing laptop details
        seller_id: ObjectId of the user creating the listing
        
    Returns:
        dict: The created laptop document with its new ID and timestamps
    """
    db = await get_database()
    
    now = datetime.now(timezone.utc)
    
    laptop_doc = {
        "title": laptop_data.title,
        "brand": laptop_data.brand,
        "model": laptop_data.model,
        "condition": laptop_data.condition,
        "price": laptop_data.price,
        "description": laptop_data.description,
        "image_url": None,
        "seller_id": seller_id,
        "created_at": now,
        "updated_at": now,
    }
    
    insert_result = await db[LAPTOPS_COLLECTION].insert_one(laptop_doc)
    
    created_laptop = await db[LAPTOPS_COLLECTION].find_one({"_id": insert_result.inserted_id})
    if created_laptop is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create laptop listing"
        )
    
    return created_laptop


async def list_laptops(skip: int, limit: int) -> list[dict]:
    """
    List all laptop listings with pagination.
    
    Args:
        skip: Number of laptops to skip (for pagination)
        limit: Maximum number of laptops to return
        
    Returns:
        list[dict]: List of laptop documents
    """
    db = await get_database()
    
    laptops_cursor = db[LAPTOPS_COLLECTION].find().skip(skip).limit(limit)
    return await laptops_cursor.to_list(length=limit)


async def get_laptop(laptop_id: str) -> dict:
    """
    Get a single laptop listing by its ID.
    
    Args:
        laptop_id: String representation of the laptop's ObjectId
        
    Returns:
        dict: Laptop document
        
    Raises:
        HTTPException 400: If ID format is invalid
        HTTPException 404: If laptop not found
    """
    db = await get_database()
    
    try:
        obj_id = ObjectId(laptop_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid laptop ID format"
        )
    
    laptop = await db[LAPTOPS_COLLECTION].find_one({"_id": obj_id})
    if laptop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laptop not found"
        )
    
    return laptop


async def update_laptop(laptop_id: str, laptop_data: LaptopUpdate, current_user_id: ObjectId) -> dict:
    """
    Update an existing laptop listing.
    
    Args:
        laptop_id: String representation of the laptop's ObjectId
        laptop_data: Pydantic model with fields to update
        current_user_id: ObjectId of the user attempting the update
        
    Returns:
        dict: Updated laptop document
        
    Raises:
        HTTPException 400: If ID format is invalid
        HTTPException 403: If user is not the seller
        HTTPException 404: If laptop not found
    """
    db = await get_database()
    
    try:
        obj_id = ObjectId(laptop_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid laptop ID format"
        )
    
    laptop = await db[LAPTOPS_COLLECTION].find_one({"_id": obj_id})
    if laptop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laptop not found"
        )
    
    # Ownership check
    if str(laptop["seller_id"]) != str(current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own laptop listings"
        )
    
    # Build update document with only provided fields
    update_data = {}
    if laptop_data.title is not None:
        update_data["title"] = laptop_data.title
    if laptop_data.brand is not None:
        update_data["brand"] = laptop_data.brand
    if laptop_data.model is not None:
        update_data["model"] = laptop_data.model
    if laptop_data.condition is not None:
        update_data["condition"] = laptop_data.condition
    if laptop_data.price is not None:
        update_data["price"] = laptop_data.price
    if laptop_data.description is not None:
        update_data["description"] = laptop_data.description
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db[LAPTOPS_COLLECTION].update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )
    
    updated_laptop = await db[LAPTOPS_COLLECTION].find_one({"_id": obj_id})
    if updated_laptop is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated laptop"
        )
    
    return updated_laptop


async def delete_laptop(laptop_id: str, current_user_id: ObjectId) -> None:
    """
    Delete a laptop listing.
    
    Args:
        laptop_id: String representation of the laptop's ObjectId
        current_user_id: ObjectId of the user attempting the deletion
        
    Raises:
        HTTPException 400: If ID format is invalid
        HTTPException 403: If user is not the seller
        HTTPException 404: If laptop not found
    """
    db = await get_database()
    
    try:
        obj_id = ObjectId(laptop_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid laptop ID format"
        )
    
    laptop = await db[LAPTOPS_COLLECTION].find_one({"_id": obj_id})
    if laptop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laptop not found"
        )
    
    # Ownership check
    if str(laptop["seller_id"]) != str(current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own laptop listings"
        )
    
    await db[LAPTOPS_COLLECTION].delete_one({"_id": obj_id})
