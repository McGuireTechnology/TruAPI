import pytest

from truapi.adapters.repositories.user.in_memory import InMemoryUserRepository
from truapi.use_cases.exceptions import UserNotFoundError
from truapi.use_cases.user.create import CreateInput, create
from truapi.use_cases.user.delete import delete


@pytest.mark.asyncio
async def test_delete_removes_user():
    repo = InMemoryUserRepository()
    user = create(CreateInput(username="alice", email="alice@example.com", display_name="Alice"))
    await repo.save(user)
    await delete(user.id, repo)
    assert await repo.get(id=user.id) is None
    assert await repo.exists(id=user.id) is False


@pytest.mark.asyncio
async def test_delete_raises_when_missing():
    repo = InMemoryUserRepository()
    from truapi.domain.value_objects.id import ID
    missing = ID.new()
    with pytest.raises(UserNotFoundError):
        await delete(missing, repo)
