#! /usr/bin/env python
# ruff: noqa: E402
"""Repository tests exercising both inmemory and sqlalchemy backends.

Tests are parameterized to run against all configured repository
implementations, ensuring consistent behavior across persistence adapters.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator

import pytest

# Ensure 'api' directory is on path
API_DIR = Path(__file__).resolve().parents[1]
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from truapi.users.db import Base, InMemoryUserRepository, SQLAlchemyUserRepository, UserRepository  # noqa: E402
from truapi.users.models import Email, User, UserId  # noqa: E402


@pytest.fixture
async def inmemory_repo() -> AsyncIterator[UserRepository]:
    """Provide a fresh in-memory repository for each test."""
    repo = InMemoryUserRepository()
    yield repo
    # No cleanup needed; repo is discarded after test


@pytest.fixture
async def sqlalchemy_repo() -> AsyncIterator[UserRepository]:
    """Provide a SQLAlchemy repository with an in-memory SQLite database."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()

    repo = SQLAlchemyUserRepository(session)
    yield repo

    session.close()
    engine.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "repo_fixture", ["inmemory_repo", "sqlalchemy_repo"]
)
async def test_save_and_find_by_id(repo_fixture: str, request):
    """Test saving a user and retrieving by ID."""
    repo: UserRepository = request.getfixturevalue(repo_fixture)

    user = User(
        id=UserId.new(),
        email=Email("alice@example.com"),
        first_name="Alice",
        last_name="Smith",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    await repo.save(user)
    found = await repo.find_by_id(user.id)

    assert found is not None
    assert found.id.value == user.id.value
    assert found.email.value == "alice@example.com"
    assert found.first_name == "Alice"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "repo_fixture", ["inmemory_repo", "sqlalchemy_repo"]
)
async def test_find_by_email(repo_fixture: str, request):
    """Test finding a user by email."""
    repo: UserRepository = request.getfixturevalue(repo_fixture)

    user = User(
        id=UserId.new(),
        email=Email("bob@example.com"),
        first_name="Bob",
        last_name="Builder",
    )

    await repo.save(user)
    found = await repo.find_by_email(Email("bob@example.com"))

    assert found is not None
    assert found.first_name == "Bob"
    assert found.email.value == "bob@example.com"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "repo_fixture", ["inmemory_repo", "sqlalchemy_repo"]
)
async def test_exists_by_email(repo_fixture: str, request):
    """Test checking email existence."""
    repo: UserRepository = request.getfixturevalue(repo_fixture)

    user = User(
        id=UserId.new(),
        email=Email("exists@example.com"),
        first_name="Exists",
        last_name="User",
    )

    assert not await repo.exists_by_email(Email("exists@example.com"))
    await repo.save(user)
    assert await repo.exists_by_email(Email("exists@example.com"))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "repo_fixture", ["inmemory_repo", "sqlalchemy_repo"]
)
async def test_find_all_with_pagination(repo_fixture: str, request):
    """Test listing users with skip/limit pagination."""
    repo: UserRepository = request.getfixturevalue(repo_fixture)

    for i in range(5):
        user = User(
            id=UserId.new(),
            email=Email(f"user{i}@example.com"),
            first_name=f"User{i}",
            last_name="Test",
        )
        await repo.save(user)

    all_users = await repo.find_all(skip=0, limit=10)
    assert len(all_users) == 5

    page1 = await repo.find_all(skip=0, limit=2)
    assert len(page1) == 2

    page2 = await repo.find_all(skip=2, limit=2)
    assert len(page2) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "repo_fixture", ["inmemory_repo", "sqlalchemy_repo"]
)
async def test_delete(repo_fixture: str, request):
    """Test deleting a user."""
    repo: UserRepository = request.getfixturevalue(repo_fixture)

    user = User(
        id=UserId.new(),
        email=Email("delete@example.com"),
        first_name="Delete",
        last_name="Me",
    )

    await repo.save(user)
    assert await repo.find_by_id(user.id) is not None

    await repo.delete(user.id)
    assert await repo.find_by_id(user.id) is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "repo_fixture", ["inmemory_repo", "sqlalchemy_repo"]
)
async def test_count(repo_fixture: str, request):
    """Test counting total users."""
    repo: UserRepository = request.getfixturevalue(repo_fixture)

    assert await repo.count() == 0

    for i in range(3):
        user = User(
            id=UserId.new(),
            email=Email(f"count{i}@example.com"),
            first_name=f"Count{i}",
            last_name="Test",
        )
        await repo.save(user)

    assert await repo.count() == 3


@pytest.mark.asyncio
async def test_inmemory_defensive_copy(inmemory_repo: UserRepository):
    """Test that InMemoryUserRepository returns defensive copies."""
    user = User(
        id=UserId.new(),
        email=Email("copy@example.com"),
        first_name="Original",
        last_name="Name",
    )

    await inmemory_repo.save(user)
    found = await inmemory_repo.find_by_id(user.id)

    assert found is not None
    # Mutate the returned object
    found.first_name = "Modified"

    # Retrieve again and verify internal storage was not mutated
    found_again = await inmemory_repo.find_by_id(user.id)
    assert found_again is not None
    assert found_again.first_name == "Original"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "repo_fixture", ["inmemory_repo", "sqlalchemy_repo"]
)
async def test_update_user(repo_fixture: str, request):
    """Test updating an existing user via save."""
    repo: UserRepository = request.getfixturevalue(repo_fixture)

    user = User(
        id=UserId.new(),
        email=Email("update@example.com"),
        first_name="Initial",
        last_name="User",
    )

    await repo.save(user)

    # Update the user
    user.update_profile(first_name="Updated", last_name="User")
    await repo.save(user)

    found = await repo.find_by_id(user.id)
    assert found is not None
    assert found.first_name == "Updated"
