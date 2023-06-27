"""Symbol-related tests."""

import ast
import re
import pytest
import pandas as pd
import yaml
from tessa.price import PricePoint
from tessa.symbol import Symbol

# pylint: disable=missing-function-docstring


def test_initializer():
    s = Symbol(name="x", source="coingecko", query="qq")
    assert s.name == "x"
    assert s.source == "coingecko"
    assert s.query == "qq"


def test_initializer_with_defaults():
    s = Symbol(name="AAPL")
    assert s.source == "yahoo"
    assert s.query == "AAPL"


def test_repr_can_be_transformed_back_into_symbol():
    s = Symbol(name="x")
    params = re.findall(r"Symbol\((.*)\)", repr(s))[0]
    params_as_dict = "{" + re.sub(r"(^|, )((\w+)=)", r"\1'\3':", params) + "}"
    assert Symbol(**ast.literal_eval(params_as_dict)) == s


def test_matches():
    s = Symbol(name="X", aliases=["X", "Y", "Z.DE"])
    assert s.matches("X")
    assert s.matches("Y")
    assert s.matches("Z.DE")
    assert s.matches("Z")
    assert not s.matches("A")


def test_to_yaml():
    s = Symbol(name="X", aliases=["X", "Y", "Z"])
    k, v = list(yaml.safe_load(s.to_yaml()).items())[0]
    assert Symbol(k, **v) == s


@pytest.mark.net
def test_price_functions():
    s = Symbol(name="MSFT")
    df, crncy = s.price_history()
    assert isinstance(df, pd.DataFrame)
    assert crncy == "USD"
    assert isinstance(s.price_latest(), PricePoint)
    assert round(s.price_latest().price) == round(float(df.iloc[-1]["close"]))
    assert s.price_latest().when == df.iloc[-1].name
    assert s.currency() == crncy
    assert round(s.price_point("2020-01-10").price) == round(
        float(df.loc["2020-01-10"]["close"].iloc[0])
    )
    # Check that the method returns the nearest price if necessary:
    assert s.price_point("2020-01-01").when == pd.Timestamp(
        "2019-12-31 05:00:00+0000", tz="UTC"
    )


@pytest.mark.net
def test_currency_preference():
    for check_currency in ["USD", "CHF"]:
        Symbol.currency_preference = check_currency
        assert Symbol("bitcoin", source="coingecko").currency() == check_currency
