from abc import ABC, abstractmethod
from typing import Any, List, Optional

from truapi.domain.entities.user import User
from truapi.domain.value_objects.id import ID


class UserRepository(ABC):
    """Port: abstraction for user persistence (async).

    Implementations should only perform persistence operations.
    """

    @abstractmethod
    async def get(self, **filters: Any) -> Optional[User]:
        """Return a single user matching filters (e.g., id=ID, username=str)."""

    @abstractmethod
    async def list(self, **filters: Any) -> List[User]:
        """Return users matching optional filters; empty list if none."""

    @abstractmethod
    async def save(self, user: User) -> None:
        """Insert or update a user (upsert semantics)."""

    @abstractmethod
    async def exists(self, **filters: Any) -> bool:
        """Check existence of a user matching filters."""

    @abstractmethod
    async def delete(self, user_id: ID) -> None:
        """Delete a user by ID; no-op if absent."""


# Adapters implement this port; see `api.adapters.repositories.user.in_memory` for a simple in-memory adapter.
