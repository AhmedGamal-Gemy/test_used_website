# Used Laptops & Parts Marketplace API

FastAPI backend for a marketplace where users can sign up, list used laptops and computer parts for sale, and upload images locally.

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB (PyMongo Async)
- **Auth**: JWT (PyJWT) + Argon2 password hashing (pwdlib)
- **Package Manager**: uv

## Prerequisites

- Python 3.13+
- MongoDB running locally
- [uv](https://docs.astral.sh/uv/) package manager

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

| Variable | Description | Default |
|---|---|---|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_DB_NAME` | Database name | `used_laptops_db` |
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens | (change in production) |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |

### 3. Run the server

```bash
uv run uvicorn app.main:app --reload
```

Server starts at `http://127.0.0.1:8000`

## API Documentation

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **OpenAPI JSON**: `http://127.0.0.1:8000/openapi.json`

## API Overview

### Authentication
- `POST /api/auth/signup` — Register a new user
- `POST /api/auth/signin` — Login and get JWT token
- `POST /api/auth/signout` — Logout (client-side token discard)

### Laptops
- `POST /api/laptops` — Create laptop listing (auth required)
- `GET /api/laptops` — List all laptops (paginated)
- `GET /api/laptops/{id}` — Get single laptop
- `PUT /api/laptops/{id}` — Update laptop (owner only)
- `DELETE /api/laptops/{id}` — Delete laptop (owner only)
- `POST /api/laptops/{id}/image` — Upload laptop image (owner only)

### Parts
- `POST /api/parts` — Create part listing (auth required)
- `GET /api/parts` — List all parts (paginated)
- `GET /api/parts/{id}` — Get single part
- `PUT /api/parts/{id}` — Update part (owner only)
- `DELETE /api/parts/{id}` — Delete part (owner only)
- `POST /api/parts/{id}/image` — Upload part image (owner only)

## Architecture

Layered design following SOLID principles:

```
Request → Router (HTTP) → Service (Business Logic) → Repository (Data Access) → MongoDB
```

- **Routers**: HTTP layer only — parse requests, delegate to services, return responses
- **Services**: Business logic — validation, ownership checks, domain exceptions
- **Repositories**: Data access — generic CRUD operations on MongoDB collections
- **Core**: Config constants, domain exceptions, security utilities

## Project Structure

```
├── app/
│   ├── core/
│   │   ├── config.py          # Centralized config (JWT, image, pagination)
│   │   ├── exceptions.py      # Domain exceptions + HTTP handlers
│   │   └── security.py        # JWT + password hashing (Argon2)
│   ├── db/
│   │   └── database.py        # MongoDB AsyncMongoClient (singleton)
│   ├── models/
│   │   ├── auth.py            # Auth Pydantic schemas
│   │   ├── laptops.py         # Laptop Pydantic schemas
│   │   └── parts.py           # Parts Pydantic schemas
│   ├── repositories/
│   │   ├── base.py            # Generic BaseRepository (CRUD, pagination)
│   │   └── user_repo.py       # UserRepository (find_by_email)
│   ├── routers/
│   │   ├── auth.py            # Auth endpoints (signup, signin, signout)
│   │   ├── laptops.py         # Laptop CRUD endpoints
│   │   └── parts.py           # Parts CRUD endpoints
│   ├── services/
│   │   ├── base.py            # BaseService (ownership, ID validation)
│   │   ├── auth_service.py    # User signup/lookup logic
│   │   ├── image_service.py   # Image upload/replace logic
│   │   ├── laptop_service.py  # Laptop CRUD (inherits BaseService)
│   │   └── part_service.py    # Part CRUD (inherits BaseService)
│   └── main.py                # FastAPI app entry point (lifespan)
├── uploads/                   # Uploaded images (served as static)
├── docs/postman/              # Postman collections
├── pyproject.toml             # Project dependencies (uv)
└── .env.example               # Environment template
```
