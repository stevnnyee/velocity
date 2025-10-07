#!/usr/bin/env python3
"""
VelocityCache - Main entry point for the distributed cache project.

This is the main entry point for running the cache, tests, and benchmarks.
"""

import sys
import os
from cache.core import VelocityCache


def demo_cache():
    """Demo the cache functionality."""
    print("🚀 VelocityCache Demo")
    print("=" * 50)
    
    # Create cache
    cache = VelocityCache(max_size=5)
    
    # Basic operations
    print("📝 Setting values...")
    cache.set("BTC-USD", 43250.12, ttl=5)
    cache.set("ETH-USD", 2650.50, ttl=10)
    cache.set("ADA-USD", 0.45, ttl=3)
    
    print("🔍 Getting values...")
    print(f"BTC-USD: ${cache.get('BTC-USD')}")
    print(f"ETH-USD: ${cache.get('ETH-USD')}")
    print(f"ADA-USD: ${cache.get('ADA-USD')}")
    
    # Check stats
    print("\n📊 Cache Stats:")
    stats = cache.stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test expiration
    print("\n⏰ Testing expiration...")
    import time
    time.sleep(4)  # Wait for ADA to expire
    print(f"ADA-USD after 4s: ${cache.get('ADA-USD')}")  # Should be None
    
    print("\n✅ Demo complete!")


def run_tests():
    """Run the test suite."""
    print("🧪 Running VelocityCache Tests...")
    import subprocess
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/unit/test_cache_core.py", "-v"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0


def run_benchmarks():
    """Run performance benchmarks."""
    print("⚡ Running VelocityCache Benchmarks...")
    import subprocess
    
    result = subprocess.run([
        sys.executable, "-m", "tests.benchmark_performance"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python main.py [demo|test|benchmark|all]")
        print("  demo      - Run cache demo")
        print("  test      - Run test suite")
        print("  benchmark - Run performance benchmarks")
        print("  all       - Run demo, tests, and benchmarks")
        return
    
    command = sys.argv[1].lower()
    
    if command == "demo":
        demo_cache()
    elif command == "test":
        success = run_tests()
        sys.exit(0 if success else 1)
    elif command == "benchmark":
        success = run_benchmarks()
        sys.exit(0 if success else 1)
    elif command == "all":
        demo_cache()
        print("\n" + "=" * 60)
        success1 = run_tests()
        print("\n" + "=" * 60)
        success2 = run_benchmarks()
        sys.exit(0 if (success1 and success2) else 1)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
