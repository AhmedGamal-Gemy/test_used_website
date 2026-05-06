"""
Image service for validation, save, delete, and replace operations.

This module contains business logic for image handling,
separating it from the router layer.
"""

from fastapi import HTTPException, status, UploadFile
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
import uuid
import os

from app.db.database import get_database


# Allowed MIME types for image uploads
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/webp"]

# Maximum file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

# Directory where uploaded images are stored
UPLOADS_DIR = "uploads"


async def upload_image(
    entity_id: str,
    collection_name: str,
    file: UploadFile,
    current_user_id: ObjectId,
    owner_field: str = "seller_id"
) -> dict:
    """
    Upload or replace an image for a laptop or part listing.
    
    Args:
        entity_id: String representation of the entity's ObjectId
        collection_name: Name of the MongoDB collection ("laptops" or "parts")
        file: The uploaded image file
        current_user_id: ObjectId of the user attempting the upload
        owner_field: Field name for ownership check (default: "seller_id")
        
    Returns:
        dict: Updated entity document with new image URL
        
    Raises:
        HTTPException 400: If ID format is invalid or file validation fails
        HTTPException 403: If user is not the owner
        HTTPException 404: If entity not found
    """
    db = await get_database()
    
    # Validate entity ID
    try:
        obj_id = ObjectId(entity_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )
    
    # Look up the entity
    entity = await db[collection_name].find_one({"_id": obj_id})
    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )
    
    # Ownership check
    if str(entity.get(owner_field, "")) != str(current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload images for your own listings"
        )
    
    # Validate file type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed types: JPEG, PNG, WebP"
        )
    
    # Read file content and validate size
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit"
        )
    
    # Generate unique filename
    unique_filename = str(uuid.uuid4())
    
    # Determine file extension based on content type
    if file.content_type == "image/jpeg":
        extension = ".jpg"
    elif file.content_type == "image/png":
        extension = ".png"
    elif file.content_type == "image/webp":
        extension = ".webp"
    else:
        extension = ".jpg"
    
    full_filename = unique_filename + extension
    file_path = os.path.join(UPLOADS_DIR, full_filename)
    
    # Delete old image if one exists
    old_image_url = entity.get("image_url")
    if old_image_url:
        old_filename = os.path.basename(old_image_url)
        old_file_path = os.path.join(UPLOADS_DIR, old_filename)
        if os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
            except OSError:
                # Log error but don't fail the request
                pass
    
    # Ensure uploads directory exists
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    
    # Save new image to disk
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Update entity with new image URL
    image_url = f"/{UPLOADS_DIR}/{full_filename}"
    
    await db[collection_name].update_one(
        {"_id": obj_id},
        {"$set": {"image_url": image_url, "updated_at": datetime.now(timezone.utc)}}
    )
    
    # Retrieve and return updated entity
    updated_entity = await db[collection_name].find_one({"_id": obj_id})
    if updated_entity is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated entity"
        )
    
    return updated_entity
