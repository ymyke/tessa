"""Everything coingecko-related (other than search)."""

from typing import Tuple
import pandas as pd
from pycoingecko import CoinGeckoAPI


def dataframify_price_list(prices: list) -> pd.DataFrame:
    """Turn price list returned by Coingecko API into a pricing dataframe in the form
    that we use.
    """
    df = pd.DataFrame(prices)
    df.columns = ["date", "close"]
    df["date"] = pd.to_datetime(df["date"] / 1000, unit="s", utc=True)
    df = df.set_index("date")
    return df


def get_price_history(
    query: str, currency_preference: str = "usd"
) -> Tuple[pd.DataFrame, str]:
    """Get price history for a given cryptocurrency."""
    return (
        dataframify_price_list(
            CoinGeckoAPI().get_coin_market_chart_by_id(
                id=query,
                vs_currency=currency_preference,
                days="max",  # FIXME Add some lower default bound similar to yahoo?
                interval="daily",
            )["prices"]
        ),
        currency_preference,
    )
    # FIXME Check for ValueError when id doesn't exist. Add common exception
    # SymbolNotFoundError or so. Reraise that exception in such cases. Same in yahoo
    # module. Add a test for such error condition to coingecko test module (already
    # there -- move from generic price module to coingecko module)
