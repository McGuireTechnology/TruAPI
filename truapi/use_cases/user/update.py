from dataclasses import dataclass
from typing import Optional

from truapi.domain.entities.user import User
from truapi.domain.value_objects.id import ID
from truapi.ports.repositories.user import UserRepository
from truapi.use_cases.exceptions import UserNotFoundError


@dataclass
class UpdateInput:
    display_name: Optional[str] = None
    email: Optional[str] = None


async def update(user_id: ID, input: UpdateInput, repo: UserRepository) -> User:
    user = await repo.get(id=user_id)
    if not user:
        raise UserNotFoundError("User not found")
    if input.display_name is not None:
        user.display_name = input.display_name
    if input.email is not None:
        user.email = input.email
    await repo.save(user)
    return user
