"""
Orders router for managing purchase orders.

Provides endpoints for users to create and view orders,
and for admins to manage all orders and update statuses.
"""

from fastapi import APIRouter, Depends, status

from app.models.orders import OrderCreate, OrderStatusUpdate, OrderResponse
from app.routers.auth import get_current_user
from app.services.order_service import (
    create_order,
    get_user_orders,
    get_order,
    get_all_orders,
    update_order_status,
    order_to_response,
)
from app.db.database import get_db

router = APIRouter(prefix="/api", tags=["orders"])


async def require_admin(current_user: dict = Depends(get_current_user)):
    """Ensure the current user is an admin."""
    if current_user.get("role") != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order_endpoint(
    body: OrderCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new order for a listing.

    Validates the listing exists and creates an order with status 'pending'.
    The listing_type must be 'laptop', 'part', or 'service'.
    """
    db = get_db()
    order = await create_order(
        str(current_user["_id"]),
        body.listing_id,
        body.listing_type,
        body.notes,
        db,
    )
    return OrderResponse(**await order_to_response(order, db))


@router.get("/orders", response_model=list[OrderResponse])
async def list_user_orders(
    current_user: dict = Depends(get_current_user),
):
    """Get all orders for the currently authenticated user."""
    db = get_db()
    orders = await get_user_orders(str(current_user["_id"]), db)
    return [OrderResponse(**await order_to_response(o, db)) for o in orders]


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order_endpoint(
    order_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a single order by ID.

    Users can only view their own orders.
    Admins can view any order.
    """
    db = get_db()
    order = await get_order(order_id, db)

    # Security check: user must own the order or be admin
    user_id = str(current_user["_id"])
    order_user_id = str(order["user_id"])
    if order_user_id != user_id and current_user.get("role") != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not authorized to view this order")

    return OrderResponse(**await order_to_response(order, db))


@router.get("/admin/orders", response_model=list[OrderResponse])
async def admin_get_all_orders(
    current_user: dict = Depends(require_admin),
):
    """Get all orders (admin view). Returns every order in the system."""
    db = get_db()
    orders = await get_all_orders(db)
    return [OrderResponse(**await order_to_response(o, db)) for o in orders]


@router.put("/admin/orders/{order_id}/status", response_model=OrderResponse)
async def admin_update_order_status(
    order_id: str,
    body: OrderStatusUpdate,
    current_user: dict = Depends(require_admin),
):
    """Update the status of an order (admin only).

    Valid statuses: pending, confirmed, processing, shipped, completed, cancelled.
    """
    db = get_db()
    order = await update_order_status(order_id, body.status, body.admin_notes, db)
    return OrderResponse(**await order_to_response(order, db))
