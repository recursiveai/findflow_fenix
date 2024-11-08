# Copyright 2024 Recursive AI

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreateUserGroup(BaseModel):
    id: str
    organization_id: str


class UserGroup(CreateUserGroup):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
