# Copyright 2024 Recursive AI

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from ..app_context import users_service
from ..models.users import UserRole
from ..schemas.users import CreateUser, UpdateUser, User
from ..services.users import UsersService
from . import PaginatedResponse

router = APIRouter(
    prefix="/v1/users",
    tags=["Users"],
)


@router.post("/", description="Create new user")
async def create_user(
    create_user: CreateUser,
    users_service: Annotated[UsersService, Depends(users_service)],
) -> User:
    return await users_service.create_user(create_user)


@router.get("/{email}", description="Get user")
async def get_user(
    email: Annotated[str, Path()],
    users_service: Annotated[UsersService, Depends(users_service)],
) -> User:
    return await users_service.get_user(email)


@router.get("/", description="Get users")
async def get_users(
    users_service: Annotated[UsersService, Depends(users_service)],
    organization: Annotated[str | None, Query()] = None,
    role: Annotated[UserRole | None, Query()] = None,
    email: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query()] = 0,
    page_size: Annotated[int, Query()] = 20,
) -> PaginatedResponse[User]:
    data = await users_service.get_users(
        organization,
        role,
        email,
        page,
        page_size,
    )
    total = await users_service.get_user_count(
        organization,
        role,
        email,
    )
    return PaginatedResponse[User](
        data=data,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.put("/user/{email}", description="Update user")
async def update_user(
    email: Annotated[str, Path()],
    update_user: UpdateUser,
    users_service: Annotated[UsersService, Depends(users_service)],
) -> User:
    return await users_service.update_user(email, update_user)
