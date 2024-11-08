# Copyright 2024 Recursive AI

from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from recursiveai.findflow.assistant.common.exceptions import (
    AlreadyExistsError,
    DoesNotExistError,
)

from ..models.organisations import Organisation as OrganisationModel
from ..schemas.organisations import CreateOrganisation, Organisation


class OrganisationsService:
    def __init__(
        self,
        session_provider: async_sessionmaker[AsyncSession],
    ) -> None:
        self._session_provider = session_provider

    async def _get_organisation(self, id: str) -> OrganisationModel | None:
        stmt = select(OrganisationModel).where(OrganisationModel.id == id)
        async with self._session_provider() as session:
            result = await session.execute(stmt)
            return result.scalar()

    async def create_organisation(self, create_org: CreateOrganisation) -> Organisation:
        organisation = await self._get_organisation(create_org.id)
        if organisation is not None:
            raise AlreadyExistsError(f"Organisation '{create_org.id}' already exists")

        organisation = OrganisationModel(**create_org.model_dump())
        async with self._session_provider() as session:
            session.add(organisation)
            await session.commit()
            # await session.refresh(organisation)

            return Organisation.model_validate(organisation)

    async def get_organisation(self, id: str) -> Organisation:
        organisation = await self._get_organisation(id)
        if organisation is None:
            raise DoesNotExistError(f"Organisation '{id}' does no exist")

        return Organisation.model_validate(organisation)

    async def get_organisations(
        self,
        id: str | None = None,
        page: int = 0,
        page_size: int = 20,
    ) -> Iterable[Organisation]:
        stmt = select(OrganisationModel)

        if id is not None:
            stmt = stmt.where(OrganisationModel.id.contains(id))

        stmt = stmt.order_by(OrganisationModel.id)
        stmt = stmt.offset(page * page_size).limit(page_size)

        async with self._session_provider() as session:
            result = await session.execute(stmt)
            return map(Organisation.model_validate, result.scalars().all())

    async def get_organisation_count(
        self,
        id: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(OrganisationModel)

        if id is not None:
            stmt = stmt.where(OrganisationModel.id.contains(id))

        async with self._session_provider() as session:
            result = await session.execute(stmt)
            return result.scalar_one()
