"""SymbolCollection-related tests."""

# pylint: disable=missing-function-docstring

import pytest
from tessa.symbol import SymbolCollection, Symbol


def test_initializer():
    sc = SymbolCollection()
    assert sc.symbols == []


def test_load_yaml(tmp_path):
    file = tmp_path / "symbols.yaml"
    file.write_text(
        """
A:
B:
    aliases: [BB, BBB]
    type_: etf
    country: switzerland
    query: p
C:
"""
    )
    sc = SymbolCollection()
    sc.load_yaml(file)
    assert sc.find_one("A")
    b = sc.find_one("B")
    assert b
    assert b.type_ == "etf"
    assert b.country == "switzerland"
    assert b.query == "p"
    assert sc.find_one("BB")
    assert sc.find_one("BBB")
    assert sc.find_one("C")
    assert sc.find_one("D") is None
    assert len(sc.symbols) == 3


def test_add():
    sc = SymbolCollection()
    sc.add(Symbol("A"))
    sc.add([Symbol("B"), Symbol("C")])
    assert sc.symbols == [Symbol("A"), Symbol("B"), Symbol("C")]


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
    sc = SymbolCollection()
    sc.load_yaml(file)
    assert sc.find_one("A")
    assert sc.find_one("B")
    assert sc.find_one("C")
    assert sc.find_one("BB")
    with pytest.raises(ValueError):
        sc.find_one("X")


def test_to_and_save_yaml(tmp_path):
    # Test to_yaml:
    sc1 = SymbolCollection()
    sc1.add([Symbol("A"), Symbol("B")])
    assert sc1.to_yaml() == Symbol("A").to_yaml() + Symbol("B").to_yaml()
    # Test save_yaml:
    file = tmp_path / "symbols.yaml"
    sc1.save_yaml(file)
    sc2 = SymbolCollection()
    sc2.load_yaml(file)
    assert sc2.symbols == sc1.symbols
