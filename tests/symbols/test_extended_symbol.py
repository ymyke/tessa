"""ExtendedSymbol-related tests."""

from tessa.symbol import ExtendedSymbol

# pylint: disable=missing-function-docstring


def test_initializer():
    s = ExtendedSymbol("MSFT", delisted=True)
    assert s.name == "MSFT"
    assert not s.watch
    assert s.delisted
    assert s.jurisdiction == "US"
    assert s.isin is None
    assert s.strategy == []


def test_standard_jurisdictions():
    assert ExtendedSymbol("X", jurisdiction="US").region == "North America"
    assert ExtendedSymbol("X", jurisdiction="DE").region == "Europe"


def test_jurisdiction_updates():
    assert ExtendedSymbol("X", jurisdiction="CH").region == "Switzerland"
    assert ExtendedSymbol("X", jurisdiction="CN").region == "China"
    assert ExtendedSymbol("X", jurisdiction="several").region == "Other"
