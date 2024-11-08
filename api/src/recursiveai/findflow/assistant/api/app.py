# Copyright 2024 Recursive AI

import importlib.metadata
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from .app_context import app_config, exception_handler
from .routers import (
    blocked_keywords,
    conversations,
    health_checks,
    organisations,
    user_groups,
    users,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await app_config()
    yield


def run_app() -> FastAPI:
    return create_app(lifespan_context=lifespan)


def create_app(lifespan_context=None) -> FastAPI:
    version = importlib.metadata.version("recursiveai-findflow-assistant")
    app = FastAPI(
        title="FindFlow Assistant API",
        version=version,
        redoc_url=None,
        lifespan=lifespan_context,
    )

    # TODO: Should be disabled for stream endpoints or client side tweak
    app.add_middleware(GZipMiddleware)

    # TODO: Load from configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(organisations.router)
    app.include_router(users.router)
    app.include_router(user_groups.router)
    app.include_router(health_checks.router)

    app.include_router(conversations.router)
    app.include_router(blocked_keywords.router)

    app.add_exception_handler(
        Exception,
        exception_handler,
    )

    return app
