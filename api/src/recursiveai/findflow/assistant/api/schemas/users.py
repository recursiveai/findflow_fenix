# Copyright 2024 Recursive AI

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from ..models.users import UserLanguage, UserRole


class CreateUser(BaseModel):
    email: EmailStr
    organization_id: str

    role: UserRole
    language: UserLanguage


class UpdateUser(BaseModel):
    role: UserRole | None = None
    language: UserLanguage | None = None


class User(CreateUser):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
