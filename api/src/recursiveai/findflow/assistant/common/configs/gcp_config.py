# Copyright 2023 Recursive AI

from typing import Any, Type, TypeVar

import yaml
from google.cloud import secretmanager
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

T = TypeVar("T")


def load_string_from_secrets(secret_version_name: str) -> str:
    """Load string from secret version"""
    client = secretmanager.SecretManagerServiceClient()

    request = secretmanager.AccessSecretVersionRequest(
        name=secret_version_name,  # "projects/*/secrets/*/versions/*"
    )
    secret_version = client.access_secret_version(request=request)
    secret_version_value = secret_version.payload.data.decode(encoding="utf-8")

    return secret_version_value


def load_configuration_from_secrets(clazz: Type[T], secret_version_name: str) -> T:
    """Load configuration from secret version"""
    secret_version_value = load_string_from_secrets(secret_version_name)

    app_config = yaml.safe_load(secret_version_value)
    return clazz(**app_config)


class GoogleSecretManagerConfigSettingsSource(PydanticBaseSettingsSource):
    """
    A settings class that loads settings from Google Secret Manager.

    The account under which the application is executed should have the
    required access to Google Secret Manager.
    """

    def get_field_value(
        self,
        field: FieldInfo,
        field_name: str,
    ) -> tuple[Any, str, bool]:
        # Nothing to do here. Only implement the return statement to make mypy happy
        return None, "", False

    def __init__(self, settings_cls: Type[BaseSettings], secret_version_name: str):
        super().__init__(settings_cls)
        self.secret_version_name = secret_version_name

    def __call__(self) -> dict[str, Any]:
        d: dict[str, Any] = {}

        secret_version_value = load_string_from_secrets(self.secret_version_name)
        d = yaml.safe_load(secret_version_value)

        return d
