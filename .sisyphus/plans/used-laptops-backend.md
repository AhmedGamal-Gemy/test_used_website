# Used Laptops & Parts Marketplace — Backend Plan

## TL;DR

> **Quick Summary**: Build a FastAPI backend with PyMongo Async for a marketplace where users can sign up, list used laptops and parts for sale, and upload images locally. Clean, flat architecture with inline comments for junior dev onboarding.
>
> **Deliverables**:
> - Auth module (signup, signin, signout with JWT access tokens)
> - Laptop CRUD module with image upload and pagination
> - Parts CRUD module with image upload and pagination
> - Postman collections for each module in `/docs/postman/`
> - README with setup, env vars, and API overview
> - `session.md` tracking file
>
> **Estimated Effort**: Short
> **Parallel Execution**: YES — 3 waves
> **Critical Path**: Scaffolding → Auth → Laptops/Parts/Image → Docs → QA

---

## Context

### Original Request
Build a FastAPI + MongoDB backend for a used laptops and parts marketplace. Phase 1 scope only: auth, laptop CRUD, parts CRUD, basic image upload to local `/uploads` folder.

### Interview Summary
**Key Discussions**:
- **JWT Library**: User originally specified python-jose, but I recommended PyJWT due to CVE-2024-23342 and FastAPI's official switch. User agreed.
- **Auth**: Email-only login, access token only (no refresh), timing attack protection with DUMMY_HASH.
- **Listing Fields**: Laptop: title, brand, model, condition, price, description, image_url, seller_id, created_at, updated_at. Parts: title, category, compatible_models[], condition, price, description, image_url, seller_id, created_at, updated_at.
- **Image Upload**: Single image per listing, JPEG/PNG/WebP, max 5MB, saved to local `/uploads`.
- **Pagination**: skip/limit on all list endpoints.
- **DB Name**: `used_laptops_db`
- **Python Version**: 3.14
- **Architecture**: Simple and flat — one router file per feature, Pydantic models in `/models`, DB connection in `/db`, security in `/core`.

### Metis Review
**Identified Gaps** (addressed):
- **python-jose CVE**: Flagged CVE-2024-23342, recommended PyJWT instead — user agreed
- **Missing test infrastructure**: Added Agent-Executed QA scenarios as primary verification (no unit tests in Phase 1)
- **Image validation scope**: Clarified file type (JPEG/PNG/WebP) and size (5MB) limits
- **Ownership enforcement**: Explicitly added 403 checks for cross-user edits/deletes
- **Session tracking**: Added session.md requirement as deliverable

---

## Work Objectives

### Core Objective
Build a production-ready FastAPI backend with MongoDB (PyMongo Async) for user authentication and marketplace listings (laptops + parts) with local image uploads.

### Concrete Deliverables
- `app/core/security.py` — JWT creation/verification, password hashing
- `app/db/database.py` — AsyncMongoClient connection management
- `app/models/` — Pydantic schemas for auth, laptops, parts
- `app/routers/auth.py` — Signup, signin, signout endpoints
- `app/routers/laptops.py` — Full CRUD for laptop listings
- `app/routers/parts.py` — Full CRUD for parts listings
- `app/main.py` — FastAPI app entry point
- `/uploads/` — Local image storage directory
- `/docs/postman/` — Postman collections per module
- `pyproject.toml`, `.env.example`, `README.md`, `session.md`

### Definition of Done
- [ ] `uvicorn app.main:app --reload` starts without errors
- [ ] Swagger UI at `/docs` shows all endpoints correctly
- [ ] All auth endpoints tested (signup, signin, signout)
- [ ] All laptop CRUD endpoints tested with auth protection
- [ ] All parts CRUD endpoints tested with auth protection
- [ ] Image upload works for laptops and parts (5MB limit, JPEG/PNG/WebP)
- [ ] Pagination works on list endpoints
- [ ] Postman collections exported for each module
- [ ] `session.md` updated with all completed tasks

### Must Have
- Async MongoDB via PyMongo AsyncMongoClient
- JWT access tokens with PyJWT (HS256)
- Password hashing with pwdlib (Argon2)
- Route protection via `Depends()`
- Inline comments explaining each step (junior dev)
- Pagination (skip/limit) on list endpoints
- Image validation (type + size) before saving
- Conventional commits

