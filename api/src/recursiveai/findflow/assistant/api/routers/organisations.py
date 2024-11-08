# Copyright 2024 Recursive AI

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from ..app_context import organisations_service
from ..schemas.organisations import CreateOrganisation, Organisation
from ..services.organisations import OrganisationsService
from . import PaginatedResponse

router = APIRouter(
    prefix="/v1/organisations",
    tags=["Organisations"],
)


@router.post("/", description="Create new organisation")
async def create_organisation(
    create: CreateOrganisation,
    service: Annotated[OrganisationsService, Depends(organisations_service)],
) -> Organisation:
    return await service.create_organisation(create)


@router.get("/{id}", description="Get organisation")
async def get_organisation(
    id: Annotated[str, Path()],
    service: Annotated[OrganisationsService, Depends(organisations_service)],
) -> Organisation:
    return await service.get_organisation(id)


@router.get("/", description="Get all organisations")
async def get_organisations(
    service: Annotated[OrganisationsService, Depends(organisations_service)],
    name: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query()] = 0,
    page_size: Annotated[int, Query()] = 20,
) -> PaginatedResponse[Organisation]:
    data = await service.get_organisations(
        name,
        page,
        page_size,
    )
    total = await service.get_organisation_count(
        name,
    )
    return PaginatedResponse[Organisation](
        data=data,
        page=page,
        page_size=page_size,
        total=total,
    )
