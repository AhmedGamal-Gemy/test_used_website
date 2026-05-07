"""
Review service for managing seller ratings and reviews.

Business logic for creating reviews and computing aggregate ratings.
HTTP concerns are handled in the router layer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.db.database import get_db


def _validate_id(id_str: str, label: str) -> ObjectId:
    """Validate and convert a string ID to ObjectId."""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError, ValueError):
        raise ValidationError(f"Invalid {label} ID format")


async def create_review(
    reviewer_id: str, seller_id: str, rating: int, comment: str
) -> dict:
    """Create a review for a seller. Raises ConflictError if reviewer already rated this seller."""
    reviewer_oid = _validate_id(reviewer_id, "reviewer")
    seller_oid = _validate_id(seller_id, "seller")

    if reviewer_oid == seller_oid:
        raise ValidationError("You cannot review yourself")

    reviews_col = get_db().reviews

    # Check if reviewer already rated this seller
    existing = await reviews_col.find_one({
        "reviewer_id": reviewer_oid,
        "seller_id": seller_oid,
    })
    if existing:
        raise ConflictError("You already reviewed this seller")

    review_doc = {
        "reviewer_id": reviewer_oid,
        "seller_id": seller_oid,
        "rating": rating,
        "comment": comment,
        "created_at": datetime.now(timezone.utc),
    }

    result = await reviews_col.insert_one(review_doc)
    review_doc["_id"] = result.inserted_id
    return review_doc


async def get_seller_reviews(seller_id: str) -> list[dict]:
    """Get all reviews for a seller."""
    seller_oid = _validate_id(seller_id, "seller")
    reviews_col = get_db().reviews

    cursor = reviews_col.find({"seller_id": seller_oid}).sort("created_at", -1)
    return await cursor.to_list(length=100)


async def get_seller_rating(seller_id: str) -> dict:
    """Get aggregate rating stats for a seller."""
    reviews = await get_seller_reviews(seller_id)
    if not reviews:
        return {
            "seller_id": seller_id,
            "average_rating": 0.0,
            "total_reviews": 0,
            "reviews": [],
        }

    total = sum(r["rating"] for r in reviews)
    return {
        "seller_id": seller_id,
        "average_rating": round(total / len(reviews), 1),
        "total_reviews": len(reviews),
        "reviews": reviews,
    }