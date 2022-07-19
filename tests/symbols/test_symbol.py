"""Symbol-related tests."""

import pytest
import pandas as pd
from tessa.symbols import Symbol

# pylint: disable=no-member,missing-function-docstring

# FIXME Also check the tests in fignal around tickerconfig and Asset

# FIXME Add more tests


def test_initiator():
    s = Symbol("AAPL", {"type": "stock", "country": "united states", "query": "qq"})
    assert s.name == "AAPL"
    assert s.type == "stock"
    assert s.country == "united states"
    assert s.query == "qq"


def test_initiator_with_defaults():
    s = Symbol("AAPL", {})
    assert s.type == "stock"
    assert s.country == "united states"
    assert s.query == "AAPL"


def test_matches():
    s = Symbol("X", {"aliases": ["X", "Y", "Z.DE"]})
    assert s.matches("X")
    assert s.matches("Y")
    assert s.matches("Z.DE")
    assert s.matches("Z")
    assert not s.matches("A")


@pytest.mark.net
def test_price_functions():
    s = Symbol("MSFT", {})
    df, crncy = s.price_history()
    assert isinstance(df, pd.DataFrame)
    assert crncy == "USD"
    assert s.latest_price() == (df.iloc[-1].name, float(df.iloc[-1]["close"]), crncy)
    assert s.today_price() == float(df.iloc[-1]["close"])
    assert s.today() == df.iloc[-1].name
    assert s.currency() == crncy
    assert s.lookup_price("2020-01-10") == float(df.loc["2020-01-10"]["close"])
    # FIXME What should happen in case there is no date, e.g., 2020-01-01?
