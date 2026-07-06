"""TypedDict definitions for crawler data structures."""

from typing import NotRequired, TypedDict


class PaperDict(TypedDict, total=False):
    title: str
    authors: list[str]
    abstract: str
    arxiv_id: str
    doi: str
    published_date: str
    categories: list[str]
    updated: str


class RepoDict(TypedDict, total=False):
    name: str
    full_name: str
    description: str
    html_url: str
    stargazers_count: int
    forks_count: int
    language: str
    topics: list[str]
    updated_at: str


class NewsItemDict(TypedDict, total=False):
    title: str
    description: str
    link: str
    source: str
    published_date: str


class PaperS2Dict(TypedDict, total=False):
    paper_id: str
    title: str
    abstract: str
    authors: list[str]
    year: int
    citation_count: int
    influential_citation_count: int
    arxiv_id: str
    reference_count: int


class CrawlRequest(TypedDict, total=False):
    """Typed request parameters for crawler.crawl() methods.

    All fields are optional. Each crawler extracts the subset it supports
    and ignores the rest.
    """
    query: str
    max_results: int
    categories: list[str]
    since: str
    arxiv_ids: list[str]
    search_query: str