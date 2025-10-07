"""
Performance benchmarks for VelocityCache.

Target: 30,000+ operations per second
Run with: python -m tests.benchmark_performance
"""

import time
import logging as std_logging
from cache.core import VelocityCache

# Configure logging
std_logging.basicConfig(
    level=std_logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logging = std_logging.getLogger(__name__)


def benchmark_set_operations(cache_size=10000, operations=50000):
    """Benchmark SET operations with TTL."""
    cache = VelocityCache(max_size=cache_size)

    logging.info(f"Benchmarking {operations:,} SET operations...")
    start_time = time.time()

    for i in range(operations):
        cache.set(f"key_{i}", f"value_{i}", ttl=1.0)

    end_time = time.time()
    duration = end_time - start_time
    ops_per_sec = operations / duration

    logging.info(f"SET Operations: {ops_per_sec:,.0f} ops/sec ({duration:.3f}s)")
    return ops_per_sec


def benchmark_get_operations(cache_size=10000, operations=50000):
    """Benchmark GET operations with TTL checking."""
    cache = VelocityCache(max_size=cache_size)

    # Fill cache first
    for i in range(cache_size):
        cache.set(f"key_{i}", f"value_{i}", ttl=10.0)

    logging.info(f"Benchmarking {operations:,} GET operations...")
    start_time = time.time()

    for i in range(operations):
        cache.get(f"key_{i % cache_size}")

    end_time = time.time()
    duration = end_time - start_time
    ops_per_sec = operations / duration

    logging.info(f"GET Operations: {ops_per_sec:,.0f} ops/sec ({duration:.3f}s)")
    return ops_per_sec


def benchmark_mixed_operations(cache_size=10000, operations=50000):
    """Benchmark mixed GET/SET operations (80% GET, 20% SET)."""
    cache = VelocityCache(max_size=cache_size)

    # Fill cache first
    for i in range(cache_size):
        cache.set(f"key_{i}", f"value_{i}", ttl=10.0)

    logging.info(f"Benchmarking {operations:,} mixed operations (80% GET, 20% SET)...")
    start_time = time.time()

    for i in range(operations):
        if i % 5 == 0:  # 20% SET operations
            cache.set(f"key_{i % cache_size}", f"value_{i}", ttl=10.0)
        else:  # 80% GET operations
            cache.get(f"key_{i % cache_size}")

    end_time = time.time()
    duration = end_time - start_time
    ops_per_sec = operations / duration

    logging.info(f"Mixed Operations: {ops_per_sec:,.0f} ops/sec ({duration:.3f}s)")
    return ops_per_sec


def benchmark_ttl_expiration(cache_size=1000, operations=10000):
    """Benchmark TTL expiration handling."""
    cache = VelocityCache(max_size=cache_size)

    logging.info(f"Benchmarking {operations:,} operations with TTL expiration...")
    start_time = time.time()

    for i in range(operations):
        # Set with very short TTL
        cache.set(f"key_{i % cache_size}", f"value_{i}", ttl=0.001)

        # Try to get (will likely be expired)
        cache.get(f"key_{i % cache_size}")

    end_time = time.time()
    duration = end_time - start_time
    ops_per_sec = operations / duration

    logging.info(f"TTL Operations: {ops_per_sec:,.0f} ops/sec ({duration:.3f}s)")

    # Print stats
    stats = cache.stats()
    logging.info(f"Stats: {stats}")
    return ops_per_sec


def run_all_benchmarks():
    """Run all benchmark tests."""
    logging.info("=" * 60)
    logging.info("VelocityCache TTL Performance Benchmarks")
    logging.info("=" * 60)

    results = {}

    # Run benchmarks
    results["set"] = benchmark_set_operations()
    logging.info("")

    results["get"] = benchmark_get_operations()
    logging.info("")

    results["mixed"] = benchmark_mixed_operations()
    logging.info("")

    results["ttl"] = benchmark_ttl_expiration()
    logging.info("")

    # Summary
    logging.info("=" * 60)
    logging.info("SUMMARY")
    logging.info("=" * 60)

    for test_name, ops_per_sec in results.items():
        status = "PASS" if ops_per_sec >= 30000 else "FAIL"
        logging.info(f"{test_name.upper():<10}: {ops_per_sec:>8,.0f} ops/sec {status}")

    overall_avg = sum(results.values()) / len(results)
    overall_status = "PASS" if overall_avg >= 30000 else "FAIL"
    logging.info(f"{'OVERALL':<10}: {overall_avg:>8,.0f} ops/sec {overall_status}")

    return results


if __name__ == "__main__":
    run_all_benchmarks()
