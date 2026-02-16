import time
from collections import deque
from dataclasses import dataclass
from threading import Lock

from fastapi import HTTPException


@dataclass(frozen=True)
class Limit:
    max_requests: int
    window_seconds: int


class InMemoryRateLimiter:
    def __init__(self):
        self._buckets: dict[str, deque[float]] = {}
        self._lock = Lock()

    def hit(self, key: str, limit: Limit):
        now = time.time()
        window_start = now - limit.window_seconds

        with self._lock:
            bucket = self._buckets.setdefault(key, deque())
            while bucket and bucket[0] < window_start:
                bucket.popleft()

            if len(bucket) >= limit.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Max {limit.max_requests} requests per {limit.window_seconds}s."
                )

            bucket.append(now)


rate_limiter = InMemoryRateLimiter()