### Must NOT Have (Guardrails)
- No fastapi-users library
- No Motor driver
- No Docker
- No cloud storage (S3, Cloudinary, etc.)
- No refresh tokens
- No payments
- No domain/hosting config
- No unnecessary abstraction layers (keep it flat)
- No AI slop: no excessive comments, no over-abstraction, no generic variable names like `data`, `result`, `item`, `temp`

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO (fresh project)
- **Automated tests**: None (Phase 1 focus on functional delivery)
- **Agent-Executed QA**: MANDATORY — all tasks verified via curl/Playwright/bash

### QA Policy
Every task MUST include agent-executed QA scenarios:
- **API endpoints**: curl requests with assertions on status codes and response fields
- **Auth flow**: Full signup → signin → protected route → signout chain
- **Image upload**: curl with file upload, verify saved file exists
- **Error cases**: Invalid tokens, missing fields, oversized files, wrong file types
- **Evidence saved**: `.sisyphus/evidence/task-{N}-{scenario}.{ext}`

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — foundation + scaffolding):
├── Task 1: Project scaffolding + config files [quick]
├── Task 2: Database connection module [quick]
└── Task 3: Security module (JWT + password hashing) [unspecified-high]

Wave 2 (After Wave 1 — all 3 independent):
├── Task 4: Auth module — signup + signin + signout [deep]
├── Task 5: Laptop CRUD module [deep]
└── Task 6: Parts CRUD module [deep]

Wave 3 (After Wave 2 — integration + docs):
├── Task 7: Image upload integration (laptops + parts) [unspecified-high]
├── Task 8: Postman collections + README + session.md [quick]
└── Task 9: Full end-to-end QA verification [unspecified-high]

