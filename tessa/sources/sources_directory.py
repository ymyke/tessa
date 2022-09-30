"""The directory (i.e., dictionary) of all know sources. To be accessed via the
functions in `tessa.sources.sources`. This module is factored out so the directory can
be imported late within functions in order to prevent circular dependencies.
"""

from typing import Dict, Final
from .sources import Source
from .sourcetype import SourceType
from .rate_limiter import RateLimiter
from ..price import yahoo as yahooprice, coingecko as coingeckoprice
from ..search import yahoo as yahoosearch, coingecko as coingeckosearch

SOURCES_DIRECTORY: Final[Dict[SourceType, Source]] = {
    "yahoo": Source(
        get_price_history=yahooprice.get_price_history,
        get_search_results=yahoosearch.yahoo_search,
        rate_limiter=RateLimiter(0.5),
    ),
    "coingecko": Source(
        get_price_history=coingeckoprice.get_price_history,
        get_search_results=coingeckosearch.coingecko_search,
        rate_limiter=RateLimiter(2.5),
    ),
}
