# Authentication Architecture

## Overview

The API implements **OAuth2 Bearer authentication** with JWT (JSON Web Tokens) following hexagonal architecture principles. Authentication infrastructure lives in the **core layer** (`api/core/auth/`) as it's shared infrastructure used across multiple bounded contexts.

## Architecture Decision: Where Does Authentication Live?

### Split Between Core and Users

Following hexagonal/DDD principles, authentication is **split between layers**:

**Core Layer (`api/core/auth/`)** - Generic utilities with NO domain knowledge:
1. **Password hashing**: `hash_password()`, `verify_password()` - works with any string
2. **JWT utilities**: `create_access_token()`, `decode_access_token()` - generic token handling
3. **OAuth2 scheme**: FastAPI security scheme configuration
4. **Token schemas**: Generic `Token`, `TokenData` models

**Users Layer (`api/users/`)** - User-specific authentication:
1. **Login endpoint**: `/auth/token` in `users/auth_routes.py` - uses UserService
2. **Auth dependencies**: `get_current_user()` in `users/auth_dependencies.py` - returns User entities
3. **User authentication**: `UserService.authenticate_user()` - business logic for user login

### Why This Split?

**✅ Preserves dependency rules:**
```
Users → Core ✅  (Users uses core JWT/password utilities)
Core → Users ❌  (Core NEVER imports from Users)
```

**✅ Core stays generic:**
- Password hashing works for any future entity (Admin, Customer, etc.)
- JWT utilities don't know about Users - just encode/decode tokens
- Other bounded contexts (Orders, Payments) can use same utilities

**✅ Users owns User-specific logic:**
- Login endpoint knows about User entities
- `get_current_user()` returns User, not a generic type
- User authentication includes business rules (active check)

## Structure

```
api/
├── core/
│   ├── auth/                          # Generic authentication utilities (Core Layer)
│   │   ├── __init__.py               # Package exports
│   │   ├── password.py               # Password hashing utilities (generic)
│   │   ├── jwt.py                    # JWT token creation/validation (generic)
│   │   ├── oauth2.py                 # OAuth2 Bearer scheme
│   │   ├── schemas.py                # Token request/response models
│   │   └── exceptions.py             # Auth-specific exceptions
│   ├── settings/
│   │   └── security.py               # JWT configuration (algorithm, expiration)
│   └── database/                      # Database infrastructure
└── users/                             # Users bounded context (Domain Layer)
    ├── models.py                     # User entity with hashed_password
    ├── services.py                   # authenticate_user(), create_user() with passwords
    ├── routes.py                     # User CRUD endpoints
    ├── auth_routes.py                # /auth/token login endpoint (User-specific)
    ├── auth_dependencies.py          # get_current_user dependency (returns User)
    ├── schemas.py                    # UserCreate with password field
    └── database/                     # User persistence adapters
```

## Authentication Flow

### 1. User Registration (Create User)

```
POST /users
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword123"
}
```

**Flow:**
1. Request → `users/routes.py::create_user()`
2. Route calls → `users/services.py::UserService.create_user()`
3. Service imports → `core/auth/password.py::hash_password()` (lazy import to avoid circular dependency)
4. Password is hashed using bcrypt
5. User entity created with `hashed_password` field
6. User saved to database via repository

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "created_at": "2025-12-01T...",
  "updated_at": "2025-12-01T...",
  "full_name": "John Doe"
}
```

### 2. User Login (Get Token)

```
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword123
```

**Flow:**
1. Request → `users/auth_routes.py::login()`
2. Route gets `UserService` via dependency injection
3. Route calls → `users/services.py::UserService.authenticate_user()`
4. Service:
   - Finds user by email
   - Imports → `core/auth/password.py::verify_password()` (lazy import)
   - Verifies password against hashed_password
   - Returns User entity if valid
5. Route calls → `core/auth/jwt.py::create_access_token()`
6. JWT token created with user claims (sub=user_id, email=email)
7. Token signed with secret key using HS256 algorithm

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Protected Route Access

```
GET /users/{user_id}
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Flow:**
1. Request → Protected route with `Depends(get_current_user)`
2. Dependency → `users/auth_dependencies.py::get_current_user()`
3. Dependency:
   - Extracts token from `Authorization: Bearer <token>` header via `core.auth.oauth2_scheme`
   - Calls → `core/auth/jwt.py::decode_access_token()`
   - Validates token signature and expiration
   - Extracts user_id from `sub` claim
   - Gets `UserService` via dependency injection
   - Calls → `users/services.py::UserService.get_user(user_id)`
   - Returns User entity
