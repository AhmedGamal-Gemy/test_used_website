"""
Message service for contact-us inquiries and admin replies.

Business logic for sending inquiries, admin replying, retrieving conversations.
Now routes all user messages to admins (single-company shop model).
HTTP concerns are handled in the router layer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId

from app.core.exceptions import NotFoundError, ValidationError
from app.db.database import get_db
from app.repositories.user_repo import UserRepository


def _validate_id(id_str: str, label: str) -> ObjectId:
    """Validate and convert a string ID to ObjectId."""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError, ValueError):
        raise ValidationError(f"Invalid {label} ID format")


async def get_admin_user() -> dict | None:
    """Get the first admin user to route messages to."""
    col = get_db().users
    admin = await col.find_one({"role": "admin"})
    return admin


async def send_inquiry(
    sender_id: str, listing_id: str, listing_type: str, content: str
) -> dict:
    """Send an inquiry about a listing. Routes to an admin."""
    sender_oid = _validate_id(sender_id, "sender")
    listing_oid = _validate_id(listing_id, "listing")

    if listing_type not in ("laptop", "part", "service"):
        raise ValidationError("listing_type must be 'laptop', 'part', or 'service'")

    # Find an admin to route the message to
    admin = await get_admin_user()
    if not admin:
        raise ValidationError("No admin available to receive messages")

    recipient_oid = admin["_id"]

    col = get_db().messages

    msg_doc = {
        "sender_id": sender_oid,
        "recipient_id": recipient_oid,
        "listing_id": listing_oid,
        "listing_type": listing_type,
        "content": content,
        "created_at": datetime.now(timezone.utc),
        "is_admin_reply": False,
    }

    result = await col.insert_one(msg_doc)
    msg_doc["_id"] = result.inserted_id

    return msg_doc


async def admin_reply(
    admin_id: str, listing_id: str, listing_type: str, content: str
) -> dict:
    """Admin replies to a conversation thread about a listing.
    
    Finds the original sender of the first message in this conversation
    and sends the reply to them.
    """
    admin_oid = _validate_id(admin_id, "admin")
    listing_oid = _validate_id(listing_id, "listing")

    if listing_type not in ("laptop", "part", "service"):
        raise ValidationError("listing_type must be 'laptop', 'part', or 'service'")

    col = get_db().messages

    # Find the first message in this conversation to get the original sender
    first_msg = await col.find_one(
        {"listing_id": listing_oid, "listing_type": listing_type},
        sort=[("created_at", 1)],
    )
    if not first_msg:
        raise NotFoundError("No conversation found for this listing")

    # The recipient is the original sender (they're the customer)
    recipient_id = first_msg["sender_id"]

    msg_doc = {
        "sender_id": admin_oid,
        "recipient_id": recipient_id,
        "listing_id": listing_oid,
        "listing_type": listing_type,
        "content": content,
        "created_at": datetime.now(timezone.utc),
        "is_admin_reply": True,
    }

    result = await col.insert_one(msg_doc)
    msg_doc["_id"] = result.inserted_id

    return msg_doc


async def get_conversation(
    listing_id: str, listing_type: str, user_id: str | None = None
) -> list[dict]:
    """Get all messages for a specific listing.
    
    If user_id is provided, only returns messages where the user is
    either sender or recipient (user privacy filter).
    If user_id is None, returns ALL messages (admin view).
    """
    listing_oid = _validate_id(listing_id, "listing")
    col = get_db().messages

    query: dict = {
        "listing_id": listing_oid,
        "listing_type": listing_type,
    }

    if user_id is not None:
        user_oid = _validate_id(user_id, "user")
        query["$or"] = [
            {"sender_id": user_oid},
            {"recipient_id": user_oid},
        ]

    cursor = col.find(query).sort("created_at", 1)
    return await cursor.to_list(length=200)


async def get_user_conversations(user_id: str) -> list[dict]:
    """Get unique conversations the user is involved in."""
    user_oid = _validate_id(user_id, "user")
    col = get_db().messages

    pipeline = [
        {"$match": {"$or": [{"sender_id": user_oid}, {"recipient_id": user_oid}]}},
        {"$sort": {"created_at": -1}},
        {"$group": {
            "_id": {"listing_id": "$listing_id", "listing_type": "$listing_type"},
            "last_message": {"$first": "$content"},
            "last_at": {"$first": "$created_at"},
            "is_admin_reply": {"$first": "$is_admin_reply"},
        }},
        {"$sort": {"last_at": -1}},
    ]

    cursor = await col.aggregate(pipeline)
    return await cursor.to_list(length=50)


async def get_all_conversations() -> list[dict]:
    """Get ALL unique conversations (admin view)."""
    db = get_db()
    col = db.messages

    pipeline = [
        {"$sort": {"created_at": -1}},
        {"$group": {
            "_id": {"listing_id": "$listing_id", "listing_type": "$listing_type"},
            "last_message": {"$first": "$content"},
            "last_at": {"$first": "$created_at"},
            "sender_id": {"$first": "$sender_id"},
            "message_count": {"$sum": 1},
        }},
        {"$sort": {"last_at": -1}},
        {"$limit": 100},
    ]

    cursor = await col.aggregate(pipeline)
    conversations = await cursor.to_list(length=100)

    user_repo = UserRepository(db.users)

    # Enrich with user info and listing info
    enriched = []
    for conv in conversations:
        listing_id_str = str(conv["_id"]["listing_id"])
        listing_type = conv["_id"]["listing_type"]

        # Get listing title
        collection_map = {"laptop": "laptops", "part": "parts", "service": "services"}
        collection_name = collection_map.get(listing_type)
        listing_title = None
        if collection_name:
            listing_col = getattr(db.db, collection_name, None)
            if listing_col is not None:
                listing = await listing_col.find_one(
                    {"_id": ObjectId(listing_id_str)},
                    {"title": 1}
                )
                if listing:
                    listing_title = listing.get("title")

        # Get sender info
        sender_id = str(conv["sender_id"]) if isinstance(conv["sender_id"], ObjectId) else conv["sender_id"]
        sender = await user_repo.find_by_id(sender_id)

        enriched.append({
            "listing_id": listing_id_str,
            "listing_type": listing_type,
            "listing_title": listing_title,
            "last_message": conv.get("last_message"),
            "last_at": conv["last_at"].isoformat() if conv.get("last_at") else None,
            "sender_email": sender.get("email") if sender else "Unknown",
            "sender_name": sender.get("full_name") if sender else None,
            "message_count": conv.get("message_count", 0),
        })

    return enriched


async def get_listing_title(listing_id: str, listing_type: str) -> str | None:
    """Get the title of a listing."""
    listing_oid = _validate_id(listing_id, "listing")
    collection_map = {
        "laptop": "laptops",
        "part": "parts",
        "service": "services",
    }
    collection_name = collection_map.get(listing_type)
    if not collection_name:
        return None

    col = get_db().db[collection_name]
    if col is None:
        return None

    listing = await col.find_one({"_id": listing_oid}, {"title": 1})
    if listing:
        return listing.get("title")
    return None
