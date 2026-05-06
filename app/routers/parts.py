"""
Parts CRUD router for creating, reading, updating, and deleting computer part listings.

HTTP layer only - delegates business logic to PartService.
"""

from fastapi import APIRouter, Depends, Query, UploadFile, File
from datetime import datetime
from bson import ObjectId

from app.models.parts import PartCreate, PartUpdate, PartResponse
from app.routers.auth import get_current_user
from app.services.part_service import PartService
from app.services.image_service import upload_image
from app.repositories.base import BaseRepository
from app.db.database import get_db

# Repository instance for part operations
part_repo = BaseRepository(get_db().parts)

router = APIRouter(prefix="/api/parts", tags=["parts"])

# Service instance with injected repository
part_service = PartService(part_repo)


def serialize_part(part: dict) -> dict:
    """Convert a MongoDB part document to a dictionary suitable for API response."""
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


@router.post("", response_model=PartResponse, status_code=201)
async def create_part_endpoint(
    part_data: PartCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new part listing."""
    created = await part_service.create(part_data, current_user["_id"])
    return PartResponse(**serialize_part(created))


@router.get("", response_model=list[PartResponse])
async def list_parts_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    category: str | None = Query(default=None),
    condition: str | None = Query(default=None),
    price_min: float | None = Query(default=None, ge=0),
    price_max: float | None = Query(default=None, ge=0),
    search: str | None = Query(default=None),
):
    """List all part listings with pagination and filtering."""
    parts = await part_service.search(
        category=category,
        condition=condition,
        price_min=price_min,
        price_max=price_max,
        search=search,
        skip=skip,
        limit=limit,
    )
    return [PartResponse(**serialize_part(part)) for part in parts]


@router.get("/{part_id}", response_model=PartResponse)
async def get_part_endpoint(part_id: str):
    """Get a single part listing by its ID."""
    part = await part_service.get(part_id)
    return PartResponse(**serialize_part(part))


@router.put("/{part_id}", response_model=PartResponse)
async def update_part_endpoint(
    part_id: str,
    part_data: PartUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update an existing part listing."""
    updated = await part_service.update(part_id, part_data, current_user["_id"])
    return PartResponse(**serialize_part(updated))


@router.delete("/{part_id}", status_code=204)
async def delete_part_endpoint(
    part_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a part listing."""
    await part_service.delete(part_id, current_user["_id"])


@router.post("/{part_id}/image", response_model=PartResponse)
async def upload_part_image(
    part_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload or replace the image for a part listing."""
    updated = await upload_image(
        part_id, get_db().parts, file, current_user["_id"], "seller_id"
    )
    return PartResponse(**serialize_part(updated))
