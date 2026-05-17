"""
Messages router for contact-us inquiries and admin replies.

Now routes all user messages to admins (single-company shop model).
"""

from fastapi import APIRouter, Depends, Query

from app.models.messages import MessageCreate, MessageResponse
from app.routers.auth import get_current_user
from app.services.message_service import (
    send_inquiry,
    get_conversation,
    get_user_conversations,
    get_all_conversations,
    admin_reply,
    get_listing_title,
)
from app.repositories.user_repo import UserRepository
from app.db.database import get_db

router = APIRouter(prefix="/api/messages", tags=["messages"])


def serialize_message(msg: dict) -> dict:
    """Convert a MongoDB message document to API response dict."""
    return {
        "id": str(msg["_id"]),
        "sender_id": str(msg["sender_id"]),
        "recipient_id": str(msg["recipient_id"]),
        "listing_id": str(msg["listing_id"]),
        "listing_type": msg["listing_type"],
        "content": msg["content"],
        "created_at": msg["created_at"].isoformat() if msg.get("created_at") else None,
        "is_admin_reply": msg.get("is_admin_reply", False),
    }


@router.post("/contact", response_model=MessageResponse, status_code=201)
async def send_contact_inquiry(
    body: MessageCreate,
    current_user: dict = Depends(get_current_user),
):
    """Send a contact inquiry about a listing. Routes to admins."""
    msg = await send_inquiry(
        current_user["_id"],
        body.listing_id,
        body.listing_type,
        body.content,
    )
    return MessageResponse(**serialize_message(msg))


@router.get("/conversation")
async def get_conversation_endpoint(
    listing_id: str = Query(),
    listing_type: str = Query(),
    current_user: dict = Depends(get_current_user),
):
    """Get all messages for a specific listing (user's own conversations)."""
    user_id = current_user["_id"]
    messages = await get_conversation(listing_id, listing_type, user_id=user_id)
    return [MessageResponse(**serialize_message(m)) for m in messages]


@router.get("/conversations")
async def my_conversations(current_user: dict = Depends(get_current_user)):
    """Get all unique conversations the user is involved in."""
    conversations = await get_user_conversations(current_user["_id"])
    result = []
    for c in conversations:
        lid = str(c["_id"]["listing_id"])
        ltype = c["_id"]["listing_type"]
        title = await get_listing_title(lid, ltype)
        result.append({
            "listing_id": lid,
            "listing_type": ltype,
            "listing_title": title,
            "last_message": c.get("last_message"),
            "last_message_at": c["last_at"].isoformat() if c.get("last_at") else None,
            "is_admin_reply": c.get("is_admin_reply", False),
        })
    return result


# --- Admin-only endpoints for managing inquiries ---


async def require_admin(current_user: dict = Depends(get_current_user)):
    """Ensure the current user is an admin."""
    if current_user.get("role") != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/admin/conversations")
async def admin_get_all_conversations(
    current_user: dict = Depends(require_admin),
):
    """Get ALL conversations (admin view)."""
    conversations = await get_all_conversations()
    return conversations


@router.get("/admin/conversation")
async def admin_get_conversation(
    listing_id: str = Query(),
    listing_type: str = Query(),
    current_user: dict = Depends(require_admin),
):
    """Get all messages for a specific listing (admin sees everything)."""
    messages = await get_conversation(listing_id, listing_type, user_id=None)
    return [MessageResponse(**serialize_message(m)) for m in messages]


@router.post("/admin/reply", response_model=MessageResponse, status_code=201)
async def admin_reply_to_conversation(
    body: MessageCreate,
    current_user: dict = Depends(require_admin),
):
    """Admin replies to a conversation about a listing."""
    msg = await admin_reply(
        current_user["_id"],
        body.listing_id,
        body.listing_type,
        body.content,
    )
    return MessageResponse(**serialize_message(msg))
