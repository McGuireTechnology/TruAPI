# Core Authentication Module - Cross-Context Usage

## Why Core Has Auth Infrastructure

The `api/core/auth` module provides **generic, reusable authentication utilities** that have **no knowledge of domain entities**. This follows the **Shared Infrastructure** pattern in DDD.

### Key Principle
- ✅ **Core**: Generic utilities (password hashing, JWT creation/validation)
- ✅ **Bounded Contexts**: Entity-specific logic (login with User, login with Admin, etc.)
- ❌ **Core NEVER imports from modules**: Keeps dependency direction clean

## What's in core.auth

```python
# Generic utilities - NO domain knowledge
from api.core.auth import (
    hash_password,         # Hash any password
    verify_password,       # Verify any password
    create_access_token,   # Create JWT with any claims
    decode_access_token,   # Decode JWT to dict
    oauth2_scheme,         # OAuth2PasswordBearer config
    Token,                 # Generic token response schema
    TokenData              # Generic token payload schema
)
```

These are **infrastructure primitives** - they work with strings and dicts, not domain entities.

## Example 1: Users Bounded Context (Current)

### Problem: Users need authentication
Users need to:
- Hash passwords when creating accounts
- Verify passwords during login
- Issue JWT tokens after successful login
- Protect routes requiring a User entity

### Solution: Users uses core.auth utilities

```python
# api/users/services.py
from api.core.auth import hash_password, verify_password, create_access_token

class UserService:
    async def create_user(self, email: Email, password: str, ...) -> User:
        """Register new user with password."""
        # Use core utility to hash password
        hashed = hash_password(password)

        user = User(
            id=UserId.new(),
            email=email,
            hashed_password=hashed,  # Store hashed, never plain
            ...
        )
        await self._repository.save(user)
        return user

    async def authenticate_user(self, email: Email, password: str) -> User:
        """Verify user credentials."""
        user = await self._repository.find_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")

        # Use core utility to verify password
        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")

        if not user.is_active:
            raise ValueError("User is inactive")

        return user


# api/users/auth/routes.py
from api.core.auth import Token, create_access_token

@router.post("/auth/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    """Login endpoint - User-specific."""
    # Authenticate using User entity
    user = await user_service.authenticate_user(
        Email(form_data.username),
        form_data.password
    )

    # Use core utility to create JWT with User claims
    access_token = create_access_token(
        data={
            "sub": str(user.id.value),  # User ULID
            "email": user.email.value,
            "type": "user"  # Distinguish from admin/service tokens
        }
    )

    return Token(access_token=access_token, token_type="bearer")


# api/users/auth/dependencies.py
from api.core.auth import oauth2_scheme, decode_access_token

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """Extract User entity from JWT token."""
    try:
        # Use core utility to decode JWT
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Fetch User entity from database
        user = await user_service.get_user(UserId.from_string(user_id))

        if not user.is_active:
            raise HTTPException(status_code=401, detail="Inactive user")

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Key Point**: Users bounded context uses core.auth utilities but adds User-specific logic.

---

## Example 2: Admin Bounded Context

### Problem: Admins need separate authentication
You want an admin panel with different users, permissions, and login flow.

### Solution: Admin context uses the SAME core.auth utilities

```python
# api/admin/models.py
from dataclasses import dataclass
from ulid import ULID

@dataclass
class AdminId:
    value: ULID

    @classmethod
    def new(cls) -> AdminId:
        return cls(ULID())

@dataclass
class Admin:
    """Admin entity - completely separate from User."""
    id: AdminId
    username: str
    hashed_password: str
    role: AdminRole  # SUPER_ADMIN, MODERATOR, etc.
    is_active: bool
    permissions: list[str]


# api/admin/services.py
from api.core.auth import hash_password, verify_password  # REUSE!

class AdminService:
    async def create_admin(self, username: str, password: str, role: AdminRole) -> Admin:
        """Create new admin account."""
        # Use the SAME core utility
        hashed = hash_password(password)

        admin = Admin(
            id=AdminId.new(),
            username=username,
            hashed_password=hashed,
            role=role,
            is_active=True,
            permissions=role.get_permissions()
        )
        await self._repository.save(admin)
        return admin

    async def authenticate_admin(self, username: str, password: str) -> Admin:
        """Verify admin credentials."""
        admin = await self._repository.find_by_username(username)
        if not admin:
            raise ValueError("Invalid credentials")

        # Use the SAME core utility
        if not verify_password(password, admin.hashed_password):
            raise ValueError("Invalid credentials")

        if not admin.is_active:
            raise ValueError("Admin is inactive")

        return admin


# api/admin/auth/routes.py
from api.core.auth import Token, create_access_token  # REUSE!

