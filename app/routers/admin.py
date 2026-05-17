"""
Admin router for bulk operations on marketplace resources.

All endpoints require admin privileges.
"""

from fastapi import APIRouter, Depends, Body
from bson import ObjectId

from app.routers.auth import get_current_user
from app.services.laptop_service import LaptopService
from app.services.part_service import PartService
from app.services.service_service import ServiceService
from app.repositories.base import BaseRepository
from app.repositories.user_repo import UserRepository
from app.db.database import get_db

router = APIRouter(prefix="/api/admin/bulk-delete", tags=["admin"])


async def require_admin(current_user: dict = Depends(get_current_user)):
    """Ensure the current user is an admin."""
    if current_user.get("role") != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.post("/laptops")
async def bulk_delete_laptops(
    body: dict = Body(...),
    current_user: dict = Depends(require_admin),
):
    """Delete multiple laptop listings by IDs (admin only)."""
    ids = body.get("ids", [])
    if not isinstance(ids, list) or not ids:
        return {"deleted": 0, "errors": []}
    repo = BaseRepository(get_db().laptops)
    service = LaptopService(repo)
    return await service.bulk_delete(ids, current_user["_id"])


@router.post("/parts")
async def bulk_delete_parts(
    body: dict = Body(...),
    current_user: dict = Depends(require_admin),
):
    """Delete multiple part listings by IDs (admin only)."""
    ids = body.get("ids", [])
    if not isinstance(ids, list) or not ids:
        return {"deleted": 0, "errors": []}
    repo = BaseRepository(get_db().parts)
    service = PartService(repo)
    return await service.bulk_delete(ids, current_user["_id"])


@router.post("/services")
async def bulk_delete_services(
    body: dict = Body(...),
    current_user: dict = Depends(require_admin),
):
    """Delete multiple service listings by IDs (admin only)."""
    ids = body.get("ids", [])
    if not isinstance(ids, list) or not ids:
        return {"deleted": 0, "errors": []}
    repo = BaseRepository(get_db().services)
    service = ServiceService(repo)
    return await service.bulk_delete(ids, current_user["_id"])


@router.post("/users")
async def bulk_delete_users(
    body: dict = Body(...),
    current_user: dict = Depends(require_admin),
):
    """Delete multiple user accounts by IDs (admin only)."""
    ids = body.get("ids", [])
    if not isinstance(ids, list) or not ids:
        return {"deleted": 0, "errors": []}

    # Prevent admin from deleting themselves
    caller_id = str(current_user["_id"])
    filtered_ids = [uid for uid in ids if uid != caller_id]
    skipped_self = len(ids) != len(filtered_ids)

    repo = BaseRepository(get_db().users)
    result = await repo.delete_many(filtered_ids)
    resp = {"deleted": result, "errors": []}
    if skipped_self:
        resp["errors"] = [{"id": caller_id, "error": "Cannot delete your own account"}]
    return resp
