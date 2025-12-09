from truapi.domain.entities.user import User
from truapi.domain.value_objects.id import ID
from truapi.ports.repositories.user import UserRepository
from truapi.use_cases.exceptions import UserNotFoundError


async def get(user_id: ID, repo: UserRepository) -> User:
    user = await repo.get(id=user_id)
    if user is None:
        raise UserNotFoundError("User not found")
    return user