@router.post("/admin/auth/token", response_model=Token)
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    admin_service: AdminService = Depends(get_admin_service)
):
    """Admin login endpoint - completely separate from users."""
    # Authenticate using Admin entity
    admin = await admin_service.authenticate_admin(
        form_data.username,
        form_data.password
    )

    # Use the SAME core utility but with Admin claims
    access_token = create_access_token(
        data={
            "sub": str(admin.id.value),
            "username": admin.username,
            "role": admin.role.value,
            "permissions": admin.permissions,
            "type": "admin"  # Different type!
        }
    )

    return Token(access_token=access_token, token_type="bearer")


# api/admin/auth/dependencies.py
from api.core.auth import oauth2_scheme, decode_access_token  # REUSE!

# Separate OAuth2 scheme for admin (different tokenUrl)
admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/auth/token")

async def get_current_admin(
    token: str = Depends(admin_oauth2_scheme),
    admin_service: AdminService = Depends(get_admin_service)
) -> Admin:
    """Extract Admin entity from JWT token."""
    try:
        # Use the SAME core utility
        payload = decode_access_token(token)

        # Verify it's an admin token
        if payload.get("type") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        admin_id = payload.get("sub")
        admin = await admin_service.get_admin(AdminId.from_string(admin_id))

        if not admin.is_active:
            raise HTTPException(status_code=401, detail="Inactive admin")

        return admin
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def require_permission(permission: str):
    """Dependency to check admin has specific permission."""
    async def permission_checker(admin: Admin = Depends(get_current_admin)) -> Admin:
        if permission not in admin.permissions:
            raise HTTPException(status_code=403, detail=f"Permission required: {permission}")
        return admin
    return permission_checker


# Usage in admin routes
@router.delete("/admin/users/{user_id}")
async def delete_user_by_admin(
    user_id: str,
    admin: Admin = Depends(require_permission("users:delete"))  # Permission check
):
    """Only super admins can delete users."""
    # admin is already verified to have "users:delete" permission
    ...
```

**Key Point**: Admin context is completely separate from Users, but both use the same core.auth primitives.

---

## Example 3: Service Accounts / API Keys

### Problem: Microservices need to authenticate to each other
You have background jobs, external services, or other systems that need API access without user login.

### Solution: Service context uses core.auth for API key verification

```python
# api/services/models.py
@dataclass
class ServiceAccount:
    """Service account for system-to-system auth."""
    id: ServiceAccountId
    name: str  # e.g., "payment-processor", "email-service"
    hashed_api_key: str  # API key hashed like a password
    scopes: list[str]  # e.g., ["orders:read", "payments:write"]
    is_active: bool


# api/services/service.py
from api.core.auth import hash_password, verify_password  # REUSE!

class ServiceAccountService:
    async def create_service_account(self, name: str, scopes: list[str]) -> tuple[ServiceAccount, str]:
        """Create service account and return raw API key (only time it's shown)."""
        import secrets

        # Generate cryptographically secure API key
        raw_api_key = f"sk_{secrets.token_urlsafe(32)}"

        # Use the SAME core utility to hash it
        hashed = hash_password(raw_api_key)

        service = ServiceAccount(
            id=ServiceAccountId.new(),
            name=name,
            hashed_api_key=hashed,
            scopes=scopes,
            is_active=True
        )
        await self._repository.save(service)

        # Return both (only time raw key is available!)
        return service, raw_api_key

    async def authenticate_service(self, api_key: str) -> ServiceAccount:
        """Verify API key."""
        # Extract service ID from key prefix (or lookup all and try each)
        service = await self._repository.find_by_api_key_prefix(api_key[:10])

        if not service:
            raise ValueError("Invalid API key")

        # Use the SAME core utility
        if not verify_password(api_key, service.hashed_api_key):
            raise ValueError("Invalid API key")

        if not service.is_active:
            raise ValueError("Service account is inactive")

        return service


# api/services/auth/dependencies.py
from api.core.auth import create_access_token, decode_access_token  # REUSE!
from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_service(
    credentials: HTTPAuthorizationCredentials = Security(security),
    service_service: ServiceAccountService = Depends(get_service_service)
) -> ServiceAccount:
    """Extract service account from API key."""
    api_key = credentials.credentials

    # Authenticate service
    service = await service_service.authenticate_service(api_key)

    return service


async def require_scope(scope: str):
    """Dependency to check service has required scope."""
    async def scope_checker(service: ServiceAccount = Depends(get_current_service)) -> ServiceAccount:
        if scope not in service.scopes:
            raise HTTPException(status_code=403, detail=f"Scope required: {scope}")
        return service
    return scope_checker


# Usage in API routes
@router.post("/api/orders")
async def create_order_via_api(
    order_data: OrderCreate,
    service: ServiceAccount = Depends(require_scope("orders:write"))
):
    """Service accounts with orders:write scope can create orders."""
    # service is already verified to have "orders:write" scope
    ...
