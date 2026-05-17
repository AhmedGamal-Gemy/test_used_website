"""
User profile router for viewing and updating user profiles.

HTTP layer only - delegates business logic to user_service.
"""

from fastapi import APIRouter, Depends
from bson import ObjectId

from app.models.auth import UserProfileResponse, UserProfileUpdate
from app.routers.auth import get_current_user
from app.services.user_service import get_user_profile, update_user_profile
from app.repositories.user_repo import UserRepository
from app.db.database import get_db

user_repo = UserRepository(get_db().users)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Get the authenticated user's own profile."""
    user = await get_user_profile(current_user["_id"], user_repo)
    return UserProfileResponse(
        id=str(user["_id"]),
        email=user["email"],
        full_name=user.get("full_name"),
        phone=user.get("phone"),
        location=user.get("location"),
        avatar_url=user.get("avatar_url"),
        role=user.get("role", "user"),
        favorite_laptops=[str(oid) for oid in user.get("favorite_laptops", [])],
        favorite_parts=[str(oid) for oid in user.get("favorite_parts", [])],
    )


@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update the authenticated user's own profile."""
    update_dict = profile_data.model_dump(exclude_unset=True)
    user = await update_user_profile(current_user["_id"], update_dict, user_repo)
    return UserProfileResponse(
        id=str(user["_id"]),
        email=user["email"],
        full_name=user.get("full_name"),
        phone=user.get("phone"),
        location=user.get("location"),
        avatar_url=user.get("avatar_url"),
        role=user.get("role", "user"),
    )


@router.get("/", tags=["admin"])
async def list_users(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
):
    """List all users (admin only)."""
    if current_user.get("role") != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = await user_repo.list(skip, limit)
    return [
        {
            "id": str(u["_id"]),
            "email": u["email"],
            "full_name": u.get("full_name"),
            "role": u.get("role", "user"),
            "created_at": u.get("created_at"),
        }
        for u in users
    ]


