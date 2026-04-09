"""Everything Yahoo-Finance-related (other than search)."""

import pandas as pd
import yfinance as yf
from yfinance.exceptions import YFRateLimitError
from .types import PriceHistory, RateLimitHitError

# Ensure yfinance raises exceptions instead of silently failing
yf.config.debug.hide_exceptions = False

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
    try:
        ticker = yf.Ticker(query)
        df = ticker.history(start=START_FROM)
    except YFRateLimitError as exc:
        raise RateLimitHitError(source="yahoo") from exc

    # Simplify dataframe:
    df = df.copy()
    df = df[["Close"]]
    df.index = pd.to_datetime(df.index, utc=True)
    df.index.name = "date"
    df.rename(columns={"Close": "close"}, inplace=True)

    # Get currency from metadata already populated by history() above.
    # Don't use get_history_metadata() — it triggers a second intraday request
    # that fails for some tickers. See https://github.com/ranaroussi/yfinance/issues/2745
    # TODO Revert to get_history_metadata() once the issue is fixed in yfinance.
    currency = ticker._price_history._history_metadata["currency"]
    return PriceHistory(df, currency)
