"""
MongoDB database connection using a Database class.

Replaces global variables with an instance that manages the client and database.
"""

from dotenv import load_dotenv
load_dotenv()

import os
from pymongo import AsyncMongoClient

from app.core.config import database_config


class Database:
    """Manages MongoDB client and database instances."""

    def __init__(self) -> None:
        self._client = AsyncMongoClient(database_config.url)
        self._db = self._client[database_config.db_name]

    @property
    def db(self):
        """Get the database instance."""
        return self._db

    async def close(self) -> None:
        """Close the MongoDB client connection."""
        await self._client.close()

    @property
    def users(self):
        """Shortcut to the users collection."""
        return self._db.users

    @property
    def laptops(self):
        """Shortcut to the laptops collection."""
        return self._db.laptops

    @property
    def parts(self):
        """Shortcut to the parts collection."""
        return self._db.parts


def create_database() -> Database:
    """Factory function to create a Database instance.

    Validates that required environment variables are set.
    """
    if not database_config.url:
        raise ValueError(
            "MONGODB_URL environment variable is not set. "
            "Please add it to your .env file (e.g., MONGODB_URL=mongodb://localhost:27017)"
        )
    if not database_config.db_name:
        raise ValueError(
            "MONGODB_DB_NAME environment variable is not set. "
            "Please add it to your .env file (e.g., MONGODB_DB_NAME=used_laptops_db)"
        )
    return Database()


# Singleton instance - created on first access
_db_instance: Database | None = None


def get_db() -> Database:
    """Get or create the singleton Database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = create_database()
    return _db_instance
