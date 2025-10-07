# VelocityCache 🚀

A high-performance, thread-safe in-memory cache with TTL support and LRU eviction.

## Features

- ✅ **TTL Support** - Automatic expiration with configurable time-to-live
- ✅ **LRU Eviction** - O(1) least-recently-used eviction when cache is full
- ✅ **Thread-Safe** - Concurrent access from multiple threads
- ✅ **Metrics Tracking** - Hit/miss rates, evictions, expirations
- ✅ **High Performance** - 1M+ operations per second

## Quick Start

```bash
# Activate environment
./runvelo

# Run demo
python main.py demo

# Run tests
python main.py test

# Run benchmarks
python main.py benchmark

# Run everything
python main.py all
```

## Usage

```python
from cache.core import VelocityCache

# Create cache
cache = VelocityCache(max_size=1000)

# Set with TTL (5 seconds)
cache.set("BTC-USD", 43250.12, ttl=5)

# Get value
price = cache.get("BTC-USD")

# Check if key exists (checks expiration)
if cache.exists("BTC-USD"):
    print("Key is valid and not expired")

# Get performance stats
stats = cache.stats()
print(f"Hit rate: {stats['hit_rate']}")
```

## API

### Core Methods

- `set(key, value, ttl=None)` - Store key-value pair with optional TTL
- `get(key)` - Retrieve value (returns None if expired/missing)
- `delete(key)` - Remove key and return its value
- `exists(key)` - Check if key exists and is not expired
- `clear()` - Remove all items from cache

### Utility Methods

- `stats()` - Get performance metrics
- `size()` - Get current number of items
- `keys()` - Get list of all keys (LRU order)

## Performance

**Benchmark Results:**
- SET Operations: 906,355 ops/sec
- GET Operations: 1,530,221 ops/sec  
- Mixed Operations: 1,344,854 ops/sec
- **Overall: 1,112,023 ops/sec** (37x target!)

## Project Structure

```
velocity/
├── cache/
│   └── core.py              # Main VelocityCache implementation
├── tests/
│   ├── unit/
│   │   └── test_cache_core.py  # Test suite (16 tests)
│   └── benchmark_performance.py # Performance benchmarks
├── main.py                  # Entry point for demo/tests/benchmarks
├── runvelo                  # Environment activation script
└── README.md
```

## Week 1 Complete ✅

- TTL support with lazy expiration
- Comprehensive metrics tracking
- Thread-safe operations
- 16 focused tests (all passing)
- Performance benchmarks (1M+ ops/sec)
- Clean project structure with main entry point

**Ready for Week 2: Data Structures (Lists & Sets)**
