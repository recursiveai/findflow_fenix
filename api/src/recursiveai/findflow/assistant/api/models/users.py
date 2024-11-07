# Copyright 2024 Recursive AI

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from . import AppBase


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class UserLanguage(str, enum.Enum):
    ENGLISH = "en"
    JAPANESE = "ja"


class User(AppBase):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        index=True,
    )

    organization: Mapped[str] = mapped_column(
        ForeignKey("organizations.name"),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    language: Mapped[UserLanguage] = mapped_column(Enum(UserLanguage), nullable=False)

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
