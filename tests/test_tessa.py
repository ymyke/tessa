"""Note that tests will hit the network and therefore will take a while to run."""

# pylint: disable=missing-docstring

import pandas as pd
from pandas.core.dtypes.dtypes import DatetimeTZDtype
from tessa import __version__, price_history


def test_version():
    assert __version__ == "0.1.0"


def test_price_history_investpy_stock_including_caching():
    df, crncy = price_history("AAPL", "stock", country="united states")
    assert crncy == "USD"
    assert df.index[0] == pd.Timestamp("1980-12-12", tz="UTC")
    assert df.shape[0] > 10000
    assert df.shape[1] == 1
    assert isinstance(df.index.dtype, DatetimeTZDtype)
    assert df.dtypes.to_string() == "close    float64"
    assert price_history.cache_info().misses == 1
    assert price_history.cache_info().hits == 0

    # Retrieve again and check that the cache is used:
    df2, crncy2 = price_history("AAPL", "stock", country="united states")
    assert crncy2 == crncy
    assert df2.equals(df)
    assert price_history.cache_info().misses == 1
    assert price_history.cache_info().hits == 1


def test_price_history_investpy_searchobj():
    df, crncy = price_history(
        {
            "id_": 995876,
            "name": "UBS MSCI Emerging Markets UCITS",
            "symbol": "EMMUSA",
            "country": "switzerland",
            "tag": "/etfs/ubs-etf-msci-emerging-markets-a?cid=995876",
            "pair_type": "etfs",
            "exchange": "Switzerland",
        },
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
    assert crncy == "chf"
    assert df.index[0] == pd.Timestamp("2015-08-07", tz="UTC")
    assert df.shape[0] > 1000
    assert df.shape[1] == 1
    assert isinstance(df.index.dtype, DatetimeTZDtype)
    assert df.dtypes.to_string() == "close    float64"
