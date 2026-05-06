"""
Image service for validation, save, delete, and replace operations.

Uses config constants for allowed types and file size limits.
Raises domain exceptions instead of HTTPException.
"""

from fastapi import UploadFile
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
import uuid
import os

from app.core.config import image_config
from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError


async def upload_image(
    entity_id: str,
    collection,  # type: ignore[no-any-unimported] - async MongoDB collection
    file: UploadFile,
    current_user_id: ObjectId,
    owner_field: str = "seller_id",
) -> dict:
    """Upload or replace an image for a laptop or part listing."""

    # Validate entity ID
    try:
        obj_id = ObjectId(entity_id)
    except (InvalidId, TypeError, ValueError):
        raise ValidationError("Invalid ID format")

    # Look up the entity
    entity = await collection.find_one({"_id": obj_id})
    if entity is None:
        raise NotFoundError("Entity not found")

    # Ownership check
    if str(entity.get(owner_field, "")) != str(current_user_id):
        raise ForbiddenError("You can only upload images for your own listings")

    # Validate file type
    if file.content_type not in image_config.allowed_types:
        raise ValidationError("Invalid file type. Allowed types: JPEG, PNG, WebP")

    # Read and validate file size
    file_content = await file.read()
    if len(file_content) > image_config.max_size_bytes:
        raise ValidationError("File size exceeds 5MB limit")

    # Generate unique filename with correct extension
    extension_map = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
    extension = extension_map.get(file.content_type, ".jpg")
    full_filename = str(uuid.uuid4()) + extension
    file_path = os.path.join(image_config.upload_dir, full_filename)

    # Delete old image if one exists
    old_image_url = entity.get("image_url")
    if old_image_url:
        old_filename = os.path.basename(old_image_url)
        old_file_path = os.path.join(image_config.upload_dir, old_filename)
        if os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
            except OSError:
                pass  # Log error but don't fail the request

    # Ensure uploads directory exists and save new image
    os.makedirs(image_config.upload_dir, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file_content)

    # Update entity with new image URL
    image_url = f"/{image_config.upload_dir}/{full_filename}"
    await collection.update_one(
        {"_id": obj_id},
        {"$set": {"image_url": image_url, "updated_at": datetime.now(timezone.utc)}},
    )

    # Retrieve and return updated entity
    updated_entity = await collection.find_one({"_id": obj_id})
    if updated_entity is None:
        raise NotFoundError("Failed to retrieve updated entity")

    return updated_entity
