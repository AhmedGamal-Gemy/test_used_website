"""
Messages router for buyer-seller communication per listing.

HTTP layer only - delegates business logic to message_service.
"""

from fastapi import APIRouter, Depends, Query

from app.models.messages import MessageCreate, MessageResponse, ConversationResponse
from app.routers.auth import get_current_user
from app.services.message_service import (
    send_message,
    get_conversation,
    get_user_conversations,
    get_listing_owner,
)

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
    }


@router.post("", response_model=MessageResponse, status_code=201)
async def send(
    msg_data: MessageCreate,
    listing_id: str = Query(description="Listing ID to message about"),
    listing_type: str = Query(description="Type: 'laptop' or 'part'"),
    current_user: dict = Depends(get_current_user),
):
    """Send a message to a seller about a listing."""
    seller_id = await get_listing_owner(listing_id, listing_type)
    if not seller_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Listing not found")

    if seller_id == current_user["_id"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="You cannot message yourself")

    msg = await send_message(
        current_user["_id"],
        seller_id,
        listing_id,
        listing_type,
        msg_data.content,
    )
    return MessageResponse(**serialize_message(msg))


@router.get("/conversation")
async def get_conversation_endpoint(
    listing_id: str = Query(),
    listing_type: str = Query(),
    current_user: dict = Depends(get_current_user),
):
    """Get all messages for a specific listing (conversation thread)."""
    messages = await get_conversation(listing_id, listing_type)
    return [MessageResponse(**serialize_message(m)) for m in messages]


@router.get("/conversations")
async def my_conversations(current_user: dict = Depends(get_current_user)):
    """Get all unique conversations the user is involved in."""
    conversations = await get_user_conversations(current_user["_id"])
    return [
        {
            "listing_id": str(c["_id"]["listing_id"]),
            "listing_type": c["_id"]["listing_type"],
            "last_message": c["last_message"],
            "last_at": c["last_at"].isoformat() if c.get("last_at") else None,
        }
        for c in conversations
    ]
