"""Test everything related to `investing_search` module.

Note that tests will hit the network and therefore will take a while to run.
"""

# pylint: disable=invalid-name,missing-docstring

import pytest
from tessa.search.investing import (
    investing_search,
    search_name_or_symbol,
    search_for_searchobjs,
)
from tessa.symbol import Symbol
from tessa.search import SearchResult
from tessa import set_enabled_investing_types_temporarily


@pytest.mark.net
def test_investing_search_returns_correct_combined_results():
    with set_enabled_investing_types_temporarily(["stock"]):
        res = investing_search("AAPL")
    assert isinstance(res, SearchResult)
    assert len(res.symbols) > 0
    # Make sure there are results from both investing-search sub-functions:
    # pylint: disable=protected-access
    assert any(s._Symbol__querytype == "stock" for s in res.symbols)  # type: ignore
    assert any(s._Symbol__querytype == "searchobj" for s in res.symbols)  # type: ignore


# ----- search_name_or_symbol related -----


@pytest.mark.net
def test_searchnamesymbol_returns_empty_result_for_non_existent_query():
    with set_enabled_investing_types_temporarily(["stock"]):
        assert search_name_or_symbol("non_existent_name").symbols == []


@pytest.mark.net
def test_searchnamesymbol_returns_plausible_results_inluding_when_filtering():
    with set_enabled_investing_types_temporarily(["stock", "fund", "etf"]):
        r0 = search_name_or_symbol("carbon")
    assert len(r0.symbols) > 0
    assert isinstance(r0.symbols[0], Symbol)
    with set_enabled_investing_types_temporarily(["stock", "fund"]):
        r1 = search_name_or_symbol("carbon")
    assert len(r1.symbols) > 0
    assert len(r0.symbols) > len(r1.symbols)
    with set_enabled_investing_types_temporarily(["stock"]):
        r2 = search_name_or_symbol("carbon")
    assert len(r2.symbols) > 0
    assert len(r0.symbols) > len(r2.symbols)
    assert len(r1.symbols) > len(r2.symbols)


# ----- search_for_searchobjs related -----


@pytest.mark.net
def test_searchobjs_returns_empty_result_for_non_existent_query():
    assert search_for_searchobjs("non_existent_name").symbols == []


@pytest.mark.net
def test_searchobjs_returns_list_of_correct_symbol_objects_including_searchobj_query():
    besthits = (
        search_for_searchobjs("one").filter(country="switzerland").buckets[0].symbols
    )
    assert len(besthits) == 1
    assert isinstance(besthits[0], Symbol)
    assert besthits[0].query == {
        "id_": 949673,
        "name": "ONE swiss bank SA",
        "symbol": "ONE",
        "country": "switzerland",
        "tag": "/equities/banque-profil-de-gestion-sa",
        "pair_type": "stocks",
        "exchange": "Switzerland",
    }
