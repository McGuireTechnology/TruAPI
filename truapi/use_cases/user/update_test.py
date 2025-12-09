import pytest

from truapi.adapters.repositories.user.in_memory import InMemoryUserRepository
from truapi.use_cases.exceptions import UserNotFoundError
from truapi.use_cases.user.create import CreateInput, create
from truapi.use_cases.user.update import UpdateInput, update


@pytest.mark.asyncio
async def test_update_persists_changes():
    repo = InMemoryUserRepository()
    user = create(CreateInput(username="alice", email="alice@example.com", display_name="Alice"))
    await repo.save(user)
    updated = await update(user.id, UpdateInput(display_name="Alice A."), repo)
    assert updated.display_name == "Alice A."
    # verify persisted
    reloaded = await repo.get(id=user.id)
    assert reloaded is not None
    assert reloaded.display_name == "Alice A."


@pytest.mark.asyncio
async def test_update_raises_when_missing():
    repo = InMemoryUserRepository()
    from truapi.domain.value_objects.id import ID
    missing = ID.new()
    with pytest.raises(UserNotFoundError):
        await update(missing, UpdateInput(display_name="x"), repo)
