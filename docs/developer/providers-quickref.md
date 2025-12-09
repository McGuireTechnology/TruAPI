# Provider Quick Reference

Quick reference for database and file providers in TruLedgr API.

## Database Providers

### SQLAlchemy (Production)

```python
from api.shared.database import SQLAlchemyProvider

# PostgreSQL
db = SQLAlchemyProvider("postgresql://user:pass@localhost/db")

# MySQL
db = SQLAlchemyProvider("mysql://user:pass@localhost/db")

# SQLite
db = SQLAlchemyProvider("sqlite:///./data.db")

# Connect and use
await db.connect()
async with db.session() as session:
    sa_session = session.get_native_session()
    result = sa_session.query(User).all()
    await session.commit()
await db.disconnect()
```

### InMemory (Testing)

```python
from api.shared.database import InMemoryProvider

db = InMemoryProvider()
await db.connect()

async with db.session() as session:
    storage = session.get_native_session()
    storage["users"] = [{"id": "1", "name": "Alice"}]
    await session.commit()

users = db.get_collection("users")
await db.disconnect()
```

## File Providers

### Disk (Local Development)

```python
from api.shared.files import DiskContentProvider

files = DiskContentProvider(
    base_path="/var/data",
    max_size_bytes=1024 * 1024 * 1024,  # 1GB
)

# Save
await files.save("docs/file.pdf", pdf_bytes, "application/pdf")

# Read
content = await files.read("docs/file.pdf")

# Stream
async for chunk in files.read_stream("docs/large.mp4"):
    process(chunk)

# List
all_docs = await files.list_files(prefix="docs/")

# Delete
await files.delete("docs/file.pdf")
```

### S3 (Production)

```python
from api.shared.files import S3ContentProvider

files = S3ContentProvider(
    bucket="my-bucket",
    aws_access_key_id="AKIA...",
    aws_secret_access_key="secret...",
    region_name="us-east-1",
    prefix="uploads",  # optional
)

# Usage identical to Disk provider
await files.save("file.pdf", content)
url = await files.get_url("file.pdf", expires_in=3600)
```

### InMemory (Testing)

```python
from api.shared.files import InMemoryContentProvider

files = InMemoryContentProvider(max_size_bytes=10 * 1024 * 1024)

await files.save("test.txt", b"Hello")
content = await files.read("test.txt")
```

## FastAPI Dependency Injection

```python
from fastapi import Depends, FastAPI
from api.shared.database import SQLAlchemyProvider, DatabaseSession
from api.shared.files import DiskContentProvider

app = FastAPI()

# Create providers at startup
db_provider = SQLAlchemyProvider("postgresql://...")
file_provider = DiskContentProvider("/var/data")

@app.on_event("startup")
async def startup():
    await db_provider.connect()

@app.on_event("shutdown")
async def shutdown():
    await db_provider.disconnect()

# Dependencies
async def get_db() -> DatabaseSession:
    async with db_provider.session() as session:
        yield session

def get_files() -> DiskContentProvider:
    return file_provider

# Use in routes
@app.post("/users")
async def create_user(
    db: DatabaseSession = Depends(get_db),
    files: DiskContentProvider = Depends(get_files),
):
    # Use providers
    pass
```

## Common Patterns

### Transaction Management

```python
# Good - auto rollback on error
async with db.session() as session:
    # Do work
    await session.commit()

# Manual control
async with db.session() as session:
    try:
        # Do work
        await session.commit()
    except Exception:
        await session.rollback()
        raise
```

### File Streaming (Large Files)

```python
# Good - memory efficient
async for chunk in files.read_stream("large.mp4", chunk_size=8192):
    await response.write(chunk)

# Bad - loads entire file
content = await files.read("large.mp4")
await response.write(content)
```

### Error Handling

```python
from api.shared.files import FileNotFoundError, StorageQuotaError

try:
    content = await files.read("missing.txt")
except FileNotFoundError:
    raise HTTPException(404, "File not found")
except StorageQuotaError:
    raise HTTPException(507, "Storage full")
```

## Testing

```python
import pytest
from api.shared.database import InMemoryProvider
from api.shared.files import InMemoryContentProvider

@pytest.fixture
async def db():
    provider = InMemoryProvider()
    await provider.connect()
    yield provider
    await provider.disconnect()

@pytest.fixture
def files():
    return InMemoryContentProvider()

async def test_user(db, files):
    # Use in-memory providers
    async with db.session() as session:
        storage = session.get_native_session()
        storage["users"] = [{"id": "1"}]
        await session.commit()
    
    await files.save("avatar.jpg", b"data")
```

## Configuration

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    db_provider: str = "sqlalchemy"
    db_url: str = "postgresql://..."
    
    # Files
    file_provider: str = "disk"
    file_base_path: str = "/var/data"
    
    # S3 (if file_provider=s3)
    s3_bucket: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""

# Factory functions
def create_db_provider(settings: Settings):
    if settings.db_provider == "sqlalchemy":
        return SQLAlchemyProvider(url=settings.db_url)
    elif settings.db_provider == "inmemory":
        return InMemoryProvider()

def create_file_provider(settings: Settings):
    if settings.file_provider == "disk":
        return DiskContentProvider(base_path=settings.file_base_path)
    elif settings.file_provider == "s3":
        return S3ContentProvider(
            bucket=settings.s3_bucket,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
        )
    elif settings.file_provider == "inmemory":
        return InMemoryContentProvider()
```

## See Also

- [Full Provider Documentation](providers.md)
- [Architecture Guide](architecture.md)
- [Settings Configuration](settings-architecture.md)
