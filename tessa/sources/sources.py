"""Source class and related functions."""

from dataclasses import dataclass
from typing import Callable, Generator
from .sourcetype import SourceType
from .rate_limiter import RateLimiter


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


def get_source(name: SourceType) -> Source:
    """Get a specific source."""
    # Prevent circular dependencies -- pylint: disable=import-outside-toplevel
    from .sources_directory import SOURCES_DIRECTORY

    try:
        return SOURCES_DIRECTORY[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown source. Supported source are: {SOURCES_DIRECTORY.keys()}"
        ) from exc


def get_all_sources() -> Generator:
    """Get all the known sources."""
    # Prevent circular dependencies -- pylint: disable=import-outside-toplevel
    from .sources_directory import SOURCES_DIRECTORY

    for source in SOURCES_DIRECTORY.values():
        yield source


def reset_rate_limiters() -> None:
    """Reset the rate limiters of all sources."""
    for source in get_all_sources():
        source.rate_limiter.reset()
