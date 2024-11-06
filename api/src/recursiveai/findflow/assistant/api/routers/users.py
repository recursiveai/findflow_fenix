# Copyright 2024 Recursive AI

import logging
from enum import Enum
from typing import Annotated, Generic, Iterable, TypeVar

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from firebase_admin import exceptions as firebase_exceptions
from pydantic import BaseModel, EmailStr, Field

_logger = logging.getLogger(__name__)


class StatusEnum(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    FAIL = "fail"


class UpdatePasswordRequest(BaseModel):
    email: EmailStr
    password: str


class UpdatePasswordResponse(BaseModel):
    status: StatusEnum
    data: dict[str, str] = Field(default_factory=dict)


class RequesterUser(BaseModel):
    email: EmailStr
    role: RoleStrEnum


class User(BaseModel):
    email: EmailStr
    role: str

T = TypeVar("T")

class Paginated(BaseModel, Generic[T]):
    result: Iterable[User]
    page_number: int
    page_size: int
    total_size: int

class Users(Paginated[User]):
    pass


router = APIRouter(
    prefix="/v1/users",
    tags=["Users"],
    dependencies=[
        Depends(app_context.validate_api_key_header),
    ],
)


@router.post("/", description="Create new user")
async def create_user(
    new_user: CreateUser,
) -> User:
    return User(email=user_email, role="user")


@router.get("/{user_email}", description="Get user by email")
async def get_user(
    user_email: Annotated[str, Path()],
) -> User:
    return User(email=user_email, role="user")


@router.get("/", description="Get all users")
async def get_users(
    organization: Annotated[str, Query()],
    email: Annotated[str, Query()] = None,
    skip: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 100,
) -> Users:
    return Users(

    )

@router.put("/user")
async def update_user(
    user_to_update: UpdateUser,
) -> UpdateUser:
    try:
        await users_services.update_user(user_to_update=user_to_update)
    except Exception as exc:
        _logger.error("Error updating user %s: %s", user_to_update.email, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User was not updated"
        ) from exc
    _logger.warning(
        "Updated information for user [%s]",
        user_to_update.email,
    )
    return user_to_update


@router.delete("/{user_email}", description="Delete user by email")
async def delete_user(
    user_email: Annotated[str, Path()]
) -> None:
    pass