Wave FINAL (After ALL tasks — 4 parallel reviews):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
```

### Dependency Matrix
- **1**: - → 2, 3
- **2**: 1 → 4, 5, 6
- **3**: 1 → 4
- **4**: 2, 3 → 5, 6, 7
- **5**: 2, 4 → 7
- **6**: 2, 4 → 7
- **7**: 4, 5, 6 → 8
- **8**: 7 → 9
- **9**: 8 → F1-F4
- **F1-F4**: 9 → user okay

### Agent Dispatch Summary
- **Wave 1**: T1 → `quick`, T2 → `quick`, T3 → `unspecified-high`
- **Wave 2**: T4 → `deep`, T5 → `deep`, T6 → `deep`
- **Wave 3**: T7 → `unspecified-high`, T8 → `quick`, T9 → `unspecified-high`
- **FINAL**: F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. Project Scaffolding + Configuration

  **What to do**:
  - Create directory structure: `app/routers/`, `app/models/`, `app/db/`, `app/core/`, `uploads/`, `docs/postman/`
  - Create `app/__init__.py`, `app/routers/__init__.py`, `app/models/__init__.py`, `app/db/__init__.py`, `app/core/__init__.py`
  - Create `requirements.txt` with: `fastapi`, `uvicorn[standard]`, `pymongo`, `pyjwt[crypto]`, `pwdlib[argon2]`, `pydantic`, `python-multipart`, `python-dotenv`
  - Create `.env.example` with: `MONGODB_URL`, `MONGODB_DB_NAME`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
  - Create `.gitignore` for Python (`.venv/`, `__pycache__/`, `*.pyc`, `.env`, `uploads/`)
  - Create `session.md` at project root with initial milestone header

  **Must NOT do**:
  - Do NOT create any implementation code yet
  - Do NOT add dependencies not listed above

  **Recommended Agent Profile**:
  - **Category**: `quick` — Straightforward file/folder creation
  - **Skills**: `[]` — No specialized skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: 2, 3
  - **Blocked By**: None

  **References**:
  - Standard Python project structure

  **Acceptance Criteria**:
  - All directories exist with `__init__.py` files
  - `requirements.txt` has all 8 dependencies
  - `.env.example` has all 5 env vars with descriptions
  - `.gitignore` covers Python artifacts, `.env`, and `uploads/`
  - `session.md` exists at project root

  **QA Scenarios**:
  ```
  Scenario: Directory structure exists
    Tool: Bash
    Steps:
      1. Run: ls -la app/ app/routers/ app/models/ app/db/ app/core/ uploads/ docs/postman/
      2. Verify all directories listed without errors
    Expected Result: All 7 directories exist and are accessible
    Evidence: .sisyphus/evidence/task-1-dir-structure.txt

  Scenario: requirements.txt has all dependencies
    Tool: Bash
    Steps:
      1. Run: cat requirements.txt
      2. Verify each of the 8 packages is present
    Expected Result: fastapi, uvicorn[standard], pymongo, pyjwt[crypto], pwdlib[argon2], pydantic, python-multipart, python-dotenv all listed
    Evidence: .sisyphus/evidence/task-1-requirements.txt
  ```

  **Commit**: YES (with 2, 3)
  - Message: `chore: initialize project structure and configuration`

- [x] 2. Database Connection Module

  **What to do**:
  - Create `app/db/database.py` with AsyncMongoClient setup
  - Use `os.environ` or `python-dotenv` to read `MONGODB_URL` and `MONGODB_DB_NAME`
  - Create `get_database()` async function that returns the database instance
  - Create `close_database()` async function to close the client
  - Add startup/shutdown event hooks in the module (to be used by main.py)
  - Add inline comments explaining each step

  **Must NOT do**:
  - Do NOT use Motor — only `pymongo.AsyncMongoClient`
  - Do NOT hardcode connection strings

  **Recommended Agent Profile**:
  - **Category**: `quick` — Simple async connection wrapper
  - **Skills**: `[]` — Standard PyMongo Async patterns

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: 4, 5, 6
  - **Blocked By**: 1

  **References**:
  - PyMongo Async docs: `from pymongo import AsyncMongoClient` — all operations return coroutines requiring `await`
  - Context7 pattern: `client = AsyncMongoClient("mongodb://localhost:27017")` with `await client.close()`

  **Acceptance Criteria**:
  - `app/db/database.py` exists with `get_database()` and `close_database()` functions
  - Uses `AsyncMongoClient` (not Motor)
  - Reads config from environment variables
  - Inline comments present

  **QA Scenarios**:
  ```
  Scenario: Database module imports without errors
    Tool: Bash
    Steps:
      1. Set env: $env:MONGODB_URL="mongodb://localhost:27017"; $env:MONGODB_DB_NAME="used_laptops_db"
      2. Run: python -c "from app.db.database import get_database, close_database; print('OK')"
    Expected Result: Prints "OK" with no import errors
    Evidence: .sisyphus/evidence/task-2-import-test.txt

  Scenario: Database connection functions are async
    Tool: Bash
    Steps:
      1. Run: python -c "import inspect, asyncio; from app.db.database import get_database, close_database; assert inspect.iscoroutinefunction(get_database); assert inspect.iscoroutinefunction(close_database); print('OK')"
    Expected Result: Prints "OK", both functions are coroutine functions
    Evidence: .sisyphus/evidence/task-2-async-check.txt
  ```

  **Commit**: YES
  - Message: `feat(db): add AsyncMongoClient connection module`

- [x] 3. Security Module (JWT + Password Hashing)

  **What to do**:
  - Create `app/core/security.py`
  - Import `pwdlib.PasswordHash` and create `password_hash = PasswordHash.recommended()`
  - Create `get_password_hash(password: str) -> str` function
  - Create `verify_password(plain_password: str, hashed_password: str) -> bool` function
  - Create `DUMMY_HASH` constant for timing attack protection
  - Import `jwt` (PyJWT) and create:
    - `create_access_token(data: dict, expires_delta: timedelta | None = None) -> str`
    - `decode_access_token(token: str) -> dict` with proper error handling for `InvalidTokenError`
  - Read `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` from env
  - Add inline comments explaining JWT flow and password hashing

  **Must NOT do**:
  - Do NOT use python-jose
  - Do NOT use fastapi-users
  - Do NOT implement refresh token logic

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high` — Security-critical code needs careful implementation
  - **Skills**: `[]` — Standard JWT and pwdlib patterns

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: 4
  - **Blocked By**: 1

  **References**:
  - FastAPI security tutorial: `from pwdlib import PasswordHash` with `PasswordHash.recommended()`
  - FastAPI JWT: `import jwt`, `from jwt.exceptions import InvalidTokenError`
  - pwdlib: `password_hash.hash()` and `password_hash.verify()`
  - PyJWT: `jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)` and `jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])`

  **Acceptance Criteria**:
  - `app/core/security.py` exists with all 5 functions/constants
  - Uses pwdlib for password hashing (Argon2)
  - Uses PyJWT for token creation/decoding
  - DUMMY_HASH present for timing attack protection
  - Inline comments explaining each function

  **QA Scenarios**:
  ```
  Scenario: Password hash and verify work correctly
    Tool: Bash
    Steps:
      1. Run: python -c "from app.core.security import get_password_hash, verify_password; h = get_password_hash('Test1234!'); assert verify_password('Test1234!', h); assert not verify_password('WrongPass', h); print('OK')"
    Expected Result: Prints "OK", correct password verifies, wrong password fails
    Evidence: .sisyphus/evidence/task-3-password-hash.txt

  Scenario: Access token creation and decoding work
    Tool: Bash
    Steps:
      1. Set env vars for JWT config
      2. Run: python -c "from app.core.security import create_access_token, decode_access_token; t = create_access_token({'sub': 'test@test.com'}); d = decode_access_token(t); assert d['sub'] == 'test@test.com'; print('OK')"
    Expected Result: Prints "OK", decoded token contains correct subject
    Evidence: .sisyphus/evidence/task-3-jwt-roundtrip.txt

  Scenario: Invalid token raises proper error
    Tool: Bash
    Steps:
      1. Run: python -c "from app.core.security import decode_access_token; decode_access_token('invalid.token.here')" 2>&1
      2. Verify it raises an exception (not silent failure)
    Expected Result: Raises InvalidTokenError or equivalent exception
    Evidence: .sisyphus/evidence/task-3-invalid-token.txt
  ```

  **Commit**: YES (with 1, 2)
  - Message: `chore: initialize project structure and configuration`

