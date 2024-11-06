# Copyright 2024 Recursive AI

from functools import cached_property

from api.src.recursiveai.findflow.assistant.common.configs.base_config import (
    BaseAppConfig,
)


class AppConfig(BaseAppConfig):

    database: DatabaseConfig

    auth: CloudAuthConfig = Field(default_factory=CloudAuthConfig)

    api_keys: list[SecretStr]

    @cached_property
    def get_api_keys(self) -> list[str]:
        return [key.get_secret_value() for key in self.api_keys]

    @staticmethod
    def _get_meta():
        return MetaConfig(
            config_file_path="config/local/support_config.yaml",
            run_env=RunEnv.LOCAL,
        )