4. Route receives authenticated User entity
5. Route executes business logic with user context

## Components

### Password Hashing (`core/auth/password.py`)

Uses **passlib** with **bcrypt** algorithm:

```python
from api.core.auth import hash_password, verify_password

# Hash password
hashed = hash_password("plaintext")

# Verify password
is_valid = verify_password("plaintext", hashed)
```

**Features:**
- Bcrypt algorithm (industry standard, slow by design)
- Automatic salt generation
- Configurable work factor for future-proofing

### JWT Tokens (`core/auth/jwt.py`)

Uses **python-jose** with **cryptography** backend:

```python
from api.core.auth import create_access_token, decode_access_token
from datetime import timedelta

# Create token
token = create_access_token(
    data={"sub": user_id, "email": email},
    expires_delta=timedelta(minutes=30)
)

# Decode and validate token
payload = decode_access_token(token)
user_id = payload["sub"]
```

**Configuration** (in `core/settings/security.py`):
- `SECURITY_JWT_ALGORITHM`: HS256 (default)
- `SECURITY_JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: 30 minutes (default)
- `SECURITY_SECRET_KEY`: Secret key for signing

### OAuth2 Scheme (`core/auth/oauth2.py`)

FastAPI OAuth2 Bearer scheme:

```python
from api.core.auth import oauth2_scheme

# Automatically extracts token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
```

**Features:**
- Automatic OpenAPI documentation generation
- "Authorize" button in Swagger UI (`/docs`)
- Standard OAuth2 password flow

### Protected Routes (`users/auth_dependencies.py`)

FastAPI dependencies for authentication:

```python
from api.users import get_current_user, get_current_active_user
from fastapi import Depends

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    # current_user is automatically injected
    return {"user_id": current_user.id.value}
```

**Available dependencies:**
- `get_current_user`: Returns authenticated User, raises 401 if invalid
- `get_current_active_user`: Returns User only if `is_active=True`, raises 403 if inactive

## Security Configuration

### Environment Variables

```bash
# Required in production
SECURITY_SECRET_KEY=your-secret-key-min-32-chars

# Optional (with defaults)
SECURITY_JWT_ALGORITHM=HS256
SECURITY_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
SECURITY_ALLOWED_HOSTS=*
```

### Secret Key Generation

**Production:**
```bash
# Generate secure random secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Development:**
Uses default `dev-secret-key-change-in-production` (insecure, never use in production!)

## Domain Integration

### User Model (`users/models.py`)

```python
@dataclass
class User:
    id: UserId
    email: Email
    first_name: str
    last_name: str
    hashed_password: str  # ← Password stored as hash
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

**Important:**
- Password is NEVER stored in plain text
- `hashed_password` field contains bcrypt hash
- Original password is never logged or returned in API responses

### User Service (`users/services.py`)

```python
class UserService:
    async def create_user(self, email: Email, first_name: str, last_name: str, password: str) -> User:
        # Hashes password and creates user
        ...

    async def authenticate_user(self, email: Email, password: str) -> User:
        # Verifies password and returns user if valid
        # Raises ValueError if invalid
        ...
```

**Design notes:**
- Uses lazy imports (`from ..core.auth import hash_password`) to avoid circular dependencies
- Raises `ValueError` for consistency with other domain methods
- Authentication is a domain service method because it involves business rules (active user check)

## Circular Import Prevention

### The Problem

Initial implementation had circular imports:
```
core.auth → users.dependencies → users.services → core.auth ❌
```

### The Solution

**Lazy imports** in `users/services.py`:

```python
async def create_user(self, ..., password: str) -> User:
    # Import here to avoid circular imports
    from ..core.auth import hash_password

    hashed_password = hash_password(password)
    ...
