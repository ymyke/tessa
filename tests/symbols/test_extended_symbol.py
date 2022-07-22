"""ExtendedSymbol-related tests."""

from tessa.symbols import ExtendedSymbol

# pylint: disable=missing-function-docstring


def test_initializer():
    s = ExtendedSymbol("MSFT", delisted=True)
    assert s.name == "MSFT"
    assert not s.watch
    assert s.delisted
    assert s.jurisdiction == "US"
    assert s.isin is None
    assert s.strategy == []
