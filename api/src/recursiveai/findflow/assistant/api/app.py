# Copyright 2024 Recursive AI

import importlib.metadata
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from .app_context import app_config_provider
from .routers import health_checks, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await app_config_provider()
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

    app.add_middleware(GZipMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://www.website.com"],
        allow_methods=["POST"],
        allow_headers=["*"],
    )

    app.include_router(users.router)
    app.include_router(health_checks.router)
    return app