@router.patch("/{user_id}/role", tags=["admin"])
async def update_user_role(
    user_id: str,
    body: dict,
    current_user: dict = Depends(get_current_user),
):
    """Update user role (admin only)."""
    if current_user.get("role") != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    
    role = body.get("role")
    if role not in ["admin", "user"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'admin' or 'user'")
    
    await user_repo.update(user_id, {"role": role})
    return {"message": f"User role updated to {role}"}


@router.delete("/{user_id}", tags=["admin"])
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a user account (admin only). Cannot delete yourself."""
    if current_user.get("role") != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")

    caller_id = str(current_user["_id"])
    if user_id == caller_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    await user_repo.delete(user_id)
    return {"message": "User deleted successfully"}


@router.get("/analytics/dashboard", tags=["admin"])
async def get_dashboard_analytics(
    current_user: dict = Depends(get_current_user),
):
    """Get dashboard analytics (admin only)."""
    if current_user.get("role") != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_db()
    
    # Count all collections
    total_users = await db.users.count_documents({})
    total_laptops = await db.laptops.count_documents({})
    total_parts = await db.parts.count_documents({})
    total_services = await db.services.count_documents({}) if "services" in await db.db.list_collection_names() else 0
    total_reviews = await db.reviews.count_documents({})
    total_messages = await db.messages.count_documents({})
    total_favorites = 0
    
    # Count favorites
    try:
        laptop_favs_cursor = await db.laptops.aggregate([
            {"$match": {"favorite_count": {"$exists": True}}},
            {"$group": {"_id": None, "total": {"$sum": "$favorite_count"}}}
        ])
        laptop_favs = await laptop_favs_cursor.to_list(1)
        total_favorites = laptop_favs[0]["total"] if laptop_favs else 0
    except:
        pass
    
    # Count admin users
    total_admins = await db.users.count_documents({"role": "admin"})
    
    # Get activity (recently created listings)
    from datetime import datetime, timezone, timedelta
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    recent_laptops = await db.laptops.count_documents({"created_at": {"$gte": thirty_days_ago}})
    recent_parts = await db.parts.count_documents({"created_at": {"$gte": thirty_days_ago}})
    
    # --- New analytics ---
    
    # User signups over time (last 6 months)
    six_months_ago = datetime.now(timezone.utc) - timedelta(days=180)
    user_signups_pipeline = [
        {"$match": {"created_at": {"$gte": six_months_ago}}},
        {"$group": {
            "_id": {"year": {"$year": "$created_at"}, "month": {"$month": "$created_at"}},
            "count": {"$sum": 1},
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1}},
    ]
    try:
        signups_cursor = await db.users.aggregate(user_signups_pipeline)
        user_signups = await signups_cursor.to_list(length=12)
        user_signups_data = [
            {
                "year": s["_id"]["year"],
                "month": s["_id"]["month"],
                "count": s["count"],
            }
            for s in user_signups
        ]
    except Exception:
        user_signups_data = []
    
    # Message inquiry stats
    total_inquiries = await db.messages.count_documents({"is_admin_reply": {"$ne": True}})
    total_replies = await db.messages.count_documents({"is_admin_reply": True})
    unanswered_inquiries = 0
    try:
        # Conversations where the last message is not an admin reply
        conv_pipeline = [
            {"$sort": {"created_at": -1}},
            {"$group": {
                "_id": {"listing_id": "$listing_id", "listing_type": "$listing_type"},
                "last_is_admin_reply": {"$first": "$is_admin_reply"},
            }},
            {"$match": {"last_is_admin_reply": {"$ne": True}}},
            {"$count": "count"},
        ]
        result_cursor = await db.messages.aggregate(conv_pipeline)
        result = await result_cursor.to_list(1)
        unanswered_inquiries = result[0]["count"] if result else 0
    except Exception:
        pass
    
    total_conversations = 0
    try:
        conv_cursor = await db.messages.aggregate([
            {"$group": {
                "_id": {"listing_id": "$listing_id", "listing_type": "$listing_type"},
            }},
            {"$count": "count"},
        ])
        conv_count = await conv_cursor.to_list(1)
        total_conversations = conv_count[0]["count"] if conv_count else 0
    except Exception:
        pass
    
    # Most favorited listings (top 5)
    top_favorited = []
    try:
        laptop_favs_pipeline = [
            {"$match": {"favorite_count": {"$exists": True, "$gt": 0}}},
            {"$sort": {"favorite_count": -1}},
            {"$limit": 5},
            {"$project": {"title": 1, "favorite_count": 1, "price": 1}},
        ]
        part_favs_pipeline = [
            {"$match": {"favorite_count": {"$exists": True, "$gt": 0}}},
            {"$sort": {"favorite_count": -1}},
            {"$limit": 5},
            {"$project": {"title": 1, "favorite_count": 1, "price": 1}},
        ]
        top_laptops_cursor = await db.laptops.aggregate(laptop_favs_pipeline)
        top_laptops = await top_laptops_cursor.to_list(5)
        top_parts_cursor = await db.parts.aggregate(part_favs_pipeline)
        top_parts = await top_parts_cursor.to_list(5)
        for t in top_laptops:
            top_favorited.append({
                "title": t.get("title", "Untitled"),
                "type": "laptop",
                "favorite_count": t.get("favorite_count", 0),
                "price": t.get("price"),
            })
        for t in top_parts:
            top_favorited.append({
                "title": t.get("title", "Untitled"),
                "type": "part",
                "favorite_count": t.get("favorite_count", 0),
                "price": t.get("price"),
            })
        top_favorited.sort(key=lambda x: x["favorite_count"], reverse=True)
        top_favorited = top_favorited[:5]
    except Exception:
        pass
    
    # Listing price ranges (for laptops only)
    price_ranges = {"budget": 0, "mid": 0, "premium": 0}
    try:
        laptop_prices_cursor = await db.laptops.aggregate([
            {"$match": {"price": {"$exists": True}}},
            {"$project": {
                "range": {
                    "$cond": [
                        {"$lte": ["$price", 500]},
                        "budget",
                        {"$cond": [
                            {"$lte": ["$price", 1500]},
                            "mid",
                            "premium"
                        ]}
                    ]
                }
            }},
            {"$group": {"_id": "$range", "count": {"$sum": 1}}},
        ])
        laptop_prices = await laptop_prices_cursor.to_list(10)
        for r in laptop_prices:
            price_ranges[r["_id"]] = r["count"]
    except Exception:
        pass
    
    return {
        "total_users": total_users,
        "total_admins": total_admins,
        "total_laptops": total_laptops,
        "total_parts": total_parts,
        "total_services": total_services,
        "total_reviews": total_reviews,
        "total_messages": total_messages,
        "total_favorites": total_favorites,
        "total_listings": total_laptops + total_parts + total_services,
        "recent_activity_30d": recent_laptops + recent_parts,
        "recent_laptops_30d": recent_laptops,
        "recent_parts_30d": recent_parts,
        # New analytics
        "user_signups": user_signups_data,
        "total_inquiries": total_inquiries,
        "total_admin_replies": total_replies,
        "unanswered_inquiries": unanswered_inquiries,
        "total_conversations": total_conversations,
        "top_favorited": top_favorited,
        "price_ranges": price_ranges,
    }