```

**Key Point**: Service accounts use password hashing for API keys - same primitive, different entity.

---

## Example 4: OAuth2 Social Login (Users with Google/GitHub)

### Problem: Users want to login with Google/GitHub instead of password
You want social login but still need local accounts.

### Solution: Users context adapts core.auth for social login

```python
# api/users/models.py
from enum import Enum

class AuthProvider(Enum):
    LOCAL = "local"      # Password-based
    GOOGLE = "google"    # OAuth2 Google
    GITHUB = "github"    # OAuth2 GitHub

@dataclass
class User:
    id: UserId
    email: Email
    hashed_password: str | None  # None for social login users
    auth_provider: AuthProvider
    provider_id: str | None  # Google/GitHub user ID
    ...


# api/users/services.py
from api.core.auth import hash_password, create_access_token  # REUSE!

class UserService:
    async def create_user_from_google(self, google_user_info: dict) -> User:
        """Create user from Google OAuth2 callback."""
        user = User(
            id=UserId.new(),
            email=Email(google_user_info["email"]),
            first_name=google_user_info.get("given_name", ""),
            last_name=google_user_info.get("family_name", ""),
            hashed_password=None,  # No password for social login
            auth_provider=AuthProvider.GOOGLE,
            provider_id=google_user_info["sub"],  # Google user ID
            is_active=True
        )
        await self._repository.save(user)
        return user

    async def authenticate_social_user(self, email: Email, provider: AuthProvider, provider_id: str) -> User:
        """Authenticate user via social login."""
        user = await self._repository.find_by_email(email)

        if not user:
            raise ValueError("User not found")

        # Verify it's the same provider and ID
        if user.auth_provider != provider or user.provider_id != provider_id:
            raise ValueError("Invalid provider credentials")

        if not user.is_active:
            raise ValueError("User is inactive")

        return user


# api/users/auth/routes.py
from api.core.auth import Token, create_access_token  # REUSE!
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@router.get("/auth/google/callback")
async def google_callback(
    request: Request,
    user_service: UserService = Depends(get_user_service)
):
    """Handle Google OAuth2 callback."""
    # Exchange code for token and get user info
    token = await oauth.google.authorize_access_token(request)
    google_user = token.get('userinfo')

    # Find or create user
    try:
        user = await user_service.authenticate_social_user(
            Email(google_user['email']),
            AuthProvider.GOOGLE,
            google_user['sub']
        )
    except ValueError:
        # First time login - create account
        user = await user_service.create_user_from_google(google_user)

    # Use the SAME core utility to create JWT
    access_token = create_access_token(
        data={
            "sub": str(user.id.value),
            "email": user.email.value,
            "auth_provider": user.auth_provider.value,
            "type": "user"
        }
    )

    return Token(access_token=access_token, token_type="bearer")
```

**Key Point**: Social login users don't have passwords, but still use core.auth for JWT tokens.

---

## Summary: Why Core Has Auth

| Module | Uses core.auth For | Entity Type |
|--------|-------------------|-------------|
| **Users** | Hash user passwords, verify user login, issue user JWT | `User` |
| **Admin** | Hash admin passwords, verify admin login, issue admin JWT | `Admin` |
| **Services** | Hash API keys, verify service auth, check scopes | `ServiceAccount` |
| **Social Login** | Issue JWT after OAuth2 (no password hashing) | `User` with provider |

### Core Principle

```
┌─────────────────────────────────────────┐
│         api/core/auth                   │
│  (Infrastructure - No Domain Knowledge) │
│                                         │
│  • hash_password(str) -> str            │
│  • verify_password(str, str) -> bool    │
│  • create_access_token(dict) -> str     │
│  • decode_access_token(str) -> dict     │
└──────────────┬──────────────────────────┘
               │ Used by ↓
       ┌───────┴────────┬──────────┬──────────┐
       │                │          │          │
   ┌───▼───┐      ┌────▼────┐  ┌──▼───┐   ┌──▼──────┐
   │ Users │      │  Admin  │  │ APIs │   │ Social  │
   │       │      │         │  │      │   │ Login   │
   │ User  │      │  Admin  │  │ Svc  │   │ User    │
   │entity │      │ entity  │  │ Acct │   │ OAuth2  │
   └───────┘      └─────────┘  └──────┘   └─────────┘
  (Bounded       (Bounded      (Bounded   (Bounded
   Context)       Context)      Context)   Context)
```

**Key Insight**: core.auth provides the **tools** (password hashing, JWT), but each bounded context provides the **business logic** (who can login, what claims to include, what permissions exist).

This is **proper DDD** - infrastructure in core, domain logic in contexts! 🎯
