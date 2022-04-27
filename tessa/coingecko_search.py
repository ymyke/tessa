"""Everything related to searching via coingecko."""

import functools
from pycoingecko import CoinGeckoAPI


@functools.cache
def get_symbol_map() -> dict:
    """Get the symbol map. Separate function to use caching, so the API doesn't get
    hit too often.
    """
    return CoinGeckoAPI().get_coins_list()


def search_for_id(query: str, silent: bool = False) -> dict:
    """Help find coingecko ids.

    Args:

    - query: The query to search for.
    - silent: No print output if True.

    Example call:
    ```
    from tessa.coingecko_search import search_for_id
    r = search_for_id("jenny")
    ```
    """
    res = {}
    for category in ("symbol", "name"):
        for prefix, find_in in (
            ("perfect", lambda x: query.lower() == x.lower()),
            ("other", lambda x: query.lower() in x.lower()),
        ):
            categoryname = f"{prefix}_{category}"
            matches = [x for x in get_symbol_map() if find_in(x[category])]
            if matches:
                res[categoryname] = matches
                if not silent:
                    print(f"'{categoryname}' matches: {len(matches)}")
    return res
