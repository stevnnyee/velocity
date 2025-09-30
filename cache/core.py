"""
VelocityCache: Simple in-memory key-value store with LRU eviction.
"""

from typing import Any, Optional
import time
import threading