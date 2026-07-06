"""TypedDict definitions for extractor data structures."""

from typing import TypedDict


class ExtractionRequest(TypedDict, total=False):
    """Typed request parameters for extractor.extract() methods.

    All fields are optional. Each extractor extracts the subset it supports
    and ignores the rest.
    """
    text: str
    source: str
    max_concepts: int
    categories: list[str]
