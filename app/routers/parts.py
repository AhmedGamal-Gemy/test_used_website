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

from app.models.parts import PartCreate, PartUpdate, PartResponse
from app.routers.auth import get_current_user
from app.services.part_service import (
    create_part as svc_create_part,
    list_parts as svc_list_parts,
    get_part as svc_get_part,
    update_part as svc_update_part,
    delete_part as svc_delete_part,
)
from app.services.image_service import upload_image

# ------------------------------------------------------------------------------
# Router Configuration
# ------------------------------------------------------------------------------

# All parts endpoints will be prefixed with /api/parts
# tags=["parts"] groups these endpoints together in the OpenAPI docs (Swagger UI)
router = APIRouter(prefix="/api/parts", tags=["parts"])


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
async def create_part_endpoint(
    part_data: PartCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new part listing.

    Flow for junior developers:
    1. Client sends part data in the request body (title, category, compatible_models, condition, price, description)
    2. FastAPI validates the request using PartCreate model
    3. get_current_user dependency extracts the authenticated user from the JWT token
    4. We use the part service to create the listing
    5. We return the created part with its new ID and timestamps

    Authentication: Required (seller_id is set from the authenticated user's ID)
    """
    # Use part service to create the listing
    created_part = await svc_create_part(part_data, current_user["_id"])

    # Convert MongoDB document to API response format
    return PartResponse(**serialize_part(created_part))


@router.get("", response_model=list[PartResponse])
async def list_parts_endpoint(
    skip: int = Query(default=0, ge=0, description="Number of parts to skip (for pagination)"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of parts to return (max 100)")
):
    """
    List all part listings with pagination.

    Flow for junior developers:
    1. Client can optionally provide skip and limit query parameters
    2. skip=0, limit=20 by default (returns the first 20 parts)
    3. We use the part service to query the database with pagination
    4. We convert each part document to the response format
    5. We return the list of parts

    Pagination example:
    - Page 1: skip=0, limit=20 → parts 1-20
    - Page 2: skip=20, limit=20 → parts 21-40

    Authentication: Not required (anyone can browse parts)
    """
    # Use part service to list parts
    parts = await svc_list_parts(skip, limit)

    # Convert each MongoDB document to the API response format
    return [PartResponse(**serialize_part(part)) for part in parts]


@router.get("/{part_id}", response_model=PartResponse)
async def get_part_endpoint(part_id: str):
    """
    Get a single part listing by its ID.

    Flow for junior developers:
    1. Client provides the part ID in the URL path
    2. We use the part service to look up the part
    3. If found, we return it; if not, service raises 404 Not Found

    Authentication: Not required (anyone can view a part listing)
    """
    # Use part service to get the part (handles ID validation and 404)
    part = await svc_get_part(part_id)

    # Convert MongoDB document to API response format
    return PartResponse(**serialize_part(part))


@router.put("/{part_id}", response_model=PartResponse)
async def update_part_endpoint(
    part_id: str,
    part_data: PartUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing part listing.

    Flow for junior developers:
    1. Client provides the part ID in the URL and the fields to update in the request body
    2. We use the part service to update the listing (handles validation, ownership check)
    3. We return the updated part

    Authentication: Required (only the seller can update their part)
    Ownership check: Compares part["seller_id"] with current_user["_id"]
    """
    # Use part service to update the listing (handles ownership check and 403/404)
    updated_part = await svc_update_part(part_id, part_data, current_user["_id"])

    # Convert MongoDB document to API response format
    return PartResponse(**serialize_part(updated_part))


@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_part_endpoint(
    part_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a part listing.

    Flow for junior developers:
    1. Client provides the part ID in the URL path
    2. We use the part service to delete the listing (handles ownership check and 403/404)
    3. We return 204 No Content (standard for successful delete with no response body)

    Authentication: Required (only the seller can delete their part)
    Ownership check: Compares part["seller_id"] with current_user["_id"]
    """
    # Use part service to delete the listing (handles ownership check and 403/404)
    await svc_delete_part(part_id, current_user["_id"])

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
    2. We use the image service to handle validation, old image deletion, and saving
    3. We return the updated part with the new image URL

    Authentication: Required (only the seller can upload images for their part)
    """

    # Use image service to handle the upload (handles validation, ownership check, file operations)
    updated_part = await upload_image(
        part_id,
        "parts",
        file,
        current_user["_id"],
        "seller_id"
    )

    # Convert MongoDB document to API response format
    return PartResponse(**serialize_part(updated_part))
