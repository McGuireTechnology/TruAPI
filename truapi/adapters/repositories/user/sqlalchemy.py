from typing import Any, Callable, List, Optional

from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from ....domain.entities.user import User
from ....domain.value_objects.id import ID
from ....ports.repositories.user import UserRepository


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str]
    email: Mapped[str]
    display_name: Mapped[str]

    @classmethod
    def from_entity(cls, user: User) -> "UserRow":
        return cls(
            id=str(user.id),
            username=user.username,
            email=user.email,
            display_name=user.display_name,
        )

    def to_entity(self) -> User:
        # Rehydrate domain entity; ID.from_str ensures validation
        return User(id=ID.from_str(self.id), username=self.username, email=self.email, display_name=self.display_name)


def _apply_filters(stmt, **filters: Any):
    if not filters:
        return stmt
    for key, value in filters.items():
        if value is None:
            continue
        column = getattr(UserRow, key, None)
        if column is not None:
            stmt = stmt.where(column == (str(value) if key == "id" else value))
    return stmt


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self._session_factory = session_factory

    async def get(self, **filters: Any) -> Optional[User]:
        async with self._session_factory() as session:
            stmt = _apply_filters(select(UserRow).limit(1), **filters)
            result = await session.execute(stmt)
            row: Optional[UserRow] = result.scalar_one_or_none()
            return row.to_entity() if row else None

    async def list(self, **filters: Any) -> List[User]:
        async with self._session_factory() as session:
            stmt = _apply_filters(select(UserRow), **filters)
            result = await session.execute(stmt)
            rows: List[UserRow] = list(result.scalars().all())
            return [r.to_entity() for r in rows]

    async def save(self, user: User) -> None:
        async with self._session_factory() as session:
            # Upsert using merge to avoid relying on rowcount
            await session.merge(UserRow.from_entity(user))
            await session.commit()

    async def exists(self, **filters: Any) -> bool:
        async with self._session_factory() as session:
            stmt = _apply_filters(select(UserRow.id).limit(1), **filters)
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None

    async def delete(self, user_id: ID) -> None:
        async with self._session_factory() as session:
            stmt = sa_delete(UserRow).where(UserRow.id == str(user_id))
            await session.execute(stmt)
            await session.commit()
