# Used Laptops & Parts Marketplace API

FastAPI backend for a marketplace where users can sign up, list used laptops and computer parts for sale, communicate with sellers, and review vendors.

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
| `NOTIFICATION_PROVIDER` | Notification backend | `console` |
| `WHATSAPP_TOKEN` | WhatsApp Business API token | _(empty)_ |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp phone number ID | _(empty)_ |
| `WHATSAPP_TEMPLATE_NAME` | WhatsApp template name | `notification_template` |

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
- `POST /api/auth/signin` — Login and get access + refresh token
- `POST /api/auth/signout` — Logout (invalidates refresh token)
- `POST /api/auth/refresh` — Exchange refresh token for new access + refresh token

### User Profile
- `GET /api/users/me` — Get current user profile
- `PUT /api/users/me` — Update profile (full_name, phone, location, avatar_url)

### Laptops
- `POST /api/laptops` — Create laptop listing (auth required)
- `GET /api/laptops` — List laptops with search & filtering (brand, category, condition, price range, search)
- `GET /api/laptops/{id}` — Get single laptop
- `PUT /api/laptops/{id}` — Update laptop (owner only)
- `DELETE /api/laptops/{id}` — Delete laptop (owner only)
- `POST /api/laptops/{id}/image` — Upload laptop image (owner only)

### Parts
- `POST /api/parts` — Create part listing (auth required)
- `GET /api/parts` — List parts with search & filtering
- `GET /api/parts/{id}` — Get single part
- `PUT /api/parts/{id}` — Update part (owner only)
- `DELETE /api/parts/{id}` — Delete part (owner only)
- `POST /api/parts/{id}/image` — Upload part image (owner only)

### Favorites
- `POST /api/favorites/laptops/{id}` — Add laptop to favorites
- `DELETE /api/favorites/laptops/{id}` — Remove laptop from favorites
- `POST /api/favorites/parts/{id}` — Add part to favorites
- `DELETE /api/favorites/parts/{id}` — Remove part from favorites

### Reviews & Ratings
- `POST /api/reviews/seller/{seller_id}` — Rate a seller (1-5 stars, one per seller)
- `GET /api/reviews/seller/{seller_id}` — Get seller rating + all reviews

### Messaging
- `POST /api/messages` — Send a message about a listing
- `GET /api/messages/conversation` — Get messages for a listing
- `GET /api/messages/conversations` — Get user's active conversations

## Notification System

The marketplace sends automatic notifications for:
- **New message** — Notifies the listing owner when someone messages about their listing
- **New review** — Notifies the seller when they receive a review

Notification backends:
- **ConsoleProvider** (default/dev) — Prints notifications to console and logs them
- **WhatsAppProvider** (production) — Sends via WhatsApp Business Cloud API (stubbed, ready for credentials)

To enable WhatsApp notifications, set `NOTIFICATION_PROVIDER=whatsapp` and configure the `WHATSAPP_*` env vars.

## Architecture

Layered design following SOLID principles:

```
Request → Router (HTTP) → Service (Business Logic) → Repository (Data Access) → MongoDB
                                              ↘ NotificationProvider (Console/WhatsApp)
```

- **Routers**: HTTP layer only — parse requests, delegate to services, return responses
- **Services**: Business logic — validation, ownership checks, domain exceptions, notification triggers
- **Repositories**: Data access — generic CRUD operations on MongoDB collections
- **Core**: Config (frozen dataclasses), domain exceptions, security, notification providers

## Project Structure

```
├── app/
│   ├── core/
│   │   ├── config.py          # Centralized config (JWT, image, pagination, notification, WhatsApp)
│   │   ├── exceptions.py      # Domain exceptions + HTTP handlers
│   │   ├── notifications.py   # NotificationProvider abstraction (Console, WhatsApp)
│   │   └── security.py        # JWT + password hashing (Argon2)
│   ├── db/
│   │   └── database.py        # MongoDB AsyncMongoClient (singleton)
│   ├── models/
│   │   ├── auth.py            # Auth Pydantic schemas
│   │   ├── laptops.py         # Laptop Pydantic schemas
│   │   ├── parts.py           # Parts Pydantic schemas
│   │   ├── reviews.py         # Review Pydantic schemas
│   │   └── messages.py        # Message Pydantic schemas
│   ├── repositories/
│   │   ├── base.py            # Generic BaseRepository (CRUD, pagination)
│   │   └── user_repo.py       # UserRepository (email, refresh tokens)
│   ├── routers/
│   │   ├── auth.py            # Auth endpoints (signup, signin, signout, refresh)
│   │   ├── laptops.py         # Laptop CRUD + search endpoints
│   │   ├── parts.py           # Parts CRUD + search endpoints
│   │   ├── users.py           # User profile endpoints
│   │   ├── favorites.py       # Favorites/wishlist endpoints
│   │   ├── reviews.py         # Review & rating endpoints
│   │   └── messages.py        # Messaging endpoints
│   ├── services/
│   │   ├── base.py            # BaseService (ownership, ID validation)
│   │   ├── auth_service.py    # Signup, signin, refresh tokens
│   │   ├── image_service.py   # Image upload/replace logic
│   │   ├── laptop_service.py  # Laptop CRUD + search
│   │   ├── part_service.py    # Part CRUD + search
│   │   ├── user_service.py    # Profile management
│   │   ├── favorite_service.py # Favorites/wishlist
│   │   ├── review_service.py  # Reviews + ratings (triggers notifications)
│   │   ├── message_service.py # Messaging (triggers notifications)
│   │   └── notification_service.py # Notification dispatch service
│   └── main.py                # FastAPI app entry point (lifespan)
├── uploads/                   # Uploaded images (served as static)
├── docs/postman/              # Postman collections
├── pyproject.toml             # Project dependencies (uv)
└── .env.example               # Environment template
```
