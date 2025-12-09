# Database and File Providers

This document describes the database and file provider system for the TruLedgr API.

## Overview

The API uses a **provider pattern** to abstract database and file storage operations, allowing you to swap implementations without changing application code. This follows hexagonal/ports-and-adapters architecture principles.

## Provider Types

### Database Providers (`api.shared.database`)

Handle data persistence operations (CRUD, transactions, queries).

**Available Implementations:**
- **SQLAlchemy**: Relational databases (PostgreSQL, MySQL, SQLite, Oracle, MSSQL)
- **InMemory**: In-memory storage for testing

### File/Content Providers (`api.shared.files`)

Handle file/object storage operations (save, read, delete, list).

**Available Implementations:**
- **Disk**: Local filesystem storage
- **S3**: Amazon S3 or S3-compatible services (MinIO, DigitalOcean Spaces, Wasabi)
- **InMemory**: In-memory storage for testing

## Database Provider Usage

### SQLAlchemy Provider

```python
from api.shared.database import SQLAlchemyProvider
from sqlalchemy.orm import DeclarativeBase

# Define your models
class Base(DeclarativeBase):
    pass

# Create provider
db_provider = SQLAlchemyProvider(
    url="postgresql://user:pass@localhost/dbname",
    echo=True,  # Log SQL statements
    pool_size=5,
    max_overflow=10,
    base=Base,
)

# Connect
await db_provider.connect()

# Use sessions
async with db_provider.session() as session:
    # Get native SQLAlchemy session
    sa_session = session.get_native_session()
    
    # Perform operations
    result = sa_session.query(User).all()
    
    # Commit or rollback
    await session.commit()
    # await session.rollback()

# Health check
health = await db_provider.health_check()
print(health)  # {'status': 'healthy', 'connected': True, ...}

# Create tables (development only!)
await db_provider.create_tables()

# Disconnect
await db_provider.disconnect()
```

### InMemory Provider

```python
from api.shared.database import InMemoryProvider

# Create provider
db_provider = InMemoryProvider()

# Connect
await db_provider.connect()

# Use sessions
async with db_provider.session() as session:
    storage = session.get_native_session()
    
    # Direct access to collections (dict of lists)
    storage["users"] = [
        {"id": "1", "email": "user@example.com"},
    ]
    
    await session.commit()

# Helper methods
users = db_provider.get_collection("users")
db_provider.set_collection("users", [...])
```

### Database Provider Interface

All database providers implement:

```python
# Connection management
await provider.connect()
await provider.disconnect()
is_connected = await provider.is_connected()

# Session/transaction management
async with provider.session() as session:
    await session.commit()
    await session.rollback()
    await session.close()
    native_session = session.get_native_session()

# Utilities
health = await provider.health_check()
await provider.create_tables()  # Development only
await provider.drop_tables()    # Dangerous!
```

## File Provider Usage

### Disk Provider

```python
from api.shared.files import DiskContentProvider

# Create provider
file_provider = DiskContentProvider(
    base_path="/var/data/uploads",
    max_size_bytes=1024 * 1024 * 1024,  # 1GB limit
    create_dirs=True,
)

# Save file
metadata = await file_provider.save(
    path="documents/report.pdf",
    content=pdf_bytes,
    content_type="application/pdf",
    metadata={"user_id": "123"},
)

# Read file
content = await file_provider.read("documents/report.pdf")

# Stream file
async for chunk in file_provider.read_stream("documents/report.pdf"):
    process_chunk(chunk)

# Check existence
exists = await file_provider.exists("documents/report.pdf")

# Get metadata
metadata = await file_provider.get_metadata("documents/report.pdf")
print(f"Size: {metadata.size_bytes}, Type: {metadata.content_type}")

# List files
files = await file_provider.list_files(prefix="documents/", recursive=True)

# Copy/Move
await file_provider.copy("doc1.pdf", "doc2.pdf")
await file_provider.move("old.pdf", "new.pdf")

# Delete
await file_provider.delete("documents/report.pdf")

# Get URL
url = await file_provider.get_url("documents/report.pdf")
```

### S3 Provider

```python
from api.shared.files import S3ContentProvider

# Create provider
file_provider = S3ContentProvider(
    bucket="my-bucket",
    aws_access_key_id="AKIA...",
    aws_secret_access_key="secret...",
    region_name="us-east-1",
    endpoint_url=None,  # For S3-compatible services like MinIO
    prefix="uploads",   # Optional key prefix
)

# Usage is identical to Disk provider
metadata = await file_provider.save("document.pdf", pdf_bytes)

# Get pre-signed URL (valid for 1 hour by default)
url = await file_provider.get_url("document.pdf", expires_in=3600)
```

