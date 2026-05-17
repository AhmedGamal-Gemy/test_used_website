"""
Order service for managing purchase orders.

Business logic for creating orders, listing user orders,
admin order management, and status updates.
HTTP concerns are handled in the router layer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId

from app.core.exceptions import NotFoundError, ValidationError
from app.db.database import Database
from app.models.orders import VALID_STATUSES


def _validate_id(id_str: str, label: str) -> ObjectId:
    """Validate and convert a string ID to ObjectId."""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError, ValueError):
        raise ValidationError(f"Invalid {label} ID format")


async def create_order(
    user_id: str, listing_id: str, listing_type: str, notes: str | None, db: Database
) -> dict:
    """Create a new order for a listing.

    Validates the listing exists in the correct collection,
    then creates an order document with status 'pending'.
    """
    if listing_type not in ("laptop", "part", "service"):
        raise ValidationError("listing_type must be 'laptop', 'part', or 'service'")

    listing_oid = _validate_id(listing_id, "listing")

    # Fetch the listing from the correct collection
    collection_map = {
        "laptop": db.laptops,
        "part": db.parts,
        "service": db.services,
    }
    listing_col = collection_map[listing_type]
    listing = await listing_col.find_one({"_id": listing_oid})

    if not listing:
        raise NotFoundError(f"{listing_type.capitalize()} listing not found")

    # Create order document
    order_doc = {
        "user_id": ObjectId(user_id),
        "listing_id": listing_oid,
        "listing_type": listing_type,
        "listing_title": listing.get("title", ""),
        "listing_price": listing.get("price"),
        "status": "pending",
        "notes": notes,
        "admin_notes": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
    }

    col = db.db["orders"]
    result = await col.insert_one(order_doc)
    order_doc["_id"] = result.inserted_id

    return order_doc


async def get_user_orders(user_id: str, db: Database) -> list[dict]:
    """Get all orders for a specific user, sorted by most recent first."""
    user_oid = _validate_id(user_id, "user")
    col = db.db["orders"]
    cursor = col.find({"user_id": user_oid}).sort("created_at", -1)
    return await cursor.to_list(length=100)


async def get_order(order_id: str, db: Database) -> dict:
    """Get a single order by its ID."""
    order_oid = _validate_id(order_id, "order")
    col = db.db["orders"]
    order = await col.find_one({"_id": order_oid})
    if not order:
        raise NotFoundError("Order not found")
    return order


async def get_all_orders(db: Database) -> list[dict]:
    """Get all orders (admin view), sorted by most recent first."""
    col = db.db["orders"]
    cursor = col.find().sort("created_at", -1)
    return await cursor.to_list(length=200)


async def update_order_status(
    order_id: str, new_status: str, admin_notes: str | None, db: Database
) -> dict:
    """Update the status of an order (admin only)."""
    if new_status not in VALID_STATUSES:
        raise ValidationError(f"Invalid status. Must be one of {VALID_STATUSES}")

    order_oid = _validate_id(order_id, "order")
    col = db.db["orders"]

    update_fields: dict = {
        "status": new_status,
        "updated_at": datetime.now(timezone.utc),
    }
    if admin_notes is not None:
        update_fields["admin_notes"] = admin_notes

    result = await col.find_one_and_update(
        {"_id": order_oid},
        {"$set": update_fields},
        return_document=True,
    )

    if not result:
        raise NotFoundError("Order not found")

    return result


async def order_to_response(order: dict, db: Database) -> dict:
    """Convert a MongoDB order document to an API response dict.

    Fetches the user's email from the users collection,
    converts ObjectId fields to strings, and formats datetime fields as ISO strings.
    """
    # Fetch user email
    user_id = order["user_id"]
    user = await db.users.find_one({"_id": user_id}, {"email": 1})
    user_email = user.get("email", "") if user else ""

    return {
        "id": str(order["_id"]),
        "user_id": str(order["user_id"]),
        "user_email": user_email,
        "listing_id": str(order["listing_id"]),
        "listing_type": order["listing_type"],
        "listing_title": order["listing_title"],
        "listing_price": order.get("listing_price"),
        "status": order["status"],
        "notes": order.get("notes"),
        "admin_notes": order.get("admin_notes"),
        "created_at": order["created_at"].isoformat() if order.get("created_at") else "",
        "updated_at": order["updated_at"].isoformat() if order.get("updated_at") else None,
    }
