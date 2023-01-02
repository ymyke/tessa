"""Everything Yahoo-Finance-related (other than search)."""

import io
import contextlib
import pandas as pd
import yfinance as yf
from .types import PriceHistory, SymbolNotFoundError

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

    Note that yfinance has some strange error behavior, e.g., when a ticker doesn't
    exist: `history()` will return an empty dataframe (but with all the column headers
    as usual) and print "No data found, symbol may be delisted" to stdout.
    """
    stdout = io.StringIO()
    ticker = yf.Ticker(query)
    with contextlib.redirect_stdout(stdout):
        df = ticker.history(start=START_FROM, debug=True)
    if "No data found" in stdout.getvalue():
        raise SymbolNotFoundError(source="yahoo", query=query)

    # Simplify dataframe:
    df = df.copy()
    df = df[["Close"]]
    df.index = pd.to_datetime(df.index, utc=True)
    df.index.name = "date"
    df.rename(columns={"Close": "close"}, inplace=True)

    return PriceHistory(df, ticker.get_history_metadata()["currency"])
