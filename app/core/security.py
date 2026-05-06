"""
Security module for password hashing and JWT token management.

For junior developers:
- Password Hashing: We use `pwdlib` with Argon2 (via `PasswordHash.recommended()`) because it's the current
  industry best practice for securely hashing passwords. NEVER store plain-text passwords in a database!
- JWT (JSON Web Tokens): Used for user authentication. When a user logs in with valid credentials, we issue
  them an access token. They include this token in future requests to prove their identity.
- Timing Attack Protection: When verifying passwords, if the stored hash is invalid (e.g., corrupted, wrong format),
  we still perform a verification against a `DUMMY_HASH` to ensure the response time is identical to a normal
  failed password check. This prevents attackers from guessing if a stored hash is valid based on response time.
"""

import os
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone


# ------------------------------------------------------------------------------
# Password Hashing Configuration
# ------------------------------------------------------------------------------

# Initialize password hasher with recommended settings (Argon2, the current best practice for password hashing)
password_hash = PasswordHash.recommended()

# Dummy hash for timing attack protection. If a stored hash is invalid, we verify against this dummy hash
# to keep the function's execution time consistent with a normal failed verification.
# This is a hash of the string "dummy_timing_protection_password" using our configured password hasher.
DUMMY_HASH = password_hash.hash("dummy_timing_protection_password")


def get_password_hash(password: str) -> str:
    """Hash a plain-text password using the recommended Argon2 hasher."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a stored hashed password.
    
    Args:
        plain_password: The plain-text password to verify
        hashed_password: The hashed password from the database
        
    Returns:
        True if the password matches the hash, False otherwise.
        Also returns False if the stored hash is invalid (after performing a dummy verification
        to prevent timing attacks).
    """
    try:
        # Normal case: verify the password against the stored hash
        return password_hash.verify(plain_password, hashed_password)
    except Exception:
        # If the stored hash is invalid (corrupted, wrong format, etc.), verify against the dummy hash
        # This ensures the function takes the same amount of time as a normal failed verification
        password_hash.verify(plain_password, DUMMY_HASH)
        return False


# ------------------------------------------------------------------------------
# JWT Configuration (read from environment variables)
# ------------------------------------------------------------------------------

# IMPORTANT: In production, always set these via environment variables, especially JWT_SECRET_KEY!
# Defaults are provided for development only.
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "super-secret-key-change-in-production")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

# Token expiration: default to 30 minutes if not set or invalid
try:
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))
except ValueError:
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ------------------------------------------------------------------------------
# JWT Token Functions
# ------------------------------------------------------------------------------

def create_access_token(token_payload: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token for user authentication.
    
    JWT Flow for Junior Developers:
    1. We take input data (e.g., {"sub": "user@example.com"}) and add an expiration time
    2. We sign this data with our secret key using the specified algorithm (HS256)
    3. The resulting token is given to the user, who includes it in the Authorization header
       of future requests (as "Bearer <token>")
    
    Args:
        token_payload: Dictionary of data to encode in the token (typically contains user identifier as "sub")
        expires_delta: Optional custom expiration time. If not provided, uses JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        
    Returns:
        Encoded JWT token string
    """
    to_encode = token_payload.copy()
    
    # Calculate expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Encode and sign the token
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: The JWT token string to decode (extracted from the Authorization header)
        
    Returns:
        The decoded payload dictionary if the token is valid (contains the original data we encoded)
        
    Raises:
        InvalidTokenError: If the token is expired, tampered with, or otherwise invalid.
            The original PyJWT error message is included for debugging.
    """
    try:
        # Decode the token, verifying the signature and expiration
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except InvalidTokenError as e:
        # Re-raise with a clearer message for the application
        raise InvalidTokenError(f"Could not validate access token: {str(e)}") from e
