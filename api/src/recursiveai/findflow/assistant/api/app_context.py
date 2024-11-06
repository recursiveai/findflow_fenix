# Copyright 2024 Recursive AI

import json
import logging
from typing import Annotated, AsyncGenerator, Iterable

import firebase_admin
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, ConfigDict
from recursiveai.findflow.core.database import (
    a_create_all,
    create_async_engine_provider,
    create_async_session_provider,
)
from recursiveai.findflow.core.elastic import IndexService, create_elastic_client
from recursiveai.findflow.core.model.api_metrics import APIMetricsBase
from recursiveai.findflow.core.model.audit_logs import AuditLogsBase
from recursiveai.findflow.core.model.blocked_keywords import BlockedKeywordsBase
from recursiveai.findflow.core.model.conversations import ConversationsBase
from recursiveai.findflow.core.model.departments import DepartmentsBase
from recursiveai.findflow.core.model.documents import DocumentsBase
from recursiveai.findflow.core.model.users import UsersBase
from recursiveai.findflow.core.service.audit_logs import AuditLogsService
from recursiveai.findflow.core.service.blocked_keywords import BlockedKeywordsService
from recursiveai.findflow.core.service.conversations import ConversationsService
from recursiveai.findflow.core.service.departments import DepartmentsService
from recursiveai.findflow.core.service.documents import DocumentsService
from recursiveai.findflow.core.service.metrics import MetricsService
from recursiveai.findflow.core.service.users import UsersService
from recursiveai.findflow.support.config import AppConfig
from recursiveai.findflow.util.cloud_auth import (
    AWSAuthService,
    CloudAuthService,
    GCPAuthService,
    get_cognito_client,
)
from recursiveai.findflow.util.dependencies import (
    AsyncProvider,
    Provider,
    ProviderFactory,
    async_singleton,
    singleton,
)
from recursiveai.findflow.util.gcp.gcp_config import load_string_from_secrets
from recursiveai.findflow.util.storage import (
    AWSStorageService,
    CloudProvider,
    GCPStorageService,
    StorageService,
)
from recursiveai.findflow.worker.service.queue_manager import (
    PubSubQueueManager,
    QueueManager,
    SQSQueueManager,
    get_sqs_client,
)
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

_logger = logging.getLogger(__name__)


@singleton
def app_config_provider() -> AppConfig:
    _logger.debug("Creating AppConfig")
    config = AppConfig()
    _logger.info("Configuration: %s", config.model_dump())
    return config


@singleton
def elastic_client_provider(
    config: Annotated[AppConfig, Depends(app_config_provider)],
) -> AsyncElasticsearch:
    _logger.debug("Creating Elastic Client")
    return create_elastic_client(config.elastic)


@singleton
def index_service_provider(
    elastic_client: Annotated[AsyncElasticsearch, Depends(elastic_client_provider)],
    config: Annotated[AppConfig, Depends(app_config_provider)],
) -> IndexService:
    _logger.debug("Creating Index Service")
    return IndexService(elastic_client, config=config.elastic)


@async_singleton
async def create_async_engine(
    config: Annotated[AppConfig, Depends(app_config_provider)],
) -> AsyncEngine:
    _logger.debug("Creating Async Engine")
    return await create_async_engine_provider(config.database)


@singleton
def create_async_session_maker(
    engine: Annotated[AsyncEngine, Depends(create_async_engine)],
) -> async_sessionmaker[AsyncSession]:
    _logger.debug("Creating Async Session Maker")
    return create_async_session_provider(engine)


async def async_session_provider(
    maker: Annotated[
        async_sessionmaker[AsyncSession],
        Depends(create_async_session_maker),
    ],
) -> AsyncGenerator[AsyncSession, None]:
    session = maker()
    _logger.debug("Creating Async Session ID:[%s]", id(session))
    try:
        yield session
    finally:
        _logger.debug("Closing Async Session: ID:[%s]", id(session))
        await session.close()


async def audit_logs_service(
    engine: Annotated[AsyncEngine, Depends(create_async_engine)],
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(create_async_session_maker)
    ],
) -> AuditLogsService:
    _logger.debug("Creating Audit Logs Service")
    await a_create_all(engine, AuditLogsBase)
    return AuditLogsService(session_maker=session_maker)


async def blocked_keywords_service(
    engine: Annotated[AsyncEngine, Depends(create_async_engine)],
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(create_async_session_maker)
    ],
) -> BlockedKeywordsService:
    _logger.debug("Creating Blocked Keywords Service")
    await a_create_all(engine, BlockedKeywordsBase)
    return BlockedKeywordsService(session_maker=session_maker)


