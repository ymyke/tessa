"""Symbol class."""

from typing import Tuple, Union
from dataclasses import dataclass, field
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .. import price_history

pd.plotting.register_matplotlib_converters()


@dataclass
class Symbol:
    """Symbol class. Encapsulates all the relevant information around a financial symbol
    and some functionality to get price information, display graphs, etc.

    Notes:
    - Price-related functions rely on caching happening on lower levels to be efficient;
      this is fulfilled thanks to the way tessa's caching works.
    - The initializers don't hit the network -- it will only be hit when accessing the
      price functions or related functions such as `currency` or `today`.
    """

    name: str
    type_: str = "stock"
    query: str = None
    country: str = "united states"
    aliases: list[str] = field(default_factory=list)

    _querytype: str = field(init=False)

    def __post_init__(self) -> None:
        """Re(set) some attributes."""
        if self.query is None:
            self.query = self.name
        self._querytype = "searchobj" if isinstance(self.query, dict) else self.type_
        if self._querytype in ["crypto", "searchobj"]:  # Reset country default
            self.country = None

    def __str__(self) -> str:
        txt = f"Symbol {self.name} of type {self.type_}"
        if getattr(self, "country", None):
            txt += f" ({self.country})"
        return txt

    def p(self) -> None:
        """Convenience method to print the symbol."""
        print(str(self))

    def today(self) -> pd.Timestamp:
        """Return the latest date for which there is price information for this
        symbol."""
        return self.latest_price()[0]

    def today_price(self) -> float:
        """Return the latest close price."""
        return self.latest_price()[1]

    def currency(self) -> str:
        """Return currency for this symbol."""
        currency = self.latest_price()[2]
        return currency and currency.upper()

    def latest_price(self) -> Tuple[pd.Timestamp, float, str]:
        """Return the latest close price. Returns a tuple of timestamp, price and
        currency.
        """
        df, currency = self.price_history()
        return (df.iloc[-1].name, float(df.iloc[-1]["close"]), currency)

    def price_history(self) -> Tuple[pd.DataFrame, str]:
        """Return a tuple of the full price history as a DataFrame of dates and close
        prices and the currency.
        """
        args = {
            "query": str(self.query),
            "type_": self._querytype,
        }
        if self.country is not None:
            args["country"] = self.country
        return price_history(**args)

    def lookup_price(self, date: Union[str, pd.Timestamp]) -> float:
        """Look up price at given date."""
        return float(self.price_history()[0].loc[date])

    def pricegraph(self, monthsback: int = 6) -> tuple:
        """Display this symbol's price graph over the last monthsback months.

        Returns from_date, fig, and ax in order for subclass functions to add to the
        information and even the graph displayed here.
        """
        fig, ax = plt.subplots(figsize=(16, 8))
        hist = self.price_history()[0]

        # Calc start date:
        from_date = datetime.date.today() - pd.offsets.DateOffset(months=monthsback)
        from_date = from_date.strftime("%Y-%m-%d")

        # Plot the prices:
        sns.lineplot(ax=ax, data=hist.loc[from_date:, "close"], marker="o").set(
            title=self.name
        )

        return from_date, fig, ax

    def matches(self, what: str) -> bool:
        """Check if `what` matches this symbol's name or aliases. Also tries to match
        things like SPICHA if SPICHA.SW is in the aliases.
        """
        candidates = [c.lower() for c in [self.name] + self.aliases]
        candidates += [c.split(".")[0] for c in candidates]
        return what.lower() in candidates
