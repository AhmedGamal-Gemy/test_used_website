"""
Security module for password hashing and JWT token management.

Uses Argon2 for password hashing (via pwdlib) and HS256 for JWT signing.
Includes timing attack protection for password verification.
"""

import os
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone


# Initialize password hasher with recommended settings (Argon2)
password_hash = PasswordHash.recommended()

# Dummy hash for timing attack protection
DUMMY_HASH = password_hash.hash("dummy_timing_protection_password")


def get_password_hash(password: str) -> str:
    """Hash a plain-text password using Argon2."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored hash.

    Uses a dummy hash comparison when the stored hash is invalid
    to prevent timing-based user enumeration attacks.
    """
    try:
        return password_hash.verify(plain_password, hashed_password)
    except Exception:
        password_hash.verify(plain_password, DUMMY_HASH)
        return False


from app.core.config import jwt_config


def create_access_token(
    token_payload: dict, expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token with the given payload."""
    to_encode = token_payload.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=jwt_config.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, jwt_config.secret_key, algorithm=jwt_config.algorithm)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token.

    Raises InvalidTokenError if the token is expired or invalid.
    """
    try:
        return jwt.decode(
            token, jwt_config.secret_key, algorithms=[jwt_config.algorithm]
        )
    except InvalidTokenError as e:
        raise InvalidTokenError(
            f"Could not validate access token: {str(e)}"
        ) from e
