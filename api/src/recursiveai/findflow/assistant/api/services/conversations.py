# Copyright 2024 Recursive AI

from typing import Iterable

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from recursiveai.findflow.assistant.common.exceptions import DoesNotExistError

from ..models.conversations import Conversation as ConversationModel
from ..models.conversations import ConversationEntry as ConversationEntryModel
from ..schemas.conversations import (
    Conversation,
    ConversationEntry,
    CreateConversation,
    CreateConversationEntry,
    UpdateConversation,
    UpdateConversationEntry,
)


class ConversationsService:
    def __init__(
        self,
        session_provider: async_sessionmaker[AsyncSession],
    ) -> None:
        self._session_provider = session_provider

    async def _get_conversation(self, id: int) -> ConversationModel | None:
        stmt = select(ConversationModel).where(ConversationModel.id == id)
        async with self._session_provider() as session:
            result = await session.execute(stmt)
            return result.scalar()

    async def create_conversation(self, create_cnv: CreateConversation) -> Conversation:
        conversation = ConversationModel(**create_cnv.model_dump())
        async with self._session_provider() as session:
            session.add(conversation)
            await session.commit()

            return Conversation.model_validate(conversation)

    async def get_conversation(self, id: int) -> Conversation:
        conversation = await self._get_conversation(id)
        if conversation is None:
            raise DoesNotExistError(f"Conversation '{id}' does no exist")

        return Conversation.model_validate(conversation)

    async def get_conversations(
        self,
        organization_id: str | None = None,
        title: str | None = None,
        page: int = 0,
        page_size: int = 20,
    ) -> Iterable[Conversation]:
        stmt = select(func.count()).select_from(ConversationModel)

        if organization_id is not None:
            stmt = stmt.where(ConversationModel.organization_id == organization_id)

        if title is not None:
            stmt = stmt.where(ConversationModel.title.contains(title))

        stmt = stmt.order_by(ConversationModel.id.asc())
        stmt = stmt.offset(page * page_size).limit(page_size)

        async with self._session_provider() as session:
            result = await session.execute(stmt)
            return map(Conversation.model_validate, result.scalars().all())

    async def update_conversation(
        self, id: int, update_cnv: UpdateConversation
    ) -> Conversation:
        conversation = await self._get_conversation(id)
        if conversation is None:
            raise DoesNotExistError(f"Conversation '{id}' does no exist")

        stmt = (
            update(ConversationModel)
            .where(ConversationModel.id == id)
            .values(**update_cnv.model_dump(exclude_none=True))
        )

        async with self._session_provider() as session:
            await session.execute(stmt)
            await session.commit()

        return await self.get_conversation(id)

    async def delete_conversation(self, id: int) -> None:
        conversation = await self._get_conversation(id)
        if conversation is None:
            raise DoesNotExistError(f"Conversation '{id}' does no exist")

        stmt = delete(ConversationModel).where(ConversationModel.id == id)

        async with self._session_provider() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_conversation_count(
        self,
        organization_id: str | None = None,
        title: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(ConversationModel)

        if organization_id is not None:
            stmt = stmt.where(ConversationModel.organization_id == organization_id)

        if title is not None:
            stmt = stmt.where(ConversationModel.title.contains(title))

        async with self._session_provider() as session:
            result = await session.execute(stmt)
            return result.scalar_one()

    # Conversation Entries

    async def _get_entry(
        self, conversation_id: int, id: int
    ) -> ConversationEntryModel | None:
        stmt = (
            select(ConversationEntryModel)
            .where(ConversationEntryModel.conversation_id == conversation_id)
            .where(ConversationEntryModel.id == id)
        )
        async with self._session_provider() as session:
            result = await session.execute(stmt)
            return result.scalar()

    async def create_entry(
        self, create_ce: CreateConversationEntry
    ) -> ConversationEntry:
        c_entry = ConversationEntryModel(**create_ce.model_dump())
        async with self._session_provider() as session:
            session.add(c_entry)
            await session.commit()

            return ConversationEntry.model_validate(c_entry)

    async def get_entry(self, conversation_id: int, id: int) -> ConversationEntry:
        entry = await self._get_entry(conversation_id, id)
        if entry is None:
            raise DoesNotExistError(
                f"Conversation Entry '{conversation_id}/{id}' does no exist"
            )

        return ConversationEntry.model_validate(entry)

    async def get_entries(
        self,
        conversation_id: str | None = None,
        page: int = 0,
        page_size: int = 20,
    ) -> Iterable[ConversationEntry]:
        stmt = select(func.count()).select_from(ConversationEntryModel)

        if conversation_id is not None:
            stmt = stmt.where(ConversationEntryModel.conversation_id == conversation_id)

        stmt = stmt.order_by(ConversationEntryModel.id.asc())
        stmt = stmt.offset(page * page_size).limit(page_size)

        async with self._session_provider() as session:
            result = await session.execute(stmt)
            return map(ConversationEntry.model_validate, result.scalars().all())

    async def update_entry(
        self,
        conversation_id: int,
        id: int,
        update_ce: UpdateConversationEntry,
    ) -> ConversationEntry:
        entry = await self._get_entry(conversation_id, id)
        if entry is None:
            raise DoesNotExistError(
                f"Conversation Entry '{conversation_id}/{id}' does no exist"
            )

        stmt = (
            update(ConversationEntryModel)
            .where(ConversationEntryModel.id == id)
            .values(**update_ce.model_dump(exclude_none=True))
        )

        async with self._session_provider() as session:
            await session.execute(stmt)
            await session.commit()

        return await self.get_conversation(id)

    async def get_entry_count(
        self,
        conversation_id: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(ConversationEntryModel)

        if conversation_id is not None:
            stmt = stmt.where(ConversationEntryModel.conversation_id == conversation_id)

        async with self._session_provider() as session:
            result = await session.execute(stmt)
            return result.scalar_one()
