"""Unified search."""

from .coingecko import coingecko_search
from . import SearchResult


def search(query: str, silent: bool = False) -> SearchResult:
    """Unified search function. Returns a `tessa.search.SearchResult`.

    !! ONLY SUPPORTS COINGECKO CURRENTLY BECAUSE INVESTPY IS END OF LIFE !!

    - `query`: The string to search for. (Note that this query attribute has a different
      semantics to the query attribute in the `Symbol` class.)
    - `silent`: No print output if True.
    """
    # FIXME Add similar map to the one in price.
    # FIXME Add yahoo search somehow?
    res = coingecko_search(query)
    if not silent:
        res.p()
    return res
