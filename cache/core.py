"""
VelocityCache: Production-grade in-memory key-value store with O(1) LRU eviction.

Uses OrderedDict for efficient LRU implementation - all operations are O(1).
Thread-safe with proper locking on all shared state access.
"""
from collections import OrderedDict
import threading
from typing import Any, Optional


class VelocityCache:
    """Thread-safe in-memory cache with O(1) LRU eviction.
    
    All operations (get, set, delete) are O(1) time complexity.
    Uses OrderedDict internally for efficient LRU tracking.
    """
    
    def __init__(self, max_size: int = 1000):
        """Initialize cache with maximum size.
        
        Args:
            max_size: Maximum number of items to store. Must be positive.
            
        Raises:
            ValueError: If max_size is not positive.
        """
        if max_size <= 0:
            raise ValueError("max_size must be positive")
            
        # OrderedDict is a dictionary that remembers the order of the keys
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._max_size = max_size
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value by key. Updates LRU order.
        
        Args:
            key: The key to look up.
            
        Returns:
            The value if key exists, None otherwise.
            
        Time Complexity: O(1)
        """
        with self._lock:
            if key not in self._cache:
                return None
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return self._cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """Set key-value pair. Evicts oldest item if at capacity.
        
        Args:
            key: The key to store.
            value: The value to associate with key.
            
        Time Complexity: O(1)
        """
        with self._lock:
            if key in self._cache:
                # Update existing key
                self._cache[key] = value
                self._cache.move_to_end(key)
            else:
                # Add new key
                if len(self._cache) >= self._max_size:
                    # Remove least recently used (first item)
                    self._cache.popitem(last=False)
                self._cache[key] = value
    
    def delete(self, key: str) -> Optional[Any]:
        """Delete key and return its value.
        
        Args:
            key: The key to delete.
            
        Returns:
            The deleted value if key existed, None otherwise.
            
        Time Complexity: O(1)
        """
        with self._lock:
            return self._cache.pop(key, None)
    
    def size(self) -> int:
        """Return number of items in cache.
        
        Returns:
            Current number of cached items.
            
        Time Complexity: O(1)
        """
        with self._lock:
            return len(self._cache)
    
    def clear(self) -> None:
        """Remove all items from cache.
        
        Time Complexity: O(1)
        """
        with self._lock:
            self._cache.clear()
    
    def keys(self) -> list[str]:
        """Return list of all keys in LRU order (oldest first).
        
        Returns:
            List of keys from least to most recently used.
            
        Time Complexity: O(n)
        """
        with self._lock:
            return list(self._cache.keys())
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache without updating LRU order.
        
        Args:
            key: The key to check.
            
        Returns:
            True if key exists, False otherwise.
            
        Time Complexity: O(1)
        """
        with self._lock:
            return key in self._cache
    
    def __len__(self) -> int:
        """Return number of items in cache.
        
        Returns:
            Current number of cached items.
        """
        return self.size()