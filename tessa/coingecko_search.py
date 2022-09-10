"""Everything related to searching via coingecko."""

import functools
from pycoingecko import CoinGeckoAPI
from tessa.symbol import Symbol


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
            type_="crypto",
            query=x["id"],
            aliases=[x["id"], x["name"]],
        )
        for x in matches
    ]


def coingecko_search(query: str) -> dict:
    """Help find coingecko ids.

    Args:

    - query: The query to search for.

    Example call:

    ```
    from tessa.coingecko_search import coingecko_search
    r = coingecko_search("jenny")
    r["coingecko_other_name"][0].price_latest()
    ```
    """
    res = {}
    for category in ("symbol", "name"):
        for prefix, find_in in (
            ("coingecko_perfect", lambda x: query.lower() == x.lower()),
            ("coingecko_other", lambda x: query.lower() in x.lower()),
        ):
            matches = [x for x in get_symbol_map() if find_in(x[category])]
            if matches:
                res[f"{prefix}_{category}"] = _matches_to_symbols(matches)
    return res
