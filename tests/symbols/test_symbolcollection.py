"""SymbolCollection-related tests."""

# pylint: disable=missing-function-docstring,invalid-name

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
    source: coingecko
    query: p
C:
"""
    )
    sc = SymbolCollection()
    sc.load_yaml(file)
    assert sc.find_one("A")
    b = sc.find_one("B")
    assert b
    assert b.source == "coingecko"
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


def test_add_with_wrong_type():
    sc = SymbolCollection()
    with pytest.raises(ValueError):
        sc.add(1)  # type: ignore


def test_add_with_duplicate_names_in_new_symbols():
    sc = SymbolCollection()
    with pytest.raises(ValueError):
        sc.add([Symbol("A"), Symbol("A")])


def test_add_with_duplicate_names_in_existing_plus_new_symbols():
    sc = SymbolCollection([Symbol("A")])
    with pytest.raises(ValueError):
        sc.add(Symbol("A"))


def test_find_and_find_one(tmp_path):
    file = tmp_path / "symbols.yaml"
    file.write_text(
        """
A:
B:
    aliases: [X]
BB:
C:  # Will be overwritten by the second C
b:  # This, however, will be separate from the earlier B, because it's lower-case
C:
    aliases: [X]
"""
    )
    sc = SymbolCollection()
    sc.load_yaml(file)

    # find:
    assert sc.find("Z") == []
    assert len(sc.find("X")) == 2
    # There will only be 1 C name bc yaml expects unique keys and pyyaml silently
    # overwrites the first entry when it encounters the second by the same name:
    assert len(sc.find("C")) == 1
    # There will, however, be two B/b symbols because B and b qualify as different keys
    # in the load_yaml method but the `matches` method in `Symbol` ignores case:
    assert len(sc.find("B")) == 2
    assert len(sc.find("b")) == 2

    # find_one:
    assert sc.find_one("A")
    assert sc.find_one("A") == sc.find_one("a")  # find ignores case
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
