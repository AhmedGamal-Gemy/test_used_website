"""
Services router for repair/fixing service listings.

HTTP layer only - delegates business logic to ServiceService.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Query
from bson import ObjectId

from app.models.services import ServiceCreate, ServiceUpdate
from app.routers.auth import get_current_user
from app.services.service_service import ServiceService
from app.repositories.base import BaseRepository
from app.db.database import get_db

router = APIRouter(prefix="/api/services", tags=["services"])


def get_service_service() -> ServiceService:
    db = get_db()
    return ServiceService(BaseRepository(db.services))


@router.post("")
async def create_service(
    data: ServiceCreate,
    current_user: dict = Depends(get_current_user),
    service_service: ServiceService = Depends(get_service_service),
):
    """Create a new service listing (admin only)."""
    service = await service_service.create(data, current_user["_id"])
    return {"data": _format_service(service)}


@router.get("")
async def list_services(
    service_type: str | None = Query(None, alias="service_type"),
    brand: str | None = Query(None),
    min_price: float | None = Query(None, alias="min_price"),
    max_price: float | None = Query(None, alias="max_price"),
    search: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service_service: ServiceService = Depends(get_service_service),
):
    """List services with optional filters."""
    services = await service_service.search(service_type, brand, min_price, max_price, search, skip, limit)
    return {"data": [_format_service(s) for s in services]}


@router.get("/{service_id}")
async def get_service(
    service_id: str,
    service_service: ServiceService = Depends(get_service_service),
):
    """Get a single service listing."""
    service = await service_service.get(service_id)
    return {"data": _format_service(service)}


@router.put("/{service_id}")
async def update_service(
    service_id: str,
    data: ServiceUpdate,
    current_user: dict = Depends(get_current_user),
    service_service: ServiceService = Depends(get_service_service),
):
    """Update a service listing (admin only)."""
    service = await service_service.update(service_id, data, current_user["_id"])
    return {"data": _format_service(service)}


@router.delete("/{service_id}")
async def delete_service(
    service_id: str,
    current_user: dict = Depends(get_current_user),
    service_service: ServiceService = Depends(get_service_service),
):
    """Delete a service listing (admin only)."""
    await service_service.delete(service_id, current_user["_id"])
    return {"message": "Service deleted successfully"}


def _format_service(service: dict) -> dict:
    """Format service document for API response."""
    return {
        "id": str(service["_id"]),
        "title": service.get("title"),
        "description": service.get("description"),
        "price": service.get("price"),
        "service_type": service.get("service_type"),
        "brand": service.get("brand"),
        "turnaround_time": service.get("turnaround_time"),
        "warranty_days": service.get("warranty_days"),
        "image_url": service.get("image_url"),
        "seller_id": str(service.get("seller_id")),
        "created_at": str(service.get("created_at")),
        "updated_at": str(service.get("updated_at")),
    }
