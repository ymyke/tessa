"""Generic module that provides central access to the underlying individual APIs."""

from datetime import datetime
import functools
from frozendict import frozendict
import pandas as pd
import investpy
from investpy.utils.search_obj import SearchObj
from pycoingecko import CoinGeckoAPI
from . import rate_limiter # pylint: disable=unused-import

# import api.investing
# import api.yahooscraper


def freezeargs(func):
    """Transform mutable dictionary into immutable useful to be compatible with cache.

    Based on:
    https://stackoverflow.com/questions/6358481/using-functools-lru-cache-with-dictionary-arguments
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        return func(
            *[frozendict(x) if isinstance(x, dict) else x for x in args],
            **{
                k: frozendict(v) if isinstance(v, dict) else v
                for k, v in kwargs.items()
            },
        )

    return wrapped


def turn_price_history_into_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Small helper function to turn what investpy returns into a pricing dataframe in
    the form that we use it.
    """
    df = df.copy()  # To prevent the SettingWithCopyWarning
    df = df[["Close"]]
    df.index = pd.to_datetime(df.index, utc=True)
    df.index.name = "date"
    df.rename(columns={"Close": "close"}, inplace=True)
    return df


def turn_prices_list_into_df(prices: list) -> pd.DataFrame:
    """Turn price list returned by Coingecko API into a pricing dataframe in the form
    that we use.
    """
    df = pd.DataFrame(prices)
    df.columns = ["date", "close"]
    df["date"] = pd.to_datetime(df["date"] / 1000, unit="s", utc=True)
    df = df.set_index("date")
    return df


# @cache
# def price_history(ticker: str) -> pd.DataFrame:
#     """Get price history for ticker and return dataframe.

#     Caches the result in memory therefore returns a copy of the resulting dataframe so
#     the cached original doesn't change when the dataframe is modified.
#     """
#     # FIXME: Look up ticker in tickerconfig.py and use the correct API.
#     return api.investing.get_pricehistory(ticker).copy()


@freezeargs
@functools.cache
def price_history(query: str, type_: str, country: str = None) -> pd.DataFrame:
    """Get price history and return dataframe.

    Args:

    - query: FIXME
    - type_: FIXME

    Optional/situational args:

    - country: Used w types "stock" and similar.

    FIXME Make this function as simple and straightforward as possible and then add
    another function that is as lenient and forgiving as possible and tries to assume
    reasonable defaults wherever possible. I.e., set country to us if undefined or cycle
    through types if none given.
    """
    # FIXME Make sure we always return a copy of the resulting dataframe so the cached
    # original does not get modified by the caller.

    if type_ == "crypto":
        try:
            return turn_prices_list_into_df(
                CoinGeckoAPI().get_coin_market_chart_by_id(
                    # id=symbol_to_id(query), # FIXME Something for the lenient version?
                    id=query,
                    vs_currency="chf",  # FIXME What to do here?
                    days="max",
                    interval="daily",
                )["prices"]
            )
        except ValueError as exc:
            raise RuntimeError(f"Failed to look up crypto ticker {query}") from exc

    # Investing / investpy:

    investing_types = ["stock", "etf", "fund", "crypto", "bond", "index", "certificate"]
    commonargs = {
        "from_date": "01/01/1900",
        "to_date": datetime.now().strftime("%d/%m/%Y"),
    }

    if type_ in investing_types:
        commonargs["country"] = country
        commonargs[type_] = query
        return turn_price_history_into_prices(
            getattr(investpy, "get_" + type_ + "_historical_data")(**commonargs)
        )

    if type_ == "searchobj":
        return turn_price_history_into_prices(
            SearchObj(**query).retrieve_historical_data(**commonargs)
        )

    raise ValueError(f"Unsupported equity type {type_}.")
