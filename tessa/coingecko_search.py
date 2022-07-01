"""Everything related to searching via coingecko."""

import functools
from pycoingecko import CoinGeckoAPI


@functools.lru_cache(maxsize=None)
def get_symbol_map() -> list:
    """Get the symbol map. Separate function to use caching, so the API doesn't get
    hit too often.
    """
    return CoinGeckoAPI().get_coins_list()


def coingecko_search(query: str) -> dict:
    """Help find coingecko ids.

    Args:

    - query: The query to search for.

    Example call:
    
    ```
    from tessa import coingecko_search
    r = coingecko_search("jenny")
    # Then use r["other_name][0]["id"] to get the coingecko id to get price information.
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
                res[f"{prefix}_{category}"] = matches
    return res
