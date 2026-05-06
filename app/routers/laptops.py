"""
Laptop CRUD router for creating, reading, updating, and deleting laptop listings.

For junior developers:
- This router handles all endpoints related to laptop listings
- All write operations (POST, PUT, DELETE) require authentication via get_current_user
- Only the seller who created a laptop can update or delete it (ownership check)
- Pagination is implemented on the list endpoint (skip/limit)
- Laptop IDs in URLs are MongoDB ObjectIds (24-character hex strings)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
import uuid
import os

from app.db.database import get_database
from app.models.laptops import LaptopCreate, LaptopUpdate, LaptopResponse
from app.routers.auth import get_current_user

# ------------------------------------------------------------------------------
# Router Configuration
# ------------------------------------------------------------------------------

# All laptop endpoints will be prefixed with /api/laptops
# tags=["laptops"] groups these endpoints together in the OpenAPI docs (Swagger UI)
router = APIRouter(prefix="/api/laptops", tags=["laptops"])

# The name of the MongoDB collection where laptops are stored
LAPTOPS_COLLECTION = "laptops"


# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------

def serialize_laptop(laptop: dict) -> dict:
    """
    Convert a MongoDB laptop document to a dictionary suitable for API response.

    For junior developers:
    - MongoDB returns documents with an _id field that is an ObjectId (not a string)
    - Our API responses need the id as a string, so we convert it
    - We also convert seller_id to string for consistency
    - created_at and updated_at are converted to ISO format strings for JSON serialization
    """
    return {
        "id": str(laptop["_id"]),
        "title": laptop["title"],
        "brand": laptop["brand"],
        "model": laptop["model"],
        "condition": laptop["condition"],
        "price": laptop["price"],
        "description": laptop.get("description", ""),
        "image_url": laptop.get("image_url"),
        "seller_id": str(laptop["seller_id"]),
        "created_at": laptop["created_at"].isoformat() if isinstance(laptop.get("created_at"), datetime) else str(laptop.get("created_at", "")),
        "updated_at": laptop["updated_at"].isoformat() if isinstance(laptop.get("updated_at"), datetime) else str(laptop.get("updated_at", "")),
    }


# ------------------------------------------------------------------------------
# Laptop Endpoints
# ------------------------------------------------------------------------------

@router.post("", response_model=LaptopResponse, status_code=status.HTTP_201_CREATED)
async def create_laptop(
    laptop_data: LaptopCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new laptop listing.

    Flow for junior developers:
    1. Client sends laptop data in the request body (title, brand, model, condition, price, description)
    2. FastAPI validates the request using LaptopCreate model
    3. get_current_user dependency extracts the authenticated user from the JWT token
    4. We create a new laptop document with the current user as the seller
    5. We insert the document into the laptops collection
    6. We return the created laptop with its new ID and timestamps

    Authentication: Required (seller_id is set from the authenticated user's ID)
    """
    db = await get_database()

    # Get the current time in UTC for timestamps
    # We use timezone-aware datetimes for consistency
    now = datetime.now(timezone.utc)

    # Create the laptop document
    # seller_id is set to the current user's ID (from the JWT token)
    # This ensures only the authenticated user is recorded as the seller
    laptop_doc = {
        "title": laptop_data.title,
        "brand": laptop_data.brand,
        "model": laptop_data.model,
        "condition": laptop_data.condition,
        "price": laptop_data.price,
        "description": laptop_data.description,
        "image_url": None,  # Image upload is handled separately (Task 7)
        "seller_id": current_user["_id"],  # ObjectId from the authenticated user
        "created_at": now,
        "updated_at": now,
    }

    # Insert the laptop into the database
    insert_result = await db[LAPTOPS_COLLECTION].insert_one(laptop_doc)

    # Retrieve the inserted document to return it with all fields
    # We use the inserted_id to find the document we just created
    created_laptop = await db[LAPTOPS_COLLECTION].find_one({"_id": insert_result.inserted_id})
    if created_laptop is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create laptop listing"
        )

    # Convert MongoDB document to API response format
    return LaptopResponse(**serialize_laptop(created_laptop))


