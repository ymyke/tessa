"""Price-related types."""

from typing import NamedTuple
import pandas as pd
from .. import SourceType

PriceHistory = NamedTuple("PriceHistory", [("df", pd.DataFrame), ("currency", str)])
PricePoint = NamedTuple(
    "PricePoint", [("when", pd.Timestamp), ("price", float), ("currency", str)]
)


class SymbolNotFoundError(Exception):
    def __init__(self, source: SourceType, query: str, *args, **kwargs):
        msg = f"No symbol found on source '{source}' for query '{query}'."
        super().__init__(msg, *args, **kwargs)


class CurrencyPreferenceNotFoundError(Exception):
    def __init__(self, source: SourceType, cur_pref: str, *args, **kwargs):
        msg = f"No currency preference found on source '{source}' for '{cur_pref}'."
        super().__init__(msg, *args, **kwargs)


class RateLimitHitError(Exception):
    def __init__(self, source: SourceType, *args, **kwargs):
        msg = f"Rate limit hit on source '{source}'."
        super().__init__(msg, *args, **kwargs)
