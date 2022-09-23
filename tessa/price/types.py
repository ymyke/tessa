"""Price-related types."""

from typing import NamedTuple
import pandas as pd

PriceHistory = NamedTuple("PriceHistory", [("df", pd.DataFrame), ("currency", str)])
PricePoint = NamedTuple(
    "PricePoint", [("when", pd.Timestamp), ("price", float), ("currency", str)]
)
