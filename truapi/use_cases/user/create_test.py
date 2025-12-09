import pytest

from truapi.use_cases.user.create import CreateInput, create


def test_create_returns_user_entity():
    user = create(CreateInput(username="alice", email="alice@example.com", display_name="Alice"))
    assert user.username == "alice"
    assert user.email == "alice@example.com"
    assert user.display_name == "Alice"
    # ID value object should stringify to non-empty ULID
    from truapi.domain.value_objects.id import ID
    assert isinstance(user.id, ID)
    assert isinstance(str(user.id), str)
    assert len(str(user.id)) > 0