- [x] 4. Auth Module — Signup, Signin, Signout

  **What to do**:
  - Create `app/models/auth.py` with Pydantic schemas:
    - `UserSignup(email: EmailStr, password: str)` — password min 8 chars
    - `UserSignin(email: EmailStr, password: str)`
    - `UserResponse(id: str, email: str, created_at: datetime)`
    - `TokenResponse(access_token: str, token_type: str = "bearer")`
  - Create `app/routers/auth.py` with FastAPI router:
    - `POST /api/auth/signup` — validate email unique, hash password, save to `users` collection, return user data (201)
    - `POST /api/auth/signin` — find user by email, verify password, create JWT, return token (200)
    - `POST /api/auth/signout` — return 200 with message (client-side token discard)
  - Use `OAuth2PasswordBearer` for token URL configuration
  - Inline comments explaining auth flow

  **Must NOT do**:
  - Do NOT implement refresh tokens
  - Do NOT use fastapi-users
  - Do NOT store tokens in database

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: 5, 6, 7
  - **Blocked By**: 2, 3

  **References**:
  - `app/db/database.py` — `get_database()`
  - `app/core/security.py` — `create_access_token()`, `get_password_hash()`, `verify_password()`, `DUMMY_HASH`
  - FastAPI: `from fastapi.security import OAuth2PasswordBearer`
  - Pydantic: `from pydantic import EmailStr`

  **Acceptance Criteria**:
  - Signup returns 201, duplicates return 409
  - Signin returns token on success, 401 on wrong credentials
  - Signout returns 200
  - Passwords stored as Argon2 hashes
  - DUMMY_HASH used for timing attack protection

  **QA Scenarios**:
  ```
  Scenario: Happy path — signup, signin, signout
    Tool: Bash (curl)
    Steps:
      1. Signup: curl -s -w "\n%{http_code}" -X POST http://127.0.0.1:8000/api/auth/signup -H "Content-Type: application/json" -d "{\"email\":\"test@test.com\",\"password\":\"Test1234!\"}"
      2. Verify 201
      3. Signin: curl -s -X POST http://127.0.0.1:8000/api/auth/signin -H "Content-Type: application/json" -d "{\"email\":\"test@test.com\",\"password\":\"Test1234!\"}"
      4. Verify has access_token and token_type=bearer
      5. Signout: curl -s -X POST http://127.0.0.1:8000/api/auth/signout
      6. Verify 200
    Expected Result: All 3 steps succeed
    Evidence: .sisyphus/evidence/task-4-auth-happy-path.json

  Scenario: Duplicate email returns 409
    Tool: Bash (curl)
    Steps:
      1. Signup same email twice
      2. Verify second returns 409
    Expected Result: 409 Conflict
    Evidence: .sisyphus/evidence/task-4-duplicate-signup.json

  Scenario: Wrong password returns 401
    Tool: Bash (curl)
    Steps:
      1. Signin with valid email, wrong password
      2. Verify 401
    Expected Result: 401 Unauthorized
    Evidence: .sisyphus/evidence/task-4-wrong-password.json

  Scenario: Invalid email format returns 422
    Tool: Bash (curl)
    Steps:
      1. Signup with email="not-an-email"
      2. Verify 422
    Expected Result: 422 validation error
    Evidence: .sisyphus/evidence/task-4-invalid-email.json
  ```

  **Commit**: YES
  - Message: `feat(auth): add signup, signin, and signout endpoints`

