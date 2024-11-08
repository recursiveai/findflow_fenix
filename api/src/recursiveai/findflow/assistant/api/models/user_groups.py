# Copyright 2024 Recursive AI

import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from . import AppBase
from .organisations import Organisation


class UserGroup(AppBase):
    __tablename__ = "user_groups"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    organization_id: Mapped[str] = mapped_column(
        ForeignKey(Organisation.id),
        primary_key=True,
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
