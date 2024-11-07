# Copyright 2024 Recursive AI

from typing import Iterable

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from recursiveai.findflow.assistant.api.schemas.users import (
    CreateUser,
    UpdateUser,
    User,
)
from recursiveai.findflow.assistant.common.auths.base_auth import AuthService
from recursiveai.findflow.assistant.common.exceptions import (
    AlreadyExistsError,
    DoesNotExistError,
)

from ..models.users import User as UserModel
from ..models.users import UserRole


class UsersService:
    def __init__(
        self,
        session_provider: async_sessionmaker[AsyncSession],
        auth_service: AuthService,
    ) -> None:
        self._session_provider = session_provider
        self._auth_service = auth_service

    async def _get_user(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email)
        async with self._session_provider() as session:
            result = await session.execute(stmt)
            result = result.scalar()
            return result

    async def create_user(self, create_user: CreateUser) -> User:
        user = await self._get_user(create_user.email)
        if user is not None:
            raise AlreadyExistsError(f"User '{create_user.email}' already exists")

        user = UserModel(**create_user.model_dump())
        async with self._session_provider() as session:
            session.add(user)
            await session.commit()
            # await session.refresh(user)

        await self._auth_service.create_user(create_user.email)

        return User.model_validate(user)

    async def get_user(self, email: str) -> User:
        user = await self._get_user(email)
        if user is None:
            raise DoesNotExistError(f"User '{email}' does no exist")

        return User.model_validate(user)

    async def get_users(
        self,
        organization: str | None = None,
        role: UserRole | None = None,
        email: str | None = None,
        page: int = 0,
        page_size: int = 20,
    ) -> Iterable[User]:
        stmt = select(UserModel)

        if organization is not None:
            stmt = stmt.where(UserModel.organization.contains(organization))

        if role is not None:
            stmt = stmt.where(UserModel.role == role)

        if email is not None:
            stmt = stmt.where(UserModel.email.contains(email))

        stmt = stmt.order_by(UserModel.email)
        stmt = stmt.offset(page * page_size).limit(page_size)

        async with self._session_provider() as session:
            result = await session.execute(stmt)
            organisations = result.scalars().all()
            return map(User.model_validate, organisations)

    async def update_user(self, email: str, update_user: UpdateUser) -> User:
        user = await self._get_user(email)
        if user is None:
            raise DoesNotExistError(f"User '{email}' does no exist")

        stmt = (
            update(UserModel)
            .where(UserModel.email == email)
            .values(**update_user.model_dump(exclude_none=True))
        )

        async with self._session_provider() as session:
            await session.execute(stmt)
            await session.commit()

        return await self.get_user(email)

    async def get_user_count(
        self,
        organization: str | None = None,
        role: UserRole | None = None,
        email: str | None = None,
    ) -> int:
        stmt = select(func.count(UserModel.email.distinct()))

        if organization is not None:
            stmt = stmt.where(UserModel.organization.contains(organization))

        if role is not None:
            stmt = stmt.where(UserModel.role == role)

        if email is not None:
            stmt = stmt.where(UserModel.email.contains(email))

        async with self._session_provider() as session:
            result = await session.execute(stmt)
            return result.scalar_one()
