# Copyright 2024 Recursive AI

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreateOrganisation(BaseModel):
    name: str


class Organisation(CreateOrganisation):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
