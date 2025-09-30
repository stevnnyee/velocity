"""
Tests for VelocityCache core functionality.

Comprehensive test suite covering all operations, edge cases, and performance characteristics.
All tests are deterministic - no timing dependencies.
"""
import pytest
import threading
import time
from cache.core import VelocityCache


class TestBasicOperations:
    """Test fundamental cache operations."""
    
    def test_get_set_delete(self):
        """Test basic get/set/delete operations."""
        cache = VelocityCache()
        
        # Test set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Test get non-existent key
        assert cache.get("nonexistent") is None
        
        # Test delete existing key
        assert cache.delete("key1") == "value1"
        assert cache.get("key1") is None
        
        # Test delete non-existent key
        assert cache.delete("nonexistent") is None
    
    def test_update_existing_key(self):
        """Test updating value for existing key."""
        cache = VelocityCache(max_size=2)
        
        cache.set("key1", "old_value")
        cache.set("key2", "value2")
        
        # Update existing key - should not trigger eviction
        cache.set("key1", "new_value")
        
        assert cache.size() == 2
        assert cache.get("key1") == "new_value"
        assert cache.get("key2") == "value2"
    
    def test_size_and_clear(self):
        """Test size tracking and clear functionality."""
        cache = VelocityCache()
        
        assert cache.size() == 0
        assert len(cache) == 0  # Test __len__
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        assert cache.size() == 2
        assert len(cache) == 2
        
        cache.clear()
        assert cache.size() == 0
        assert cache.get("key1") is None
    
    def test_contains(self):
        """Test __contains__ method."""
        cache = VelocityCache()
        
        assert "key1" not in cache
        
        cache.set("key1", "value1")
        assert "key1" in cache
        
        cache.delete("key1")
        assert "key1" not in cache


class TestLRUEviction:
    """Test LRU eviction behavior."""
    
    def test_lru_eviction_deterministic(self):
        """Test LRU eviction without timing dependencies."""
        cache = VelocityCache(max_size=3)
        
        # Fill cache to capacity
        cache.set("first", 1)
        cache.set("second", 2)
        cache.set("third", 3)
        
        assert cache.size() == 3
        
        # Access first item to make it recently used
        cache.get("first")
        
        # Add fourth item - should evict second (oldest unaccessed)
        cache.set("fourth", 4)
        
        assert cache.size() == 3
        assert cache.get("first") == 1      # Still there (recently accessed)
        assert cache.get("second") is None  # Evicted (oldest)
        assert cache.get("third") == 3      # Still there
        assert cache.get("fourth") == 4     # New item
    
    def test_lru_order_tracking(self):
        """Test that LRU order is maintained correctly."""
        cache = VelocityCache(max_size=3)
        
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        
        # Initial order: a, b, c (a is oldest)
        assert cache.keys() == ["a", "b", "c"]
        
        # Access 'a' - should move to end
        cache.get("a")
        assert cache.keys() == ["b", "c", "a"]
        
        # Update 'b' - should move to end
        cache.set("b", 22)
        assert cache.keys() == ["c", "a", "b"]
    
    def test_eviction_on_capacity(self):
        """Test eviction behavior when at capacity."""
        cache = VelocityCache(max_size=2)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Cache is at capacity
        assert cache.size() == 2
        
        # Adding new key should evict oldest
        cache.set("key3", "value3")
        
        assert cache.size() == 2
        assert cache.get("key1") is None    # Evicted
        assert cache.get("key2") == "value2"  # Still there
        assert cache.get("key3") == "value3"  # New key
    
    def test_no_eviction_on_update(self):
        """Test that updating existing key doesn't trigger eviction."""
        cache = VelocityCache(max_size=2)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Update existing key
        cache.set("key1", "updated_value")
        
        # Both keys should still be present
        assert cache.size() == 2
        assert cache.get("key1") == "updated_value"
        assert cache.get("key2") == "value2"


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_invalid_max_size(self):
        """Test that invalid max_size raises error."""
        with pytest.raises(ValueError, match="max_size must be positive"):
            VelocityCache(max_size=0)
        
        with pytest.raises(ValueError, match="max_size must be positive"):
            VelocityCache(max_size=-1)
    
    def test_empty_cache_operations(self):
        """Test operations on empty cache."""
        cache = VelocityCache()
        
        assert cache.get("any_key") is None
        assert cache.delete("any_key") is None
        assert cache.size() == 0
        assert cache.keys() == []
        
        # Clear empty cache should work
        cache.clear()
        assert cache.size() == 0
    
    def test_single_item_cache(self):
        """Test cache with max_size=1."""
        cache = VelocityCache(max_size=1)
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Adding second item should evict first
        cache.set("key2", "value2")
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.size() == 1
    
    def test_large_values(self):
        """Test cache with various data types."""
        cache = VelocityCache()
        
        # Test different value types
        cache.set("string", "hello")
        cache.set("number", 42)
        cache.set("list", [1, 2, 3])
        cache.set("dict", {"a": 1, "b": 2})
        cache.set("none", None)
        
        assert cache.get("string") == "hello"
        assert cache.get("number") == 42
        assert cache.get("list") == [1, 2, 3]
        assert cache.get("dict") == {"a": 1, "b": 2}
        assert cache.get("none") is None


