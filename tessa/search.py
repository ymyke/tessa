"""Unified search."""

from .investing_search import investing_search
from .coingecko_search import coingecko_search
from .investing_types import InvestingType, ListOrItemOptional


def search(
    query: str,
    types: ListOrItemOptional[InvestingType] = None,
    countries: ListOrItemOptional[str] = None,
    silent: bool = False,
) -> dict:
    """Unified search function.

    Standard args:

    - `query`: The string to search for.
    - `silent`: No print output if True.

    Situational, optional args:

    - `countries`: One or a list of countries to search in.
    - `types`: One or a list of types such as "stock" or "etf" to search for.
      See `investing_types.InvestingType` for a complete list.

    Both `countries` and `types` will only be used for the searches
    on investing. They can be a list or a string. They can also be `None`, in which case
    all types (called products in investpy) or countries are searched. `types`
    "type-hints" possible strings via `investing_types.InvestingType`.

    Returns:

    - dict of category names (str), each containing the `Symbol`s found in this
      category. Empty categories are omitted.

    Example calls:

    ```
    from tessa import search
    r1 = search("soft")
    r2 = search("carbon", types=["etf", "fund"])
    r3 = search("btc")
    ```
    """
    res = investing_search(
        query, countries=countries, types=types
    ) | coingecko_search(query)
    if not silent:
        for k, v in res.items():
            num = len(v) if isinstance(v, list) else v.shape[0]
            print(f"{num:5d} of {k}")
    return res
