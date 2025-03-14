"""Everything coingecko-related (other than search)."""

import pandas as pd
from pycoingecko import CoinGeckoAPI
from .types import (
    PriceHistory,
    SymbolNotFoundError,
    CurrencyPreferenceNotFoundError,
    RateLimitHitError,
)


def dataframify_price_list(prices: list) -> pd.DataFrame:
    """Turn price list returned by Coingecko API into a pricing dataframe in the form
    that we use.
    """
    df = pd.DataFrame(prices)
    df.columns = ["date", "close"]
    df["date"] = pd.to_datetime(df["date"] / 1000, unit="s", utc=True)
    df = df.set_index("date")
    return df


def get_price_history(query: str, currency_preference: str = "USD") -> PriceHistory:
    """Get price history for a given cryptocurrency."""
    try:
        res = CoinGeckoAPI().get_coin_market_chart_by_id(
            id=query,
            vs_currency=currency_preference,
            days="365",  # Public API is limited to 365 days back
            interval="daily",
        )["prices"]
    except ValueError as exc:
        if "invalid vs_currency" in str(exc):
            raise CurrencyPreferenceNotFoundError(
                source="coingecko", cur_pref=currency_preference
            ) from exc
        if "429" in str(exc):
            # (pycoingecko masks the underlying HTTPError.)
            raise RateLimitHitError(source="coingecko") from exc
        if "exceeds the allowed time range" in str(exc):
            raise ValueError(
                "Coingecko's public API is limited to historical data 365 days back."
            ) from exc
        raise SymbolNotFoundError(source="coingecko", query=query) from exc

    return PriceHistory(dataframify_price_list(res), currency_preference)
