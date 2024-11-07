# Copyright 2024 Recursive AI

import asyncio
import functools
import logging
from contextlib import contextmanager
from typing import Awaitable, Callable, ParamSpec, TypeVar

_logger = logging.getLogger(__name__)

T = TypeVar("T")
Provider = Callable[[], T]
ProviderFactory = Provider[Provider[T]]
AsyncProvider = Callable[[], Awaitable[T]]
AsyncProviderFactory = Provider[AsyncProvider[T]]

F = TypeVar("F")
P = ParamSpec("P")

_store_registry = {}


@contextmanager
def empty_store_registry():
    global _store_registry  # pylint: disable=global-statement
    backup = _store_registry
    _store_registry = {}
    try:
        yield None
    finally:
        _store_registry = backup


def singleton(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    lock = asyncio.Lock()

    @functools.wraps(func)
    async def singleton_decorator(*args, **kwargs) -> T:
        async with lock:
            if func not in _store_registry:
                _logger.debug("Creating Singleton %s", func.__name__)
                _store_registry[func] = func(*args, **kwargs)
            else:
                _logger.debug("Reusing Singleton %s", func.__name__)
        return _store_registry[func]

    return singleton_decorator


def async_singleton(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    lock = asyncio.Lock()

    @functools.wraps(func)
    async def singleton_decorator(*args, **kwargs) -> T:
        async with lock:
            if func not in _store_registry:
                _logger.debug("Creating AsyncSingleton %s", func.__name__)
                _store_registry[func] = await func(*args, **kwargs)
            else:
                _logger.debug("Reusing Async Singleton %s", func.__name__)
        return _store_registry[func]

    return singleton_decorator
