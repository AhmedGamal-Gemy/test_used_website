"""
Pydantic schemas for order management.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, field_validator


VALID_STATUSES = ["pending", "confirmed", "processing", "shipped", "completed", "cancelled"]


class OrderCreate(BaseModel):
    """Schema for creating a new order."""
    listing_id: str
    listing_type: str
    notes: Optional[str] = None

    @field_validator("listing_type")
    @classmethod
    def validate_listing_type(cls, v: str) -> str:
        if v not in ("laptop", "part", "service"):
            raise ValueError("listing_type must be 'laptop', 'part', or 'service'")
        return v


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    status: str
    admin_notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}")
        return v


class OrderResponse(BaseModel):
    """Schema returned for an order."""
    id: str
    user_id: str
    user_email: str
    listing_id: str
    listing_type: str
    listing_title: str
    listing_price: Optional[float] = None
    status: str
    notes: Optional[str] = None
    admin_notes: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
