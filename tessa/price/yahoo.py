"""Everything Yahoo-Finance-related (other than search)."""

import functools
from typing import Tuple
import pandas as pd
import yfinance as yf
from ..utils.freezeargs import freezeargs

START_FROM = "2000-01-01"
"""Adjust this date if you need to get historical data further in the past. Note that
extending this date will lead to increased load on the Yahoo Finance servers.
"""


@freezeargs
@functools.lru_cache(maxsize=None)
def get_ticker_info(query: str) -> dict:
    """FIXME add documentation"""
    return yf.Ticker(query).get_info()  # type: ignore


def get_price_history(
    query: str, currency_preference: str = "usd"  # pylint: disable=unused-argument
) -> Tuple[pd.DataFrame, str]:  # FIXME Use PriceHistory here (also in coingecko)
    """Get price history for a given query. Note that `currency_preference` will be
    ignored since Yahoo Finance returns each ticker in the one currency that is set for
    that ticker.
    """

    df = yf.Ticker(query).history(start=START_FROM, debug=False)

    # Simplify dataframe:
    df = df.copy()
    df = df[["Close"]]
    df.index = pd.to_datetime(df.index, utc=True)
    df.index.name = "date"
    df.rename(columns={"Close": "close"}, inplace=True)

    return (df, get_ticker_info(query)["currency"])
