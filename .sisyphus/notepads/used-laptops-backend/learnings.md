# Used Laptops Backend - Learnings

## Task 2: Database Connection Module

### What Was Done
- Created `app/db/database.py` with `AsyncMongoClient` setup (PyMongo native async, NOT Motor)
- Implemented `get_database()` async function with lazy initialization and caching
- Implemented `close_database()` async function for clean shutdown
- Used `python-dotenv` to load `MONGODB_URL` and `MONGODB_DB_NAME` from environment
- Added comprehensive inline comments for junior developer readability

### Patterns & Conventions
- **Flat architecture**: No extra abstraction layers, functions are module-level
- **Global state pattern**: `_client` and `_db` as module-level globals with lazy init
- **Environment validation**: Explicit `ValueError` with helpful messages if env vars missing
- **Async throughout**: Both `get_database()` and `close_database()` are async functions

### Key Technical Details
- `from pymongo import AsyncMongoClient` — PyMongo's native async client (Python 3.14+)
- `load_dotenv()` called at module import time to populate `os.environ`
- `AsyncMongoClient(mongodb_url)` doesn't connect immediately — connection happens on first operation
- `await _client.close()` releases network resources asynchronously

### Gotchas
- `load_dotenv()` must be called before `os.environ.get()` — order matters
- `AsyncMongoClient` is from `pymongo` directly, NOT `motor.motor_asyncio`
- The database reference `_client[db_name]` is lazy — no network call until first use

## Task 3: Security Module (JWT + Password Hashing)

### What Was Done
- Created `app/core/security.py` with password hashing and JWT token management
- Implemented `get_password_hash()` and `verify_password()` using `pwdlib` with Argon2
- Implemented `create_access_token()` and `decode_access_token()` using PyJWT (NOT python-jose)
- Added `DUMMY_HASH` constant for timing attack protection
- Configured JWT settings from environment variables with sensible defaults

### Patterns & Conventions
- **Flat architecture**: Module-level functions, no class abstractions
- **Inline documentation**: Extensive comments explaining JWT flow and password hashing for junior developers
- **Error handling**: `verify_password()` catches all exceptions and performs dummy verification to prevent timing attacks
- **Environment configuration**: Uses `os.environ.get()` with defaults for development

### Key Technical Details
- `from pwdlib import PasswordHash` — uses `PasswordHash.recommended()` which defaults to Argon2id
- `import jwt` and `from jwt.exceptions import InvalidTokenError` — PyJWT library (CVE-2024-23342 safe)
- `DUMMY_HASH = password_hash.hash("dummy_timing_protection_password")` — pre-computed hash for timing attack protection
- JWT expiration uses `datetime.now(timezone.utc)` with `timedelta` for timezone-aware datetimes
- `InvalidTokenError` is caught and re-raised with a clearer message for application use

### Gotchas
- PyRight LSP may cache import resolution — `pwdlib` installed but LSP shows `reportMissingImports` error
  - The code works correctly when run (verified with functional tests)
  - This is a PyRight caching issue, not an actual import problem
- Argon2 produces different hashes each time (salt + time cost) — `verify_password()` must be used, not string comparison
- JWT `decode()` requires `algorithms=[JWT_ALGORITHM]` as a list, not a string
- Environment variables are read at module import time — changes require module reload (or restart)
- PowerShell uses `;` not `&&` for command chaining

## Task 4: Auth Module (Signup, Signin, Signout)

### What Was Done
- Created `app/models/auth.py` with Pydantic schemas: `UserSignup`, `UserSignin`, `UserResponse`, `TokenResponse`
- Created `app/routers/auth.py` with FastAPI router containing three endpoints:
  - `POST /api/auth/signup` (201 Created, 409 Conflict for duplicate email)
  - `POST /api/auth/signin` (200 OK with JWT token, 401 for wrong credentials)
  - `POST /api/auth/signout` (200 OK with message)
- Implemented `get_current_user` dependency using JWT decoding and `OAuth2PasswordBearer`
- Added comprehensive inline comments explaining auth flow for junior developers

### Patterns & Conventions
- **Pydantic models**: Used `EmailStr` for email validation, `BaseModel` for request/response schemas
- **FastAPI router**: Used `APIRouter` with prefix `/api/auth` and tags for OpenAPI docs
- **OAuth2PasswordBearer**: Configured with `tokenUrl="/api/auth/signin"` for Swagger UI
- **Timing attack protection**: Always call `verify_password()` even if user doesn't exist (using `DUMMY_HASH`)
- **Stateless JWT**: No token storage in database (as per requirements)
- **Flat architecture**: Module-level functions and dependencies, no class abstractions

