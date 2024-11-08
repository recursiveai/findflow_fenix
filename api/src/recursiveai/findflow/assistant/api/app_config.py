# Copyright 2024 Recursive AI


from pydantic import SecretStr

from recursiveai.findflow.assistant.common.auths import AuthConfig
from recursiveai.findflow.assistant.common.database import DatabaseConfig

from ..common.configs.base_config import BaseAppConfig, Env, MetaConfig


class AppConfig(BaseAppConfig):

    database: DatabaseConfig

    auth: AuthConfig

    api_key: SecretStr

    @staticmethod
    def _get_meta():
        return MetaConfig(
            config_file_path="config/local/api_config.yaml",
            env=Env.LOCAL,
        )
