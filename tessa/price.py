"""Generic module that provides central access to the underlying individual APIs."""

import functools
from typing import Tuple

import investpy
import pandas as pd
import pendulum
from frozendict import frozendict
from investpy.utils.search_obj import SearchObj
from pycoingecko import CoinGeckoAPI

from . import rate_limiter  # pylint: disable=unused-import


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

    wrapped.cache_info = func.cache_info
    wrapped.cache_clear = func.cache_clear
    return wrapped


def get_currency_from_dataframe(df: pd.DataFrame) -> str:
    """Get currency from investpy dataframe."""
    currencies = list(df["Currency"].unique())
    if len(currencies) > 1:
        raise ValueError(f"Expected only one currency, got {currencies}.")
    return currencies[0]


def turn_price_history_into_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Turn investpy dataframe into a pricing dataframe in the form that we use it."""
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
def price_history(
    query: str, type_: str, country: str = None, currency_preference: str = "usd"
) -> Tuple[pd.DataFrame, str]:
    """Get price history and return tuple of dataframe and currency.

    Args:

    - query: FIXME
    - type_: FIXME

    Optional/situational args:

    - currency_preference: The currency to the prices should be returned in. The
      effective currency might differ and will be returned in the second return value.
    - country: Used w types "stock" and similar.

    FIXME Make this function as simple and straightforward as possible and then add
    another function that is as lenient and forgiving as possible and tries to assume
    reasonable defaults wherever possible. I.e., set country to us if undefined or cycle
    through types if none given.
    """
    # FIXME Make sure we always return a copy of the resulting dataframe so the cached
    # original does not get modified by the caller.

    if type_ == "crypto":
        return (
            turn_prices_list_into_df(
                CoinGeckoAPI().get_coin_market_chart_by_id(
                    # id=symbol_to_id(query), # FIXME For the lenient version?
                    id=query,
                    vs_currency=currency_preference,
                    days="max",
                    interval="daily",
                )["prices"]
            ),
            currency_preference,
        )

    # Investing / investpy:

    investing_types = ["stock", "etf", "fund", "crypto", "bond", "index", "certificate"]
    commonargs = {
        "from_date": "01/01/1900",
        "to_date": pendulum.now().strftime("%d/%m/%Y"),
    }

    if type_ in investing_types:
        commonargs["country"] = country
        commonargs[type_] = query
        prices = getattr(investpy, "get_" + type_ + "_historical_data")(**commonargs)
        return (
            turn_price_history_into_prices(prices),
            get_currency_from_dataframe(prices),
        )

    if type_ == "searchobj":
        searchobj = SearchObj(**query)
        return (
            turn_price_history_into_prices(
                searchobj.retrieve_historical_data(**commonargs),
            ),
            searchobj.retrieve_currency(),
        )

    raise ValueError(f"Unsupported asset type {type_}.")
