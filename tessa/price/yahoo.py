"""Everything Yahoo-Finance-related (other than search).

Note that yfinance has some inconsistent/strange error behavior. E.g., when a ticker
doesn't exist:
- `history()` will return an empty dataframe (but with all the column headers as usual)
  and print "No data found, symbol may be delisted" to stdout.
- `get_info()` will simply return a json such as this one: `{'regularMarketPrice': None,
  'preMarketPrice': None, 'logo_url': ''}`.
This module will streamline this behavior and raise a `RuntimeError` in such cases.

"""

import io
import contextlib
import functools
import pandas as pd
import yfinance as yf
from .types import PriceHistory, SymbolNotFoundError
from ..utils.freezeargs import freezeargs

START_FROM = "2000-01-01"
"""Adjust this date if you need to get historical data further in the past. Note that
extending this date will lead to increased load on the Yahoo Finance servers.
"""


@freezeargs
@functools.lru_cache(maxsize=None)
def get_ticker_info(query: str) -> dict:
    """Get the meta information for a ticker and return it as a dict."""
    res = yf.Ticker(query).get_info()
    failed_get_info_output = {
        "regularMarketPrice": None,
        "preMarketPrice": None,
        "logo_url": "",
    }
    if res == failed_get_info_output:
        raise SymbolNotFoundError(source="yahoo", query=query)
    return res  # type: ignore


def get_price_history(
    query: str, currency_preference: str = "USD"  # pylint: disable=unused-argument
) -> PriceHistory:
    """Get price history for a given query. Note that `currency_preference` will be
    ignored since Yahoo Finance returns each ticker in the one currency that is set for
    that ticker.
    """
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        df = yf.Ticker(query).history(start=START_FROM, debug=True)
    if "No data found" in stdout.getvalue():
        raise SymbolNotFoundError(source="yahoo", query=query)

    # Simplify dataframe:
    df = df.copy()
    df = df[["Close"]]
    df.index = pd.to_datetime(df.index, utc=True)
    df.index.name = "date"
    df.rename(columns={"Close": "close"}, inplace=True)

    return PriceHistory(df, get_ticker_info(query)["currency"])
