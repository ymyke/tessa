"""Price information."""

import functools
from typing import Union, Dict, Callable
import pandas as pd

from . import coingecko, yahoo
from . import PriceHistory, PricePoint
from .. import SourceType
from ..utils.freezeargs import freezeargs
from ..utils.rate_limiter import rate_limit


# FIXME Move this to a separate file? Would it make sense to move this to the
# __init__.py??
SOURCE_TO_PRICE_HISTORY_MAP: Dict[SourceType, Callable] = {
    "yahoo": yahoo.get_price_history,
    "coingecko": coingecko.get_price_history,
}


@freezeargs
@functools.lru_cache(maxsize=None)
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
    - `currency_preference`: The currency to the prices should be returned in; defaults
      to "USD". The effective currency might differ and will be returned in the second
      return value.
    """
    rate_limit(source)
    try:
        df, effective_currency = SOURCE_TO_PRICE_HISTORY_MAP[source](
            query, currency_preference
        )
    except KeyError as exc:
        raise ValueError(
            "Unknown source. Supported source are: "
            f"{SOURCE_TO_PRICE_HISTORY_MAP.keys()}"
        ) from exc
    return PriceHistory(df.copy(), effective_currency.upper())
    # (Returning a copy of the dataframe so the cached original is preserved even if it
    # gets modified by the caller.)


def price_point(
    query: str,
    when: Union[str, pd.Timestamp],
    source: SourceType = "yahoo",
    currency_preference: str = "USD",
) -> PricePoint:
    """Return the price at a given point in time given by `when`. Look for the closest
    point in time if the exact point in time is not found. Returns a `PricePoint`, i.e.,
    a tuple of the price, the effective timestamp of the price, and the currency.

    Arguments other than `when` are the same as with `price_history`.

    Example call:
    ```
    price_point("AAPL", "2020-01-01")
    ```
    """
    df, currency = price_history(query, source, currency_preference)
    price = df.iloc[df.index.get_indexer([when], method="nearest")[0]]
    return PricePoint(when=price.name, price=float(price), currency=currency)


def price_point_strict(
    query: str,
    when: str,
    source: SourceType = "yahoo",
    currency_preference: str = "USD",
) -> PricePoint:
    """Same as `price_point` but will return either the price at the exact point in time
    or raise a KeyError.
    """
    df, currency = price_history(query, source, currency_preference)
    return PricePoint(
        when=df.loc[when].name, price=float(df.loc[when]["close"]), currency=currency
    )


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
