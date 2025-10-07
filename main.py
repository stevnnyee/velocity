#!/usr/bin/env python3
"""
VelocityCache - Main entry point for the distributed cache project.

This is the main entry point for running the cache, tests, and benchmarks.
"""

import sys
import logging as std_logging
from cache.core import VelocityCache

# Configure logging
std_logging.basicConfig(
    level=std_logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logging = std_logging.getLogger(__name__)


def demo_cache():
    """Demo the cache functionality."""
    logging.info("VelocityCache Demo")
    logging.info("=" * 50)

    # Create cache
    cache = VelocityCache(max_size=5)

    # Basic operations
    logging.info("Setting values...")
    cache.set("BTC-USD", 43250.12, ttl=5)
    cache.set("ETH-USD", 2650.50, ttl=10)
    cache.set("ADA-USD", 0.45, ttl=3)

    logging.info("Getting values...")
    logging.info(f"BTC-USD: ${cache.get('BTC-USD')}")
    logging.info(f"ETH-USD: ${cache.get('ETH-USD')}")
    logging.info(f"ADA-USD: ${cache.get('ADA-USD')}")

    # Check stats
    logging.info("Cache Stats:")
    stats = cache.stats()
    for key, value in stats.items():
        logging.info(f"  {key}: {value}")

    # Test expiration
    logging.info("Testing expiration...")
    import time

    time.sleep(4)  # Wait for ADA to expire
    logging.info(f"ADA-USD after 4s: ${cache.get('ADA-USD')}")  # Should be None

    logging.info("Demo complete!")


def run_tests():
    """Run the test suite."""
    logging.info("Running VelocityCache Tests...")
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/unit/test_cache_core.py", "-v"],
        capture_output=True,
        text=True,
    )

    logging.info(result.stdout)
    if result.stderr:
        logging.error("Errors: %s", result.stderr)

    return result.returncode == 0


def run_benchmarks():
    """Run performance benchmarks."""
    logging.info("Running VelocityCache Benchmarks...")
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "tests.benchmark_performance"],
        capture_output=True,
        text=True,
    )

    logging.info(result.stdout)
    if result.stderr:
        logging.error("Errors: %s", result.stderr)

    return result.returncode == 0


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        logging.info("Usage: python main.py [demo|test|benchmark|all]")
        logging.info("  demo      - Run cache demo")
        logging.info("  test      - Run test suite")
        logging.info("  benchmark - Run performance benchmarks")
        logging.info("  all       - Run demo, tests, and benchmarks")
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
        logging.error("Unknown command: %s", command)
        sys.exit(1)


if __name__ == "__main__":
    main()
