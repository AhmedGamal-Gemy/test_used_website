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

from app.db.database import get_database, close_database
from app.routers import auth, laptops, parts

# ------------------------------------------------------------------------------
# FastAPI Application Initialization
# ------------------------------------------------------------------------------

# Create the FastAPI application instance
# title, description, and version appear in the OpenAPI docs (Swagger UI)
app = FastAPI(
    title="Used Laptops API",
    description="API for buying and selling used laptops and computer parts",
    version="1.0.0"
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

# ------------------------------------------------------------------------------
# Lifecycle Events
# ------------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """
    Initialize database connection on startup.
    
    For junior developers:
    - This function runs when the FastAPI app starts up
    - We call get_database() to establish the MongoDB connection
    - The connection is cached in the database module for reuse
    """
    await get_database()


@app.on_event("shutdown")
async def shutdown_event():
    """
    Close database connection on shutdown.
    
    For junior developers:
    - This function runs when the FastAPI app shuts down
    - We call close_database() to cleanly close the MongoDB connection
    - This prevents connection leaks and ensures graceful shutdown
    """
    await close_database()
