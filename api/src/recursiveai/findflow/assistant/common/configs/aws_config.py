# Copyright 2024 Recursive AI

from typing import Any, Type, TypeVar

import boto3
import yaml
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

T = TypeVar("T")


def load_configuration_from_parameter(clazz: Type[T], parameter_name: str) -> T:
    """Load application configuration from provided path"""
    ssm_client = boto3.client("ssm")

    parameter_response = ssm_client.get_parameter(Name=parameter_name)
    parameter_value = parameter_response["Parameter"]["Value"]

    app_config = yaml.safe_load(parameter_value)
    return clazz(**app_config)


def load_parameter_store_value(parameter_name: str) -> dict[str, Any]:
    """
    Load parameter store value.

    Args:
        parameter_name: The name of the parameter.

    Returns:
        The loaded parameter store value.
    """
    ssm_client = boto3.client("ssm")
    parameter_response = ssm_client.get_parameter(Name=parameter_name)
    parameter_value = parameter_response["Parameter"]["Value"]
    app_config = yaml.safe_load(parameter_value)
    return app_config


class AWSParamStoreConfigSettingsSource(PydanticBaseSettingsSource):
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

    def __init__(self, settings_cls: Type[BaseSettings], parameter_name: str):
        super().__init__(settings_cls)
        self.parameter_name = parameter_name

    def __call__(self) -> dict[str, Any]:
        return load_parameter_store_value(self.parameter_name)
