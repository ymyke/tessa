"""Source class and related functions."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Generator, TYPE_CHECKING
import warnings
import requests
from .sourcetype import SourceType
from .rate_limiter import RateLimiter
from ..price.types import RateLimitHitError

if TYPE_CHECKING:
    from ..price import PriceHistory


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

    def get_price_history_bruteforcefully(
        self, query: str, currency_preference: str = "USD"
    ) -> PriceHistory:
        """Variant of `get_price_history` that will ignore some server-side errors
        (which often seem to be intermittent, at least on Coingecko) and just
        retries.
        """
        max_tries = 100
        tries = 0
        while True:
            tries += 1
            try:
                res = self.get_price_history(query, currency_preference)
                self.rate_limiter.reset_back_off()
                return res
            except requests.HTTPError as exc:
                if exc.response.status_code not in [504, 503, 502]:
                    raise exc
                if tries > max_tries:
                    raise ConnectionError(
                        f"Cannot access source, even after {max_tries} tries. "
                        "(Reraising from latest exception, there might have been "
                        "several.)"
                    ) from exc
                warnings.warn(
                    f"Latest request raised for status code {exc.response.status_code}."
                    f" Retrying ({tries}/{max_tries}).",
                    RuntimeWarning,
                )
            except RateLimitHitError:
                warnings.warn(
                    "Rate limit hit (429). "
                    f"Backing off {self.rate_limiter.back_off_time} seconds."
                )
                self.rate_limiter.back_off()


def get_source(name: SourceType) -> Source:
    """Get a specific source."""
    # Prevent circular dependencies -- pylint: disable=import-outside-toplevel
    from .sources_directory import SOURCES_DIRECTORY

    try:
        return SOURCES_DIRECTORY[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown source '{name}'. Supported source are: {SOURCES_DIRECTORY.keys()}"
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
