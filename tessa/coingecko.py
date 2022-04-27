"""Everything coingecko-related."""

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
                days="max",
                interval="daily",
            )["prices"]
        ),
        currency_preference,
    )