@router.get("", response_model=list[LaptopResponse])
async def list_laptops(
    skip: int = Query(default=0, ge=0, description="Number of laptops to skip (for pagination)"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of laptops to return (max 100)")
):
    """
    List all laptop listings with pagination.

    Flow for junior developers:
    1. Client can optionally provide skip and limit query parameters
    2. skip=0, limit=20 by default (returns the first 20 laptops)
    3. We query the database with skip and limit for pagination
    4. We convert each laptop document to the response format
    5. We return the list of laptops

    Pagination example:
    - Page 1: skip=0, limit=20 → laptops 1-20
    - Page 2: skip=20, limit=20 → laptops 21-40

    Authentication: Not required (anyone can browse laptops)
    """
    db = await get_database()

    # Query the database with pagination
    # skip(): number of documents to skip (for pagination offset)
    # limit(): maximum number of documents to return
    # to_list(length): converts the cursor to a list (length hint helps MongoDB optimize)
    laptops_cursor = db[LAPTOPS_COLLECTION].find().skip(skip).limit(limit)
    laptops = await laptops_cursor.to_list(length=limit)

    # Convert each MongoDB document to the API response format
    return [LaptopResponse(**serialize_laptop(laptop)) for laptop in laptops]


@router.get("/{laptop_id}", response_model=LaptopResponse)
async def get_laptop(laptop_id: str):
    """
    Get a single laptop listing by its ID.

    Flow for junior developers:
    1. Client provides the laptop ID in the URL path
    2. We validate that the ID is a valid MongoDB ObjectId format
    3. We look up the laptop in the database
    4. If found, we return it; if not, we return 404 Not Found

    Authentication: Not required (anyone can view a laptop listing)
    """
    db = await get_database()

    # Validate that the laptop_id is a valid MongoDB ObjectId
    # ObjectIds are 24-character hexadecimal strings
    try:
        obj_id = ObjectId(laptop_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid laptop ID format"
        )

    # Look up the laptop in the database
    laptop = await db[LAPTOPS_COLLECTION].find_one({"_id": obj_id})
    if laptop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laptop not found"
        )

    # Convert MongoDB document to API response format
    return LaptopResponse(**serialize_laptop(laptop))


@router.put("/{laptop_id}", response_model=LaptopResponse)
async def update_laptop(
    laptop_id: str,
    laptop_data: LaptopUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing laptop listing.

    Flow for junior developers:
    1. Client provides the laptop ID in the URL and the fields to update in the request body
    2. We validate the laptop ID format
    3. We look up the laptop and check if it exists (404 if not)
    4. We check if the current user is the seller (403 if not - ownership check)
    5. We build an update document with only the fields that were provided
    6. We update the laptop in the database and set updated_at to now
    7. We return the updated laptop

    Authentication: Required (only the seller can update their laptop)
    Ownership check: Compares laptop["seller_id"] with current_user["_id"]
    """
    db = await get_database()

    # Validate that the laptop_id is a valid MongoDB ObjectId
    try:
        obj_id = ObjectId(laptop_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid laptop ID format"
        )

    # Look up the existing laptop
    laptop = await db[LAPTOPS_COLLECTION].find_one({"_id": obj_id})
    if laptop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laptop not found"
        )

    # OWNERSHIP CHECK: Only the seller who created the laptop can update it
    # We compare the string representations of the ObjectIds
    # This is a critical security check to prevent users from editing other users' listings
    if str(laptop["seller_id"]) != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own laptop listings"
        )

    # Build the update document with only the fields that were provided
    # LaptopUpdate has Optional fields, so we only include fields that are not None
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

    # Always update the updated_at timestamp when making changes
    update_data["updated_at"] = datetime.now(timezone.utc)

    # Perform the update in the database
    await db[LAPTOPS_COLLECTION].update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )

    # Retrieve the updated document to return it
    updated_laptop = await db[LAPTOPS_COLLECTION].find_one({"_id": obj_id})
    if updated_laptop is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated laptop"
        )

    # Convert MongoDB document to API response format
    return LaptopResponse(**serialize_laptop(updated_laptop))


@router.delete("/{laptop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_laptop(
    laptop_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a laptop listing.

    Flow for junior developers:
    1. Client provides the laptop ID in the URL path
    2. We validate the laptop ID format
    3. We look up the laptop and check if it exists (404 if not)
    4. We check if the current user is the seller (403 if not - ownership check)
    5. We delete the laptop from the database
    6. We return 204 No Content (standard for successful delete with no response body)

    Authentication: Required (only the seller can delete their laptop)
    Ownership check: Compares laptop["seller_id"] with current_user["_id"]
    """
    db = await get_database()

    # Validate that the laptop_id is a valid MongoDB ObjectId
    try:
        obj_id = ObjectId(laptop_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid laptop ID format"
        )

    # Look up the existing laptop
    laptop = await db[LAPTOPS_COLLECTION].find_one({"_id": obj_id})
    if laptop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laptop not found"
        )

    # OWNERSHIP CHECK: Only the seller who created the laptop can delete it
    # This is the same security check as in the update endpoint
    if str(laptop["seller_id"]) != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own laptop listings"
        )

    # Delete the laptop from the database
    await db[LAPTOPS_COLLECTION].delete_one({"_id": obj_id})

    # Return 204 No Content (standard for successful DELETE)
    # FastAPI handles the empty response body for 204 status code


