from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Dict

from fastapi import HTTPException, status

from app.core.config import get_settings


@dataclass
class Bucket:
    capacity: int
    refill_rate_per_sec: float
    tokens: float
    last_refill: float


class InMemoryRateLimiter:
    def __init__(self, capacity: int, per_minute: int):
        self.capacity = capacity
        self.refill_rate_per_sec = per_minute / 60.0
        self._buckets: Dict[str, Bucket] = {}
        self._lock = threading.Lock()

    def allow(self, key: str, cost: int = 1) -> bool:
        now = time.monotonic()
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                bucket = Bucket(self.capacity, self.refill_rate_per_sec, self.capacity, now)
                self._buckets[key] = bucket
            # Refill tokens
            elapsed = now - bucket.last_refill
            if elapsed > 0:
                bucket.tokens = min(bucket.capacity, bucket.tokens + elapsed * bucket.refill_rate_per_sec)
                bucket.last_refill = now
            if bucket.tokens >= cost:
                bucket.tokens -= cost
                return True
            return False


# Singleton configured from settings
_limiter: InMemoryRateLimiter | None = None

def get_rate_limiter() -> InMemoryRateLimiter:
    global _limiter
    if _limiter is None:
        s = get_settings()
        _limiter = InMemoryRateLimiter(capacity=s.rate_limit_burst, per_minute=s.rate_limit_per_min)
    return _limiter


def enforce_rate_limit(key: str) -> None:
    limiter = get_rate_limiter()
    if not limiter.allow(key):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
