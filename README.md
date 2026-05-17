# Used Laptops & Parts Marketplace

Full-stack marketplace application where users can sign up, list used laptops and computer parts for sale, communicate with sellers, and review vendors.

**Quick Links**:
- [Backend API Docs](#api-documentation)
- [Frontend Setup](#frontend-setup)
- [Quick Start Guide](#quick-start-guide)

---

## Quick Start Guide

### Start Backend (Terminal 1)
```bash
# Install backend dependencies
uv sync

# Start MongoDB (if not running)
# Windows: net start MongoDB
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod

# Copy environment config (first time only)
cp .env.example .env
# Edit .env to set your PORT (default: 8000)

# Start the API server — uses PORT from .env
uv run python app/main.py
# OR specify port explicitly:
# uv run uvicorn app.main:app --reload --port 8000
```
Backend runs on the port configured in `.env` (default `http://127.0.0.1:8000`)

### Start Frontend (Terminal 2)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Copy environment config (first time only)
cp .env.example .env
# Edit .env to set VITE_API_URL to match your backend port

# Start development server
npm run dev
```
Frontend runs on `http://localhost:5173`

### Access the Application
1. Open browser to `http://localhost:5173`
2. Register a new account
3. Start browsing and creating listings!

---

## Backend

### Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB (PyMongo Async)
- **Auth**: JWT (PyJWT) + Argon2 password hashing (pwdlib)
- **Package Manager**: uv

### Prerequisites

- Python 3.13+
- MongoDB running locally
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

#### 1. Install dependencies

```bash
uv sync
```

#### 2. Configure environment

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
| `HOST` | Backend server host | `127.0.0.1` |
| `PORT` | Backend server port | `8000` |
| `FRONTEND_URLS` | CORS allowed origins (comma-separated) | `http://localhost:5173,http://127.0.0.1:5173` |
| `NOTIFICATION_PROVIDER` | Notification backend | `console` |
| `WHATSAPP_TOKEN` | WhatsApp Business API token | _(empty)_ |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp phone number ID | _(empty)_ |
| `WHATSAPP_TEMPLATE_NAME` | WhatsApp template name | `notification_template` |
| `ADMIN_EMAIL` | Email address for admin user | _(empty)_ |

**Admin User**: The first user to register becomes admin automatically. Additionally, any user registering with the email specified in `ADMIN_EMAIL` will be granted admin privileges.

#### 3. Run the server

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

### Services
- `POST /api/services` — Create service listing (admin only)
- `GET /api/services` — List services with filters (service_type, brand, price range)
- `GET /api/services/{id}` — Get single service
- `PUT /api/services/{id}` — Update service (admin only)
- `DELETE /api/services/{id}` — Delete service (admin only)

### Orders
- `POST /api/orders` — Create order for a listing (auth required)
- `GET /api/orders` — Get current user's orders
- `GET /api/orders/{id}` — Get single order
- `GET /api/admin/orders` — Get all orders (admin only)
- `PUT /api/admin/orders/{id}/status` — Update order status (admin only)

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

### Users (Admin)
- `GET /api/users` — List all users with pagination (admin only)
- `PUT /api/users/{id}/role` — Change user role (admin only)

### Admin — Bulk Operations
- `POST /api/admin/bulk-delete/laptops` — Delete multiple laptops by IDs (admin only)
- `POST /api/admin/bulk-delete/parts` — Delete multiple parts by IDs (admin only)
- `POST /api/admin/bulk-delete/services` — Delete multiple services by IDs (admin only)
- `POST /api/admin/bulk-delete/users` — Delete multiple user accounts by IDs (admin only, cannot delete self)

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
│   │   ├── messages.py        # Message Pydantic schemas
│   │   ├── orders.py          # Order Pydantic schemas
│   │   ├── parts.py           # Parts Pydantic schemas
│   │   ├── reviews.py         # Review Pydantic schemas
│   │   └── services.py        # Service Pydantic schemas
│   ├── repositories/
│   │   ├── base.py            # Generic BaseRepository (CRUD, pagination)
│   │   └── user_repo.py       # UserRepository (email, refresh tokens)
│   ├── routers/
│   │   ├── admin.py           # Admin bulk-delete operations
│   │   ├── auth.py            # Auth endpoints (signup, signin, signout, refresh)
│   │   ├── favorites.py       # Favorites/wishlist endpoints
│   │   ├── laptops.py         # Laptop CRUD + search endpoints
│   │   ├── messages.py        # Messaging endpoints
│   │   ├── orders.py          # Order CRUD + admin status management
│   │   ├── parts.py           # Parts CRUD + search endpoints
│   │   ├── reviews.py         # Review & rating endpoints
│   │   ├── services.py        # Service listings CRUD endpoints
│   │   └── users.py           # User profile + admin user management
│   ├── services/
│   │   ├── base.py            # BaseService (ownership, ID validation)
│   │   ├── auth_service.py    # Signup, signin, refresh tokens
│   │   ├── favorite_service.py # Favorites/wishlist
│   │   ├── image_service.py   # Image upload/replace logic
│   │   ├── laptop_service.py  # Laptop CRUD + search
│   │   ├── message_service.py # Messaging (triggers notifications)
│   │   ├── notification_service.py # Notification dispatch service
│   │   ├── order_service.py   # Order business logic
│   │   ├── part_service.py    # Part CRUD + search
│   │   ├── review_service.py  # Reviews + ratings (triggers notifications)
│   │   ├── service_service.py # Service listing CRUD + search
│   │   └── user_service.py    # Profile management
│   └── main.py                # FastAPI app entry point (lifespan)
├── uploads/                   # Uploaded images (served as static)
├── docs/postman/              # Postman collections
├── pyproject.toml             # Project dependencies (uv)
├── .env.example               # Environment template
├── e2e-master-test.mjs        # Comprehensive E2E tests (106 tests)
├── e2e-edge-cases.mjs         # Security + edge-case E2E tests (44 tests)
└── package.json               # Node dependencies for E2E tests
```

## Frontend Setup

### Prerequisites
- Node.js 18+

### Installation
```bash
cd frontend
npm install
```

### Development
```bash
npm run dev
```
Starts Vite dev server on `http://localhost:5173`

### Production Build
```bash
npm run build
```

### Environment Variables
Both backend and frontend share a single `.env` file at the project root:
```bash
# Set the backend port and frontend API URL together
PORT=8000
VITE_API_URL=http://127.0.0.1:8000
```

> **Note**: Vite only exposes variables prefixed with `VITE_` to client-side code. The `VITE_API_URL` is read by the frontend at runtime and can differ from the backend `PORT` (e.g., when using a reverse proxy).

### Tech Stack
- React 19
- Vite 8
- Tailwind CSS 4
- React Router DOM
- Axios
- Lucide React Icons

### Features
- User authentication (signup, signin, signout, refresh tokens)
- **Admin-only listing management** (create, edit, delete laptops, parts, and service listings)
- Browse laptops, parts, and services with search and filters
- Order system with admin status management (pending → confirmed → processing → shipped → completed / cancelled)
- Admin dashboard with KPIs and full order oversight
- Favorites/wishlist
- Messaging system (contact seller + admin reply)
- Seller reviews and ratings
- User profile management
- Responsive design (mobile + desktop)

### User Roles
- **Admin**: Can create, edit, and delete all listings; manage orders; view all users and change roles. First user to register becomes admin automatically, or use `ADMIN_EMAIL` environment variable.
- **User**: Can browse listings, place orders, add to favorites, send messages, write reviews, and manage their profile.

### Frontend Project Structure
```
frontend/
├── public/
│   ├── favicon.svg
│   └── icons.svg
├── src/
│   ├── api/
│   │   ├── client.js
│   │   └── index.js
│   ├── assets/
│   │   ├── hero.png
│   │   └── react.svg
│   ├── components/
│   │   ├── Badge.jsx
│   │   ├── Button.jsx
│   │   ├── Card.jsx
│   │   ├── EmptyState.jsx
│   │   ├── Footer.jsx
│   │   ├── ImageUpload.jsx
│   │   ├── Input.jsx
│   │   ├── Navbar.jsx
│   │   ├── ProtectedRoute.jsx
│   │   ├── PublicRoute.jsx
│   │   ├── Spinner.jsx
│   │   ├── StarRating.jsx
│   │   └── Toast.jsx
│   ├── contexts/
│   │   └── AuthContext.jsx
│   ├── hooks/
│   │   └── useToast.jsx
│   ├── pages/
│   │   ├── AdminDashboard.jsx # Admin dashboard with KPIs
│   │   ├── AdminListings.jsx  # Admin bulk listing management
│   │   ├── AdminOrders.jsx    # Admin order management
│   │   ├── BrowseLaptops.jsx
│   │   ├── BrowseParts.jsx
│   │   ├── CreateListing.jsx
│   │   ├── EditListing.jsx
│   │   ├── Favorites.jsx
│   │   ├── Home.jsx
│   │   ├── ListingDetail.jsx
│   │   ├── Login.jsx
│   │   ├── Messages.jsx
│   │   ├── Profile.jsx
│   │   ├── Register.jsx
│   │   └── SellerProfile.jsx
│   ├── App.css
│   ├── App.jsx
│   ├── index.css
│   └── main.jsx
├── index.html
├── package.json
├── vite.config.js
└── eslint.config.js
```

---

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use a different port
uv run uvicorn app.main:app --port 8001
```

**MongoDB connection error:**
```bash
# Ensure MongoDB is running
# Windows: net start MongoDB
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod
```

### Frontend Issues

**Cannot connect to backend:**
1. Verify backend is running: `curl http://127.0.0.1:8000/api/laptops`
2. Check `VITE_API_URL` in `frontend/.env`
3. Ensure CORS is enabled in backend (should be automatic)

**Build fails:**
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Port 5173 already in use:**
```bash
# Use a different port
npm run dev -- --port 5174
```

### Common Errors

**"Failed to fetch" in browser console:**
- Backend is not running
- CORS not configured correctly
- Wrong API URL in frontend

**Token expired errors:**
- Refresh token flow should handle this automatically
- Try logging out and back in

**Image upload fails:**
- Ensure `uploads/` directory exists and is writable
- Check file size limits (default: 5MB per image)

---

## Testing

### Prerequisites
- Both servers running: backend (port from `.env`, default `8000`), frontend on `http://localhost:5173`
- Node.js 18+ with Playwright: `npm install` (root level)
- MongoDB running locally with empty `used_laptops_db` (or one that allows new user signups)

### E2E Test Suites

Two Playwright-based test suites cover the full application:

**Master Test** (106 tests — core functionality):
```bash
node e2e-master-test.mjs
```
Covers: auth (signup, signin, refresh, signout), user profiles, laptop/part/service CRUD, favorites, messaging, reviews, orders (full lifecycle), admin dashboard, frontend UI rendering, mobile viewport, data integrity.

**Edge-Case Test** (44 tests — security + edge cases):
```bash
node e2e-edge-cases.mjs
```
Covers: NoSQL injection (5 vectors), XSS storage (3 vectors), JWT tampering/expiration (4 vectors), input sanitization (long strings, unicode, HTML, negative prices, empty/null fields, 12 tests), state transitions (order status skipping, reverse, deletion cascade, 8 tests), file upload validation, frontend edge cases (empty states, mobile viewport, loading states, auth redirect, XSS rendering, 11 tests).

### API Testing
```bash
# Quick smoke test (update port to match your .env)
curl http://127.0.0.1:8000/api/laptops
```

### Manual Testing
1. Start both backend and frontend servers
2. Open browser to `http://localhost:5173`
3. Follow the user journey: Register → Sign In → Browse → Create Listing → Message → Review

---

## Deployment

### Backend Deployment
1. Set production environment variables
2. Use a production WSGI server (e.g., Gunicorn with Uvicorn workers)
3. Deploy to cloud provider (AWS, Heroku, DigitalOcean, etc.)

### Frontend Deployment
1. Build production bundle: `npm run build`
2. Serve `frontend/dist/` directory via static file server
3. Configure environment variables for production API URL

---

## License

MIT

---

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review API documentation at `http://127.0.0.1:8000/docs`
3. Check backend logs for error details
