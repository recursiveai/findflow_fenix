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
    create_organisation: CreateOrganisation,
    organisations_service: Annotated[
        OrganisationsService, Depends(organisations_service)
    ],
) -> Organisation:
    return await organisations_service.create_organisation(create_organisation)


@router.get("/{name}", description="Get organisation")
async def get_organisation(
    name: Annotated[str, Path()],
    organisations_service: Annotated[
        OrganisationsService, Depends(organisations_service)
    ],
) -> Organisation:
    return await organisations_service.get_organisation(name)


@router.get("/", description="Get all organisations")
async def get_organisations(
    organisations_service: Annotated[
        OrganisationsService, Depends(organisations_service)
    ],
    name: Annotated[str, Query()] = None,
    page: Annotated[int, Query()] = 0,
    page_size: Annotated[int, Query()] = 20,
) -> PaginatedResponse[Organisation]:
    data = await organisations_service.get_organisations(
        name,
        page,
        page_size,
    )
    total = await organisations_service.get_organisation_count()
    return PaginatedResponse[Organisation](
        data=data,
        page=page,
        page_size=page_size,
        total=total,
    )
