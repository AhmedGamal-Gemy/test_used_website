"""
Laptop CRUD router for creating, reading, updating, and deleting laptop listings.

HTTP layer only - delegates business logic to LaptopService.
"""

from fastapi import APIRouter, Depends, Query, UploadFile, File
from datetime import datetime
from bson import ObjectId

from app.models.laptops import LaptopCreate, LaptopUpdate, LaptopResponse
from app.routers.auth import get_current_user
from app.services.laptop_service import LaptopService
from app.services.image_service import upload_image
from app.repositories.base import BaseRepository
from app.db.database import get_db

# Repository instance for laptop operations
laptop_repo = BaseRepository(get_db().laptops)

router = APIRouter(prefix="/api/laptops", tags=["laptops"])

# Service instance with injected repository
laptop_service = LaptopService(laptop_repo)


def serialize_laptop(laptop: dict) -> dict:
    """Convert a MongoDB laptop document to a dictionary suitable for API response."""
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


@router.post("", response_model=LaptopResponse, status_code=201)
async def create_laptop_endpoint(
    laptop_data: LaptopCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new laptop listing."""
    created = await laptop_service.create(laptop_data, current_user["_id"])
    return LaptopResponse(**serialize_laptop(created))


@router.get("", response_model=list[LaptopResponse])
async def list_laptops_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    brand: str | None = Query(default=None),
    condition: str | None = Query(default=None),
    price_min: float | None = Query(default=None, ge=0),
    price_max: float | None = Query(default=None, ge=0),
    search: str | None = Query(default=None),
):
    """List all laptop listings with pagination and filtering."""
    laptops = await laptop_service.search(
        brand=brand,
        condition=condition,
        price_min=price_min,
        price_max=price_max,
        search=search,
        skip=skip,
        limit=limit,
    )
    return [LaptopResponse(**serialize_laptop(laptop)) for laptop in laptops]


@router.get("/{laptop_id}", response_model=LaptopResponse)
async def get_laptop_endpoint(laptop_id: str):
    """Get a single laptop listing by its ID."""
    laptop = await laptop_service.get(laptop_id)
    return LaptopResponse(**serialize_laptop(laptop))


@router.put("/{laptop_id}", response_model=LaptopResponse)
async def update_laptop_endpoint(
    laptop_id: str,
    laptop_data: LaptopUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update an existing laptop listing."""
    updated = await laptop_service.update(laptop_id, laptop_data, current_user["_id"])
    return LaptopResponse(**serialize_laptop(updated))


@router.delete("/{laptop_id}", status_code=204)
async def delete_laptop_endpoint(
    laptop_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a laptop listing."""
    await laptop_service.delete(laptop_id, current_user["_id"])


@router.post("/{laptop_id}/image", response_model=LaptopResponse)
async def upload_laptop_image(
    laptop_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload or replace the image for a laptop listing."""
    updated = await upload_image(
        laptop_id, get_db().laptops, file, current_user["_id"], "seller_id"
    )
    return LaptopResponse(**serialize_laptop(updated))
