"""
Pydantic schemas for review and rating system.
"""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    """Schema for creating a review."""
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: str = Field(max_length=500, default="")


class ReviewResponse(BaseModel):
    """Schema returned for a review."""
    id: str
    reviewer_id: str
    reviewer_name: str | None = None
    seller_id: str
    rating: int
    comment: str
    created_at: str | None = None


class SellerRatingResponse(BaseModel):
    """Schema for seller's aggregate rating."""
    seller_id: str
    average_rating: float
    total_reviews: int
    reviews: list[ReviewResponse]