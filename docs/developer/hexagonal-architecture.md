# Hexagonal Architecture Implementation

This document explains how the McGuire Technology API implements hexagonal architecture (also known as ports and adapters) with vertical slice/DDD principles.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Entry Point                   │
│                      (api/main.py)                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Vertical Slices (Modules)                   │
│                                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │           Users Bounded Context                     │     │
│  │                                                      │     │
│  │  ┌─────────────────────────────────────────────┐   │     │
│  │  │          Domain Layer (Core)                 │   │     │
│  │  │  • User, UserId, Email (entities)            │   │     │
│  │  │  • UserRepository (port/interface)           │   │     │
│  │  │  • UserService (business logic)              │   │     │
│  │  └─────────────────────────────────────────────┘   │     │
│  │                       │                              │     │
│  │  ┌─────────────────────────────────────────────┐   │     │
│  │  │   Application Layer (Orchestration)          │   │     │
│  │  │  • dependencies.py (DI configuration)        │   │     │
│  │  │  • routes.py (HTTP handlers)                 │   │     │
│  │  └─────────────────────────────────────────────┘   │     │
│  │                       │                              │     │
│  │  ┌─────────────────────────────────────────────┐   │     │
│  │  │    Adapter Layer (Infrastructure)            │   │     │
│  │  │  • SQLAlchemyUserRepository (adapter)        │   │     │
│  │  │  • InMemoryUserRepository (adapter)          │   │     │
│  │  │  • Uses core.database.DatabaseProvider       │   │     │
│  │  └─────────────────────────────────────────────┘   │     │
│  └────────────────────────────────────────────────────┘     │
└───────────────────────┬───────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Core Infrastructure Layer                        │
│                  (api/core/)                                  │
│                                                               │
│  • DatabaseProvider (generic interface)                       │
│  • SQLAlchemyProvider (concrete implementation)               │
│  • InMemoryProvider (concrete implementation)                 │
│  • Settings (configuration)                                   │
└─────────────────────────────────────────────────────────────┘
```

## Key Principles

### 1. Dependency Inversion

**Dependencies flow inward** toward the domain:
```
Infrastructure → Application → Domain
```

The domain layer **never** imports from infrastructure. Instead:
- Domain defines interfaces (ports): `UserRepository`
- Infrastructure implements adapters: `SQLAlchemyUserRepository`
- Application layer wires them together: `dependencies.py`

### 2. Vertical Slices

Each bounded context (Users, Orders, Payments, etc.) is a **self-contained vertical slice**:

```
api/users/
  ├── models.py          # Domain entities
  ├── database/
  │   ├── generic.py     # Port (UserRepository interface)
  │   ├── sqlalchemy.py  # Adapter (SQLAlchemy implementation)
  │   └── inmemory.py    # Adapter (in-memory implementation)
  ├── services.py        # Business logic
  ├── routes.py          # HTTP handlers
  ├── dependencies.py    # DI wiring
  └── settings.py        # Module-specific configuration
```

### 3. Shared Infrastructure

Core infrastructure is **shared across all slices**:

```
api/core/
  ├── database/
  │   ├── generic.py         # DatabaseProvider interface
  │   ├── sqlalchemy.py      # SQLAlchemy provider
  │   ├── inmemory.py        # In-memory provider
  │   └── settings.py        # Database configuration
  └── settings.py            # Application configuration
```

## Layer Responsibilities

### Domain Layer (api/users/models.py, api/users/database/generic.py)

**What it contains:**
- Pure business entities (`User`, `UserId`, `Email`)
- Repository interfaces (ports)
- Domain events
- Business rules

**What it does NOT contain:**
- Database code
- HTTP code
- External service calls
- Framework dependencies

**Example:**
```python
# Domain entity
class User:
    id: UserId
    email: Email
    first_name: str
    # Pure business logic, no infrastructure

# Domain port (interface)
class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> None: ...
```

### Application Layer (api/users/routes.py, dependencies.py)

**What it contains:**
- HTTP route handlers
- Dependency injection configuration
- Request/response DTOs (schemas)
- Orchestration logic

**What it does:**
- Receives requests from outside
- Validates input
- Calls domain services
- Returns responses

**Example:**
```python
@router.post("/users", response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    service: UserService = Depends(get_user_service)
):
    user = await service.create_user(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name
    )
    return UserResponse.from_domain(user)
```

### Adapter Layer (api/users/database/sqlalchemy.py, inmemory.py)

**What it contains:**
- Concrete implementations of domain ports
- ORM models (UserORM)
- Database queries
- External service clients

**What it does:**
- Implements repository interfaces
- Translates between domain and infrastructure
- Uses core infrastructure (DatabaseProvider)

**Example:**
```python
class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, provider: DatabaseProvider):
        self._provider = provider  # Uses core infrastructure

    async def save(self, user: User) -> None:
        async with self._provider.session() as session:
            # Database operations
            ...
```

### Infrastructure Layer (api/core/database/)

**What it contains:**
- Database connection management
- Transaction handling
- Session/context management
- Generic infrastructure utilities

**What it does:**
- Provides DatabaseProvider abstraction
- Manages connections, pools, transactions
- No knowledge of domain entities

**Example:**
```python
class DatabaseProvider(ABC):
    @abstractmethod
    async def session(self) -> AsyncContextManager[DatabaseSession]: ...
```

## Configuration Strategy

### Centralized Infrastructure Decisions

Repository backend is configured **once** in core settings:

```python
# api/core/database/settings.py
class DatabaseSettings(BaseSettings):
    repository_backend: str = Field(default="inmemory")
