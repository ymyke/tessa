"""Generic module that provides central access to the underlying individual APIs."""

import datetime
import functools
from frozendict import frozendict
import pandas as pd
import investpy
from investpy.utils.search_obj import SearchObj

# import api.investing
# import api.yahooscraper


def freezeargs(func):
    """Transform mutable dictionary into immutable useful to be compatible with cache.

    Source:
    https://stackoverflow.com/questions/6358481/using-functools-lru-cache-with-dictionary-arguments
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        args = tuple(
            [frozendict(arg) if isinstance(arg, dict) else arg for arg in args]
        )
        kwargs = {
            k: frozendict(v) if isinstance(v, dict) else v for k, v in kwargs.items()
        }
        return func(*args, **kwargs)

    return wrapped


def turn_price_history_into_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Small helper function to turn what investpy returns into a pricing dataframe in
    the form that we use it.
    """
    rf = df.copy()  # To prevent the SettingWithCopyWarning
    rf = rf[["Close"]]
    rf.index = pd.to_datetime(rf.index, utc=True)
    rf.index.name = "date"
    rf.rename(columns={"Close": "close"}, inplace=True)
    return rf


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
    name: str, namespace: str, type: str, country: str = None
) -> pd.DataFrame:
    if namespace == "investing":
        fromdate = "01/01/1900"
        todate = datetime.datetime.now().strftime("%d/%m/%Y")
        commonargs = {"country": country, "from_date": fromdate, "to_date": todate}
        if type == "stock":
            prices = investpy.get_stock_historical_data(stock=name, **commonargs)
        elif type == "etf":
            prices = investpy.get_etf_historical_data(etf=name, **commonargs)
        elif type == "fund":
            prices = investpy.get_fund_historical_data(fund=name, **commonargs)
        else:
            raise ValueError(f"Unsupported equity type {type}.")
        # time.sleep(2)
        return turn_price_history_into_prices(prices)
    elif namespace == "investpy_searchobj":
        # FIXME Is name really the right parameter for the searchobj spec? What if this
        # was in a class, what would we use as the name then?
        fromdate = "01/01/1900"
        todate = datetime.datetime.now().strftime("%d/%m/%Y")
        return turn_price_history_into_prices(
            SearchObj(**name).retrieve_historical_data(fromdate, todate)
        )