- [x] 5. Laptop CRUD Module

  **What to do**:
  - Create `app/models/laptops.py`:
    - `LaptopCreate(title, brand, model, condition, price: float, description: str = "")`
    - `LaptopUpdate` — all fields optional
    - `LaptopResponse(id, title, brand, model, condition, price, description, image_url: str | None, seller_id, created_at, updated_at)`
  - Create `app/routers/laptops.py`:
    - `POST /api/laptops` — create (auth required, sets seller_id) (201)
    - `GET /api/laptops` — list with pagination (skip=0, limit=20) (200)
    - `GET /api/laptops/{laptop_id}` — get single or 404
    - `PUT /api/laptops/{laptop_id}` — update (only if seller, 403 otherwise) (200)
    - `DELETE /api/laptops/{laptop_id}` — delete (only if seller) (204)
  - Add `get_current_user` dependency
  - Inline comments

  **Must NOT do**:
  - Do NOT implement image upload here (Task 7)
  - Do NOT allow non-auth access to write operations
  - Do NOT allow cross-user edits

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 6)
  - **Parallel Group**: Wave 2 (with Tasks 4, 6)
  - **Blocks**: 7
  - **Blocked By**: 2, 4

  **References**:
  - `app/db/database.py` — `get_database()`
  - `app/core/security.py` — `decode_access_token()`
  - `app/routers/auth.py` — `get_current_user` pattern
  - MongoDB: `collection.find().skip(skip).limit(limit).to_list(length=limit)`

  **Acceptance Criteria**:
  - All 5 CRUD endpoints work
  - Auth required for all operations
  - Ownership enforced on PUT/DELETE
  - Pagination works

  **QA Scenarios**:
  ```
  Scenario: Create laptop listing
    Tool: Bash (curl)
    Steps:
      1. Signin to get token
      2. POST /api/laptops with token and laptop data
      3. Verify 201, has id and seller_id
    Expected Result: 201 with laptop data
    Evidence: .sisyphus/evidence/task-5-create-laptop.json

  Scenario: List with pagination
    Tool: Bash (curl)
    Steps:
      1. Create 5 laptops
      2. GET /api/laptops?skip=0&limit=2
      3. Verify array with max 2 items
    Expected Result: Correct pagination
    Evidence: .sisyphus/evidence/task-5-pagination.json

  Scenario: Non-owner cannot delete (403)
    Tool: Bash (curl)
    Steps:
      1. User A creates laptop
      2. User B tries DELETE with their token
      3. Verify 403
    Expected Result: 403 Forbidden
    Evidence: .sisyphus/evidence/task-5-unauthorized-delete.json

  Scenario: Unauthenticated access returns 401
    Tool: Bash (curl)
    Steps:
      1. POST /api/laptops without token
      2. Verify 401
    Expected Result: 401 Unauthorized
    Evidence: .sisyphus/evidence/task-5-unauthenticated.json
  ```

  **Commit**: YES
  - Message: `feat(laptops): add CRUD routes with MongoDB async`

