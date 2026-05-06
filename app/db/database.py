# Load environment variables from .env file into os.environ
# This must be called before accessing any environment variables
from dotenv import load_dotenv
load_dotenv()

import os
# Import PyMongo's asynchronous MongoDB client (NOT Motor - as specified in requirements)
from pymongo import AsyncMongoClient

# Global variables to hold the client and database instances
# These are initialized as None and created lazily on first use of get_database()
_client = None
_db = None


async def get_database():
    """
    Returns the MongoDB database instance.
    Initializes the AsyncMongoClient on first call using environment variables.
    
    Returns:
        The MongoDB database instance for the configured database name
    """
    global _client, _db
    
    # If database is already initialized, return the cached instance
    if _db is not None:
        return _db
    
    # Read connection parameters from environment variables
    # These should be set in your .env file (e.g., MONGODB_URL=mongodb://localhost:27017)
    mongodb_url = os.environ.get("MONGODB_URL")
    mongodb_db_name = os.environ.get("MONGODB_DB_NAME")
    
    # Validate that required environment variables are set
    # This prevents runtime errors with unclear causes
    if not mongodb_url:
        raise ValueError(
            "MONGODB_URL environment variable is not set. "
            "Please add it to your .env file (e.g., MONGODB_URL=mongodb://localhost:27017)"
        )
    if not mongodb_db_name:
        raise ValueError(
            "MONGODB_DB_NAME environment variable is not set. "
            "Please add it to your .env file (e.g., MONGODB_DB_NAME=used_laptops_db)"
        )
    
    # Create the asynchronous MongoDB client using the URL from environment
    # AsyncMongoClient is PyMongo's native async client (not Motor)
    # The client is non-blocking and works with FastAPI's async endpoints
    _client = AsyncMongoClient(mongodb_url)
    
    # Get the database instance by name from the client
    # This doesn't actually connect yet - the connection happens on first operation
    _db = _client[mongodb_db_name]
    
    return _db


async def close_database():
    """
    Closes the MongoDB client connection if it exists.
    Resets global state for clean shutdown.
    """
    global _client, _db
    
    # Only attempt to close if client was initialized
    if _client is not None:
        # Close the client connection asynchronously
        # This releases all network resources used by the client
        await _client.close()
        
        # Reset global variables to None to allow reconnection if needed
        _client = None
        _db = None
