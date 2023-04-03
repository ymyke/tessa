"""Sources-related tests."""

# pylint: disable=missing-docstring

import warnings
import pytest
import requests
from tessa.sources import rate_limiter, Source, sources
from tessa.price import PriceHistory


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


# ----- get_price_history_bruteforcefully tests -----


def test_get_price_history_bruteforcefully_success(mocker):
    def mock_get_price_history_success(*_, **__) -> PriceHistory:
        return PriceHistory(df=None, currency=None)

    mocker.patch("warnings.warn")
    source = Source(
        get_price_history=mock_get_price_history_success,
        get_search_results=None,
        rate_limiter=None,
    )
    source.get_price_history_bruteforcefully("BTC")
    warnings.warn.assert_not_called()


def test_get_price_history_bruteforcefully_exceeds_max_tries(mocker):
    def mock_get_price_history_retryable_error(*_, **__) -> PriceHistory:
        response = requests.Response()
        response.status_code = 504
        raise requests.HTTPError(response=response)

    mocker.patch("warnings.warn")
    source = Source(
        get_price_history=mock_get_price_history_retryable_error,
        get_search_results=None,
        rate_limiter=None,
    )
    with pytest.raises(
        ConnectionError, match="Cannot access source, even after 100 tries"
    ):
        source.get_price_history_bruteforcefully("BTC")
    assert warnings.warn.call_count == 100


def test_get_price_history_bruteforcefully_non_retriable_error(mocker):
    def mock_get_price_history_non_retriable_error(*_, **__) -> PriceHistory:
        response = requests.Response()
        response.status_code = 400
        raise requests.HTTPError(response=response)

    mocker.patch("warnings.warn")
    source = Source(
        get_price_history=mock_get_price_history_non_retriable_error,
        get_search_results=None,
        rate_limiter=None,
    )
    with pytest.raises(requests.HTTPError) as exc_info:
        source.get_price_history_bruteforcefully("BTC")
    assert exc_info.value.response.status_code == 400
    warnings.warn.assert_not_called()
