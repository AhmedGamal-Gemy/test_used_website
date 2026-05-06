"""
Parts CRUD router for creating, reading, updating, and deleting computer part listings.

For junior developers:
- This router handles all endpoints related to computer part listings (CPUs, RAM, hard drives, etc.)
- All write operations (POST, PUT, DELETE) require authentication via get_current_user
- Only the seller who created a part can update or delete it (ownership check)
- Pagination is implemented on the list endpoint (skip/limit)
- Part IDs in URLs are MongoDB ObjectIds (24-character hex strings)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
import uuid
import os

from app.db.database import get_database
from app.models.parts import PartCreate, PartUpdate, PartResponse
from app.routers.auth import get_current_user

# ------------------------------------------------------------------------------
# Router Configuration
# ------------------------------------------------------------------------------

# All parts endpoints will be prefixed with /api/parts
# tags=["parts"] groups these endpoints together in the OpenAPI docs (Swagger UI)
router = APIRouter(prefix="/api/parts", tags=["parts"])

# The name of the MongoDB collection where parts are stored
PARTS_COLLECTION = "parts"


# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------

def serialize_part(part: dict) -> dict:
    """
    Convert a MongoDB part document to a dictionary suitable for API response.

    For junior developers:
    - MongoDB returns documents with an _id field that is an ObjectId (not a string)
    - Our API responses need the id as a string, so we convert it
    - We also convert seller_id to string for consistency
    - created_at and updated_at are converted to ISO format strings for JSON serialization
    - compatible_models is a list that we pass through directly
    """
    return {
        "id": str(part["_id"]),
        "title": part["title"],
        "category": part["category"],
        "compatible_models": part["compatible_models"],
        "condition": part["condition"],
        "price": part["price"],
        "description": part.get("description", ""),
        "image_url": part.get("image_url"),
        "seller_id": str(part["seller_id"]),
        "created_at": part["created_at"].isoformat() if isinstance(part.get("created_at"), datetime) else str(part.get("created_at", "")),
        "updated_at": part["updated_at"].isoformat() if isinstance(part.get("updated_at"), datetime) else str(part.get("updated_at", "")),
    }


# ------------------------------------------------------------------------------
# Part Endpoints
# ------------------------------------------------------------------------------

@router.post("", response_model=PartResponse, status_code=status.HTTP_201_CREATED)
async def create_part(
    part_data: PartCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new part listing.

    Flow for junior developers:
    1. Client sends part data in the request body (title, category, compatible_models, condition, price, description)
    2. FastAPI validates the request using PartCreate model
    3. get_current_user dependency extracts the authenticated user from the JWT token
    4. We create a new part document with the current user as the seller
    5. We insert the document into the parts collection
    6. We return the created part with its new ID and timestamps

    Authentication: Required (seller_id is set from the authenticated user's ID)
    """
    db = await get_database()

    # Get the current time in UTC for timestamps
    # We use timezone-aware datetimes for consistency
    now = datetime.now(timezone.utc)

    # Create the part document
    # seller_id is set to the current user's ID (from the JWT token)
    # This ensures only the authenticated user is recorded as the seller
    part_doc = {
        "title": part_data.title,
        "category": part_data.category,
        "compatible_models": part_data.compatible_models,
        "condition": part_data.condition,
        "price": part_data.price,
        "description": part_data.description,
        "image_url": None,  # Image upload is handled separately (Task 7)
        "seller_id": current_user["_id"],  # ObjectId from the authenticated user
        "created_at": now,
        "updated_at": now,
    }

    # Insert the part into the database
    insert_result = await db[PARTS_COLLECTION].insert_one(part_doc)

    # Retrieve the inserted document to return it with all fields
    # We use the inserted_id to find the document we just created
    created_part = await db[PARTS_COLLECTION].find_one({"_id": insert_result.inserted_id})
    if created_part is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create part listing"
        )

    # Convert MongoDB document to API response format
    return PartResponse(**serialize_part(created_part))


