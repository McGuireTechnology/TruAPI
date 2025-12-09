from typing import Annotated, List, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from truapi.domain.entities.user import User
from truapi.domain.value_objects.id import ID
from truapi.drivers.rest.dependencies import repo_dep
from truapi.ports.repositories.user import UserRepository
from truapi.use_cases.exceptions import UserNotFoundError
from truapi.use_cases.user.create import CreateInput, create
from truapi.use_cases.user.delete import delete
from truapi.use_cases.user.get import get
from truapi.use_cases.user.update import UpdateInput, update

router = APIRouter(prefix="/users", tags=["users"])


def get_user_repository() -> UserRepository:
    # Backward-compatible wrapper if imported elsewhere
    return cast(UserRepository, repo_dep("user")())


class CreateUserBody(BaseModel):
    username: str
    email: EmailStr
    display_name: str = ""


class UpdateUserBody(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    display_name: str

    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        return cls(
            id=str(user.id),
            username=user.username,
            email=user.email,
            display_name=user.display_name,
        )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(
    body: CreateUserBody,
    repo: Annotated[UserRepository, Depends(repo_dep("user"))],
) -> UserResponse:
    user = create(CreateInput(username=body.username, email=str(body.email), display_name=body.display_name))
    await repo.save(user)
    return UserResponse.from_entity(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    repo: Annotated[UserRepository, Depends(repo_dep("user"))],
) -> UserResponse:
    try:
        entity = await get(ID.from_str(user_id), repo)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return UserResponse.from_entity(entity)


@router.get("", response_model=List[UserResponse])
async def list_users(
    repo: Annotated[UserRepository, Depends(repo_dep("user"))],
    username: Optional[str] = None,
    email: Optional[str] = None,
) -> List[UserResponse]:
    users = await repo.list(username=username, email=email)
    return [UserResponse.from_entity(u) for u in users]


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    body: UpdateUserBody,
    repo: Annotated[UserRepository, Depends(repo_dep("user"))],
) -> UserResponse:
    try:
        entity = await update(
            ID.from_str(user_id),
            UpdateInput(display_name=body.display_name, email=str(body.email) if body.email is not None else None),
            repo,
        )
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return UserResponse.from_entity(entity)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> None:
    try:
        await delete(ID.from_str(user_id), repo)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
