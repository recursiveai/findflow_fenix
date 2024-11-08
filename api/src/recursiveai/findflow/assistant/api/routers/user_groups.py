# Copyright 2024 Recursive AI

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from ..app_context import user_groups_service
from ..schemas.user_groups import CreateUserGroup, UserGroup
from ..services.user_groups import UserGroupsService
from . import PaginatedResponse

router = APIRouter(
    prefix="/v1/user_groups",
    tags=["User Groups"],
)


@router.post("/", description="Create new user groups")
async def create_user_group(
    create: CreateUserGroup,
    service: Annotated[UserGroupsService, Depends(user_groups_service)],
) -> UserGroup:
    return await service.create_user_group(create)


@router.get("/{id}", description="Get user groups")
async def get_user_group(
    id: Annotated[str, Path()],
    service: Annotated[UserGroupsService, Depends(user_groups_service)],
) -> UserGroup:
    return await service.get_user_group(id)


@router.get("/", description="Get all user groups")
async def get_user_groups(
    service: Annotated[UserGroupsService, Depends(user_groups_service)],
    id: Annotated[str | None, Query()] = None,
    organisation_id: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query()] = 0,
    page_size: Annotated[int, Query()] = 20,
) -> PaginatedResponse[UserGroup]:
    data = await service.get_user_groups(
        id,
        organisation_id,
        page,
        page_size,
    )
    total = await service.get_user_group_count(
        id,
        organisation_id,
    )
    return PaginatedResponse[UserGroup](
        data=data,
        page=page,
        page_size=page_size,
        total=total,
    )
