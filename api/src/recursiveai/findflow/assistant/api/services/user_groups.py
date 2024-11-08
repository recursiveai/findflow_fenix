# Copyright 2024 Recursive AI

from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from recursiveai.findflow.assistant.common.exceptions import (
    AlreadyExistsError,
    DoesNotExistError,
)

from ..models.user_groups import UserGroup as UserGroupModel
from ..schemas.user_groups import CreateUserGroup, UserGroup


class UserGroupsService:
    def __init__(
        self,
        session_provider: async_sessionmaker[AsyncSession],
    ) -> None:
        self._session_provider = session_provider

    async def _get_user_group(
        self, id: str, organization_id: str
    ) -> UserGroupModel | None:
        stmt = (
            select(UserGroupModel)
            .where(UserGroupModel.id == id)
            .where(UserGroupModel.organization_id == organization_id)
        )
        async with self._session_provider() as session:
            result = await session.execute(stmt)
            return result.scalar()

    async def create_user_group(self, create: CreateUserGroup) -> UserGroup:
        user_group = await self._get_user_group(
            create.id,
            create.organization_id,
        )
        if user_group is not None:
            raise AlreadyExistsError(
                f"User Group '{create.organization_id}/{create.id}' already exists"
            )

        user_group = UserGroupModel(**create.model_dump())
        async with self._session_provider() as session:
            session.add(user_group)
            await session.commit()
            # await session.refresh(user_group)

            return UserGroup.model_validate(user_group)

    async def get_user_group(self, id: str, organization_id: str) -> UserGroup:
        user_group = await self._get_user_group(
            id,
            organization_id,
        )
        if user_group is None:
            raise DoesNotExistError(
                f"User Group '{organization_id}/{id}' does no exist"
            )

        return UserGroup.model_validate(user_group)

    async def get_user_groups(
        self,
        organization_id: str | None = None,
        id: str | None = None,
        page: int = 0,
        page_size: int = 20,
    ) -> Iterable[UserGroup]:
        stmt = select(UserGroupModel)

        if organization_id is not None:
            stmt = stmt.where(UserGroupModel.organization_id == organization_id)

        if id is not None:
            stmt = stmt.where(UserGroupModel.id.contains(id))

        stmt = stmt.order_by(
            UserGroupModel.organization_id.asc(), UserGroupModel.id.asc()
        )
        stmt = stmt.offset(page * page_size).limit(page_size)

        async with self._session_provider() as session:
            result = await session.execute(stmt)
            return map(UserGroup.model_validate, result.scalars().all())

    async def get_user_group_count(
        self,
        organization_id: str | None = None,
        id: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(UserGroupModel)

        if organization_id is not None:
            stmt = stmt.where(UserGroupModel.organization_id == organization_id)

        if id is not None:
            stmt = stmt.where(UserGroupModel.id.contains(id))

        async with self._session_provider() as session:
            result = await session.execute(stmt)
            return result.scalar_one()
