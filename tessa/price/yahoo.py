"""Everything Yahoo-Finance-related (other than search)."""

import pandas as pd
import yfinance as yf
from .types import PriceHistory

START_FROM = "2000-01-01"
"""Adjust this date if you need to get historical data further in the past. Note that
extending this date will lead to increased load on the Yahoo Finance servers.
"""


def get_price_history(
    query: str, currency_preference: str = "USD"  # pylint: disable=unused-argument
) -> PriceHistory:
    """Get price history for a given query. Note that `currency_preference` will be
    ignored since Yahoo Finance returns each ticker in the one currency that is set for
    that ticker.
    """
    ticker = yf.Ticker(query)
    df = ticker.history(start=START_FROM, raise_errors=True)

    # Simplify dataframe:
    df = df.copy()
    df = df[["Close"]]
    df.index = pd.to_datetime(df.index, utc=True)
    df.index.name = "date"
    df.rename(columns={"Close": "close"}, inplace=True)

    return PriceHistory(df, ticker.get_history_metadata()["currency"])
