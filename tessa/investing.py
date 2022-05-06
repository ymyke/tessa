"""Everything investing-related (other than search)."""

import ast
from typing import Tuple
import pandas as pd
import investpy
from investpy.utils.search_obj import SearchObj
import pendulum

VALID_TYPES = [
    "stock",
    "etf",
    "fund",
    "crypto",
    "bond",
    "index",
    "certificate",
    "commodity",
]
MIN_FROM_DATE = "01/01/2010"
# Adjust this date if you need to get historical data further in the past. Note that
# extending this date will lead to increased numbers of requests on investing.com's
# servers bc investpy splits requests into sub-requests covering 19 years.


def get_currency_from_dataframe(df: pd.DataFrame) -> str:
    """Get currency from investpy dataframe."""
    currencies = list(df["Currency"].unique())
    if len(currencies) > 1:
        raise ValueError(f"Expected only one currency, got {currencies}.")
    return currencies[0]


def dataframify_investpy_df(df: pd.DataFrame) -> pd.DataFrame:
    """Turn investpy dataframe into a pricing dataframe in the form that we use it."""
    df = df.copy()  # To prevent the SettingWithCopyWarning
    df = df[["Close"]]
    df.index = pd.to_datetime(df.index, utc=True)
    df.index.name = "date"
    df.rename(columns={"Close": "close"}, inplace=True)
    return df


def get_price_history(query: str, type_: str, country: str) -> Tuple[pd.DataFrame, str]:
    """Get price history for a given query using investpy's `get_*_historical_data`
    functions.
    """
    args = {
        "from_date": MIN_FROM_DATE,
        "to_date": pendulum.now().strftime("%d/%m/%Y"),
        "country": country,
        type_: query,
    }
    prices = getattr(investpy, "get_" + type_ + "_historical_data")(**args)
    return (
        dataframify_investpy_df(prices),
        get_currency_from_dataframe(prices),
    )


def get_price_history_from_searchobj(objstring: str) -> Tuple[pd.DataFrame, str]:
    """Get price history for a given `SearchObj` (in string representation)."""
    searchobj = SearchObj(**ast.literal_eval(objstring))
    return (
        dataframify_investpy_df(
            searchobj.retrieve_historical_data(
                from_date=MIN_FROM_DATE,
                to_date=pendulum.now().strftime("%d/%m/%Y"),
            ),
        ),
        searchobj.retrieve_currency(),
    )