```

**Why this works:**
- Import happens at runtime, not module load time
- `core.auth` is fully initialized by the time service methods run
- No circular dependency during module initialization

## Testing

### Test User Registration and Login

```python
import httpx

# 1. Register user
response = httpx.post(
    "http://localhost:8000/users",
    json={
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpassword123"
    }
)
user = response.json()

# 2. Login
response = httpx.post(
    "http://localhost:8000/auth/token",
    data={
        "username": "test@example.com",  # username = email
        "password": "testpassword123"
    }
)
token = response.json()["access_token"]

# 3. Access protected route
response = httpx.get(
    f"http://localhost:8000/users/{user['id']}",
    headers={"Authorization": f"Bearer {token}"}
)
```

### Test Invalid Credentials

```python
# Wrong password
response = httpx.post(
    "http://localhost:8000/auth/token",
    data={"username": "test@example.com", "password": "wrongpassword"}
)
assert response.status_code == 401

# Invalid token
response = httpx.get(
    "http://localhost:8000/users/some-id",
    headers={"Authorization": "Bearer invalid-token"}
)
assert response.status_code == 401
```

## API Reference

### POST /auth/token

**Description:** OAuth2 password login - exchange email and password for JWT token

**Request:**
```
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

**Response 200:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

**Response 401:** Invalid credentials

### POST /users

**Description:** Register a new user

**Request:**
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword123"
}
```

**Response 201:** User created (password field not returned)

**Response 400:** Validation error or email already exists

### Protected Endpoints

All user endpoints require authentication:
- `GET /users/{user_id}` - Get user details
- `PATCH /users/{user_id}` - Update user profile
- `POST /users/{user_id}/activate` - Activate user
- `POST /users/{user_id}/deactivate` - Deactivate user
- `DELETE /users/{user_id}` - Delete user

**Authorization Header:**
```
Authorization: Bearer <access_token>
```

## Best Practices

### 1. Never Log Passwords

```python
# ❌ BAD
logger.info(f"User login: {email}, password: {password}")

# ✅ GOOD
logger.info(f"User login attempt: {email}")
```

### 2. Use Lazy Imports for Auth in Domain

```python
# ❌ BAD - Circular import
from ..core.auth import hash_password

class UserService:
    async def create_user(self, password: str):
        hashed = hash_password(password)

# ✅ GOOD - Lazy import
class UserService:
    async def create_user(self, password: str):
        from ..core.auth import hash_password
        hashed = hash_password(password)
```

### 3. Always Validate User is Active

```python
# ✅ Use get_current_active_user for routes requiring active users
@router.get("/protected")
async def protected(user: User = Depends(get_current_active_user)):
    ...
```

### 4. Set Strong Secret Keys in Production

```bash
# ❌ BAD
SECURITY_SECRET_KEY=dev-secret-key-change-in-production

# ✅ GOOD
SECURITY_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

### 5. Use HTTPS in Production

JWT tokens are bearer tokens - anyone with the token can impersonate the user. Always use HTTPS to prevent token interception.

## Security Considerations

### Token Expiration

- Default: 30 minutes
- Configurable via `SECURITY_JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
- After expiration, user must login again
- No automatic refresh tokens (add if needed)

### Password Requirements

Currently enforced in schema:
- Minimum 8 characters (`min_length=8`)
- Maximum 100 characters (`max_length=100`)

**Add custom validation** for stronger requirements:
```python
from pydantic import field_validator

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase")
        # Add more rules...
        return v
```

### Brute Force Protection

Not currently implemented. Consider adding:
- Rate limiting on `/auth/token`
- Account lockout after N failed attempts
- CAPTCHA after repeated failures

### Password Reset

Not currently implemented. Future enhancement:
1. User requests password reset
2. Generate time-limited reset token
3. Send token via email
4. User submits new password with token
5. Verify token and update password

## References

- [OAuth2 Password Flow](https://oauth.net/2/grant-types/password/)
- [JWT (JSON Web Tokens)](https://jwt.io/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Hexagonal Architecture](./hexagonal-architecture.md)
- [Architecture FAQ](./architecture.md)
