# Copyright 2024 Recursive AI


from recursiveai.findflow.assistant.common.auths import AuthConfig
from recursiveai.findflow.assistant.common.database import DatabaseConfig, DatabaseType

from ..common.configs.base_config import BaseAppConfig, MetaConfig


class AppConfig(BaseAppConfig):

    database: DatabaseConfig

    auth: AuthConfig

    @staticmethod
    def _get_meta():
        return MetaConfig(
            config_file_path="config/local/api_config.yaml",
            run_env=DatabaseType.LOCAL,
        )
