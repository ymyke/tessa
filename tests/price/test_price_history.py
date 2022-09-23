"""Test `price_history` function.

Note that tests will hit the network and therefore will take a while to run.
"""

# pylint: disable=missing-docstring

import pandas as pd
import pendulum
import pytest
from pandas.core.dtypes.dtypes import DatetimeTZDtype
from tessa import price_history
from tessa.utils import rate_limiter
from tessa.price import PriceHistory


@pytest.mark.net
def test_price_history_on_yahoo_including_caching_and_ratelimiting():
    # Make sure rate limiter and cache are in a pristine setup:
    rate_limiter.reset_guards()
    assert rate_limiter.guards["yahoo"]["last_call"] == pendulum.parse("1900")
    price_history.cache_clear()

    # Retrieve asset and make sure the result is correct:
    res = price_history("AAPL", "yahoo")
    assert isinstance(res, PriceHistory)
    df, crncy = res
    assert crncy == "USD"
    assert df.index[0] == pd.Timestamp("1999-12-31", tz="UTC")
    assert df.shape[0] > 5000
    assert df.shape[1] == 1
    assert isinstance(df.index.dtype, DatetimeTZDtype)
    assert df.dtypes.to_string() == "close    float64"
    # pylint: disable=no-value-for-parameter
    assert price_history.cache_info().misses == 1
    assert price_history.cache_info().hits == 0

    # Make sure the rate limiter was updated:
    assert (
        pendulum.now() - rate_limiter.guards["yahoo"]["last_call"]
    ).total_seconds() < 30

    # Retrieve again and check that the cache is used:
    df2, crncy2 = price_history("AAPL", "yahoo")
    assert crncy2 == crncy
    assert df2.equals(df)
    assert price_history.cache_info().misses == 1
    assert price_history.cache_info().hits == 1


@pytest.mark.net
def test_price_history_coingecko():
    df, crncy = price_history("ethereum", "coingecko", currency_preference="CHF")
    assert crncy == "CHF"
    assert df.index[0] == pd.Timestamp("2015-08-07", tz="UTC")
    assert df.shape[0] > 1000
    assert df.shape[1] == 1
    assert isinstance(df.index.dtype, DatetimeTZDtype)
    assert df.dtypes.to_string() == "close    float64"


def test_error_unsupported_asset_source():
    with pytest.raises(ValueError) as excinfo:
        price_history(query="AAPL", source="xxx")
        assert "Unkown source" in excinfo
