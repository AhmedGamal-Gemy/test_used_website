"""
Message service for buyer-seller communication per listing.

Business logic for sending, retrieving, and listing messages.
HTTP concerns are handled in the router layer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId

from app.core.exceptions import NotFoundError, ValidationError
from app.db.database import get_db


def _validate_id(id_str: str, label: str) -> ObjectId:
    """Validate and convert a string ID to ObjectId."""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError, ValueError):
        raise ValidationError(f"Invalid {label} ID format")


async def send_message(
    sender_id: str, recipient_id: str, listing_id: str, listing_type: str, content: str
) -> dict:
    """Send a message to a seller about a listing."""
    sender_oid = _validate_id(sender_id, "sender")
    recipient_oid = _validate_id(recipient_id, "recipient")
    listing_oid = _validate_id(listing_id, "listing")

    if listing_type not in ("laptop", "part"):
        raise ValidationError("listing_type must be 'laptop' or 'part'")

    col = get_db().messages

    msg_doc = {
        "sender_id": sender_oid,
        "recipient_id": recipient_oid,
        "listing_id": listing_oid,
        "listing_type": listing_type,
        "content": content,
        "created_at": datetime.now(timezone.utc),
    }

    result = await col.insert_one(msg_doc)
    msg_doc["_id"] = result.inserted_id
    return msg_doc


async def get_conversation(
    listing_id: str, listing_type: str
) -> list[dict]:
    """Get all messages for a specific listing, ordered newest first."""
    listing_oid = _validate_id(listing_id, "listing")
    col = get_db().messages

    cursor = col.find({
        "listing_id": listing_oid,
        "listing_type": listing_type,
    }).sort("created_at", 1)
    return await cursor.to_list(length=200)


async def get_user_conversations(user_id: str) -> list[dict]:
    """Get unique listing conversations the user is involved in."""
    user_oid = _validate_id(user_id, "user")
    col = get_db().messages

    pipeline = [
        {"$match": {"$or": [{"sender_id": user_oid}, {"recipient_id": user_oid}]}},
        {"$sort": {"created_at": -1}},
        {"$group": {
            "_id": {"listing_id": "$listing_id", "listing_type": "$listing_type"},
            "last_message": {"$first": "$content"},
            "last_at": {"$first": "$created_at"},
        }},
        {"$sort": {"last_at": -1}},
    ]

    cursor = await col.aggregate(pipeline)
    return await cursor.to_list(length=50)


async def get_listing_owner(listing_id: str, listing_type: str) -> str | None:
    """Get the owner (seller) ID of a listing."""
    listing_oid = _validate_id(listing_id, "listing")
    collection_name = "laptops" if listing_type == "laptop" else "parts"
    col = get_db().db[collection_name]

    listing = await col.find_one({"_id": listing_oid}, {"seller_id": 1})
    if listing:
        return str(listing.get("seller_id"))
    return None