@router.get("", response_model=list[PartResponse])
async def list_parts(
    skip: int = Query(default=0, ge=0, description="Number of parts to skip (for pagination)"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of parts to return (max 100)")
):
    """
    List all part listings with pagination.

    Flow for junior developers:
    1. Client can optionally provide skip and limit query parameters
    2. skip=0, limit=20 by default (returns the first 20 parts)
    3. We query the database with skip and limit for pagination
    4. We convert each part document to the response format
    5. We return the list of parts

    Pagination example:
    - Page 1: skip=0, limit=20 → parts 1-20
    - Page 2: skip=20, limit=20 → parts 21-40

    Authentication: Not required (anyone can browse parts)
    """
    db = await get_database()

    # Query the database with pagination
    # skip(): number of documents to skip (for pagination offset)
    # limit(): maximum number of documents to return
    # to_list(length): converts the cursor to a list (length hint helps MongoDB optimize)
    parts_cursor = db[PARTS_COLLECTION].find().skip(skip).limit(limit)
    parts = await parts_cursor.to_list(length=limit)

    # Convert each MongoDB document to the API response format
    return [PartResponse(**serialize_part(part)) for part in parts]


@router.get("/{part_id}", response_model=PartResponse)
async def get_part(part_id: str):
    """
    Get a single part listing by its ID.

    Flow for junior developers:
    1. Client provides the part ID in the URL path
    2. We validate that the ID is a valid MongoDB ObjectId format
    3. We look up the part in the database
    4. If found, we return it; if not, we return 404 Not Found

    Authentication: Not required (anyone can view a part listing)
    """
    db = await get_database()

    # Validate that the part_id is a valid MongoDB ObjectId
    # ObjectIds are 24-character hexadecimal strings
    try:
        obj_id = ObjectId(part_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid part ID format"
        )

    # Look up the part in the database
    part = await db[PARTS_COLLECTION].find_one({"_id": obj_id})
    if part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Part not found"
        )

    # Convert MongoDB document to API response format
    return PartResponse(**serialize_part(part))


@router.put("/{part_id}", response_model=PartResponse)
async def update_part(
    part_id: str,
    part_data: PartUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing part listing.

    Flow for junior developers:
    1. Client provides the part ID in the URL and the fields to update in the request body
    2. We validate the part ID format
    3. We look up the part and check if it exists (404 if not)
    4. We check if the current user is the seller (403 if not - ownership check)
    5. We build an update document with only the fields that were provided
    6. We update the part in the database and set updated_at to now
    7. We return the updated part

    Authentication: Required (only the seller can update their part)
    Ownership check: Compares part["seller_id"] with current_user["_id"]
    """
    db = await get_database()

    # Validate that the part_id is a valid MongoDB ObjectId
    try:
        obj_id = ObjectId(part_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid part ID format"
        )

    # Look up the existing part
    part = await db[PARTS_COLLECTION].find_one({"_id": obj_id})
    if part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Part not found"
        )

    # OWNERSHIP CHECK: Only the seller who created the part can update it
    # We compare the string representations of the ObjectIds
    # This is a critical security check to prevent users from editing other users' listings
    if str(part["seller_id"]) != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own part listings"
        )

    # Build the update document with only the fields that were provided
    # PartUpdate has Optional fields, so we only include fields that are not None
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

    # Always update the updated_at timestamp when making changes
    update_data["updated_at"] = datetime.now(timezone.utc)

    # Perform the update in the database
    await db[PARTS_COLLECTION].update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )

    # Retrieve the updated document to return it
    updated_part = await db[PARTS_COLLECTION].find_one({"_id": obj_id})
    if updated_part is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated part"
        )

    # Convert MongoDB document to API response format
    return PartResponse(**serialize_part(updated_part))


@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_part(
    part_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a part listing.

    Flow for junior developers:
    1. Client provides the part ID in the URL path
    2. We validate the part ID format
    3. We look up the part and check if it exists (404 if not)
    4. We check if the current user is the seller (403 if not - ownership check)
    5. We delete the part from the database
    6. We return 204 No Content (standard for successful delete with no response body)

    Authentication: Required (only the seller can delete their part)
    Ownership check: Compares part["seller_id"] with current_user["_id"]
    """
    db = await get_database()

    # Validate that the part_id is a valid MongoDB ObjectId
    try:
        obj_id = ObjectId(part_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid part ID format"
        )

    # Look up the existing part
    part = await db[PARTS_COLLECTION].find_one({"_id": obj_id})
    if part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Part not found"
        )

    # OWNERSHIP CHECK: Only the seller who created the part can delete it
    # This is the same security check as in the update endpoint
    if str(part["seller_id"]) != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own part listings"
        )

    # Delete the part from the database
    await db[PARTS_COLLECTION].delete_one({"_id": obj_id})

    # Return 204 No Content (standard for successful DELETE)
    # FastAPI handles the empty response body for 204 status code


# ------------------------------------------------------------------------------
# Image Upload Endpoint
# ------------------------------------------------------------------------------

