"""
Centralized configuration using frozen dataclasses.

Settings are read from environment variables with sensible defaults.
Frozen dataclasses prevent accidental mutation at runtime.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env from project root (auto-detected from CWD)
load_dotenv()


@dataclass(frozen=True)
class ImageConfig:
    """Configuration for image uploads."""

    allowed_types: tuple[str, ...] = ("image/jpeg", "image/png", "image/webp")
    max_size_bytes: int = 5 * 1024 * 1024  # 5MB
    upload_dir: str = "uploads"


@dataclass(frozen=True)
class PaginationConfig:
    """Configuration for pagination defaults."""

    default_skip: int = 0
    default_limit: int = 20
    max_limit: int = 100


@dataclass(frozen=True)
class JWTConfig:
    """Configuration for JWT token generation and validation."""

    secret_key: str = os.environ.get(
        "JWT_SECRET_KEY", "super-secret-key-change-in-production"
    )
    algorithm: str = os.environ.get("JWT_ALGORITHM", "HS256")

    @property
    def access_token_expire_minutes(self) -> int:
        """Token expiration in minutes, defaults to 30."""
        try:
            return int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))
        except ValueError:
            return 30


@dataclass(frozen=True)
class DatabaseConfig:
    """Configuration for MongoDB connection."""

    url: str = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")
    db_name: str = os.environ.get("MONGODB_DB_NAME", "used_laptops_db")


@dataclass(frozen=True)
class ServerConfig:
    """Configuration for the API server."""

    host: str = os.environ.get("HOST", "127.0.0.1")

    @property
    def port(self) -> int:
        try:
            return int(os.environ.get("PORT", 8000))
        except (ValueError, TypeError):
            return 8000

    @property
    def frontend_urls(self) -> list[str]:
        """CORS origins — comma-separated or default localhost variants."""
        raw = os.environ.get("FRONTEND_URLS", "")
        if raw:
            return [u.strip() for u in raw.split(",") if u.strip()]
        return ["http://localhost:5173", "http://127.0.0.1:5173"]


# Singleton instances - import these directly where needed
image_config = ImageConfig()
pagination_config = PaginationConfig()
jwt_config = JWTConfig()
database_config = DatabaseConfig()
server_config = ServerConfig()


class NotificationConfig:
    """Notification provider configuration."""

    @property
    def provider(self) -> str:
        return os.getenv("NOTIFICATION_PROVIDER", "console")


class WhatsAppConfig:
    """WhatsApp Business Cloud API configuration."""

    @property
    def token(self) -> str:
        return os.getenv("WHATSAPP_TOKEN", "")

    @property
    def phone_number_id(self) -> str:
        return os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")

    @property
    def template_name(self) -> str:
        return os.getenv("WHATSAPP_TEMPLATE_NAME", "notification_template")


notification_config = NotificationConfig()
whatsapp_config = WhatsAppConfig()
