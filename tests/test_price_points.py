"""All tests related to `price_point_*` and `price_latest`.

These tests _do not_ hit the network.
"""

import pytest
import pandas as pd
from tessa import price_point, price_point_strict, price_latest


# pylint: disable=unused-argument,missing-function-docstring,redefined-outer-name


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
        return_value=(pd.DataFrame(df_as_json).set_index("date"), "usd"),
    )


def test_price_point_strict(mock_price_history):
    assert price_point_strict("xx", "xx", "2018-01-11")[0] == 2.0


def test_price_point_strict_non_existent(mock_price_history):
    with pytest.raises(KeyError):
        price_point_strict("xx", "xx", "2018-01-13")


def test_price_point_non_existent(mock_price_history):
    assert price_point("xx", "xx", "2018-01-13") == (
        3.0,
        pd.Timestamp("2018-01-12", tz="utc"),
        "usd",
    )


def test_price_latest(mock_price_history):
    assert price_latest("xx", "xx") == (
        3.0,
        pd.Timestamp("2018-01-12", tz="utc"),
        "usd",
    )
