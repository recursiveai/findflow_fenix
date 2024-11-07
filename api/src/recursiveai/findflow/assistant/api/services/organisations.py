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

    async def _get_organisation(self, name: str) -> OrganisationModel | None:
        stmt = select(OrganisationModel).where(OrganisationModel.name == name)
        async with self._session_provider() as session:
            result = await session.execute(stmt)
            result = result.scalar()
            return result

    async def create_organisation(
        self, create_organisation: CreateOrganisation
    ) -> Organisation:
        organisation = await self._get_organisation(create_organisation.name)
        if organisation is not None:
            raise AlreadyExistsError(
                f"Organisation '{create_organisation.name}' already exists"
            )

        organisation = OrganisationModel(**create_organisation.model_dump())
        async with self._session_provider() as session:
            session.add(organisation)
            await session.commit()
            # await session.refresh(organisation)

        return Organisation.model_validate(organisation)

    async def get_organisation(self, name: str) -> Organisation:
        organisation = await self._get_organisation(name)
        if organisation is None:
            raise DoesNotExistError(f"Organisation '{name}' does no exist")

        return Organisation.model_validate(organisation)

    async def get_organisations(
        self,
        name: str | None = None,
        page: int = 0,
        page_size: int = 20,
    ) -> Iterable[Organisation]:
        stmt = select(OrganisationModel)

        if name is not None:
            stmt = stmt.where(OrganisationModel.name.contains(name))

        stmt = stmt.order_by(OrganisationModel.name)
        stmt = stmt.offset(page * page_size).limit(page_size)

        async with self._session_provider() as session:
            result = await session.execute(stmt)
            organisations = result.scalars().all()
            return map(Organisation.model_validate, organisations)

    async def get_organisation_count(self) -> int:
        stmt = select(func.count(OrganisationModel.name.distinct()))
        async with self._session_provider() as session:
            result = await session.execute(stmt)
            count = result.scalar_one()
            return count
