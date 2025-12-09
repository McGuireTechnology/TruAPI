import pytest

from truapi.adapters.repositories.user.in_memory import InMemoryUserRepository
from truapi.use_cases.exceptions import UserNotFoundError
from truapi.use_cases.user.create import CreateInput, create
from truapi.use_cases.user.get import get


@pytest.mark.asyncio
async def test_get_returns_user_when_exists():
    repo = InMemoryUserRepository()
    user = create(CreateInput(username="alice", email="alice@example.com", display_name="Alice"))
    await repo.save(user)
    loaded = await get(user.id, repo)
    assert loaded.username == "alice"
    assert loaded.email == "alice@example.com"


@pytest.mark.asyncio
async def test_get_raises_when_missing():
    repo = InMemoryUserRepository()
    from truapi.domain.value_objects.id import ID
    missing = ID.new()
    with pytest.raises(UserNotFoundError):
        await get(missing, repo)
