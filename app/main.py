"""
FastAPI application entry point.

Uses lifespan for database lifecycle management.
Registers domain exception handlers for proper HTTP error responses.
"""

import os
import sys
from contextlib import asynccontextmanager

# Allow running as `python app/main.py` — add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.db.database import get_db
from app.core.exceptions import register_exception_handlers
from app.core.config import server_config
from app.routers import auth, laptops, parts, users, favorites, reviews, messages, services, orders, admin


# ------------------------------------------------------------------------------
# Lifespan Context Manager (replaces deprecated on_event)
# ------------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - database connection on startup, cleanup on shutdown."""
    # Startup: initialize database
    get_db()
    yield
    # Shutdown: close database connection
    await get_db().close()


# Create the FastAPI application instance
app = FastAPI(
    title="Used Laptops API",
    description="API for buying and selling used laptops and computer parts",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow configurable frontend origins (default: localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=server_config.frontend_urls,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register domain exception handlers
register_exception_handlers(app)

# Include all routers with their prefixes
app.include_router(auth.router)
app.include_router(laptops.router)
app.include_router(parts.router)
app.include_router(users.router)
app.include_router(favorites.router)
app.include_router(reviews.router)
app.include_router(messages.router)
app.include_router(services.router)
app.include_router(orders.router)
app.include_router(admin.router)

# Mount the uploads directory to serve uploaded images as static files
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

if __name__ == "__main__":
    """Run directly via `python app/main.py` — reads PORT from .env/config."""
    uvicorn.run(
        "app.main:app",
        host=server_config.host,
        port=server_config.port,
        reload=True,
    )
