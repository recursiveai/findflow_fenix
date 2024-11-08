# Copyright 2024 Recursive AI

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from . import AppBase
from .organisations import Organisation
from .users import User


class Conversation(AppBase):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    organization_id: Mapped[str] = mapped_column(
        ForeignKey(Organisation.id),
        nullable=False,
        index=True,
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey(User.email),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        server_onupdate=func.now(),
    )

    __table_args__ = (Index("ix_organization_user", "organization_id", "user_id"),)


class ConversationEntry(AppBase):
    __tablename__ = "conversation_entries"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    conversation_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(Conversation.id, ondelete="CASCADE"),
        index=True,
    )

    content: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        server_onupdate=func.now(),
    )
