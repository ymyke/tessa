"""Tests relating to tessa.search (as opposed to the underlying investing_search or
coingecko_search).
"""

# pylint: disable=missing-function-docstring

import pytest
from tessa import search
from tessa.symbols import Symbol


@pytest.mark.parametrize(
    "type_, symbol",
    [
        # These test the results returned by investpy's direct searches:
        ("investing_certificates_by_symbol", "NL0006454928"),
        ("investing_commodities_by_name", "Palladium"),
        ("investing_bonds_by_name", "Argentina 1Y"),
        ("investing_currency_crosses_by_name", "USD/AED"),
        ("investing_indices_by_symbol", "BKART"),
        ("investing_etfs_by_symbol", "AAA"),
        ("investing_stocks_by_symbol", "AAPL"),
        ("investing_funds_by_symbol", "0P0000A29Q"),
        # These test the results returned by investpy's searchobj-based search:
        ("investing_searchobj_perfect", "PINS"),
        # These test the results returned by coingecko's direct searches:
        ("coingecko_perfect_symbol", "ETH"),
    ],
)
@pytest.mark.net
def test_working_symbols_are_returned_by_search(type_: str, symbol: str):
    """For each possible type of symbol, will we get a working `Symbol` object?"""
    s = search(symbol)[type_][0]
    assert isinstance(s, Symbol)
    assert isinstance(s.price_latest(), tuple)
