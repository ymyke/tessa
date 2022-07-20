"""Symbol-related tests."""

import pytest
import pandas as pd
from tessa.symbols import Symbol

# pylint: disable=missing-function-docstring

# FIXME Also check the tests in fignal around tickerconfig and Asset


def test_initializer():
    s = Symbol(name="x", type_="y", country="z", query="qq")
    assert s.name == "x"
    assert s.type_ == "y"
    assert s.country == "z"
    assert s.query == "qq"


def test_initializer_with_defaults():
    s = Symbol(name="AAPL")
    assert s.type_ == "stock"
    assert s.country == "united states"
    assert s.query == "AAPL"


def test_querytype():
    # pylint: disable=protected-access
    s = Symbol(name="X", type_="fund")
    assert s._querytype == "fund"
    s = Symbol(name="X", query={})
    assert s._querytype == "searchobj"


def test_initalizer_without_country():
    s = Symbol(name="X", type_="crypto")
    assert s.country is None


def test_matches():
    s = Symbol(name="X", aliases=["X", "Y", "Z.DE"])
    assert s.matches("X")
    assert s.matches("Y")
    assert s.matches("Z.DE")
    assert s.matches("Z")
    assert not s.matches("A")


@pytest.mark.net
def test_price_functions():
    s = Symbol(name="MSFT")
    df, crncy = s.price_history()
    assert isinstance(df, pd.DataFrame)
    assert crncy == "USD"
    assert s.latest_price() == (df.iloc[-1].name, float(df.iloc[-1]["close"]), crncy)
    assert s.today_price() == float(df.iloc[-1]["close"])
    assert s.today() == df.iloc[-1].name
    assert s.currency() == crncy
    assert s.lookup_price("2020-01-10") == float(df.loc["2020-01-10"]["close"])
    # FIXME What should happen in case there is no date, e.g., 2020-01-01?
