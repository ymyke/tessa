"""Symbol-related tests."""

import pytest
import pandas as pd
import yaml
from tessa.symbols import Symbol

# pylint: disable=missing-function-docstring


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


def test_to_yaml():
    s = Symbol(name="X", aliases=["X", "Y", "Z"], country="C")
    k, v = list(yaml.safe_load(s.to_yaml()).items())[0]
    assert Symbol(k, **v) == s


@pytest.mark.net
def test_price_functions():
    s = Symbol(name="MSFT")
    df, crncy = s.price_history()
    assert isinstance(df, pd.DataFrame)
    assert crncy == "USD"
    assert s.price_latest() == (float(df.iloc[-1]["close"]), df.iloc[-1].name, crncy)
    assert s.today_price() == float(df.iloc[-1]["close"])
    assert s.today() == df.iloc[-1].name
    assert s.currency() == crncy
    assert s.price_point("2020-01-10")[0] == float(df.loc["2020-01-10"]["close"])
    # Check that the method returns the nearest price if necessary:
    assert s.price_point("2020-01-01")[1] == pd.Timestamp("2020-01-02", tz="UTC")
