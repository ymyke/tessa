"""Test the investing_types module."""

# pylint: disable=missing-function-docstring

import pytest
from tessa.utils.investing_types import (
    set_enabled_investing_types,
    get_enabled_investing_types,
    is_valid,
    singularize,
    pluralize,
    pluralize_list,
)


def test_set_enabled_investing_types_works_with_valid_types():
    set_enabled_investing_types(["stock", "etf"])
    assert get_enabled_investing_types() == ["stock", "etf"]


def test_set_enabled_investing_types_raises_with_invalid_input():
    with pytest.raises(ValueError):
        set_enabled_investing_types(["invalidtype"])


def test_is_valid():
    assert is_valid("stock")
    assert not is_valid("xxx")


def test_singularize():
    assert singularize("etfs") == "etf"


def test_pluralize():
    assert pluralize("fund") == "funds"


def test_pluralize_list():
    assert [
        singularize(x) for x in pluralize_list(get_enabled_investing_types())
    ] == get_enabled_investing_types()
