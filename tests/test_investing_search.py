"""Test everything related to `investing_search` module.

Note that tests will hit the network and therefore will take a while to run.
"""

# pylint: disable=use-implicit-booleaness-not-comparison,invalid-name

from tessa.investing_search import (
    investing_search,
    search_name_or_symbol,
    search_for_searchobjs,
)
from tessa.symbols import Symbol


# ----- investing_search related -----


def test_investing_search():
    """It returns the correct combined result."""
    res = investing_search("AAPL", countries="united states", products="stocks")
    assert len(res["investing_stocks_by_symbol"]) == 1
    assert len(res["investing_searchobj_perfect"]) == 1


# ----- search_name_or_symbol related -----


def test_searchnamesymbol_non_existent_name():
    """It returns an empty list if the name doesn't exist."""
    assert search_name_or_symbol("non_existent_name") == {}


def test_searchnamesymbol():
    """It returns a dictionary with dataframes and the filtering works correctly."""
    fullres = search_name_or_symbol("carbon")
    assert fullres != {}
    assert isinstance(fullres["investing_stocks_by_full_name"][0], Symbol)
    r1 = search_name_or_symbol("carbon", countries=["united states", "switzerland"])
    assert r1 != {}
    assert len(fullres["investing_stocks_by_full_name"]) > len(
        r1["investing_stocks_by_full_name"]
    )
    r2 = search_name_or_symbol(
        "carbon", countries=["united states", "switzerland"], products=["etfs"]
    )
    assert r2 != {}
    assert len(fullres) > len(r2)


# ----- search_for_searchobjs related -----


def test_searchobjs_non_existent_name():
    """It returns an empty list if the name doesn't exist."""
    assert search_for_searchobjs("non_existent_name") == {}


def test_searchobjs_non_existent_country():
    """It returns an empty list if the country doesn't exist."""
    assert search_for_searchobjs("one", "non_existent_country") == {}


def test_searchobjs():
    """It returns a category with a list of `Symbol` objects."""
    res = search_for_searchobjs("one", "switzerland")["investing_searchobj_perfect"]
    assert len(res) == 1
    assert res[0].query == {
        "id_": 949673,
        "name": "ONE swiss bank SA",
        "symbol": "ONE",
        "country": "switzerland",
        "tag": "/equities/banque-profil-de-gestion-sa",
        "pair_type": "stocks",
        "exchange": "Switzerland",
    }


def test_searchobjs_filter_products():
    """It works with different kinds of products filters."""
    assert search_for_searchobjs("one", "switzerland", products="etfs") == {}
    assert (
        search_for_searchobjs("one", "switzerland", products=["etfs", "stocks"]) != {}
    )
    assert (
        search_for_searchobjs(
            "one", "switzerland", products=["etfs", "stocks", "non_existent_product"]
        )
        != {}
    )
