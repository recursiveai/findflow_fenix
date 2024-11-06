# Copyright 2024 Recursive AI

import logging

from firebase_admin import auth as firebase_auth
from firebase_admin import exceptions as firebase_exceptions
from pydantic import BaseModel

from recursiveai.findflow.core.exceptions import DoesNotExistError
from recursiveai.findflow.core.schemas import CreateUser

_logger = logging.getLogger(__name__)


class CloudAuthConfig(BaseModel):
    user_pool_id: str | None = None


class GCPAuthService:
    def __init__(self, firebase_admin_app) -> None:
        self.firebase_admin = firebase_admin_app

    def _get_user_by_email(self, email: str) -> firebase_auth.UserRecord:
        return self.firebase_admin.get_user_by_email(email)
    
    def validate_user_token(self, jwt: str) -> None:
        firebase_auth.verify_id_token()

    def delete_user(self, email: str) -> None:
        try:
            gcp_user = self._get_user_by_email(email)
        except firebase_exceptions.NotFoundError as error:
            _logger.debug(error)
            raise DoesNotExistError(f"User {email} not found in cloud") from error
        firebase_auth.delete_user(gcp_user.uid)

    def create_user(self, new_user: CreateUser) -> firebase_auth.UserRecord:
        if new_user.password is None:
            return firebase_auth.create_user(email=new_user.email)
        return firebase_auth.create_user(
            email=new_user.email, password=new_user.password
        )

    def update_password(self, email: str, password: str) -> None:
        try:
            gcp_user = self._get_user_by_email(email)
        except firebase_exceptions.NotFoundError as error:
            _logger.debug(error)
            raise DoesNotExistError(f"User {email} not found in cloud") from error
        firebase_auth.update_user(gcp_user.uid, password=password)
