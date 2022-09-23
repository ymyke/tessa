"""Everything related to searching via coingecko."""

import functools
from pycoingecko import CoinGeckoAPI
from ..symbol import Symbol
from . import SearchResult


@functools.lru_cache(maxsize=None)
def get_symbol_map() -> list:
    """Get the symbol map. Separate function to use caching, so the API doesn't get
    hit too often.
    """
    return CoinGeckoAPI().get_coins_list()


def _matches_to_symbols(matches: list) -> list:
    """Convert a list of Coingecko matches to a list of `Symbol`s."""
    return [
        Symbol(
            name=x["symbol"],
            source="coingecko",
            query=x["id"],
            aliases=[x["id"], x["name"]],
        )
        for x in matches
    ]


def coingecko_search(query: str) -> SearchResult:
    """Find coingecko ids that match `query` somehow. Returns `SearchResult`."""
    # Note: No rate limiting here because search is simply a lookup in the symbol map,
    # which gets cached in the first retrieval.
    matches = [
        entry
        for entry in get_symbol_map()
        if query.lower() in entry["name"].lower()
        or query.lower() in entry["symbol"].lower()
    ]
    return SearchResult(query=query, symbols=_matches_to_symbols(matches))
