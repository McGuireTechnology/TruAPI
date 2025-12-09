# Cross-Context References

## Architecture Decision: Full Bounded Context Isolation

We use **Option 1: Full Bounded Context Isolation** for handling cross-module references. This means:

- ✅ Each bounded context (Users, Orders, Payments, etc.) is fully independent
- ✅ Contexts store only ULID strings as foreign keys
- ✅ Contexts use Published Language APIs to get data when needed
- ❌ No shared kernel for identities (no `api/shared/` with `UserId`)
- ❌ No direct imports between bounded contexts

## How to Reference Users from Other Contexts

### 1. Store ULID in Your Database

```python
# In api/orders/models.py
from dataclasses import dataclass

@dataclass
class Order:
    id: str  # ULID as string (26 chars)
    user_id: str  # Just store the ULID string - no UserId wrapper needed
    items: list[OrderItem]
    total: Decimal
```

### 2. Use the Users Public API

```python
# In api/orders/services.py
from api.users import UserReference, UsersPublicApi

class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        users_api: UsersPublicApi  # Inject the public API
    ):
        self._order_repo = order_repo
        self._users_api = users_api

    async def create_order(self, user_id: str, items: list) -> Order:  # ULID as string
        # Validate user exists and is active
        if not await self._users_api.is_user_active(user_id):
            raise ValueError("User is not active")

        # Get user info if needed for business logic
        user_ref = await self._users_api.get_user_reference(user_id)
        if not user_ref:
            raise ValueError("User not found")

        # Create order with just the UUID
        # Create order with just the ULID string
        from ulid import ULID
        order = Order(
            id=str(ULID()),
            user_id=user_id,  # Store ULID string directly
            total=calculate_total(items)
        )

        return await self._order_repo.save(order)
```

### 3. Wire Up the Dependency

```python
# In api/orders/dependencies.py
from fastapi import Depends
from api.users import get_users_public_api, UsersPublicApi
from .services import OrderService
from .repositories import OrderRepository

async def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    users_api: UsersPublicApi = Depends(get_users_public_api)
) -> OrderService:
    return OrderService(order_repo, users_api)
```

### 4. Use in Routes

```python
# In api/orders/routes.py
from fastapi import APIRouter, Depends
from api.users import get_current_user, User
from .services import OrderService
from .dependencies import get_order_service

router = APIRouter(prefix="/orders", tags=["orders"])
@router.post("/")
async def create_order(
    items: list[OrderItemCreate],
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    # current_user.id.value gives you the ULID, convert to string
    order = await order_service.create_order(
        user_id=str(current_user.id.value),_order(
        user_id=current_user.id.value,
        items=items
    )
    return order
```

## Users Public API Reference
### UserReference

Minimal user data exposed to other contexts:

```python
@dataclass(frozen=True)
class UserReference:
    id: str  # ULID as string (26 chars)
    email: str
    display_name: str
    is_active: bool
```

### UsersPublicApi Methods

```python
class UsersPublicApi:
    async def get_user_reference(self, user_id: str) -> Optional[UserReference]
        """Get minimal user info. Returns None if user not found."""

    async def is_user_active(self, user_id: str) -> bool
        """Check if user exists and is active."""

    async def validate_user_exists(self, user_id: str) -> bool
    async def validate_user_exists(self, user_id: UUID) -> bool
        """Check if user exists (regardless of active status)."""
```

## Why This Approach?

### ✅ Benefits

1. **True Bounded Context Isolation**: Each context owns its domain completely
2. **Independent Evolution**: Users can change internals without breaking other contexts
3. **Clear Boundaries**: Published Language API makes the contract explicit
4. **Database Flexibility**: Each context can use different databases if needed
5. **Testability**: Mock the public API easily in tests

### ⚠️ Tradeoffs

1. **Additional Queries**: Need to call public API to get user data (not just stored locally)
2. **Eventual Consistency**: If caching user data, it might be stale
3. **More Boilerplate**: Dependency injection for public API

### When to Use Each Pattern

| Pattern | Use When | Example |
|---------|----------|---------|
| **Full Isolation** (current) | Mature DDD, independent deployment, different teams | Microservices, large teams |
| **Shared Kernel** | Frequently shared concepts, same deployment unit | Small/medium monoliths |
| **Published Language** (current) | Need cross-context data access | All contexts using Users |

## Anti-Patterns to Avoid

❌ **DON'T import domain models directly**:
```python
from api.users.models import User  # ❌ Creates tight coupling
```

❌ **DON'T import services directly**:
```python
from api.users.services import UserService  # ❌ Breaks bounded context
```

❌ **DON'T create a shared UserId value object**:
```python
from api.shared import UserId  # ❌ We removed this - use ULID strings directly
```

✅ **DO use the public API**:
```python
from api.users import UserReference, get_users_public_api  # ✅ Clean contract
```

✅ **DO store just ULID strings**:
```python
user_id: str  # ✅ ULID as string (26 chars) - Simple, no coupling
```

## Database Schema Example

```sql
-- Users context owns this table
CREATE TABLE users (
    id VARCHAR(26) PRIMARY KEY,  -- ULID as string (26 chars)
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    hashed_password VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE
);

-- Orders context owns this table
CREATE TABLE orders (
    id VARCHAR(26) PRIMARY KEY,  -- ULID as string
    user_id VARCHAR(26) NOT NULL,  -- Just a ULID string, no FK constraint needed for bounded contexts
    total DECIMAL(10, 2),
    created_at TIMESTAMP
);

-- If you want referential integrity, you CAN add FK
-- but it couples the databases (fine for monolith)
ALTER TABLE orders
    ADD CONSTRAINT fk_order_user
    FOREIGN KEY (user_id) REFERENCES users(id);
```

## Migration from Shared Kernel

If you previously had `api/shared/` with `UserId`:

1. ✅ Remove `api/shared/` directory
2. ✅ Keep `api/users/public_api.py` (the Published Language)
3. ✅ Update other modules to store `user_id: str` (ULID strings) instead of `user_id: UserId`
4. ✅ Update other modules to import from `api.users` public API only
5. ✅ Remove any `from api.shared import UserId` imports

## Why ULID?

We use **ULID** (Universally Unique Lexicographically Sortable Identifier) instead of UUID:

- ✅ **Sortable**: ULIDs are time-ordered (first 48 bits = timestamp)
- ✅ **Compact**: 26 characters vs 36 for UUID (when represented as string)
- ✅ **URL-safe**: No special characters, perfect for REST APIs
- ✅ **Human-readable**: Base32 encoding is easier to read than hex
- ✅ **Database-friendly**: Better index performance than random UUIDs

Example ULID: `01ARZ3NDEKTSV4RRFFQ69G5FAV` (26 chars)
vs UUID: `0189e0f0-2b3a-7f3e-9c4d-5e6f7a8b9c0d` (36 chars)

The public API provides everything needed for cross-context interaction!
