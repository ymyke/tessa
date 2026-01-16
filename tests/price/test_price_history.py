"""Test `price_history` function.

Note that tests will hit the network and therefore will take a while to run.
"""

# pylint: disable=missing-docstring

import pandas as pd
import pendulum
import pytest
from pandas.core.dtypes.dtypes import DatetimeTZDtype
from tessa import price_history
from tessa.price import PriceHistory
from tessa import sources


def test_price_history_caching_and_ratelimiting(mocker):
    """Test caching and rate limiter logic without hitting real API."""
    mock_df = pd.DataFrame(
        {"close": [100.0, 101.0]},
        index=pd.to_datetime(["2020-01-01", "2020-01-02"], utc=True),
    )
    mock_df.index.name = "date"

    # Reset to pristine state:
    sources.reset_rate_limiters()
    rate_limiter = sources.get_source("yahoo").rate_limiter
    assert rate_limiter.last_call == pendulum.parse("1900")
    price_history.cache_clear()

    mocker.patch.object(
        sources.get_source("yahoo"),
        "get_price_history",
        return_value=(mock_df, "USD"),
    )

    try:
        # First call - should invoke API (mocked):
        res = price_history("AAPL", "yahoo")
        assert isinstance(res, PriceHistory)
        df, crncy = res
        assert crncy == "USD"
        assert price_history.cache_info().misses == 1
        assert price_history.cache_info().hits == 0

        # Rate limiter should be updated:
        assert (pendulum.now() - rate_limiter.last_call).total_seconds() < 30
        assert rate_limiter.count_all_calls == 1
        assert rate_limiter.count_limited_calls == 0

        # Second call - should hit cache, not API:
        df2, crncy2 = price_history("AAPL", "yahoo")
        assert crncy2 == crncy
        assert df2.equals(df)
        assert price_history.cache_info().misses == 1
        assert price_history.cache_info().hits == 1
        assert rate_limiter.count_all_calls == 1  # unchanged - cache hit
    finally:
        # Clean up cache to avoid polluting other tests
        price_history.cache_clear()


@pytest.mark.net
def test_price_history_coingecko():
    df, crncy = price_history("ethereum", "coingecko", currency_preference="CHF")
    assert crncy == "CHF"
    assert df.shape[0] == 366
    assert df.shape[1] == 1
    assert isinstance(df.index.dtype, DatetimeTZDtype)
    assert df.dtypes.to_string() == "close    float64"


def test_error_unsupported_asset_source():
    with pytest.raises(ValueError) as excinfo:
        price_history(query="AAPL", source="xxx")
    assert "Unknown source" in str(excinfo.value)
