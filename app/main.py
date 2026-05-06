"""
FastAPI application entry point.

Uses lifespan for database lifecycle management.
Registers domain exception handlers for proper HTTP error responses.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager

from app.db.database import get_db
from app.core.exceptions import register_exception_handlers
from app.routers import auth, laptops, parts, users


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

# Register domain exception handlers
register_exception_handlers(app)

# Include all routers with their prefixes
app.include_router(auth.router)
app.include_router(laptops.router)
app.include_router(parts.router)
app.include_router(users.router)

# Mount the uploads directory to serve uploaded images as static files
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
