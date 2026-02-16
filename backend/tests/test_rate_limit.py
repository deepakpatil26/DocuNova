import pytest
from fastapi import HTTPException

from app.core.rate_limit import InMemoryRateLimiter, Limit


def test_rate_limit_allows_within_limit():
    limiter = InMemoryRateLimiter()
    limit = Limit(max_requests=2, window_seconds=60)

    limiter.hit("user-1", limit)
    limiter.hit("user-1", limit)


def test_rate_limit_blocks_after_threshold():
    limiter = InMemoryRateLimiter()
    limit = Limit(max_requests=2, window_seconds=60)

    limiter.hit("user-1", limit)
    limiter.hit("user-1", limit)

    with pytest.raises(HTTPException) as exc_info:
        limiter.hit("user-1", limit)

    assert exc_info.value.status_code == 429
