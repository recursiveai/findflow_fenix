# Copyright 2024 Recursive AI

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Literal

from pydantic import BaseModel

_logger = logging.getLogger(__name__)


class AuthType(str, Enum):
    DUMMY = "dummy"
    GCP = "gcp"


class AuthService(ABC):

    @abstractmethod
    async def validate_user_token(self, user_token: str) -> str: ...

    @abstractmethod
    async def create_user(self, email: str, password: str | None = None) -> str: ...

    @abstractmethod
    async def update_password(self, email: str, password: str) -> None: ...

    @abstractmethod
    async def delete_user(self, email: str) -> None: ...


class DummyAuthConfig(BaseModel):
    type: Literal[AuthType.DUMMY] = AuthType.DUMMY


class DummyAuthService(AuthService):

    async def validate_user_token(self, user_token: str) -> None:
        _logger.info("DummyAuthService validate_user_token")
        return user_token

    async def create_user(self, email: str, password: str | None = None) -> str:
        _logger.info("DummyAuthService create_user")
        return email

    async def update_password(self, email: str, password: str):
        _logger.info("DummyAuthService update_password")
        pass

    async def delete_user(self, email: str):
        _logger.info("DummyAuthService delete_user")
        pass
