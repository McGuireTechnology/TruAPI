from truapi.domain.value_objects.id import ID
from truapi.ports.repositories.user import UserRepository
from truapi.use_cases.exceptions import UserNotFoundError


async def delete(user_id: ID, repo: UserRepository) -> None:
    exists = await repo.exists(id=user_id)
    if not exists:
        raise UserNotFoundError("User not found")
    await repo.delete(user_id)
