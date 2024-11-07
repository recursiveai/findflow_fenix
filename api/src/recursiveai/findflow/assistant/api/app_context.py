# Copyright 2024 Recursive AI

import logging
from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
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
from .services.organisations import OrganisationsService
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
            return JSONResponse(status_code=404, content=exception.message)
        case AlreadyExistsError():
            return JSONResponse(
                status_code=409,
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


# api_key_header = APIKeyHeader(name="api-key", auto_error=True)
# user_id_header = Header(name="user-id", auto_error=True)

# async def validate_api_key_header(
#     api_key: Annotated[str, Depends(api_key_header)],
#     user_id: Annotated[str, Depends(user_id_header)],
# ) -> str:
#     if api_key not in config.get_api_keys:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
#     return api_key


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
