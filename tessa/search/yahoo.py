"""Yahoo Finance search"""

import warnings
from ..search import SearchResult


def yahoo_search(query: str) -> SearchResult:
    warnings.warn(
        "Yahoo Finance search is not implemented due to their search result page changing to being JavaScript-based. Returning empty search result for Yahoo Finance.",
        UserWarning,
    )
    return SearchResult(query, [])
