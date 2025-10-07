"""
Performance benchmarks for VelocityCache.

Target: 30,000+ operations per second
Run with: python -m tests.benchmark_performance
"""

import time
from cache.core import VelocityCache


def benchmark_set_operations(cache_size=10000, operations=50000):
    """Benchmark SET operations with TTL."""
    cache = VelocityCache(max_size=cache_size)

    print(f"Benchmarking {operations:,} SET operations...")
    start_time = time.time()

    for i in range(operations):
        cache.set(f"key_{i}", f"value_{i}", ttl=1.0)

    end_time = time.time()
    duration = end_time - start_time
    ops_per_sec = operations / duration

    print(f"SET Operations: {ops_per_sec:,.0f} ops/sec ({duration:.3f}s)")
    return ops_per_sec


def benchmark_get_operations(cache_size=10000, operations=50000):
    """Benchmark GET operations with TTL checking."""
    cache = VelocityCache(max_size=cache_size)

    # Fill cache first
    for i in range(cache_size):
        cache.set(f"key_{i}", f"value_{i}", ttl=10.0)

    print(f"Benchmarking {operations:,} GET operations...")
    start_time = time.time()

    for i in range(operations):
        cache.get(f"key_{i % cache_size}")

    end_time = time.time()
    duration = end_time - start_time
    ops_per_sec = operations / duration

    print(f"GET Operations: {ops_per_sec:,.0f} ops/sec ({duration:.3f}s)")
    return ops_per_sec


def benchmark_mixed_operations(cache_size=10000, operations=50000):
    """Benchmark mixed GET/SET operations (80% GET, 20% SET)."""
    cache = VelocityCache(max_size=cache_size)

    # Fill cache first
    for i in range(cache_size):
        cache.set(f"key_{i}", f"value_{i}", ttl=10.0)

    print(f"Benchmarking {operations:,} mixed operations (80% GET, 20% SET)...")
    start_time = time.time()

    for i in range(operations):
        if i % 5 == 0:  # 20% SET operations
            cache.set(f"key_{i % cache_size}", f"value_{i}", ttl=10.0)
        else:  # 80% GET operations
            cache.get(f"key_{i % cache_size}")

    end_time = time.time()
    duration = end_time - start_time
    ops_per_sec = operations / duration

    print(f"Mixed Operations: {ops_per_sec:,.0f} ops/sec ({duration:.3f}s)")
    return ops_per_sec


def benchmark_ttl_expiration(cache_size=1000, operations=10000):
    """Benchmark TTL expiration handling."""
    cache = VelocityCache(max_size=cache_size)

    print(f"Benchmarking {operations:,} operations with TTL expiration...")
    start_time = time.time()

    for i in range(operations):
        # Set with very short TTL
        cache.set(f"key_{i % cache_size}", f"value_{i}", ttl=0.001)

        # Try to get (will likely be expired)
        cache.get(f"key_{i % cache_size}")

    end_time = time.time()
    duration = end_time - start_time
    ops_per_sec = operations / duration

    print(f"TTL Operations: {ops_per_sec:,.0f} ops/sec ({duration:.3f}s)")

    # Print stats
    stats = cache.stats()
    print(f"Stats: {stats}")
    return ops_per_sec


def run_all_benchmarks():
    """Run all benchmark tests."""
    print("=" * 60)
    print("VelocityCache TTL Performance Benchmarks")
    print("=" * 60)

    results = {}

    # Run benchmarks
    results["set"] = benchmark_set_operations()
    print()

    results["get"] = benchmark_get_operations()
    print()

    results["mixed"] = benchmark_mixed_operations()
    print()

    results["ttl"] = benchmark_ttl_expiration()
    print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for test_name, ops_per_sec in results.items():
        status = "✅ PASS" if ops_per_sec >= 30000 else "❌ FAIL"
        print(f"{test_name.upper():<10}: {ops_per_sec:>8,.0f} ops/sec {status}")

    overall_avg = sum(results.values()) / len(results)
    overall_status = "✅ PASS" if overall_avg >= 30000 else "❌ FAIL"
    print(f"{'OVERALL':<10}: {overall_avg:>8,.0f} ops/sec {overall_status}")

    return results


if __name__ == "__main__":
    run_all_benchmarks()
