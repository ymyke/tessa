"""Sources-related tests."""

# pylint: disable=missing-docstring

import pytest
from tessa import sources
from tessa.sources import rate_limiter


def test_get_source():
    src = sources.get_source("yahoo")
    assert isinstance(src, sources.Source)
    assert callable(src.get_price_history)
    assert callable(src.get_search_results)
    assert isinstance(src.rate_limiter, rate_limiter.RateLimiter)


def test_get_unknown_source():
    with pytest.raises(ValueError):
        sources.get_source("unknown_source")  # type: ignore


def test_get_all_sources():
    assert all(isinstance(s, sources.Source) for s in sources.get_all_sources())


def test_resetting_rate_limiters():
    sources.get_source("yahoo").rate_limiter.count_limited_calls = 7
    assert sources.get_source("yahoo").rate_limiter.count_limited_calls == 7
    sources.reset_rate_limiters()
    assert sources.get_source("yahoo").rate_limiter.count_limited_calls == 0