@router.post("/{part_id}/image", response_model=PartResponse, status_code=status.HTTP_200_OK)
async def upload_part_image(
    part_id: str,
    file: UploadFile = File(..., description="Image file (JPEG, PNG, or WebP, max 5MB)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload or replace the image for a part listing.

    Flow for junior developers:
    1. Client sends a POST request with the image file in the request body (multipart/form-data)
    2. We validate the part ID format (must be valid MongoDB ObjectId)
    3. We look up the part and check if it exists (404 if not)
    4. We check if the current user is the seller (403 if not - ownership check)
    5. We validate the file type (must be JPEG, PNG, or WebP)
    6. We validate the file size (must be less than 5MB)
    7. We generate a unique filename using UUID to avoid collisions
    8. If there's an existing image, we delete the old file from disk
    9. We save the new image to the uploads/ directory
    10. We update the part's image_url in MongoDB
    11. We return the updated part with the new image URL

    Authentication: Required (only the seller can upload images for their part)
    Ownership check: Compares part["seller_id"] with current_user["_id"]

    File validation:
    - Allowed content types: image/jpeg, image/png, image/webp
    - Maximum file size: 5MB (5 * 1024 * 1024 bytes)
    """

    # --------------------------------------------------------------------------
    # Step 1: Validate part ID and look up the part
    # --------------------------------------------------------------------------

    db = await get_database()

    # Validate that the part_id is a valid MongoDB ObjectId
    try:
        obj_id = ObjectId(part_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid part ID format"
        )

    # Look up the existing part
    part = await db[PARTS_COLLECTION].find_one({"_id": obj_id})
    if part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Part not found"
        )

    # --------------------------------------------------------------------------
    # Step 2: Ownership check - only the seller can upload images
    # --------------------------------------------------------------------------

    if str(part["seller_id"]) != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload images for your own part listings"
        )

    # --------------------------------------------------------------------------
    # Step 3: Validate file type (content_type)
    # --------------------------------------------------------------------------

    # Define allowed MIME types for security - only allow image formats we support
    allowed_content_types = ["image/jpeg", "image/png", "image/webp"]

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: JPEG, PNG, WebP"
        )

    # --------------------------------------------------------------------------
    # Step 4: Validate file size (read file content and check size)
    # --------------------------------------------------------------------------

    # Read the file content into memory to check its size
    # WARNING: For very large files, consider streaming instead of reading all at once
    # But for 5MB limit, reading into memory is acceptable
    file_content = await file.read()
    file_size = len(file_content)

    # Check if file size exceeds 5MB limit
    max_file_size = 5 * 1024 * 1024  # 5MB in bytes
    if file_size > max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit"
        )

    # --------------------------------------------------------------------------
    # Step 5: Generate unique filename and determine file extension
    # --------------------------------------------------------------------------

    # Generate a UUID for the filename to avoid collisions
    # This ensures that even if two users upload "image.jpg", they get different names
    unique_filename = str(uuid.uuid4())

    # Determine file extension based on content type
    # We use the content type from the uploaded file, not the filename (more secure)
    if file.content_type == "image/jpeg":
        extension = ".jpg"
    elif file.content_type == "image/png":
        extension = ".png"
    elif file.content_type == "image/webp":
        extension = ".webp"
    else:
        # This shouldn't happen due to earlier validation, but defensive programming
        extension = ".jpg"

    # Full filename with extension
    full_filename = unique_filename + extension

    # Full path where the file will be saved
    # We save to the uploads/ directory at the project root
    uploads_dir = "uploads"
    file_path = os.path.join(uploads_dir, full_filename)

    # --------------------------------------------------------------------------
    # Step 6: Delete old image if one exists
    # --------------------------------------------------------------------------

    # Check if the part already has an image
    old_image_url = part.get("image_url")
    if old_image_url:
        # Extract the filename from the old image URL
        # The URL format is like: /uploads/filename.jpg
        # We need to get just the filename part
        old_filename = os.path.basename(old_image_url)
        old_file_path = os.path.join(uploads_dir, old_filename)

        # Delete the old file if it exists on disk
        if os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
            except OSError:
                # Log the error but don't fail the request
                # The old file might have already been deleted or be in use
                pass

    # --------------------------------------------------------------------------
    # Step 7: Save the new image file to disk
    # --------------------------------------------------------------------------

    # Ensure the uploads directory exists
    os.makedirs(uploads_dir, exist_ok=True)

    # Write the file content to disk
    # We use binary write mode ("wb") because images are binary files
    with open(file_path, "wb") as f:
        f.write(file_content)

    # --------------------------------------------------------------------------
    # Step 8: Update the part's image_url in MongoDB
    # --------------------------------------------------------------------------

    # Construct the public URL for the image
    # This URL can be used by clients to display the image
    image_url = f"/uploads/{full_filename}"

    # Update the part document in MongoDB
    await db[PARTS_COLLECTION].update_one(
        {"_id": obj_id},
        {"$set": {"image_url": image_url, "updated_at": datetime.now(timezone.utc)}}
    )

    # --------------------------------------------------------------------------
    # Step 9: Retrieve and return the updated part
    # --------------------------------------------------------------------------

    updated_part = await db[PARTS_COLLECTION].find_one({"_id": obj_id})
    if updated_part is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated part"
        )

    # Convert MongoDB document to API response format
    return PartResponse(**serialize_part(updated_part))