# ------------------------------------------------------------------------------
# Image Upload Endpoint
# ------------------------------------------------------------------------------

@router.post("/{laptop_id}/image", response_model=LaptopResponse, status_code=status.HTTP_200_OK)
async def upload_laptop_image(
    laptop_id: str,
    file: UploadFile = File(..., description="Image file (JPEG, PNG, or WebP, max 5MB)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload or replace the image for a laptop listing.

    Flow for junior developers:
    1. Client sends a POST request with the image file in the request body (multipart/form-data)
    2. We validate the laptop ID format (must be valid MongoDB ObjectId)
    3. We look up the laptop and check if it exists (404 if not)
    4. We check if the current user is the seller (403 if not - ownership check)
    5. We validate the file type (must be JPEG, PNG, or WebP)
    6. We validate the file size (must be less than 5MB)
    7. We generate a unique filename using UUID to avoid collisions
    8. If there's an existing image, we delete the old file from disk
    9. We save the new image to the uploads/ directory
    10. We update the laptop's image_url in MongoDB
    11. We return the updated laptop with the new image URL

    Authentication: Required (only the seller can upload images for their laptop)
    Ownership check: Compares laptop["seller_id"] with current_user["_id"]

    File validation:
    - Allowed content types: image/jpeg, image/png, image/webp
    - Maximum file size: 5MB (5 * 1024 * 1024 bytes)
    """

    # --------------------------------------------------------------------------
    # Step 1: Validate laptop ID and look up the laptop
    # --------------------------------------------------------------------------

    db = await get_database()

    # Validate that the laptop_id is a valid MongoDB ObjectId
    try:
        obj_id = ObjectId(laptop_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid laptop ID format"
        )

    # Look up the existing laptop
    laptop = await db[LAPTOPS_COLLECTION].find_one({"_id": obj_id})
    if laptop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laptop not found"
        )

    # --------------------------------------------------------------------------
    # Step 2: Ownership check - only the seller can upload images
    # --------------------------------------------------------------------------

    if str(laptop["seller_id"]) != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload images for your own laptop listings"
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

    # Check if the laptop already has an image
    old_image_url = laptop.get("image_url")
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
    # Step 8: Update the laptop's image_url in MongoDB
    # --------------------------------------------------------------------------

    # Construct the public URL for the image
    # This URL can be used by clients to display the image
    image_url = f"/uploads/{full_filename}"

    # Update the laptop document in MongoDB
    await db[LAPTOPS_COLLECTION].update_one(
        {"_id": obj_id},
        {"$set": {"image_url": image_url, "updated_at": datetime.now(timezone.utc)}}
    )

    # --------------------------------------------------------------------------
    # Step 9: Retrieve and return the updated laptop
    # --------------------------------------------------------------------------

    updated_laptop = await db[LAPTOPS_COLLECTION].find_one({"_id": obj_id})
    if updated_laptop is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated laptop"
        )

    # Convert MongoDB document to API response format
    return LaptopResponse(**serialize_laptop(updated_laptop))
