# Copyright 2024 Recursive AI

import logging
from abc import ABC, abstractmethod
from enum import Enum
from functools import cached_property
from typing import Type

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

_logger = logging.getLogger(__name__)

try:
    from .aws_config import AWSParamStoreConfigSettingsSource
except ImportError:
    _logger.warning("AWS dependencies not available")

try:
    from .gcp_config import GoogleSecretManagerConfigSettingsSource
except ImportError:
    _logger.warning("GCP dependencies not available")


class Env(str, Enum):
    LOCAL = "local"
    GCP = "gcp"
    AWS = "aws"


class MetaConfig(BaseSettings):
    config_file_path: str
    env: Env

    model_config = SettingsConfigDict(
        env_prefix="meta__",
        env_nested_delimiter="__",
    )

    def env_source(
        self,
        settings_cls: Type[BaseSettings],
    ) -> PydanticBaseSettingsSource:
        match self.env:
            case Env.GCP:
                return GoogleSecretManagerConfigSettingsSource(
                    settings_cls,
                    secret_version_name=self.config_file_path,
                )
            case Env.AWS:
                return AWSParamStoreConfigSettingsSource(
                    settings_cls,
                    parameter_name=self.config_file_path,
                )
            case Env.LOCAL:
                return YamlConfigSettingsSource(
                    settings_cls,
                    yaml_file=self.config_file_path,
                )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            env_settings,
            dotenv_settings,
            init_settings,
        )


class BaseAppConfig(ABC, BaseSettings):
    @staticmethod
    @abstractmethod
    def _get_meta() -> MetaConfig:
        """Get the meta configuration for the app"""
        return MetaConfig()

    model_config = SettingsConfigDict(
        ignored_types=(cached_property,),
        env_prefix="app__",
        env_nested_delimiter="__",
        yaml_file_encoding="utf-8",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            cls._get_meta().env_source(settings_cls),
        )
