# Copyright 2024 Recursive AI

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreateBlockedKeyword(BaseModel):
    organization_id: str

    keyword: str


class UpdateBlockedKeyword(BaseModel):
    keyword: str | None = None


class BlockedKeyword(CreateBlockedKeyword):
    id: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