### InMemory Provider

```python
from api.shared.files import InMemoryContentProvider

# Create provider (useful for testing)
file_provider = InMemoryContentProvider(
    max_size_bytes=10 * 1024 * 1024,  # 10MB limit
)

# Usage is identical to other providers
await file_provider.save("test.txt", b"Hello World")
content = await file_provider.read("test.txt")
```

### File Provider Interface

All file providers implement:

```python
# Save/Read operations
metadata = await provider.save(path, content, content_type, metadata)
content = await provider.read(path)
async for chunk in provider.read_stream(path, chunk_size):
    ...

# Metadata operations
exists = await provider.exists(path)
metadata = await provider.get_metadata(path)
files = await provider.list_files(prefix, recursive)

# File operations
metadata = await provider.copy(source_path, dest_path)
metadata = await provider.move(source_path, dest_path)
await provider.delete(path)

# URL generation
url = await provider.get_url(path, expires_in)
```

## Dependency Injection with FastAPI

### Database Provider

```python
from fastapi import Depends
from api.shared.database import SQLAlchemyProvider, DatabaseSession

# Create provider (usually in startup event)
db_provider = SQLAlchemyProvider(url="postgresql://...")

async def get_db_session() -> DatabaseSession:
    """Dependency that provides a database session."""
    async with db_provider.session() as session:
        yield session

# Use in routes
@app.post("/users")
async def create_user(
    user_data: UserCreate,
    session: DatabaseSession = Depends(get_db_session),
):
    sa_session = session.get_native_session()
    # Use session...
    await session.commit()
```

### File Provider

```python
from fastapi import Depends, UploadFile
from api.shared.files import DiskContentProvider

# Create provider
file_provider = DiskContentProvider(base_path="/var/data")

async def get_file_provider() -> DiskContentProvider:
    """Dependency that provides file storage."""
    return file_provider

# Use in routes
@app.post("/upload")
async def upload_file(
    file: UploadFile,
    provider: DiskContentProvider = Depends(get_file_provider),
):
    content = await file.read()
    metadata = await provider.save(
        path=f"uploads/{file.filename}",
        content=content,
        content_type=file.content_type,
    )
    return {"url": await provider.get_url(metadata.path)}
```

## Configuration

### Environment Variables

```bash
# Database
DB_PROVIDER=sqlalchemy  # or: inmemory
DB_URL=postgresql://user:pass@localhost/dbname
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_ECHO=false

# File Storage
FILE_PROVIDER=disk  # or: s3, inmemory
FILE_BASE_PATH=/var/data/uploads
FILE_MAX_SIZE_BYTES=1073741824  # 1GB

# S3 (if FILE_PROVIDER=s3)
S3_BUCKET=my-bucket
S3_ACCESS_KEY_ID=AKIA...
S3_SECRET_ACCESS_KEY=secret...
S3_REGION=us-east-1
S3_ENDPOINT_URL=  # Optional, for S3-compatible services
S3_PREFIX=uploads
```

### Settings Configuration

```python
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    provider: str = "sqlalchemy"
    url: str = "sqlite:///./test.db"
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False

class FileSettings(BaseSettings):
    provider: str = "disk"
    base_path: str = "/var/data"
    max_size_bytes: int = 1024 * 1024 * 1024
    
    # S3 settings
    s3_bucket: str = ""
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_region: str = "us-east-1"
    s3_endpoint_url: str | None = None
    s3_prefix: str = ""

# Provider factory
def create_db_provider(settings: DatabaseSettings):
    if settings.provider == "sqlalchemy":
        return SQLAlchemyProvider(
            url=settings.url,
            echo=settings.echo,
            pool_size=settings.pool_size,
            max_overflow=settings.max_overflow,
        )
    elif settings.provider == "inmemory":
        return InMemoryProvider()
    else:
        raise ValueError(f"Unknown provider: {settings.provider}")

def create_file_provider(settings: FileSettings):
    if settings.provider == "disk":
        return DiskContentProvider(
            base_path=settings.base_path,
            max_size_bytes=settings.max_size_bytes,
        )
    elif settings.provider == "s3":
        return S3ContentProvider(
            bucket=settings.s3_bucket,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            region_name=settings.s3_region,
            endpoint_url=settings.s3_endpoint_url,
            prefix=settings.s3_prefix,
        )
    elif settings.provider == "inmemory":
        return InMemoryContentProvider(
            max_size_bytes=settings.max_size_bytes,
        )
    else:
        raise ValueError(f"Unknown provider: {settings.provider}")
```

## Testing

### Using InMemory Providers

