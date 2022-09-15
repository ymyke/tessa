"""Tests relating to `tessa.search` (as opposed to the underlying `investing_search` or
`coingecko_search`).
"""

# pylint: disable=missing-function-docstring

import pytest
from tessa import search
from tessa.symbol import Symbol
from tessa.search import SearchResult
from tessa import set_enabled_investing_types


@pytest.mark.parametrize(
    "querytype, symbol",
    [
        # These test the results returned by investpy's direct searches:
        ("certificate", "NL0006454928"),
        ("commodity", "Palladium"),
        ("bond", "Argentina 1Y"),
        ("currency_cross", "USD/AED"),
        ("index", "BKART"),
        ("etf", "AAA"),
        ("stock", "AAPL"),
        ("fund", "0P0000A29Q"),
        # These test the results returned by investpy's searchobj-based search:
        ("searchobj", "PINS"),
        # These test the results returned by coingecko's direct searches:
        ("crypto", "ETH"),
    ],
)
@pytest.mark.net
def test_working_symbols_are_returned_by_search(querytype: str, symbol: str):
    """For each possible type of symbol, will we get a working `Symbol` object?"""
    try:
        set_enabled_investing_types([querytype])
    except ValueError:
        pass  # So we can run the "searchobj" and "crypto" cases
    res = search(symbol)
    assert isinstance(res, SearchResult)
    # pylint: disable=protected-access
    s = [s for s in res.symbols if s._querytype == querytype][0]
    assert isinstance(s, Symbol)
