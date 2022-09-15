"""Price information."""

import functools
from typing import Union, NamedTuple, Optional
import pandas as pd

from . import coingecko, investing
from .. import QueryType, CountryName
from ..types import investing_types
from ..utils.freezeargs import freezeargs
from ..utils.rate_limiter import rate_limit


PriceHistory = NamedTuple("PriceHistory", [("df", pd.DataFrame), ("currency", str)])
PricePoint = NamedTuple(
    "PricePoint", [("when", pd.Timestamp), ("price", float), ("currency", str)]
)


@freezeargs
@functools.lru_cache(maxsize=None)
def price_history(
    query: str,
    type_: QueryType,
    country: Optional[CountryName] = None,
    currency_preference: str = "usd",
) -> PriceHistory:
    """Get price history and return tuple of dataframe and currency.

    Args:

    - query: A query string that makes sense in combination with the type. E.g.,
      "bitcoin" for "crypto", "AAPL" for a "stock", or a `investpy.utils.search_obj`
      object's string representation for "searchobj".
    - type_: A `QueryType` (i.e., including "searchobj").

    Optional/situational args:

    - currency_preference: The currency to the prices should be returned in. The
      effective currency might differ and will be returned in the second return value.
    - country: Used w types "stock" and similar.

    Examples combinations:

    - `type_="crypto", query="bitcoin"`: Use the ids the coingecko API uses ("btc" wont'
      work). Use `coingecko_search` to find the id.
    - `type_="stock", query="AAPL", country="united states"`: Use the investpy tickers.
      Use `investing_search` to find the right symbol.
    - `type_="stock", query="SREN.SW"`: Won't work, country parameter missing.
    - `type_="searchobj", query="{'id_': 995876, ...}"`: Use `investing_search` to
      find the SearchObj.

    Returns:

    - A tuple of a dataframe with the price history and the effective currency.
    - Note that the effective currency returned might differ from the
      currency_preference.

    Philosophy: This function tries to make no assumptions whatsoever. It doesn't try to
    be smart but simply takes what it gets and works with that.
    """
    rate_limit(type_)

    if type_ == "crypto":
        df, effective_currency = coingecko.get_price_history(query, currency_preference)
    elif investing_types.is_valid(type_):
        df, effective_currency = investing.get_price_history(query, type_, country)
    elif type_ == "searchobj":
        df, effective_currency = investing.get_price_history_from_searchobj(query)
    else:
        raise ValueError(
            f"Unsupported asset type '{type_}'; these are the supported types: "
            f"{', '.join(investing_types.get_singulars())}."
        )

    return PriceHistory(df.copy(), effective_currency.upper())
    # (Returning a copy of the dataframe so the cached original is preserved even if it
    # gets modified by the caller.)


def price_point(
    query: str,
    type_: QueryType,
    when: Union[str, pd.Timestamp],
    country: Optional[CountryName] = None,
    currency_preference: str = "usd",
) -> PricePoint:
    """Return the price at a given point in time given by `when`. Look for the closest
    point in time if the exact point in time is not found.

    Arguments other than `when` are the same as with `price_history`.

    Returns a PricePoint, i.e., a tuple of the price, the effective timestamp of the
    price, and the currency.

    Example call:
    ```
    price_point("AAPL", "stock", "2020-01-01", "united states")
    ```
    """
    df, currency = price_history(query, type_, country, currency_preference)
    price = df.iloc[df.index.get_indexer([when], method="nearest")[0]]
    return PricePoint(when=price.name, price=float(price), currency=currency)


def price_point_strict(
    query: str,
    type_: QueryType,
    when: str,
    country: Optional[CountryName] = None,
    currency_preference: str = "usd",
) -> PricePoint:
    """Same as `price_point` but will return either the price at the exact point in time
    or raise a KeyError.
    """
    df, currency = price_history(query, type_, country, currency_preference)
    return PricePoint(
        when=df.loc[when].name, price=float(df.loc[when]["close"]), currency=currency
    )


def price_latest(
    query: str,
    type_: QueryType,
    country: Optional[CountryName] = None,
    currency_preference: str = "usd",
) -> PricePoint:
    """Same as `price_point` but will return the latest price."""
    df, currency = price_history(query, type_, country, currency_preference)
    return PricePoint(
        when=df.iloc[-1].name, price=float(df.iloc[-1]["close"]), currency=currency
    )
