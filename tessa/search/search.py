"""Unified search."""

from .investing import investing_search
from .coingecko import coingecko_search
from ..search_result import SearchResult


def search(query: str, silent: bool = False) -> SearchResult:
    """Unified search function. Returns a `tessa.search_result.SearchResult`.

    - `query`: The string to search for. (Note that this query attribute has a different
      semantics to the query attribute in the `Symbol` class.)
    - `silent`: No print output if True.
    """
    res = investing_search(query, silent)
    res.add_symbols(coingecko_search(query).symbols)
    if not silent:
        res.p()
    return res
