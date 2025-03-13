"""Yahoo Finance search"""

from ..search import SearchResult


def yahoo_search(query: str) -> SearchResult:
    print(
        "\nWARNING: Yahoo Finance search is not implemented due to their search result page changing to being JavaScript-based. Returning empty search result for Yahoo Finance.\n"
    )
    return SearchResult(query, [])
