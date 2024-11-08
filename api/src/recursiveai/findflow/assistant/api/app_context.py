# Copyright 2024 Recursive AI

import logging
from typing import Annotated, AsyncGenerator

from fastapi import Depends, Header, HTTPException, Request, Security, status
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from ..common.auths import create_auth_service
from ..common.auths.base_auth import AuthService
from ..common.database import (
    create_async_engine_provider,
    create_async_session_provider,
)
from ..common.dependencies import async_singleton, singleton
from ..common.exceptions import AlreadyExistsError, DoesNotExistError
from .app_config import AppConfig
from .services.blocked_keywords import BlockedKeywordsService
from .services.conversations import ConversationsService
from .services.organisations import OrganisationsService
from .services.user_groups import UserGroupsService
from .services.users import UsersService

_logger = logging.getLogger(__name__)


@singleton
def app_config() -> AppConfig:
    _logger.debug("Creating AppConfig")
    config = AppConfig()

    _logger.info("AppConfig: '%s'", config.model_dump_json(indent=4))
    return config


async def exception_handler(request: Request, exception: Exception):
    match exception:
        case DoesNotExistError():
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content=exception.message
            )
        case AlreadyExistsError():
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=exception.message,
            )
        case _:
            _logger.error("Unexpected exception", exc_info=exception)
            return JSONResponse(
                status_code=500,
                content="Unexpected exception",
            )


@async_singleton
async def async_engine(
    config: Annotated[AppConfig, Depends(app_config)],
) -> AsyncEngine:
    _logger.debug("Creating Async Engine")
    return await create_async_engine_provider(config.database)


@singleton
def async_session_provider(
    engine: Annotated[AsyncEngine, Depends(async_engine)],
) -> async_sessionmaker[AsyncSession]:
    _logger.debug("Creating Async Session Provider")
    return create_async_session_provider(engine)


async def async_session(
    session_provider: Annotated[
        async_sessionmaker[AsyncSession],
        Depends(async_session_provider),
    ],
) -> AsyncGenerator[AsyncSession, None]:
    session = session_provider()
    _logger.debug("Creating Async Session ID:[%s]", id(session))
    try:
        yield session
    finally:
        _logger.debug("Closing Async Session: ID:[%s]", id(session))
        await session.close()


@singleton
def auth_service(app_config: Annotated[AppConfig, Depends(app_config)]) -> AuthService:
    _logger.debug("Creating Auth Service")
    return create_auth_service(app_config.auth)


@singleton
def organisations_service(
    session_provider: Annotated[
        async_sessionmaker[AsyncSession], Depends(async_session_provider)
    ],
) -> OrganisationsService:
    _logger.debug("Creating Organisations Service")
    return OrganisationsService(session_provider)


@singleton
def users_service(
    session_provider: Annotated[
        async_sessionmaker[AsyncSession], Depends(async_session_provider)
    ],
    auth_service: Annotated[AuthService, Depends(auth_service)],
) -> UsersService:
    _logger.debug("Creating Users Service")
    return UsersService(session_provider, auth_service)


@singleton
def user_groups_service(
    session_provider: Annotated[
        async_sessionmaker[AsyncSession], Depends(async_session_provider)
    ],
) -> UserGroupsService:
    _logger.debug("Creating User Groups Service")
    return UserGroupsService(session_provider)


@singleton
def blocked_keywords_service(
    session_provider: Annotated[
        async_sessionmaker[AsyncSession], Depends(async_session_provider)
    ],
) -> BlockedKeywordsService:
    _logger.debug("Creating Blocked Keywords Service")
    return BlockedKeywordsService(session_provider)


@singleton
def conversations_service(
    session_provider: Annotated[
        async_sessionmaker[AsyncSession], Depends(async_session_provider)
    ],
) -> ConversationsService:
    _logger.debug("Creating Conversations Service")
    return ConversationsService(session_provider)


async def jwt_auth(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(HTTPBearer(auto_error=False))],
    auth_service: Annotated[AuthService, Depends(auth_service)],
) -> str | None:
    if credentials:
        return auth_service.validate_user_token(credentials.credentials)


async def api_key_auth(
    api_key: Annotated[str, Security(APIKeyHeader(name="X-API-Key", auto_error=False))],
    config: Annotated[AppConfig, Depends(app_config)],
) -> str | None:
    if api_key and api_key == config.api_key.get_secret_value():
        return "asdf"


async def get_user_id(
    jwt_user_id: Annotated[str | None, Security(jwt_auth)],
    api_key_user_id: Annotated[str | None, Security(api_key_auth)],
) -> str:
    if not (api_key_user_id or jwt_user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )

    return jwt_user_id or api_key_user_id

# user_token_header = OAuth2(auto_error=False)

# async def validate_user_token_header(
#     user_token: Annotated[str, Depends(user_token_header)],

# ) -> str:
#     if api_key not in config.get_api_keys:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
#     return api_key

# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except InvalidTokenError:
#         raise credentials_exception
#     user = get_user(fake_users_db, username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user
