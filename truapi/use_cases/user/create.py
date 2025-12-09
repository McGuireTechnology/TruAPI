from dataclasses import dataclass

from truapi.domain.entities.user import User


@dataclass
class CreateInput:
    username: str
    email: str
    display_name: str = ""


def create(input: CreateInput) -> User:
    return User(username=input.username, email=input.email, display_name=input.display_name)
