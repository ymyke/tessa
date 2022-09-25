"""Unified search."""

from . import SearchResult

# from .. import sources    <- gets imported later to prevent circular dependency


def search(query: str, silent: bool = False) -> SearchResult:
    """Unified search function. Returns a `tessa.search.SearchResult`.

    - `query`: The string to search for. (Note that this query attribute has a different
      semantics to the query attribute in the `Symbol` class.)
    - `silent`: No print output if True.
    """
    from .. import sources  # pylint: disable=import-outside-toplevel

    res = SearchResult(query, [])
    for source in sources.get_all_sources():
        res.add_symbols(source.get_search_results(query).symbols)
    if not silent:
        res.p()
    return res
