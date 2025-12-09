# Settings Architecture

## Overview

This API uses a **hexagonal architecture** with **Domain-Driven Design (DDD)** principles. Settings are organized into modular packages following single responsibility principle. Each bounded context (domain module) can define its own settings that are specific to that domain's business rules and infrastructure needs.

## Structure

```
api/
├── core/
│   ├── settings/                # Core settings package (modular)
│   │   ├── __init__.py         # Package exports
│   │   ├── app.py              # Application settings (APP_*)
│   │   ├── cors.py             # CORS settings (CORS_*)
│   │   ├── security.py         # Security settings (SECURITY_*)
│   │   └── base.py             # Settings container and singleton
│   ├── database/
│   │   └── settings.py         # Database settings (DB_*)
│   └── utility/
│       └── settings.py         # Shared configuration helper
└── users/                       # Example bounded context
    ├── settings.py              # Users module-specific settings
    ├── dependencies.py          # DI configuration using settings
    └── ...
```

## Core Settings (`api.core.settings`)

The core settings module provides **application-wide configuration**:

- **AppSettings**: Application metadata (name, version, environment, debug)
- **DatabaseSettings**: Database connection and pooling
- **CORSSettings**: CORS middleware configuration
- **SecuritySettings**: Security policies and secrets

### Usage

```python
from api.core.settings import settings

# Access core settings
print(settings.app.name)
print(settings.db.url)
print(settings.cors.origins_list)
```

## Module-Specific Settings

Each DDD bounded context defines its own settings for:
- Business rules and policies
- Infrastructure adapter selection
- Module-specific configuration

### Example: Users Module (`api.users.settings`)

```python
from api.users.settings import users_settings

# Access users module settings
repository_backend = users_settings.repository_backend  # "inmemory" or "sqlalchemy"
min_password_length = users_settings.min_password_length
max_page_size = users_settings.max_page_size
```

## Environment Variables

Settings are loaded from environment variables (or `.env` file) using **prefixes**:

### Core Settings Prefixes
- `APP_*` - Application settings
- `DB_*` - Database settings
- `CORS_*` - CORS settings
- `SECURITY_*` - Security settings

### Module Settings Prefixes
- `USERS_*` - Users module settings
- `ORDERS_*` - Orders module settings (future)
- `BILLING_*` - Billing module settings (future)

### Example `.env`

```bash
# Core
APP_NAME=TruAPI
APP_ENVIRONMENT=production
DB_URL=postgresql://user:pass@localhost/db

# Users Module
USERS_REPOSITORY_BACKEND=sqlalchemy
USERS_MIN_PASSWORD_LENGTH=12
USERS_REQUIRE_EMAIL_VERIFICATION=true
```

## Benefits of This Architecture

### 1. **Separation of Concerns**
Each bounded context manages its own configuration without polluting global settings.

### 2. **Hexagonal Architecture**
Infrastructure adapters (repositories, external services) are configured at the application boundary through settings, making them easily swappable.

### 3. **Type Safety**
Pydantic Settings provides:
- Type validation
- Automatic parsing (strings → ints, bools, etc.)
- Clear error messages for misconfiguration

### 4. **Testability**
Each module can be tested with its own settings configuration without affecting other modules.

### 5. **Scalability**
As new bounded contexts are added, they can define their own settings without modifying core configuration.

## Adding a New Module

When creating a new DDD bounded context:

1. **Create module settings** (`api/your_module/settings.py`):

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class YourModuleSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="YOURMODULE_",
        case_sensitive=False,
    )

    some_setting: str = Field(
        default="default_value",
        description="Description of setting"
    )

your_module_settings = YourModuleSettings()
```

2. **Add environment variables** to `.env`:

```bash
YOURMODULE_SOME_SETTING=custom_value
```

3. **Use in dependencies** (`api/your_module/dependencies.py`):

```python
from .settings import your_module_settings

def configure_infrastructure():
    if your_module_settings.some_setting == "custom":
        # Configure accordingly
        pass
```

## Migration from Old Settings

If you're migrating from the old `api.shared.settings` or `api.config.settings`:

1. **Import from new location**:
   ```python
   # Old (deprecated)
   from api.shared.settings import settings

   # New
   from api.core.settings import settings
   ```

2. **Update environment variables** to use prefixes:
   ```bash
   # Old
   DATABASE_URL=...

   # New
   DB_URL=...
   ```

3. **Module-specific settings** go in their own files:
   ```python
   # Old (all in one file)
   from api.shared.settings import settings
   backend = settings.users_backend

   # New (module-specific)
   from api.users.settings import users_settings
   backend = users_settings.repository_backend
   ```

## Best Practices

1. **Use type hints**: Leverage Pydantic's validation
2. **Provide defaults**: Make development easy with sensible defaults
3. **Document settings**: Add descriptions to all fields
4. **Validate early**: Settings are validated at startup, catching errors immediately
5. **Keep secrets secret**: Use environment variables for sensitive data
6. **Module boundaries**: Keep module settings in their respective modules

## Testing

Override settings in tests:

```python
from api.users.settings import UsersModuleSettings

def test_with_custom_settings():
    test_settings = UsersModuleSettings(
        repository_backend="inmemory",
        max_page_size=10
    )
    # Use test_settings in your test
```
