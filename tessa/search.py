"""Unified search."""

from .investing_search import investing_search
from .coingecko_search import coingecko_search
from .investing_types import InvestingType, ListOrItemOptional
from .search_result import SearchResult


def search(
    query: str,
    types: ListOrItemOptional[InvestingType] = None,
    countries: ListOrItemOptional[str] = None,
    silent: bool = False,
) -> SearchResult:
    """Unified search function. Returns a `tessa.search_result.SearchResult`.

    Standard args:

    - `query`: The string to search for. (Note that this query attribute has a different
      semantics to the query attribute in the `Symbol` class.)
    - `silent`: No print output if True.

    Situational, optional args: Use the following args to filter for countries or types
    in order to go easy on the underlying APIs. Note that you can also filter on the
    returned `SearchResult` object.

    - `countries`: One or a list of countries to search in.
    - `types`: One or a list of types such as "stock" or "etf" to search for. See
      `investing_types.InvestingType` for a complete list.

    Both `countries` and `types` will only be used for the searches on investing. They
    can be a list or a string. They can also be `None`, in which case all types (called
    products in investpy) or countries are searched. `types` "type-hints" possible
    strings via `investing_types.InvestingType`.

    Example calls:

    ```
    from tessa import search
    r1 = search("soft")
    r2 = search("carbon", types=["etf", "fund"])
    r3 = search("btc")
    ```
    """
    res = investing_search(query, countries=countries, types=types)
    res.add_symbols(coingecko_search(query).symbols)
    if not silent:
        res.p()
    return res
