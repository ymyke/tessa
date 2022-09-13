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
        "tessa.price.price_history",
        return_value=PriceHistory(pd.DataFrame(df_as_json).set_index("date"), "usd"),
    )


def test_price_point_strict(mock_price_history):
    assert price_point_strict("xx", "xx", "2018-01-11").price == 2.0


def test_price_point_strict_non_existent(mock_price_history):
    with pytest.raises(KeyError):
        price_point_strict("xx", "xx", "2018-01-13")


def test_price_point_non_existent(mock_price_history):
    assert price_point("xx", "xx", "2018-01-13") == PricePoint(
        when=pd.Timestamp("2018-01-12", tz="utc"), price=3.0, currency="usd"
    )


def test_price_latest(mock_price_history):
    assert price_latest("xx", "xx") == PricePoint(
        when=pd.Timestamp("2018-01-12", tz="utc"), price=3.0, currency="usd"
    )


def test_verify_pricepoint_types_are_used(mock_price_history):
    assert isinstance(price_point("xx", "xx", "2018-01-11"), PricePoint)
    assert isinstance(price_point_strict("xx", "xx", "2018-01-11"), PricePoint)
    assert isinstance(price_latest("xx", "xx"), PricePoint)


# ----- Tests that do hit the net -----


@pytest.mark.net
def test_concrete_investing_price_point():
    assert price_point("AAPL", "stock", "2018-01-11", "united states") == PricePoint(
        when=pd.Timestamp("2018-01-11", tz="utc"), price=43.82, currency="USD"
    )


@pytest.mark.net
def test_concrete_crypto_price_point():
    assert price_point("bitcoin", "crypto", "2018-01-11") == PricePoint(
        when=pd.Timestamp("2018-01-11", tz="utc"),
        price=14050.5696063543,
        currency="USD",
    )