class TestThreadSafety:
    """Test thread safety of cache operations."""
    
    def test_concurrent_access(self):
        """Test concurrent reads and writes."""
        cache = VelocityCache(max_size=100)
        results = []
        errors = []
        
        def worker(thread_id: int):
            try:
                for i in range(50):
                    key = f"key_{thread_id}_{i}"
                    value = f"value_{thread_id}_{i}"
                    
                    cache.set(key, value)
                    retrieved = cache.get(key)
                    
                    if retrieved == value:
                        results.append(True)
                    else:
                        results.append(False)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert all(results), "Some operations failed"
        assert len(results) == 250  # 5 threads * 50 operations each
    
    def test_size_consistency(self):
        """Test that size() is always consistent."""
        cache = VelocityCache(max_size=10)
        
        def add_items():
            for i in range(20):
                cache.set(f"key_{i}", f"value_{i}")
        
        def check_size():
            for _ in range(100):
                size = cache.size()
                assert 0 <= size <= 10, f"Size {size} out of bounds"
        
        # Start threads
        adder = threading.Thread(target=add_items)
        checker = threading.Thread(target=check_size)
        
        adder.start()
        checker.start()
        
        adder.join()
        checker.join()


class TestPerformance:
    """Test performance characteristics."""
    
    def test_operations_are_fast(self):
        """Test that operations complete quickly even with large cache."""
        cache = VelocityCache(max_size=10000)
        
        # Fill cache
        start_time = time.time()
        for i in range(10000):
            cache.set(f"key_{i}", f"value_{i}")
        fill_time = time.time() - start_time
        
        # Test gets are fast
        start_time = time.time()
        for i in range(1000):
            cache.get(f"key_{i}")
        get_time = time.time() - start_time
        
        # Test eviction is fast
        start_time = time.time()
        for i in range(1000):
            cache.set(f"new_key_{i}", f"new_value_{i}")
        evict_time = time.time() - start_time
        
        # These should all be very fast (< 1 second each)
        assert fill_time < 1.0, f"Fill took too long: {fill_time}s"
        assert get_time < 0.1, f"Gets took too long: {get_time}s"
        assert evict_time < 0.5, f"Eviction took too long: {evict_time}s"
    
    def test_memory_efficiency(self):
        """Test that cache doesn't use excessive memory."""
        cache = VelocityCache(max_size=1000)
        
        # Fill cache completely
        for i in range(1000):
            cache.set(f"key_{i}", f"value_{i}")
        
        assert cache.size() == 1000
        
        # Add more items - size should stay constant
        for i in range(100):
            cache.set(f"extra_key_{i}", f"extra_value_{i}")
        
        assert cache.size() == 1000  # Should not exceed max_size