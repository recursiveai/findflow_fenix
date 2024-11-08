# Copyright 2024 Recursive AI

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from ..app_context import blocked_keywords_service
from ..schemas.blocked_keywords import (
    BlockedKeyword,
    CreateBlockedKeyword,
    UpdateBlockedKeyword,
)
from ..services.blocked_keywords import BlockedKeywordsService
from . import PaginatedResponse

router = APIRouter(
    prefix="/v1/blocked-keywords",
    tags=["Blocked Keywords"],
)


@router.post("/", description="Create new blocked keyword")
async def create_blocked_keyword(
    create: CreateBlockedKeyword,
    service: Annotated[BlockedKeywordsService, Depends(blocked_keywords_service)],
) -> BlockedKeyword:
    return await service.create_blocked_keyword(create)


@router.get("/{id}", description="Get blocked keyword")
async def get_blocked_keyword(
    id: Annotated[str, Path()],
    service: Annotated[BlockedKeywordsService, Depends(blocked_keywords_service)],
) -> BlockedKeyword:
    return await service.get_blocked_keyword(id)


@router.get("/", description="Get blocked keywords")
async def get_blocked_keywords(
    service: Annotated[BlockedKeywordsService, Depends(blocked_keywords_service)],
    organization_id: Annotated[str | None, Query()] = None,
    keyword: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query()] = 0,
    page_size: Annotated[int, Query()] = 20,
) -> PaginatedResponse[BlockedKeyword]:
    data = await service.get_blocked_keywords(
        organization_id,
        keyword,
        page,
        page_size,
    )
    total = await service.get_blocked_keyword_count(
        organization_id,
        keyword,
    )
    return PaginatedResponse[BlockedKeyword](
        data=data,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.put("/{id}", description="Update blocked keyword")
async def update_blocked_keyword(
    id: Annotated[str, Path()],
    update: UpdateBlockedKeyword,
    service: Annotated[BlockedKeywordsService, Depends(blocked_keywords_service)],
) -> BlockedKeyword:
    return await service.update_blocked_keyword(id, update)


@router.delete("/{id}", description="Delete blocked keyword")
async def delete_blocked_keyword(
    id: Annotated[str, Path()],
    service: Annotated[BlockedKeywordsService, Depends(blocked_keywords_service)],
) -> None:
    return await service.delete_blocked_keyword(id)
