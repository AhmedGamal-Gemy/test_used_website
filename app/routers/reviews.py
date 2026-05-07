"""
Reviews router for rating sellers and viewing aggregate ratings.

HTTP layer only - delegates business logic to review_service.
"""

from fastapi import APIRouter, Depends

from app.models.reviews import ReviewCreate, ReviewResponse, SellerRatingResponse
from app.routers.auth import get_current_user
from app.services.review_service import create_review, get_seller_reviews, get_seller_rating
from app.db.database import get_db

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


def serialize_review(review: dict) -> dict:
    """Convert a MongoDB review document to API response dict."""
    return {
        "id": str(review["_id"]),
        "reviewer_id": str(review["reviewer_id"]),
        "reviewer_name": review.get("reviewer_name"),
        "seller_id": str(review["seller_id"]),
        "rating": review["rating"],
        "comment": review.get("comment", ""),
        "created_at": review["created_at"].isoformat() if review.get("created_at") else None,
    }


@router.post("/seller/{seller_id}", status_code=201)
async def add_review(
    seller_id: str,
    review_data: ReviewCreate,
    current_user: dict = Depends(get_current_user),
):
    """Rate a seller (1-5 stars with optional comment)."""
    review = await create_review(
        current_user["_id"],
        seller_id,
        review_data.rating,
        review_data.comment,
    )
    return ReviewResponse(**serialize_review(review))


@router.get("/seller/{seller_id}", response_model=SellerRatingResponse)
async def get_seller_rating_endpoint(seller_id: str):
    """Get a seller's aggregate rating and all reviews."""
    data = await get_seller_rating(seller_id)
    serialized_reviews = [serialize_review(r) for r in data["reviews"]]
    return SellerRatingResponse(
        seller_id=data["seller_id"],
        average_rating=data["average_rating"],
        total_reviews=data["total_reviews"],
        reviews=[ReviewResponse(**serialize_review(r)) for r in data["reviews"]],
    )