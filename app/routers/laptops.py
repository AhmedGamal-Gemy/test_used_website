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

from app.models.laptops import LaptopCreate, LaptopUpdate, LaptopResponse
from app.routers.auth import get_current_user
from app.services.laptop_service import (
    create_laptop as svc_create_laptop,
    list_laptops as svc_list_laptops,
    get_laptop as svc_get_laptop,
    update_laptop as svc_update_laptop,
    delete_laptop as svc_delete_laptop,
)
from app.services.image_service import upload_image

# ------------------------------------------------------------------------------
# Router Configuration
# ------------------------------------------------------------------------------

# All laptop endpoints will be prefixed with /api/laptops
# tags=["laptops"] groups these endpoints together in the OpenAPI docs (Swagger UI)
router = APIRouter(prefix="/api/laptops", tags=["laptops"])


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
async def create_laptop_endpoint(
    laptop_data: LaptopCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new laptop listing.

    Flow for junior developers:
    1. Client sends laptop data in the request body (title, brand, model, condition, price, description)
    2. FastAPI validates the request using LaptopCreate model
    3. get_current_user dependency extracts the authenticated user from the JWT token
    4. We use the laptop service to create the listing
    5. We return the created laptop with its new ID and timestamps

    Authentication: Required (seller_id is set from the authenticated user's ID)
    """
    # Use laptop service to create the listing
    created_laptop = await svc_create_laptop(laptop_data, current_user["_id"])

    # Convert MongoDB document to API response format
    return LaptopResponse(**serialize_laptop(created_laptop))


@router.get("", response_model=list[LaptopResponse])
async def list_laptops_endpoint(
    skip: int = Query(default=0, ge=0, description="Number of laptops to skip (for pagination)"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of laptops to return (max 100)")
):
    """
    List all laptop listings with pagination.

    Flow for junior developers:
    1. Client can optionally provide skip and limit query parameters
    2. skip=0, limit=20 by default (returns the first 20 laptops)
    3. We use the laptop service to query the database with pagination
    4. We convert each laptop document to the response format
    5. We return the list of laptops

    Pagination example:
    - Page 1: skip=0, limit=20 → laptops 1-20
    - Page 2: skip=20, limit=20 → laptops 21-40

    Authentication: Not required (anyone can browse laptops)
    """
    # Use laptop service to list laptops
    laptops = await svc_list_laptops(skip, limit)

    # Convert each MongoDB document to the API response format
    return [LaptopResponse(**serialize_laptop(laptop)) for laptop in laptops]


@router.get("/{laptop_id}", response_model=LaptopResponse)
async def get_laptop_endpoint(laptop_id: str):
    """
    Get a single laptop listing by its ID.

    Flow for junior developers:
    1. Client provides the laptop ID in the URL path
    2. We use the laptop service to look up the laptop
    3. If found, we return it; if not, service raises 404 Not Found

    Authentication: Not required (anyone can view a laptop listing)
    """
    # Use laptop service to get the laptop (handles ID validation and 404)
    laptop = await svc_get_laptop(laptop_id)

    # Convert MongoDB document to API response format
    return LaptopResponse(**serialize_laptop(laptop))


@router.put("/{laptop_id}", response_model=LaptopResponse)
async def update_laptop_endpoint(
    laptop_id: str,
    laptop_data: LaptopUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing laptop listing.

    Flow for junior developers:
    1. Client provides the laptop ID in the URL and the fields to update in the request body
    2. We use the laptop service to update the listing (handles validation, ownership check)
    3. We return the updated laptop

    Authentication: Required (only the seller can update their laptop)
    Ownership check: Compares laptop["seller_id"] with current_user["_id"]
    """
    # Use laptop service to update the listing (handles ownership check and 403/404)
    updated_laptop = await svc_update_laptop(laptop_id, laptop_data, current_user["_id"])

    # Convert MongoDB document to API response format
    return LaptopResponse(**serialize_laptop(updated_laptop))


@router.delete("/{laptop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_laptop_endpoint(
    laptop_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a laptop listing.

    Flow for junior developers:
    1. Client provides the laptop ID in the URL path
    2. We use the laptop service to delete the listing (handles ownership check and 403/404)
    3. We return 204 No Content (standard for successful delete with no response body)

    Authentication: Required (only the seller can delete their laptop)
    Ownership check: Compares laptop["seller_id"] with current_user["_id"]
    """
    # Use laptop service to delete the listing (handles ownership check and 403/404)
    await svc_delete_laptop(laptop_id, current_user["_id"])

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
    2. We use the image service to handle validation, old image deletion, and saving
    3. We return the updated laptop with the new image URL

    Authentication: Required (only the seller can upload images for their laptop)
    """

    # Use image service to handle the upload (handles validation, ownership check, file operations)
    updated_laptop = await upload_image(
        laptop_id,
        "laptops",
        file,
        current_user["_id"],
        "seller_id"
    )

    # Convert MongoDB document to API response format
    return LaptopResponse(**serialize_laptop(updated_laptop))
