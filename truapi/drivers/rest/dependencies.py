import asyncio
from typing import Any, Callable, Dict

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from truapi.adapters.repositories.user.in_memory import InMemoryUserRepository
from truapi.adapters.repositories.user.sqlalchemy import Base as UsersBase
from truapi.adapters.repositories.user.sqlalchemy import SQLAlchemyUserRepository
from truapi.ports.repositories.user import UserRepository
from truapi.settings import get_settings


def _sqlite_session_factory(database_url: str) -> Callable[[], AsyncSession]:
    engine = create_async_engine(database_url, echo=False, future=True)
    # Create tables if they don't exist (dev convenience)
    # Note: running sync create via run_sync because Base metadata create is synchronous

    async def _create():
        async with engine.begin() as conn:
            await conn.run_sync(UsersBase.metadata.create_all)

    # Fire-and-forget init (best-effort)

    try:
        asyncio.get_event_loop().create_task(_create())
    except RuntimeError:
        # If no loop, ignore; tables can be created elsewhere
        pass

    return async_sessionmaker(engine, expire_on_commit=False)


_repo_cache: Dict[str, Any] = {}


def get_repository(kind: str) -> Any:
    settings = get_settings()
    env = (settings.ENVIRONMENT or "").lower()

    # Cache per kind to avoid recreating on every request (esp. in-memory)
    if kind in _repo_cache:
        return _repo_cache[kind]

    if kind == "user":
        if env in {"test", "testing"}:
            repo: UserRepository = InMemoryUserRepository()
        elif env in {"dev", "development"}:
            db_url = "sqlite+aiosqlite:///./users.db"
            session_factory = _sqlite_session_factory(db_url)
            repo = SQLAlchemyUserRepository(session_factory=session_factory)
        elif env in {"prod", "production"}:
            raise RuntimeError("Production environment requires explicit repository wiring for 'user'")
        else:
            repo = InMemoryUserRepository()
        _repo_cache[kind] = repo
        return repo

    raise NotImplementedError(f"No repository configured for kind: {kind}")


def repo_dep(kind: str) -> Callable[[], Any]:
    def _dep() -> Any:
        return get_repository(kind)

    return _dep
