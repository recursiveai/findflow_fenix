# Copyright 2024 Recursive AI

import logging
import uuid
from abc import ABC, abstractmethod

import boto3
from pydantic import BaseModel

from recursiveai.findflow.core.exceptions import DoesNotExistError
from recursiveai.findflow.core.schemas import CreateUser

_logger = logging.getLogger(__name__)


class CloudAuthConfig(BaseModel):
    user_pool_id: str | None = None


def get_cognito_client():
    return boto3.client("cognito-idp")


class AWSAuthService:
    def __init__(self, user_pool_id: str, cognito_client) -> None:
        _logger.debug("Creating AWS Cognito Client")
        self.cognito = cognito_client
        self.user_pool_id = user_pool_id

    def _get_user_by_email(self, email: str) -> dict:
        response = self.cognito.list_users(
            UserPoolId=self.user_pool_id, Filter=f'email = "{email}"', Limit=1
        )
        if response["Users"]:
            return response["Users"][0]
        else:
            raise DoesNotExistError(f"User {email} not found in cloud")

    def validate_user_token(self, jwt: str) -> None:
        firebase_auth.verify_id_token()

    def delete_user(self, email: str) -> None:
        aws_user = self._get_user_by_email(email)
        self.cognito.admin_delete_user(
            UserPoolId=self.user_pool_id, Username=aws_user["Username"]
        )

    def create_user(self, new_user: CreateUser) -> dict:
        """
        Creates a new user in Cognito, suppresses the welcome email, and sets a permanent password.

        Suppression of the welcome email prevents Cognito from sending the user an email with a temporary password.
        A permanent password is set immediately to move the user from 'FORCE_CHANGE_PASSWORD' to 'CONFIRMED' state, enabling password reset.
        The password is a UUID for security measures. This will not be shared with the user.
        """
        response = self.cognito.admin_create_user(
            UserPoolId=self.user_pool_id,
            Username=new_user.email,
            UserAttributes=[
                {"Name": "email", "Value": new_user.email},
                {"Name": "email_verified", "Value": "True"},
            ],
            MessageAction="SUPPRESS",
        )

        if new_user.password is None:
            password = str(uuid.uuid4())
        else:
            password = new_user.password

        self.cognito.admin_set_user_password(
            UserPoolId=self.user_pool_id,
            Username=new_user.email,
            Password=password,
            Permanent=True,
        )

        return response["User"]

    def update_password(self, email: str, password: str) -> None:
        aws_user = self._get_user_by_email(email)
        self.cognito.admin_set_user_password(
            UserPoolId=self.user_pool_id,
            Username=aws_user["Username"],
            Password=password,
            Permanent=True,
        )