```

**Why centralized?**
- Ensures consistency across all modules
- Prevents configuration conflicts
- Single source of truth
- Easier testing and deployment

### Module-Specific Business Rules

Domain-specific configuration lives **in the module**:

```python
# api/users/settings.py
class UsersModuleSettings(BaseSettings):
    min_password_length: int = 8
    max_login_attempts: int = 5
    require_email_verification: bool = True
```

## Dependency Injection Flow

### 1. Core Infrastructure Setup

```python
# Application startup
provider = SQLAlchemyProvider(
    url=settings.db.url,
    echo=settings.db.echo,
    pool_size=settings.db.pool_size
)
await provider.connect()
```

### 2. Repository Creation

```python
# Dependency injection (api/users/dependencies.py)
async def get_user_repository() -> UserRepository:
    provider = get_database_provider()  # Core infrastructure
    return SQLAlchemyUserRepository(provider)  # Domain adapter
```

### 3. Service Injection

```python
# FastAPI dependency injection
async def get_user_service(
    repo: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(repo)
```

### 4. Route Handler

```python
# HTTP endpoint
@router.post("/users")
async def create_user(
    service: UserService = Depends(get_user_service)
):
    return await service.create_user(...)
```

## Benefits of This Architecture

### 1. Testability

**Easy to test domain logic in isolation:**
```python
# Test with in-memory repository
repo = InMemoryUserRepository()
service = UserService(repo)
user = await service.create_user(...)
assert user.email == "test@example.com"
```

### 2. Flexibility

**Swap implementations without changing domain:**
```python
# Development: In-memory
repo = InMemoryUserRepository()

# Production: PostgreSQL
provider = SQLAlchemyProvider("postgresql://...")
repo = SQLAlchemyUserRepository(provider)

# Testing: Mock
repo = Mock(spec=UserRepository)
```

### 3. Independence

**Domain logic doesn't depend on:**
- Database technology
- Web framework
- External services
- Infrastructure details

### 4. Maintainability

**Clear boundaries:**
- Domain changes don't break infrastructure
- Infrastructure changes don't break domain
- Easy to locate and modify code

### 5. Scalability

**Add new features as vertical slices:**
```
api/orders/     # New bounded context
api/payments/   # Another bounded context
api/inventory/  # Yet another
```

Each slice is independent but shares core infrastructure.

## Common Patterns

### Pattern 1: Adding a New Repository Method

**Step 1:** Add to domain interface
```python
# api/users/database/generic.py
class UserRepository(ABC):
    @abstractmethod
    async def find_by_status(self, status: str) -> List[User]: ...
```

**Step 2:** Implement in adapters
```python
# api/users/database/sqlalchemy.py
async def find_by_status(self, status: str) -> List[User]:
    async with self._provider.session() as session:
        # Implementation
        ...
```

### Pattern 2: Adding a New Bounded Context

```bash
api/orders/
  ├── models.py           # Order, OrderId, OrderItem
  ├── database/
  │   ├── generic.py      # OrderRepository interface
  │   ├── sqlalchemy.py   # OrderRepository adapter
  │   └── inmemory.py     # OrderRepository adapter
  ├── services.py         # OrderService
  ├── routes.py           # Order endpoints
  ├── dependencies.py     # DI configuration
  └── settings.py         # Order-specific rules
```

Uses **same core infrastructure** (DatabaseProvider).

### Pattern 3: Changing Database Backend

**Configuration change only:**
```bash
# .env
DB_REPOSITORY_BACKEND=sqlalchemy  # or inmemory
DB_URL=postgresql://localhost/db
```

**No code changes needed** - dependency injection handles it.

## Anti-Patterns to Avoid

### ❌ Domain importing infrastructure

```python
# WRONG: Domain depends on SQLAlchemy
from sqlalchemy.orm import Session

class User:
    def save(self, session: Session): ...
```

### ❌ Multiple configuration sources

```python
# WRONG: Each module configures its own backend
class UsersSettings:
    repository_backend: str = "sqlalchemy"

class OrdersSettings:
    repository_backend: str = "inmemory"  # Inconsistent!
```

### ❌ Bypassing the repository

```python
# WRONG: Service directly uses database
class UserService:
    def __init__(self, session: Session):
        self._session = session

    async def create_user(self):
        self._session.add(UserORM(...))  # Bypasses domain
```

### ❌ Mixing concerns

```python
# WRONG: HTTP logic in domain
class User:
    def to_json_response(self): ...  # HTTP concern in domain
```

## Testing Strategy

### Unit Tests (Domain Layer)

```python
def test_user_creation():
    user = User(
        id=UserId(uuid4()),
        email=Email("test@example.com"),
        first_name="John",
        last_name="Doe"
    )
    assert user.full_name == "John Doe"
```

### Integration Tests (Application Layer)

```python
@pytest.mark.asyncio
async def test_create_user_service():
    repo = InMemoryUserRepository()
    service = UserService(repo)

    user = await service.create_user(
        email="test@example.com",
        first_name="John",
        last_name="Doe"
    )

    assert await repo.exists_by_email(Email("test@example.com"))
```

### End-to-End Tests (Full Stack)

```python
async def test_create_user_endpoint(client: AsyncClient):
    response = await client.post("/users", json={
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe"
    })
    assert response.status_code == 200
```

## Migration Guide

### From Old to New Architecture

**Before (Mixed concerns):**
```python
class UserService:
    def __init__(self, session: Session):
        self._session = session  # Direct database dependency
```

**After (Hexagonal):**
```python
class UserService:
    def __init__(self, repo: UserRepository):
        self._repo = repo  # Depends on interface
```

**Benefits:**
- Service doesn't know about SQLAlchemy
- Easy to test with mock repository
- Can swap database without changing service

## Resources

- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [DDD and Bounded Contexts](https://martinfowler.com/bliki/BoundedContext.html)
- [Vertical Slice Architecture](https://jimmybogard.com/vertical-slice-architecture/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
