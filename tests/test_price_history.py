"""Test `price_history` function.

Note that tests will hit the network and therefore will take a while to run.
"""

# pylint: disable=missing-docstring

import pandas as pd
import pendulum
import pytest
from pandas.core.dtypes.dtypes import DatetimeTZDtype
from tessa import price_history, rate_limiter
from tessa.price import PriceHistory


def test_price_history_investpy_stock_including_caching_and_ratelimiting():
    # Make sure rate limiter is in a pristine setup:
    rate_limiter.reset_guards()
    assert rate_limiter.guards["investing"]["last_call"] == pendulum.parse("1900")

    # Retrieve stock and make sure the result is correct:
    df, crncy = price_history("AAPL", "stock", country="united states")
    assert crncy == "USD"
    assert df.index[0] == pd.Timestamp("2010-01-04", tz="UTC")
    assert df.shape[0] > 3000
    assert df.shape[1] == 1
    assert isinstance(df.index.dtype, DatetimeTZDtype)
    assert df.dtypes.to_string() == "close    float64"
    assert price_history.cache_info().misses == 1
    assert price_history.cache_info().hits == 0

    # Make sure the rate limiter was updated:
    assert (
        pendulum.now() - rate_limiter.guards["investing"]["last_call"]
    ).total_seconds() < 30

    # Retrieve again and check that the cache is used:
    df2, crncy2 = price_history("AAPL", "stock", country="united states")
    assert crncy2 == crncy
    assert df2.equals(df)
    assert price_history.cache_info().misses == 1
    assert price_history.cache_info().hits == 1


def test_price_history_verify_type():
    """price_history returns the correct type. At the same time tests that price
    retrieval works w/o a country parameter for types such as currency_cross."""
    assert isinstance(
        price_history(query="usd/chf", type_="currency_cross"), PriceHistory
    )


def test_price_history_investpy_searchobj():
    df, crncy = price_history(
        "{'id_': 995876, 'name': 'UBS MSCI Emerging Markets UCITS', "
        "'symbol': 'EMMUSA', 'country': 'switzerland', "
        "'tag': '/etfs/ubs-etf-msci-emerging-markets-a?cid=995876', "
        "'pair_type': 'etfs', 'exchange': 'Switzerland'}",
        "searchobj",
    )
    assert crncy == "USD"
    assert df.index[0] == pd.Timestamp("2010-11-18", tz="UTC")
    assert df.shape[0] > 1000
    assert df.shape[1] == 1
    assert isinstance(df.index.dtype, DatetimeTZDtype)
    assert df.dtypes.to_string() == "close    float64"


def test_price_history_crypto():
    df, crncy = price_history("ethereum", "crypto", currency_preference="chf")
    assert crncy == "CHF"
    assert df.index[0] == pd.Timestamp("2015-08-07", tz="UTC")
    assert df.shape[0] > 1000
    assert df.shape[1] == 1
    assert isinstance(df.index.dtype, DatetimeTZDtype)
    assert df.dtypes.to_string() == "close    float64"


# ---------- Error conditions ----------


def test_error_crypto_non_existent_currency_preference():
    with pytest.raises(ValueError) as excinfo:
        price_history("ethereum", "crypto", currency_preference="non-existent")
        assert "invalid vs_currency" in excinfo


def test_error_crypto_non_existent_name():
    with pytest.raises(ValueError) as excinfo:
        price_history("non-existent", "crypto")
        assert "Could not find coin with the given id" in excinfo


def test_error_unsupported_asset_type():
    with pytest.raises(ValueError) as excinfo:
        price_history("AAPL", "xxx")
        assert "Unsupported asset type" in excinfo


def test_error_missing_country():
    with pytest.raises(ValueError) as excinfo:
        price_history("AAPL", "stock")
        assert "country can not be None" in excinfo


def test_error_stock_not_found():
    with pytest.raises(RuntimeError) as excinfo:
        price_history("non-existent", "stock", country="united states")
        assert "stock non-existent not found" in excinfo
