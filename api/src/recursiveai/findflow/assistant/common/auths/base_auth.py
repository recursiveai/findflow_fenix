# Copyright 2024 Recursive AI

from abc import ABC, abstractmethod

from pydantic import BaseModel

from recursiveai.findflow.core.exceptions import DoesNotExistError
from recursiveai.findflow.core.schemas import CreateUser


class AuthConfig(BaseModel):
    user_pool_id: str | None = None
    tenant_id: str


class CloudAuthService(ABC):

    @abstractmethod
    def validate_user_token(self, jwt: str) -> None:
        ...

    @abstractmethod
    def create_user(self, new_user: CreateUser):
        ...

    @abstractmethod
    def update_password(self, email: str, password: str):
        ...
    
    @abstractmethod
    def delete_user(self, email: str):
        ...
