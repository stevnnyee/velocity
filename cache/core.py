"""
VelocityCache: Production-grade in-memory key-value store with O(1) LRU eviction.

Uses OrderedDict for efficient LRU implementation - all operations are O(1).
Thread-safe with proper locking on all shared state access.
"""

from collections import OrderedDict
import threading
import time
from typing import Any, Optional, Tuple


class VelocityCache:
    """Thread-safe in-memory cache with O(1) LRU eviction and TTL support.

    All operations (get, set, delete) are O(1) time complexity.
    Uses OrderedDict internally for efficient LRU tracking.
    Supports automatic expiration via TTL (time-to-live).

    Example:
        >>> cache = VelocityCache(max_size=1000)
        >>> cache.set("BTC-USD", 43250.12, ttl=5)
        >>> price = cache.get("BTC-USD")
        >>> print(cache.stats())
    """

    def __init__(self, max_size: int = 1000):
        """Initialize cache with maximum size and metrics tracking.

        Args:
            max_size: Maximum number of items to store. Must be positive.

        Raises:
            ValueError: If max_size is not positive.
        """
        if max_size <= 0:
            raise ValueError("max_size must be positive")

        # OrderedDict stores (value, expiry_time) tuples
        # expiry_time is None for no expiration, or Unix timestamp for TTL
        self._cache: OrderedDict[str, Tuple[Any, Optional[float]]] = OrderedDict()
        self._max_size = max_size
        self._lock = threading.RLock()

        # Metrics tracking
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._expirations = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value by key. Updates LRU order and checks expiration.

        Args:
            key: The key to look up.

        Returns:
            The value if key exists and not expired, None otherwise.

        Raises:
            ValueError: If key is empty.

        Time Complexity: O(1)
        """
        if not key:
            raise ValueError("Key cannot be empty")

        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            value, expiry_time = self._cache[key]

            # Check if expired
            if expiry_time is not None and time.time() > expiry_time:
                del self._cache[key]
                self._misses += 1
                self._expirations += 1
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set key-value pair with optional TTL. Evicts oldest item if at capacity.

        Args:
            key: The key to store. Must be non-empty.
            value: The value to associate with key.
            ttl: Time to live in seconds. Must be non-negative if provided.

        Raises:
            ValueError: If key is empty or TTL is negative.

        Time Complexity: O(1)
        """
        if not key:
            raise ValueError("Key cannot be empty")

        if ttl is not None and ttl < 0:
            raise ValueError(f"TTL must be non-negative, got {ttl}")

        with self._lock:
            # Calculate expiry time if TTL provided
            expiry_time = None
            if ttl is not None:
                expiry_time = time.time() + ttl

            if key in self._cache:
                # Update existing key
                self._cache[key] = (value, expiry_time)
                self._cache.move_to_end(key)
            else:
                # Add new key
                if len(self._cache) >= self._max_size:
                    # Remove least recently used (first item)
                    self._cache.popitem(last=False)
                    self._evictions += 1
                self._cache[key] = (value, expiry_time)

    def delete(self, key: str) -> Optional[Any]:
        """Delete key and return its value.

        Args:
            key: The key to delete.

        Returns:
            The deleted value if key existed and not expired, None otherwise.

        Raises:
            ValueError: If key is empty.

        Time Complexity: O(1)
        """
        if not key:
            raise ValueError("Key cannot be empty")

        with self._lock:
            item = self._cache.pop(key, None)
            if item is None:
                return None

            value, expiry_time = item

            # If it was already expired, count it
            if expiry_time is not None and time.time() > expiry_time:
                self._expirations += 1
                return None

            return value

    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired.

        Unlike __contains__, this method checks expiration.

        Args:
            key: The key to check.

        Returns:
            True if key exists and not expired, False otherwise.

        Time Complexity: O(1)
        """
        if not key:
            return False

        with self._lock:
            if key not in self._cache:
                return False

            value, expiry_time = self._cache[key]

            # Check if expired
            if expiry_time is not None and time.time() > expiry_time:
                del self._cache[key]
                self._expirations += 1
                return False

            return True

    def size(self) -> int:
        """Return number of items in cache (including expired not yet checked).

        Returns:
            Current number of cached items.

        Time Complexity: O(1)
        """
        with self._lock:
            return len(self._cache)

    def clear(self) -> None:
        """Remove all items from cache. Metrics are not reset.

        Time Complexity: O(1)
        """
        with self._lock:
            self._cache.clear()

    def keys(self) -> list[str]:
        """Return list of all keys in LRU order (oldest first).

        Note: May include expired keys that haven't been accessed yet.

        Returns:
            List of keys from least to most recently used.

        Time Complexity: O(n)
        """
        with self._lock:
            return list(self._cache.keys())

    def stats(self) -> dict:
        """Return cache performance statistics.

        Returns:
            Dictionary with hit rate, operation counts, and cache size.
        """
        with self._lock:
            total_ops = self._hits + self._misses
            hit_rate = (self._hits / total_ops * 100) if total_ops > 0 else 0.0

            return {
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "expirations": self._expirations,
                "hit_rate": f"{hit_rate:.2f}%",
                "size": len(self._cache),
                "max_size": self._max_size,
            }

    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache without updating LRU order.

        Note: Does not check expiration for performance. Use exists() for that.

        Args:
            key: The key to check.

        Returns:
            True if key exists in cache dict, False otherwise.

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
