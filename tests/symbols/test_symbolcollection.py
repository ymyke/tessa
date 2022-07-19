"""SymbolCollection-related tests."""

# pylint: disable=missing-function-docstring

import pytest
from tessa.symbols import SymbolCollection


def test_initializer(tmp_path):
    file = tmp_path / "symbols.yaml"
    file.write_text(
        """
A:
B:
    aliases: [BB, BBB]
    type: etf
    country: switzerland
    query: p
C:
"""
    )
    sc = SymbolCollection(file)
    assert sc.find_one("A")
    assert sc.find_one("B")
    assert sc.find_one("BB")
    assert sc.find_one("BBB")
    b = sc.find_one("B")
    assert b.type == "etf"
    assert b.country == "switzerland"
    assert b.query == "p"
    assert sc.find_one("C")
    assert sc.find_one("D") is None
    assert len(sc.symbols) == 3


def test_find_one(tmp_path):
    file = tmp_path / "symbols.yaml"
    file.write_text(
        """
A:
B:
    aliases: [X]
BB:
C:
    aliases: [X]
"""
    )
    sc = SymbolCollection(file)
    assert sc.find_one("A")
    assert sc.find_one("B")
    assert sc.find_one("C")
    assert sc.find_one("BB")
    with pytest.raises(ValueError):
        sc.find_one("X")