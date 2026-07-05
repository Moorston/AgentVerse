"""Paginated response model."""

from typing import Any, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    page: int
    size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: list[Any]
    meta: PaginationMeta

    @classmethod
    def create(cls, items: list[Any], page: int, size: int, total: int) -> "PaginatedResponse":
        """Create a paginated response.

        Args:
            items: List of items for current page.
            page: Current page number (1-based).
            size: Items per page.
            total: Total number of items.
        """
        total_pages = (total + size - 1) // size if size > 0 else 0
        return cls(
            items=items,
            meta=PaginationMeta(
                page=page,
                size=size,
                total=total,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1,
            ),
        )