- [x] 6. Parts CRUD Module

  **What to do**:
  - Create `app/models/parts.py`:
    - `PartCreate(title, category, compatible_models: list[str], condition, price: float, description: str = "")`
    - `PartUpdate` — all fields optional
    - `PartResponse(id, title, category, compatible_models, condition, price, description, image_url: str | None, seller_id, created_at, updated_at)`
  - Create `app/routers/parts.py` — same 5 endpoints as laptops
  - Mirror laptop module structure for consistency

  **Must NOT do**:
  - Do NOT implement image upload here (Task 7)
  - Do NOT diverge from laptop patterns

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 5)
  - **Parallel Group**: Wave 2 (with Tasks 4, 5)
  - **Blocks**: 7
  - **Blocked By**: 2, 4

  **References**:
  - `app/routers/laptops.py` — mirror structure
  - `app/db/database.py` — `get_database()`
  - MongoDB collection: `parts`

  **Acceptance Criteria**:
  - All 5 CRUD endpoints work
  - compatible_models accepts array
  - Auth and ownership enforced

  **QA Scenarios**:
  ```
  Scenario: Create part with compatible_models
    Tool: Bash (curl)
    Steps:
      1. Signin, get token
      2. POST /api/parts with compatible_models array
      3. Verify 201, has compatible_models in response
    Expected Result: 201 with part data
    Evidence: .sisyphus/evidence/task-6-create-part.json

  Scenario: Non-owner cannot update (403)
    Tool: Bash (curl)
    Steps:
      1. User A creates part
      2. User B tries PUT
      3. Verify 403
    Expected Result: 403 Forbidden
    Evidence: .sisyphus/evidence/task-6-unauthorized-update.json

  Scenario: Delete returns 204
    Tool: Bash (curl)
    Steps:
      1. Owner deletes their part
      2. Verify 204
    Expected Result: 204 No Content
    Evidence: .sisyphus/evidence/task-6-delete.txt
  ```

  **Commit**: YES
  - Message: `feat(parts): add CRUD routes with MongoDB async`

- [x] 7. Image Upload Integration (Laptops + Parts)

  **What to do**:
  - Add to `app/routers/laptops.py`: `POST /api/laptops/{laptop_id}/image`
  - Add to `app/routers/parts.py`: `POST /api/parts/{part_id}/image`
  - Validate: JPEG/PNG/WebP only, max 5MB
  - Save to `/uploads/` with UUID filename
  - Update listing's image_url in MongoDB
  - Replace existing image (delete old file)
  - Mount static files in `app/main.py`: `app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")`

  **Must NOT do**:
  - Do NOT use cloud storage
  - Do NOT resize/process images
  - Do NOT allow upload without ownership check

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: 8
  - **Blocked By**: 4, 5, 6

  **References**:
  - FastAPI: `from fastapi import UploadFile, File`
  - FastAPI: `from fastapi.staticfiles import StaticFiles`
  - Python `uuid` for filenames
  - `python-multipart` (in requirements.txt)

  **Acceptance Criteria**:
  - Upload works for laptops and parts
  - Invalid type rejected (400)
  - Oversized file rejected (400)
  - Old image replaced and deleted
  - Image accessible via `/uploads/{filename}`

  **QA Scenarios**:
  ```
  Scenario: Upload valid image
    Tool: Bash (curl)
    Steps:
      1. Create test JPEG
      2. Signin, create laptop, get ID
      3. POST /api/laptops/{ID}/image with file
      4. Verify 200, has image_url
      5. Verify file in uploads/
      6. curl /uploads/{filename} → 200
    Expected Result: Image uploaded, saved, accessible
    Evidence: .sisyphus/evidence/task-7-upload.json

  Scenario: Reject oversized file
    Tool: Bash (curl)
    Steps:
      1. Create 6MB file
      2. Attempt upload
      3. Verify 400
    Expected Result: 400 with size error
    Evidence: .sisyphus/evidence/task-7-oversized.json

  Scenario: Reject invalid type
    Tool: Bash (curl)
    Steps:
      1. Upload .txt file
      2. Verify 400
    Expected Result: 400 with type error
    Evidence: .sisyphus/evidence/task-7-invalid-type.json
  ```

  **Commit**: YES
  - Message: `feat(upload): add image upload for laptops and parts`

