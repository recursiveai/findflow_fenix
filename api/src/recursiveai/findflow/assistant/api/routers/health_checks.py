# Copyright 2024 Recursive AI

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(
    prefix="/v1/health",
    tags=["Health Checks"],
    dependencies=[],
)


class HealthCheckResponse(BaseModel):
    version: str


@router.get("")
async def health_check(request: Request) -> HealthCheckResponse:
    return HealthCheckResponse(version=request.app.version)
