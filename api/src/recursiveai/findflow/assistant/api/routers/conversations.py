# Copyright 2024 Recursive AI

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from ..app_context import conversations_service
from ..schemas.conversations import (
    Conversation,
    ConversationEntry,
    CreateConversation,
    CreateConversationEntry,
    UpdateConversation,
    UpdateConversationEntry,
)
from ..services.conversations import ConversationsService
from . import PaginatedResponse

router = APIRouter(
    prefix="/v1/conversations",
    tags=["Conversations"],
)


@router.post("/", description="Create new conversation")
async def create_conversation(
    create: CreateConversation,
    service: Annotated[ConversationsService, Depends(conversations_service)],
) -> Conversation:
    return await service.create_conversation(create)


@router.get("/{id}", description="Get conversation")
async def get_conversation(
    id: Annotated[str, Path()],
    service: Annotated[ConversationsService, Depends(conversations_service)],
) -> Conversation:
    return await service.get_conversation(id)


@router.get("/", description="Get conversations")
async def get_conversations(
    service: Annotated[ConversationsService, Depends(conversations_service)],
    organization_id: Annotated[str | None, Query()] = None,
    keyword: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query()] = 0,
    page_size: Annotated[int, Query()] = 20,
) -> PaginatedResponse[Conversation]:
    data = await service.get_conversations(
        organization_id,
        keyword,
        page,
        page_size,
    )
    total = await service.get_conversation_count(
        organization_id,
        keyword,
    )
    return PaginatedResponse[Conversation](
        data=data,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.put("/{id}", description="Update conversation")
async def update_conversation(
    id: Annotated[str, Path()],
    update: UpdateConversation,
    service: Annotated[ConversationsService, Depends(conversations_service)],
) -> Conversation:
    return await service.update_conversation(id, update)


@router.delete("/{id}", description="Delete conversation")
async def delete_conversation(
    id: Annotated[str, Path()],
    service: Annotated[ConversationsService, Depends(conversations_service)],
) -> None:
    return await service.delete_conversation(id)


# Conversation Entries


@router.post("/{conversation_id}/entries", description="Create new conversation entry")
async def create_conversation(
    conversation_id: Annotated[str, Path()],
    create: CreateConversationEntry,
    service: Annotated[ConversationsService, Depends(conversations_service)],
) -> ConversationEntry:
    return await service.create_conversation(create)


@router.get("/{conversation_id}/entries", description="Get conversation entries")
async def get_conversation_entries(
    service: Annotated[ConversationsService, Depends(conversations_service)],
    organization_id: Annotated[str | None, Query()] = None,
    keyword: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query()] = 0,
    page_size: Annotated[int, Query()] = 20,
) -> PaginatedResponse[ConversationEntry]:
    data = await service.get_entries(
        organization_id,
        keyword,
        page,
        page_size,
    )
    total = await service.get_entry_count(
        organization_id,
        keyword,
    )
    return PaginatedResponse[ConversationEntry](
        data=data,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.put("/{conversation_id}/entries/{id}", description="Update conversation entry")
async def update_conversation_entry(
    conversation_id: Annotated[str, Path()],
    id: Annotated[str, Path()],
    update: UpdateConversationEntry,
    service: Annotated[ConversationsService, Depends(conversations_service)],
) -> ConversationEntry:
    return await service.update_entry(conversation_id, id, update)
