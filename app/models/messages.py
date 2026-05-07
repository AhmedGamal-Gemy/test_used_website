"""
Pydantic schemas for buyer-seller messaging system.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Schema for sending a message."""
    content: str = Field(min_length=1, max_length=2000, description="Message text")


class MessageResponse(BaseModel):
    """Schema returned for a single message."""
    id: str
    sender_id: str
    recipient_id: str
    listing_id: str
    listing_type: str  # "laptop" or "part"
    content: str
    created_at: str | None = None


class ConversationResponse(BaseModel):
    """Schema for a conversation thread."""
    listing_id: str
    listing_type: str
    listing_title: str
    messages: list[MessageResponse]
