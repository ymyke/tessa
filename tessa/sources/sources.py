"""Source class and related functions as well as the directory of all sources
(`sourcelist`).
"""
from dataclasses import dataclass
from typing import Callable, Dict, Generator
from .. import SourceType
from ..utils.rate_limiter import RateLimiter
from ..price import yahoo as yahooprice, coingecko as coingeckoprice
from ..search import yahoo as yahoosearch, coingecko as coingeckosearch


@dataclass
class Source:
    """A `Source` encapsulates everything related to a source such as Yahoo or
    Coingecko.
    """

    get_price_history: Callable
    """Callback to retrieve price history."""

    get_search_results: Callable
    """Callback to retrieve search results."""

    rate_limiter: RateLimiter
    """Rate limiter object."""


sourcelist: Dict[SourceType, Source] = {
    "yahoo": Source(
        get_price_history=yahooprice.get_price_history,
        get_search_results=yahoosearch.yahoo_search,
        rate_limiter=RateLimiter(0.2),
    ),
    "coingecko": Source(
        get_price_history=coingeckoprice.get_price_history,
        get_search_results=coingeckosearch.coingecko_search,
        rate_limiter=RateLimiter(2.5),
    ),
}
"""The dictionary of all know sources. To be accessed via the functions in this
module.
"""


def get_source(name: SourceType) -> Source:
    """Get a specific source."""
    try:
        return sourcelist[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown source. Supported source are: {sourcelist.keys()}"
        ) from exc


def get_all_sources() -> Generator:
    """Get all the known sources."""
    for source in sourcelist.values():
        yield source


def reset_rate_limiters() -> None:
    """Reset the rate limiters of all sources."""
    for source in get_all_sources():
        source.rate_limiter.reset()
