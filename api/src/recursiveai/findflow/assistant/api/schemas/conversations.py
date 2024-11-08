# Copyright 2024 Recursive AI

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreateConversation(BaseModel):
    organization_id: str
    user_id: str

    title: str


class UpdateConversation(BaseModel):
    title: str | None = None


class Conversation(CreateConversation):
    id: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreateConversationEntry(BaseModel):
    content: dict


class UpdateConversationEntry(BaseModel):
    content: dict | None = None


class ConversationEntry(CreateConversationEntry):
    id: str
    conversation_id: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
