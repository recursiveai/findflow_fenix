# Copyright 2024 Recursive AI

from typing import Generic, Iterable, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    data: Iterable[T]
    page: int
    page_size: int
    total: int