async def conversations_service(
    engine: Annotated[AsyncEngine, Depends(create_async_engine)],
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(create_async_session_maker)
    ],
) -> ConversationsService:
    _logger.debug("Creating Conversations Service")
    await a_create_all(engine, ConversationsBase)
    return ConversationsService(session_maker=session_maker)


@singleton
def storage_service_provider(
    config: Annotated[AppConfig, Depends(app_config_provider)]
) -> StorageService:
    _logger.debug("Creating Storage Service")
    match config.storage.cloud_provider:
        case CloudProvider.AWS:
            return AWSStorageService()

        case CloudProvider.GCP:
            if config.storage.gcp_config.get_credentials_secret_name is None:
                return GCPStorageService.from_default()

            service_account_info_str = load_string_from_secrets(
                config.storage.gcp_config.get_credentials_secret_name
            )
            service_account_info = json.loads(service_account_info_str)
            return GCPStorageService.from_service_account_info(service_account_info)
        case _:
            raise ValueError(f"Unknown cloud provider: {config.storage.cloud_provider}")


@singleton
def queue_manager_provider(
    config: Annotated[AppConfig, Depends(app_config_provider)]
) -> QueueManager:
    _logger.debug("Creating Queue Manager")
    match config.storage.cloud_provider:
        case CloudProvider.AWS:
            return SQSQueueManager(config=config.publisher, sqs_client=get_sqs_client())
        case CloudProvider.GCP:
            return PubSubQueueManager(config=config.publisher)


@singleton
def queue_manager_webcrawler(
    config: Annotated[AppConfig, Depends(app_config_provider)]
) -> QueueManager:
    _logger.debug("Creating Queue Manager for Webcrawler")
    match config.storage.cloud_provider:
        case CloudProvider.AWS:
            return SQSQueueManager(
                config=config.publisher_webcrawler, sqs_client=get_sqs_client()
            )
        case CloudProvider.GCP:
            return PubSubQueueManager(config=config.publisher_webcrawler)


async def metrics_service_provider(
    config: Annotated[AppConfig, Depends(app_config_provider)],
    engine: Annotated[AsyncEngine, Depends(create_async_engine)],
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(create_async_session_maker)
    ],
) -> MetricsService:
    _logger.debug("Creating Metrics Service")
    await a_create_all(engine, APIMetricsBase)
    return MetricsService(
        config=config.quotas,
        session_maker=session_maker,
    )


api_key_header = APIKeyHeader(name="findflow-token", auto_error=True)


async def validate_api_key_header(
    config: Annotated[AppConfig, Depends(app_config_provider)],
    api_key: str = Security(api_key_header),
) -> str:
    if api_key not in config.get_api_keys:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return api_key


@singleton
def cloud_auth_service(
    config: Annotated[AppConfig, Depends(app_config_provider)]
) -> CloudAuthService:
    _logger.debug("Creating Cloud Auth Service")
    match config.storage.cloud_provider:
        case CloudProvider.AWS:
            return AWSAuthService(
                user_pool_id=config.auth.user_pool_id,
                cognito_client=get_cognito_client(),
            )
        case CloudProvider.GCP:
            try:
                _fire_app = firebase_admin.get_app()
            except ValueError:
                _fire_app = firebase_admin.initialize_app()
            return GCPAuthService(firebase_admin_app=_fire_app)
        case _:
            raise ValueError(f"Unknown cloud provider: {config.storage.cloud_provider}")


async def users_service(
    engine: Annotated[AsyncEngine, Depends(create_async_engine)],
    session_maker: Annotated[
        async_sessionmaker[AsyncSession],
        Depends(create_async_session_maker),
    ],
) -> UsersService:
    _logger.debug("Creating Users Service")
    await a_create_all(engine, UsersBase)
    return UsersService(session_maker=session_maker)


async def documents_service_provider(
    engine: Annotated[AsyncEngine, Depends(create_async_engine)],
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(create_async_session_maker)
    ],
) -> DocumentsService:
    _logger.debug("Creating Documents Service")
    await a_create_all(engine, DocumentsBase)
    return DocumentsService(session_maker=session_maker)


async def departments_service(
    engine: Annotated[AsyncEngine, Depends(create_async_engine)],
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(create_async_session_maker)
    ],
    documents_service: Annotated[DocumentsService, Depends(documents_service_provider)],
) -> DepartmentsService:
    _logger.debug("Creating Departments Service")
    await a_create_all(engine, DepartmentsBase)
    return DepartmentsService(
        session_maker=session_maker, documents_service=documents_service
    )
