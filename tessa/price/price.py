"""Retrieve price information."""

from __future__ import annotations
from functools import lru_cache, wraps
from typing import Union, TYPE_CHECKING
import pandas as pd
from . import PriceHistory, PricePoint
from .. import sources

if TYPE_CHECKING:
    from .. import SourceType


def custom_cache_wrapper(func):
    """To preserve the function's signature _and_ give access to `cache_clear` etc."""
    cached_func = lru_cache(maxsize=None)(func)
    wrapped_func = wraps(func)(cached_func)
    return wrapped_func


@custom_cache_wrapper
def price_history(
    query: str,
    source: SourceType = "yahoo",
    currency_preference: str = "USD",
) -> PriceHistory:
    """Get price history and return `PriceHistory`, i.e., a tuple of a dataframe with
    the price history and the effective currency. Note that the effective currency
    returned might differ from the currency_preference.

    - `query`: A query string that makes sense in combination with the source. E.g.,
      "BTC-USD" for "yahoo" or "bitcoin" for "coingecko".
    - `source`: The source to query. Defaults to "yahoo".
    - `currency_preference`: The currency the prices should be returned in; defaults
      to "USD". The effective currency might differ and will be returned in the second
      return value.
    """
    src = sources.get_source(source)
    src.rate_limiter.rate_limit()
    df, effective_currency = src.get_price_history_bruteforcefully(
        query, currency_preference
    )
    return PriceHistory(df.copy(), effective_currency.upper())
    # (Returning a copy of the dataframe so the cached original is preserved even if it
    # gets modified by the caller.)


def price_point(
    query: str,
    when: Union[str, pd.Timestamp],
    source: SourceType = "yahoo",
    currency_preference: str = "USD",
    max_date_deviation_days: Union[int, None] = 10,
) -> PricePoint:
    """Return the price at a given point in time given by `when`. Look for the closest
    point in time if the exact point in time is not found. Returns a `PricePoint`, i.e.,
    a tuple of the price, the effective timestamp of the price, and the currency.

    Raises a `ValueError` if the found date is more than `max_date_deviation_days` from
    `when`. Use `None` to disable this check.

    Arguments other than `when` are the same as with `price_history`.

    Example call:
    ```
    price_point("AAPL", "2020-01-01")
    ```
    """
    df, currency = price_history(query, source, currency_preference)

    when = pd.Timestamp(when)
    if df.index.tz is not None:  # Ensure when matches the timezone of df.index
        when = when.tz_localize("UTC") if when.tz is None else when.tz_convert("UTC")

    nearest_index = df.index.get_indexer([when], method="nearest")[0]
    found_date = df.index[nearest_index]

    if (
        max_date_deviation_days is not None
        and abs((found_date - when).days) > max_date_deviation_days
    ):
        raise ValueError(
            f"Found date {found_date} is more than {max_date_deviation_days} days away "
            f"from requested date {when}"
        )

    price = df.iloc[nearest_index]
    return PricePoint(when=found_date, price=float(price.iloc[0]), currency=currency)


def price_point_strict(
    query: str,
    when: str,
    source: SourceType = "yahoo",
    currency_preference: str = "USD",
) -> PricePoint:
    """Same as `price_point` but will raise a `KeyError` if no price is found. This
    function is offered for backwards compatibility and is largely obsolete with the
    introduction of `max_date_deviation_days` in `price_point`.
    """
    try:
        return price_point(
            query, when, source, currency_preference, max_date_deviation_days=0
        )
    except ValueError as e:
        raise KeyError(f"No price found for {query} at {when}") from e


def price_latest(
    query: str,
    source: SourceType = "yahoo",
    currency_preference: str = "USD",
) -> PricePoint:
    """Same as `price_point` but will return the latest price."""
    df, currency = price_history(query, source, currency_preference)
    return PricePoint(
        when=df.iloc[-1].name, price=float(df.iloc[-1]["close"]), currency=currency
    )
