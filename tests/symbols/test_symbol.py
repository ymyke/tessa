"""Symbol-related tests."""

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