### Key Technical Details
- `from pydantic import EmailStr, BaseModel` — EmailStr validates email format automatically
- `from fastapi.security import OAuth2PasswordBearer` — Extracts Bearer token from Authorization header
- `decode_access_token()` returns payload with `sub` claim containing user ID
- MongoDB query: `db.users.find_one({"_id": ObjectId(user_id)})` — converts string to ObjectId
- `create_access_token(data={"sub": str(user["_id"])})` — stores user ID as subject in JWT
- `response_model=UserResponse` — FastAPI uses this for response validation and OpenAPI docs
- `status_code=status.HTTP_201_CREATED` — explicit status code for resource creation

### Gotchas
- `payload.get("sub")` returns `Unknown | None` — need to handle None case and cast to str
- `user["hashed_password"]` may trigger `reportOptionalSubscript` — use `user.get("hashed_password", "")` 
- `ObjectId(user_id)` can raise `InvalidId` exception — must catch and return 401
- `assert user is not None` needed for type checker after password validation (user must exist if password valid)
- JWT tokens are stateless — signout endpoint is essentially a no-op (client discards token)
- `UserResponse` must not include `hashed_password` — security best practice

## Task 5: Laptop CRUD Module

### What Was Done
- Created `app/models/laptops.py` with Pydantic schemas: `LaptopCreate`, `LaptopUpdate`, `LaptopResponse`
- Created `app/routers/laptops.py` with FastAPI router containing five endpoints:
  - `POST /api/laptops` — Create a new laptop listing (201 Created, requires auth)
  - `GET /api/laptops` — List all laptops with pagination (200 OK, public)
  - `GET /api/laptops/{laptop_id}` — Get a single laptop by ID (200 OK, public)
  - `PUT /api/laptops/{laptop_id}` — Update a laptop (200 OK, requires auth + ownership)
  - `DELETE /api/laptops/{laptop_id}` — Delete a laptop (204 No Content, requires auth + ownership)
- Implemented ownership check: only the seller (user who created the listing) can update/delete
- Implemented pagination on list endpoint using `skip` and `limit` query parameters
- Added `serialize_laptop()` helper to convert MongoDB documents to API response format

### Patterns & Conventions
- **Pydantic models**: `LaptopCreate` (required fields), `LaptopUpdate` (all Optional), `LaptopResponse` (includes system fields)
- **FastAPI router**: Used `APIRouter` with prefix `/api/laptops` and tags for OpenAPI docs
- **Authentication dependency**: Used `Depends(get_current_user)` from auth router for protected endpoints
- **Ownership check**: Compared `str(laptop["seller_id"])` with `str(current_user["_id"])` for authorization
- **Pagination**: Used `Query()` parameters with validation (`ge=0` for skip, `ge=1, le=100` for limit)
- **MongoDB ObjectId validation**: Wrapped `ObjectId(laptop_id)` in try/except to return 400 for invalid IDs
- **Flat architecture**: Module-level functions and helper, no class abstractions
- **Timezone-aware datetimes**: Used `datetime.now(timezone.utc)` for `created_at` and `updated_at`

### Key Technical Details
- `from bson import ObjectId` and `from bson.errors import InvalidId` — for MongoDB ID handling
- `from datetime import datetime, timezone` — for timezone-aware timestamps
- `LaptopUpdate` uses `str | None = None` — Pydantic v2 style Optional fields
- `serialize_laptop()` converts `_id` (ObjectId) to `id` (str) and handles `image_url` (Optional)
- `db[LAPTOPS_COLLECTION].find().skip(skip).limit(limit)` — MongoDB pagination
- `await cursor.to_list(length=limit)` — converts async cursor to list with length hint
- `update_one({"_id": obj_id}, {"$set": update_data})` — partial update using `$set` operator
- `delete_one({"_id": obj_id})` — delete single document by ID
- `status_code=status.HTTP_204_NO_CONTENT` — standard for successful DELETE with no body

### Gotchas
- `updated_laptop` after `update_one()` can be `None` — need to check and raise 500 if not found
- PyRight LSP may show `reportMissingImports` for `app.models.laptops` even though import works at runtime
  - Verified with `python -c "from app.models.laptops import ..."` — works correctly
  - This is a PyRight caching issue, not an actual import problem
- `ObjectId(laptop_id)` raises `InvalidId` (not just `TypeError`) for invalid hex strings — catch both
- `laptop.get("created_at")` may be `None` or not a datetime — use `isinstance()` check before calling `.isoformat()`
- `seller_id` in MongoDB is stored as `ObjectId` — compare using `str()` conversion for safety
- `description` field defaults to `""` in `LaptopCreate` so clients don't have to provide it
- `image_url` is `None` on creation (Task 7 will handle image uploads separately)
- PowerShell uses `;` not `&&` for command chaining in bash tool

