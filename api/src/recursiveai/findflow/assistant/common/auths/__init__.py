# Copyright 2024 Recursive AI

import logging

from .base_auth import AuthService, DummyAuthConfig, DummyAuthService
from .gcp_auth import GCPAuthConfig, GCPAuthService

_logger = logging.getLogger(__name__)

AuthConfig = DummyAuthConfig | GCPAuthConfig


def create_auth_service(auth_config: AuthConfig) -> AuthService:
    _logger.debug("Creating Auth Service")
    match auth_config:
        case GCPAuthConfig():
            return GCPAuthService(auth_config)
        case DummyAuthConfig():
            return DummyAuthService()
