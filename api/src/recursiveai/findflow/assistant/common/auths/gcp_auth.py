# Copyright 2024 Recursive AI

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Literal

import firebase_admin
from firebase_admin import App, auth, tenant_mgt
from pydantic import BaseModel

from .base_auth import AuthType


class GCPAuthConfig(BaseModel):
    type: Literal[AuthType.GCP] = AuthType.GCP
    tenant_id: str | None = None
    max_works: int = 4


def _get_or_create_app() -> App:
    try:
        return firebase_admin.get_app()
    except ValueError:
        return firebase_admin.initialize_app()


def _get_auth_client(tenant_id: str | None) -> auth.Client:
    app = _get_or_create_app()
    if tenant_id:
        return tenant_mgt.auth_for_tenant(tenant_id, app)
    return auth._get_client(app)


def run_in_executor(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, lambda: f(*args, **kwargs))

    return inner


# TODO: Add calls to threadpool to avoid blocking async loop
class GCPAuthService:
    def __init__(self, config: GCPAuthConfig) -> None:
        self._auth_client = _get_auth_client(config.tenant_id)
        self._executor = ThreadPoolExecutor(max_workers=config.max_works)

    def _get_user_by_email(self, email: str) -> auth.UserRecord:
        return self._auth_client.get_user_by_email(email)

    async def validate_user_token(self, user_token: str) -> None:
        loop = asyncio.get_running_loop()

        def _lambda():
            self._auth_client.verify_id_token(
                id_token=user_token,
                check_revoked=True,
            )

        await loop.run_in_executor(
            self._executor,
            _lambda,
        )

        asyncio.to_thread

        # self._auth_client.verify_id_token(
        #     id_token=user_token,
        #     check_revoked=True,
        # )

    async def create_user(self, email: str, password: str | None = None) -> str:
        loop = asyncio.get_running_loop()

        def _lambda():
            return self._auth_client.create_user(
                email=email,
                password=password,
            )

        new_user = await loop.run_in_executor(
            self._executor,
            _lambda,
        )

        # new_user = self._auth_client.create_user(
        #     email=email,
        #     password=password,
        # )
        return new_user.uid

    async def update_password(self, email: str, password: str) -> None:
        gcp_user = self._get_user_by_email(email)
        self._auth_client.update_user(gcp_user.uid, password=password)

    async def delete_user(self, email: str) -> None:
        gcp_user = self._get_user_by_email(email)
        self._auth_client.delete_user(gcp_user.uid)
