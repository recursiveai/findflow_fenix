# Copyright 2024 Recursive AI

from typing import Iterable

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from recursiveai.findflow.assistant.common.exceptions import DoesNotExistError

from ..models.blocked_keywords import BlockedKeyword as BlockedKeywordModel
from ..schemas.blocked_keywords import (
    BlockedKeyword,
    CreateBlockedKeyword,
    UpdateBlockedKeyword,
)


class BlockedKeywordsService:
    def __init__(
        self,
        session_provider: async_sessionmaker[AsyncSession],
    ) -> None:
        self._session_provider = session_provider

    async def _get_blocked_keyword(self, id: str) -> BlockedKeywordModel | None:
        stmt = select(BlockedKeywordModel).where(BlockedKeywordModel.id == id)
        async with self._session_provider() as session:
            result = await session.execute(stmt)
            return result.scalar()

    async def create_blocked_keyword(
        self, create_kw: CreateBlockedKeyword
    ) -> BlockedKeyword:
        kw = BlockedKeywordModel(**create_kw.model_dump())
        async with self._session_provider() as session:
            session.add(kw)
            await session.commit()
            # await session.refresh(user)

        return BlockedKeyword.model_validate(kw)

    async def get_blocked_keyword(self, id: int) -> BlockedKeyword:
        kw = await self._get_blocked_keyword(id)
        if kw is None:
            raise DoesNotExistError(f"Blocked Keyword '{id}' does no exist")

        return BlockedKeyword.model_validate(kw)

    async def get_blocked_keywords(
        self,
        organization_id: str | None = None,
        keyword: str | None = None,
        page: int = 0,
        page_size: int = 20,
    ) -> Iterable[BlockedKeyword]:
        stmt = select(BlockedKeywordModel)

        if organization_id is not None:
            stmt = stmt.where(BlockedKeywordModel.organization_id == organization_id)

        if keyword is not None:
            stmt = stmt.where(BlockedKeywordModel.keyword.contains(keyword))

        stmt = stmt.order_by(BlockedKeywordModel.keyword.asc())
        stmt = stmt.offset(page * page_size).limit(page_size)

        async with self._session_provider() as session:
            result = await session.execute(stmt)
            return map(BlockedKeyword.model_validate, result.scalars().all())

    async def update_blocked_keyword(
        self, id: int, update_kw: UpdateBlockedKeyword
    ) -> BlockedKeyword:
        kw = await self._get_blocked_keyword(id)
        if kw is None:
            raise DoesNotExistError(f"Blocked Keyword '{id}' does no exist")

        stmt = (
            update(BlockedKeywordModel)
            .where(BlockedKeywordModel.id == id)
            .values(**update_kw.model_dump(exclude_none=True))
        )

        async with self._session_provider() as session:
            await session.execute(stmt)
            await session.commit()

        return await self.get_blocked_keyword(id)

    async def delete_blocked_keyword(self, id: int) -> None:
        kw = await self._get_blocked_keyword(id)
        if kw is None:
            raise DoesNotExistError(f"Blocked Keyword '{id}' does no exist")

        stmt = delete(BlockedKeywordModel).where(BlockedKeywordModel.id == id)

        async with self._session_provider() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_blocked_keyword_count(
        self,
        organization_id: str | None = None,
        keyword: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(BlockedKeywordModel)

        if organization_id is not None:
            stmt = stmt.where(BlockedKeywordModel.organization_id == organization_id)

        if keyword is not None:
            stmt = stmt.where(BlockedKeywordModel.keyword.contains(keyword))

        async with self._session_provider() as session:
            result = await session.execute(stmt)
            return result.scalar_one()
