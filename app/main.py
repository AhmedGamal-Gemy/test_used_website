"""
FastAPI application entry point.

For junior developers:
- This is the main entry point for the FastAPI application
- We create the FastAPI app instance here
- We include all the routers from the different modules (auth, laptops, parts)
- We mount the uploads directory as static files so uploaded images can be served
- We set up startup and shutdown events for database connection management
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager

from app.db.database import get_database, close_database
from app.routers import auth, laptops, parts

# ------------------------------------------------------------------------------
# FastAPI Application Initialization
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Lifespan Context Manager (replaces deprecated on_event)
# ------------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    
    For junior developers:
    - This replaces the deprecated @app.on_event("startup") and @app.on_event("shutdown")
    - Code before yield runs on startup (database connection)
    - Code after yield runs on shutdown (database disconnection)
    - This is the modern way to handle lifecycle events in FastAPI
    """
    # Startup: connect to database
    await get_database()
    yield
    # Shutdown: close database connection
    await close_database()


# Create the FastAPI application instance
# title, description, and version appear in the OpenAPI docs (Swagger UI)
app = FastAPI(
    title="Used Laptops API",
    description="API for buying and selling used laptops and computer parts",
    version="1.0.0",
    lifespan=lifespan
)

# ------------------------------------------------------------------------------
# Router Registration
# ------------------------------------------------------------------------------

# Include all routers with their prefixes
# Each router handles a specific set of endpoints (auth, laptops, parts)
app.include_router(auth.router)
app.include_router(laptops.router)
app.include_router(parts.router)

# ------------------------------------------------------------------------------
# Static Files Mount for Uploaded Images
# ------------------------------------------------------------------------------

# Mount the uploads directory to serve uploaded images as static files
# This allows images to be accessed via URL like: http://localhost:8000/uploads/filename.jpg
# The directory is created if it doesn't exist to avoid startup errors
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
