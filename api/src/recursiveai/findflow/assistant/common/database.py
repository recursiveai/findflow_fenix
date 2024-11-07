# Copyright 2024 Recursive AI

from enum import Enum
from typing import Literal

import asyncpg
from google.cloud.sql.connector.connector import create_async_connector
from google.cloud.sql.connector.enums import IPTypes
from pydantic import BaseModel, SecretStr
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class DatabaseType(str, Enum):
    LOCAL = "local"
    GCP = "gcp"


class LocalConfig(BaseModel):
    type: Literal[DatabaseType.LOCAL] = DatabaseType.LOCAL
    connection: SecretStr


class GCPConfig(BaseModel):
    type: Literal[DatabaseType.GCP] = DatabaseType.GCP

    connection: SecretStr
    private_ip: bool = True
    name: str

    user: str
    password: SecretStr


DatabaseConfig = LocalConfig | GCPConfig


_DRIVER = "asyncpg"
_PROTOCOL = f"postgresql+{_DRIVER}://"


async def create_async_engine_provider(db_config: DatabaseConfig) -> AsyncEngine:
    match db_config:
        case LocalConfig():
            return create_async_engine(
                _PROTOCOL + db_config.connection.get_secret_value(),
                pool_pre_ping=True,
                pool_recycle=3600,
            )
        case GCPConfig():
            ip_type = IPTypes.PRIVATE if db_config.private_ip else IPTypes.PUBLIC
            connector = await create_async_connector(ip_type=ip_type)

            async def getconn() -> asyncpg.Connection:
                return await connector.connect_async(
                    db_config.connection.get_secret_value(),
                    _DRIVER,
                    user=db_config.user,
                    password=db_config.password.get_secret_value(),
                    db=db_config.name,
                )

            return create_async_engine(
                _PROTOCOL,
                async_creator=getconn,
                pool_pre_ping=True,
                pool_recycle=3600,
            )


def create_async_session_provider(
    async_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)


async def async_create_all(async_engine: AsyncEngine, base: DeclarativeBase) -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)
