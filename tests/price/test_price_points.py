"""All tests related to `price_point_*` and `price_latest`."""

import pytest
import pandas as pd
from tessa import price_point, price_point_strict, price_latest
from tessa.price import PriceHistory, PricePoint


# pylint: disable=unused-argument,missing-function-docstring,redefined-outer-name

# ----- Tests that don't hit the net -----


@pytest.fixture()
def mock_price_history(mocker):
    df_as_json = {
        "date": [
            pd.Timestamp("2017-01-11", tz="utc"),
            pd.Timestamp("2018-01-11", tz="utc"),
            pd.Timestamp("2018-01-12", tz="utc"),
        ],
        "close": [1.0, 2.0, 3.0],
    }
    mocker.patch(
        "tessa.price.price.price_history",
        return_value=PriceHistory(pd.DataFrame(df_as_json).set_index("date"), "USD"),
    )


def test_price_point_strict(mock_price_history):
    assert price_point_strict("xx", "2018-01-11").price == 2.0


def test_price_point_strict_with_non_existent_timestamp_fails(mock_price_history):
    with pytest.raises(KeyError):
        price_point_strict("xx", "2018-01-13")


def test_price_point_with_non_existent_timestamp_finds_nearest(mock_price_history):
    assert price_point("xx", "2018-01-13") == PricePoint(
        when=pd.Timestamp("2018-01-12", tz="utc"), price=3.0, currency="USD"
    )


def test_price_latest(mock_price_history):
    assert price_latest("xx") == PricePoint(
        when=pd.Timestamp("2018-01-12", tz="utc"), price=3.0, currency="USD"
    )


def test_verify_pricepoint_types_are_used(mock_price_history):
    assert isinstance(price_point("xx", "2018-01-11"), PricePoint)
    assert isinstance(price_point_strict("xx", "2018-01-11"), PricePoint)
    assert isinstance(price_latest("xx"), PricePoint)


# ----- Tests that do hit the net -----


@pytest.mark.net
def test_concrete_yahoo_price_point():
    res = price_point("AAPL", "2018-01-11", "yahoo")
    assert isinstance(res, PricePoint)
    assert res.when == pd.Timestamp("2018-01-11 05:00:00+0000", tz="UTC")
    assert round(res.price) == 41
    assert res.currency == "USD"


@pytest.mark.net
def test_concrete_coingecko_price_point():
    res = price_point("bitcoin", "2018-01-11", "coingecko")
    assert isinstance(res, PricePoint)
    assert res.when == pd.Timestamp("2018-01-11", tz="utc")
    assert round(res.price) == 14051
    assert res.currency == "USD"
