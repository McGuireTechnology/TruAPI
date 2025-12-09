from typing import Any, List, Optional

from truapi.domain.entities.user import User
from truapi.domain.value_objects.id import ID
from truapi.ports.repositories.user import UserRepository


class InMemoryUserRepository(UserRepository):
    """Minimal in-memory repository for testing and dev.

    Not thread-safe; suitable for unit tests and local prototyping.
    Uses class-level storage to mimic shared state across instances.
    """
    store: List[User] = []

    async def get(self, **filters: Any) -> Optional[User]:
        for u in self.store:
            if (f := filters.get("id")) and f == u.id:
                return u
            if (f := filters.get("username")) and f == u.username:
                return u
        return None

    async def list(self, **filters: Any) -> List[User]:
        if not filters:
            return list(self.store)
        results: List[User] = []
        for u in self.store:
            ok = True
            for k, v in filters.items():
                if k == "id" and u.id != v:
                    ok = False
                    break
                if k == "username" and u.username != v:
                    ok = False
                    break
            if ok:
                results.append(u)
        return results

    async def save(self, user: User) -> None:
        for i, u in enumerate(self.store):
            if u.id == user.id:
                self.store[i] = user
                return
        self.store.append(user)

    async def exists(self, **filters: Any) -> bool:
        return (await self.get(**filters)) is not None

    async def delete(self, user_id: ID) -> None:
        self.store = [u for u in self.store if u.id != user_id]