```python
import pytest
from api.shared.database import InMemoryProvider
from api.shared.files import InMemoryContentProvider

@pytest.fixture
async def db_provider():
    provider = InMemoryProvider()
    await provider.connect()
    yield provider
    await provider.disconnect()

@pytest.fixture
def file_provider():
    return InMemoryContentProvider()

@pytest.mark.asyncio
async def test_user_creation(db_provider):
    async with db_provider.session() as session:
        storage = session.get_native_session()
        storage["users"] = [{"id": "1", "email": "test@example.com"}]
        await session.commit()
    
    # Verify
    users = db_provider.get_collection("users")
    assert len(users) == 1
    assert users[0]["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_file_upload(file_provider):
    await file_provider.save("test.txt", b"Hello World")
    content = await file_provider.read("test.txt")
    assert content == b"Hello World"
```

## Migration from Storage Module

The old `api.shared.storage` module has been replaced. Here's how to migrate:

### Old Code (Storage Module)

```python
from api.shared.storage import FileStorageRepository, DiskFileStorageRepository

repo = DiskFileStorageRepository(base_path="/var/data")
await repo.save_file("test.txt", b"content")
```

### New Code (File Provider)

```python
from api.shared.files import DiskContentProvider

provider = DiskContentProvider(base_path="/var/data")
await provider.save("test.txt", b"content")
```

### Key Differences

| Old (Storage) | New (Files) | Notes |
|---------------|-------------|-------|
| `save_file()` | `save()` | Simpler name |
| `read_file()` | `read()` | Simpler name |
| `delete_file()` | `delete()` | Simpler name |
| `file_exists()` | `exists()` | Simpler name |
| N/A | `get_metadata()` | New method |
| N/A | `copy()` | New method |
| N/A | `move()` | New method |
| N/A | `get_url()` | New method |
| N/A | `read_stream()` | New method for large files |

## Best Practices

### 1. Use Providers via Dependency Injection

```python
# Good
async def my_route(provider = Depends(get_db_provider)):
    ...

# Bad - creates new instances
async def my_route():
    provider = SQLAlchemyProvider(...)
```

### 2. Always Use Context Managers for Sessions

```python
# Good
async with provider.session() as session:
    # Do work
    await session.commit()

# Bad - manual cleanup required
session = await provider.create_session()
await session.commit()
await session.close()
```

### 3. Handle Provider-Specific Errors

```python
from api.shared.files import FileNotFoundError, StorageQuotaError

try:
    content = await provider.read("file.txt")
except FileNotFoundError:
    raise HTTPException(404, "File not found")
except StorageQuotaError:
    raise HTTPException(507, "Storage quota exceeded")
```

### 4. Use InMemory Providers for Testing

```python
# Test configuration
if settings.environment == "testing":
    db_provider = InMemoryProvider()
    file_provider = InMemoryContentProvider()
else:
    db_provider = SQLAlchemyProvider(url=settings.db_url)
    file_provider = DiskContentProvider(base_path=settings.file_path)
```

### 5. Stream Large Files

```python
# Good - memory efficient
async for chunk in provider.read_stream("large.mp4"):
    await response.write(chunk)

# Bad - loads entire file into memory
content = await provider.read("large.mp4")
await response.write(content)
```

## Additional Providers

### Future Implementations

The provider pattern makes it easy to add new backends:

- **Database**: MongoDB, DynamoDB, Firestore, Redis
- **Files**: Azure Blob Storage, Google Cloud Storage, SFTP, FTP

### Creating Custom Providers

Implement the abstract interfaces:

```python
from api.shared.database import DatabaseProvider, DatabaseSession
from api.shared.files import ContentProvider

class MyCustomDatabaseProvider(DatabaseProvider):
    async def connect(self): ...
    async def disconnect(self): ...
    # ... implement other methods

class MyCustomFileProvider(ContentProvider):
    async def save(self, path, content, ...): ...
    async def read(self, path): ...
    # ... implement other methods
```

## Troubleshooting

### SQLAlchemy Session Issues

```python
# Issue: "Session is closed"
# Solution: Don't use session outside context manager

# Bad
async with provider.session() as session:
    sa_session = session.get_native_session()
# sa_session is closed here!

# Good
async with provider.session() as session:
    sa_session = session.get_native_session()
    # Use sa_session here
```

### S3 Connection Issues

```python
# Issue: boto3 not installed
# Solution: pip install boto3

# Issue: Invalid credentials
# Solution: Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

# Issue: Bucket not found
# Solution: Create bucket first or check bucket name
```

### File Path Traversal

```python
# Protected automatically by providers
await provider.save("../../../etc/passwd", content)
# Raises: ContentError("Invalid path: ...")
```

## See Also

- [Architecture Documentation](architecture.md)
- [Settings Configuration](settings-architecture.md)
- [Environment Setup](environment-setup.md)