- [x] 8. Main App Entry Point + Documentation

  **What to do**:
  - Create `app/main.py`:
    - FastAPI app with title, description, version
    - Startup event: connect MongoDB
    - Shutdown event: close MongoDB
    - Mount `/uploads` static files
    - Include all 3 routers with prefixes and tags
  - Export Postman collections: `docs/postman/auth.json`, `laptops.json`, `parts.json`
  - Update `README.md`: install, run, env vars table, API overview
  - Update `session.md` with final status

  **Must NOT do**:
  - Do NOT add CORS middleware
  - Do NOT add rate limiting
  - Do NOT add DB seeding

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: 9
  - **Blocked By**: 7

  **Acceptance Criteria**:
  - Server starts without errors
  - Swagger UI at `/docs` shows all endpoints
  - Postman collections exist and are valid JSON
  - README has all required sections

  **QA Scenarios**:
  ```
  Scenario: Server starts and /docs loads
    Tool: Bash (curl)
    Steps:
      1. Start server
      2. curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/docs
      3. Verify 200
    Expected Result: 200
    Evidence: .sisyphus/evidence/task-8-server.txt

  Scenario: OpenAPI spec has all endpoints
    Tool: Bash (curl)
    Steps:
      1. curl -s http://127.0.0.1:8000/openapi.json
      2. Verify paths include auth, laptops, parts routes
    Expected Result: All endpoints in spec
    Evidence: .sisyphus/evidence/task-8-openapi.json

  Scenario: Postman collections valid
    Tool: Bash
    Steps:
      1. Verify docs/postman/auth.json, laptops.json, parts.json exist
      2. Each is valid JSON
    Expected Result: All 3 files exist and parse
    Evidence: .sisyphus/evidence/task-8-postman.txt
  ```

  **Commit**: YES
  - Message: `docs: add Postman collections, README, and wire up main app`

- [x] 9. Full End-to-End QA Verification

  **What to do**:
  - Run complete integration across all modules:
    1. Signup/signin User A and B
    2. User A creates laptop + part
    3. User A uploads images to both
    4. User B tries to edit A's laptop → 403
    5. User A edits own laptop → 200
    6. User A deletes own part → 204
    7. List both with pagination
    8. Signout → verify token invalid
  - Capture all evidence
  - Verify no 500 errors

  **Must NOT do**:
  - Do NOT modify code
  - Do NOT skip scenarios

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (final before review)
  - **Blocks**: F1, F2, F3, F4
  - **Blocked By**: 8

  **Acceptance Criteria**:
  - All integration steps pass
  - Zero 500 errors
  - All evidence captured

  **QA Scenarios**:
  ```
  Scenario: Complete user journey
    Tool: Bash (curl)
    Steps:
      1. POST /api/auth/signup user A → 201
      2. POST /api/auth/signin user A → 200, get token_a
      3. POST /api/auth/signup user B → 201
      4. POST /api/auth/signin user B → 200, get token_b
      5. POST /api/laptops with token_a → 201
      6. POST /api/parts with token_a → 201
      7. POST image to laptop with token_a → 200
      8. POST image to part with token_a → 200
      9. PUT laptop with token_b → 403
      10. PUT laptop with token_a → 200
      11. DELETE part with token_a → 204
      12. GET /api/laptops?skip=0&limit=10 → 200
      13. GET /api/parts?skip=0&limit=10 → 200
      14. POST /api/auth/signout → 200
      15. GET /api/laptops with token_a → 401
    Expected Result: All 15 steps pass with expected codes
    Evidence: .sisyphus/evidence/task-9-full-journey.json
  ```

  **Commit**: YES
  - Message: `chore: end-to-end QA verification`

---

## Final Verification Wave (MANDATORY)

- [x] F1. **Plan Compliance Audit** — `oracle`
- [x] F2. **Code Quality Review** — `unspecified-high`
- [x] F3. **Real Manual QA** — `unspecified-high`
- [x] F4. **Scope Fidelity Check** — `deep`

---

## Commit Strategy

- **1**: `chore: initialize project structure and configuration`
- **2**: `feat(db): add AsyncMongoClient connection module`
- **3**: `feat(core): add JWT and password hashing utilities`
- **4**: `feat(auth): add signup, signin, signout endpoints`
- **5**: `feat(laptops): add CRUD routes with MongoDB async`
- **6**: `feat(parts): add CRUD routes with MongoDB async`
- **7**: `feat(upload): add image upload for laptops and parts`
- **8**: `docs: add Postman collections and update README`
- **9**: `chore: end-to-end QA verification`

---

## Success Criteria

### Verification Commands
```bash
uvicorn app.main:app --reload  # Expected: Server starts on http://127.0.0.1:8000
curl http://127.0.0.1:8000/docs  # Expected: HTML for Swagger UI
curl -X POST http://127.0.0.1:8000/api/auth/signup -H "Content-Type: application/json" -d '{"email":"test@test.com","password":"Test1234!"}'  # Expected: 201 with user data
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All QA scenarios pass
- [ ] Postman collections exported
- [ ] session.md up to date
