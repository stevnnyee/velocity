"""Tests for VelocityCache core functionality."""
import pytest
import time
from cache.core import VelocityCache


def test_basic_get_set():
    """Test basic get/set operations without TTL."""
    cache = VelocityCache(max_size=100)
    
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"
    
    cache.set("key1", "value2")
    assert cache.get("key1") == "value2"


def test_get_missing_key():
    """Test getting non-existent key returns None."""
    cache = VelocityCache(max_size=100)
    assert cache.get("missing") is None


def test_ttl_expiration():
    """Test that keys expire after TTL."""
    cache = VelocityCache(max_size=100)
    
    # Set with 0.1 second TTL (100ms)
    cache.set("key1", "value1", ttl=0.1)
    
    # Should exist immediately
    assert cache.get("key1") == "value1"
    
    # Wait for expiration
    time.sleep(0.15)
    
    # Should be gone
    assert cache.get("key1") is None


def test_ttl_none_means_no_expiration():
    """Test that ttl=None means never expires."""
    cache = VelocityCache(max_size=100)
    
    cache.set("key1", "value1", ttl=None)
    time.sleep(0.2)
    
    # Should still exist
    assert cache.get("key1") == "value1"


def test_lru_eviction():
    """Test LRU eviction when cache is full."""
    cache = VelocityCache(max_size=3)
    
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    
    # Access 'a' to make it recently used
    cache.get("a")
    
    # Add 'd' - should evict 'b' (least recently used)
    cache.set("d", 4)
    
    assert cache.get("a") == 1
    assert cache.get("b") is None  # Evicted
    assert cache.get("c") == 3
    assert cache.get("d") == 4


def test_metrics_hits_and_misses():
    """Test hit and miss counting."""
    cache = VelocityCache(max_size=100)
    
    cache.set("key1", "value1")
    
    # Two hits
    cache.get("key1")
    cache.get("key1")
    
    # One miss
    cache.get("missing")
    
    stats = cache.stats()
    assert stats["hits"] == 2
    assert stats["misses"] == 1
    assert stats["hit_rate"] == "66.67%"


def test_metrics_evictions():
    """Test eviction counting."""
    cache = VelocityCache(max_size=2)
    
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)  # Should evict 'a'
    
    stats = cache.stats()
    assert stats["evictions"] == 1


def test_metrics_expirations():
    """Test expiration counting."""
    cache = VelocityCache(max_size=100)
    
    cache.set("key1", "value1", ttl=0.1)
    time.sleep(0.15)
    
    # Access expired key
    cache.get("key1")
    
    stats = cache.stats()
    assert stats["expirations"] == 1
    assert stats["misses"] == 1


def test_exists_method():
    """Test exists() method checks expiration."""
    cache = VelocityCache(max_size=100)
    
    cache.set("key1", "value1")
    assert cache.exists("key1") is True
    
    assert cache.exists("missing") is False
    
    # Test with expiration
    cache.set("key2", "value2", ttl=0.1)
    assert cache.exists("key2") is True
    
    time.sleep(0.15)
    assert cache.exists("key2") is False


def test_contains_vs_exists():
    """Test that __contains__ doesn't check expiration but exists() does."""
    cache = VelocityCache(max_size=100)
    
    cache.set("key1", "value1", ttl=0.1)
    
    # Both should be true initially
    assert "key1" in cache
    assert cache.exists("key1") is True
    
    time.sleep(0.15)
    
    # __contains__ doesn't check expiration (still True)
    assert "key1" in cache
    
    # exists() checks expiration (now False)
    assert cache.exists("key1") is False


def test_delete_returns_value():
    """Test delete returns the value."""
    cache = VelocityCache(max_size=100)
    
    cache.set("key1", "value1")
    assert cache.delete("key1") == "value1"
    assert cache.get("key1") is None


def test_delete_missing_returns_none():
    """Test deleting non-existent key returns None."""
    cache = VelocityCache(max_size=100)
    assert cache.delete("missing") is None


def test_delete_expired_key():
    """Test deleting expired key returns None and counts expiration."""
    cache = VelocityCache(max_size=100)
    
    cache.set("key1", "value1", ttl=0.1)
    time.sleep(0.15)
    
    result = cache.delete("key1")
    assert result is None
    
    stats = cache.stats()
    assert stats["expirations"] == 1


def test_clear():
    """Test clearing cache."""
    cache = VelocityCache(max_size=100)
    
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.get("key1")  # Generate some stats
    
    cache.clear()
    
    assert cache.size() == 0
    assert cache.get("key1") is None
    
    # Stats should persist after clear
    stats = cache.stats()
    assert stats["hits"] == 1


def test_thread_safety():
    """Test concurrent access from multiple threads."""
    import threading
    
    cache = VelocityCache(max_size=1000)
    errors = []
    
    def worker(thread_id):
        try:
            for i in range(100):
                cache.set(f"key_{thread_id}_{i}", f"value_{i}")
                cache.get(f"key_{thread_id}_{i}")
        except Exception as e:
            errors.append(e)
    
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert len(errors) == 0
    assert cache.size() <= 1000


def test_stats_with_no_operations():
    """Test stats() with no operations returns zeros."""
    cache = VelocityCache(max_size=100)
    
    stats = cache.stats()
    assert stats["hits"] == 0
    assert stats["misses"] == 0
    assert stats["hit_rate"] == "0.00%"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])