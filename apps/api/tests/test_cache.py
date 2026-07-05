"""Tests for API cache module."""

import time
from agentverse.api.core.cache import LRUCache


def test_cache_set_and_get():
    """Test basic set and get operations."""
    cache = LRUCache(max_size=10, ttl_seconds=60)
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


def test_cache_miss():
    """Test cache miss returns None."""
    cache = LRUCache(max_size=10, ttl_seconds=60)
    assert cache.get("nonexistent") is None


def test_cache_ttl_expiry():
    """Test that values expire after TTL."""
    cache = LRUCache(max_size=10, ttl_seconds=0.001)  # 1ms TTL
    cache.set("key1", "value1")
    time.sleep(0.05)  # Wait > 1ms
    assert cache.get("key1") is None


def test_cache_lru_eviction():
    """Test LRU eviction when cache is full."""
    cache = LRUCache(max_size=3, ttl_seconds=60)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    cache.set("d", 4)  # Should evict "a"
    assert cache.get("a") is None
    assert cache.get("d") == 4


def test_cache_lru_order():
    """Test that accessing a key moves it to most recently used."""
    cache = LRUCache(max_size=3, ttl_seconds=60)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    cache.get("a")  # Access "a" to make it most recent
    cache.set("d", 4)  # Should evict "b" (least recently used)
    assert cache.get("a") == 1
    assert cache.get("b") is None


def test_cache_delete():
    """Test delete operation."""
    cache = LRUCache(max_size=10, ttl_seconds=60)
    cache.set("key1", "value1")
    cache.delete("key1")
    assert cache.get("key1") is None


def test_cache_clear():
    """Test clear operation."""
    cache = LRUCache(max_size=10, ttl_seconds=60)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.clear()
    assert cache.get("a") is None
    assert cache.get("b") is None


def test_cache_stats():
    """Test cache statistics."""
    cache = LRUCache(max_size=100, ttl_seconds=300)
    cache.set("a", 1)
    stats = cache.stats()
    assert stats["size"] == 1
    assert stats["max_size"] == 100
    assert stats["ttl_seconds"] == 300


def test_cache_overwrite():
    """Test overwriting an existing key."""
    cache = LRUCache(max_size=10, ttl_seconds=60)
    cache.set("key1", "old")
    cache.set("key1", "new")
    assert cache.get("key1") == "new"