## Task 7: Image Upload Endpoint

### What Was Done
- Created `app/main.py` as the FastAPI application entry point with:
  - FastAPI app initialization with metadata (title, description, version)
  - Router registration for auth, laptops, and parts routers
  - Static file mounting for the `uploads/` directory to serve images
  - Startup and shutdown lifecycle events for database connection management
- Added image upload endpoints to both `app/routers/laptops.py` and `app/routers/parts.py`:
  - `POST /api/laptops/{laptop_id}/image` — Upload/replace laptop image (requires auth + ownership)
  - `POST /api/parts/{part_id}/image` — Upload/replace part image (requires auth + ownership)
- Implemented file validation (type and size), UUID-based filename generation, old image cleanup, and MongoDB URL update

### Patterns & Conventions
- **FastAPI app structure**: Created `main.py` as entry point with router includes and static file mounting
- **Lifecycle events**: Used `@app.on_event("startup")` and `@app.on_event("shutdown")` for database connection management
- **Static files**: Used `app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")` to serve uploaded images
- **File upload pattern**: Used `UploadFile = File(...)` from FastAPI for multipart file uploads
- **File validation**: Checked `content_type` against allowed MIME types and read file into memory for size check
- **UUID filenames**: Generated unique filenames with `uuid.uuid4()` to avoid collisions
- **Old file cleanup**: Deleted old image file from disk when uploading a new one (if exists)
- **Ownership check**: Same pattern as update/delete — compared `str(seller_id)` with `str(current_user["_id"])`
- **Flat architecture**: Module-level functions, no class abstractions (consistent with rest of codebase)

### Key Technical Details
- `from fastapi import UploadFile, File` — FastAPI's file upload types for multipart/form-data
- `await file.read()` — reads the uploaded file content as bytes into memory
- `len(file_content)` — gets the file size in bytes for validation (5MB = 5 * 1024 * 1024)
- `allowed_content_types = ["image/jpeg", "image/png", "image/webp"]` — MIME type validation for security
- `str(uuid.uuid4())` — generates a unique filename to prevent collisions and overwriting
- `os.path.basename(old_image_url)` — extracts filename from URL for old image deletion
- `os.makedirs(uploads_dir, exist_ok=True)` — ensures uploads directory exists before saving
- `with open(file_path, "wb") as f: f.write(file_content)` — writes binary file to disk
- `image_url = f"/uploads/{full_filename}"` — constructs public URL for the uploaded image
- `app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")` — serves files from uploads/ at /uploads/ URL path

### Gotchas
- `file.read()` can only be called once per request — the file stream is consumed after reading
- `content_type` comes from the client's request headers — not fully trusted, but good first validation
- For production, consider adding virus scanning or additional file header validation (magic bytes)
- `os.path.basename()` works for URLs like `/uploads/filename.jpg` but may not work for full URLs with domain
- The uploads directory should be excluded from version control (add to `.gitignore`)
- Static file mounting must happen after all routes are registered (or it may intercept route paths)
- `@app.on_event` is deprecated in FastAPI 0.95+ in favor of lifespan events, but still works
- PowerShell uses `;` not `&&` for command chaining in bash tool


# Task 9: Full End-to-End QA Verification Results
**Date**: 2026-05-06 13:22
**Status**: COMPLETED ?

## Test Summary
- **Total Steps**: 15
- **Passed**: 15/15 (100%)}
- **Failed**: 0
- **500 Errors**: 0 ?

## Status Codes Observed
1. POST /api/auth/signup user A ? 201 ?
2. POST /api/auth/signin user A ? 200 ? (token received)
3. POST /api/auth/signup user B ? 201 ?
4. POST /api/auth/signin user B ? 200 ? (token received)
5. POST /api/laptops with token A ? 201 ?
6. POST /api/parts with token A ? 201 ?
7. POST image to laptop ? 200 ?
8. POST image to part ? 200 ?
9. PUT laptop with token B (non-owner) ? 403 ? (correctly rejected)
10. PUT laptop with token A (owner) ? 200 ?
11. DELETE part with token A ? 204 ?
12. GET /api/laptops ? 200 ?
13. GET /api/parts ? 200 ?
14. POST /api/auth/signout ? 200 ?
15. GET /api/laptops with invalid token ? 200 ? (public endpoint)

## Key Findings
- All CRUD operations work correctly
- Ownership checks work (non-owner cannot update, gets 403)
- Image uploads work for both laptops and parts
- Public endpoints don't require authentication
- JWT authentication works for protected endpoints

## Evidence Location
- .sisyphus/evidence/task-9-full-journey.json'

