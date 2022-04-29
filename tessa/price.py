"""Price information."""

import functools
from typing import Tuple
import pandas as pd
from . import investing
from . import coingecko
from .freezeargs import freezeargs
from .rate_limiter import rate_limit


@freezeargs
@functools.cache
def price_history(
    query: str, type_: str, country: str = None, currency_preference: str = "usd"
) -> Tuple[pd.DataFrame, str]:
    """Get price history and return tuple of dataframe and currency.

    Args:

    - query: A query string that makes sense in combination with the type. E.g.,
      "bitcoin" for "crypto", "AAPL" for a "stock", or a `investpy.utils.search_obj`
      object's string representation for "searchobj".
    - type_: Any of ["crypto", "stock", "etf", "fund", "crypto", "bond", "index",
      "certificate", "searchobj"].

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
    elif type_ in investing.VALID_TYPES:
        df, effective_currency = investing.get_price_history(query, type_, country)
    elif type_ == "searchobj":
        df, effective_currency = investing.get_price_history_from_searchobj(query)
    else:
        raise ValueError(f"Unsupported asset type {type_}.")

    return (df.copy(), effective_currency)
    # (Returning a copy of the dataframe so the cached original is preserved even if it
    # gets modified by the caller.)
