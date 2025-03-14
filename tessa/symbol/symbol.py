"""Symbol class."""

from typing import Union, Optional, ClassVar
from dataclasses import dataclass, field
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ..price import price_history, price_latest, price_point, PricePoint, PriceHistory
from .. import SourceType

pd.plotting.register_matplotlib_converters()


@dataclass
class Symbol:
    """Symbol class. Encapsulates all the relevant information around a financial symbol
    and some functionality to get price information, display graphs, etc.

    Notes:
    - Price-related functions rely on caching happening on lower levels to be efficient;
      this is fulfilled thanks to the way tessa's caching works.
    - The initializers don't hit the network -- it will only be hit when accessing the
      price methods or related methods such as `currency`.
    """

    name: str
    """Symbol's name and default query."""

    query: Optional[str] = None
    """Use this to use a query that is different than the name. `name` will be used as
    the `query` if it is `None`.
    """

    source: SourceType = "yahoo"
    """The source to query for this symbol. Defaults to "yahoo"."""

    aliases: list[str] = field(default_factory=list)
    """Optional other names this symbol should be found under. (Will not be used as
    additional queries but "internally" in the `matches` method.)"""

    # Class variables:
    currency_preference: ClassVar[str] = "USD"
    """Use this to set the preferred currency to get price information in.

    This is no guarantee and you should always double-check the currency that gets
    returned by any of the `price_*` methods in actuality. This is also the reason why
    this feature is slightly hidden behind an underscore.

    Since this is a class variable, you can set your preference once for all objects.
    """

    max_date_deviation_days: ClassVar[int] = 10
    """The maximum number of days a date can deviate from the requested date in the
    `price_point` method. Use `None` to disable this check.

    Since this is a class variable, you can set your preference once for all objects.
    """

    def __post_init__(self) -> None:
        """Re/set some attributes."""
        if self.query is None:
            self.query = self.name

    def __str__(self) -> str:
        return f"Symbol {self.name} with source {self.source}"

    def p(self) -> None:
        """Convenience method to print the symbol."""
        print(str(self))

    def to_yaml(self) -> str:
        """Return a YAML representation of this symbol."""
        return f"""
{self.name}:
    query: {self.query}
    aliases: [{", ".join(self.aliases)}]
    source: {self.source}
"""

    def currency(self) -> str:
        """Return currency for this symbol."""
        currency = self.price_latest().currency
        return currency and currency.upper()

    def _create_price_args(self) -> dict:
        """Create a dictionary of arguments that work with tessa's price functions."""
        args = {
            "query": self.query,
            "source": self.source,
            "currency_preference": self.currency_preference,
        }
        return args

    def price_latest(self) -> PricePoint:
        """Return the latest close price."""
        return price_latest(**self._create_price_args())

    def price_history(self) -> PriceHistory:
        """Return a tuple of the full price history."""
        return price_history(**self._create_price_args())

    def price_point(self, when: Union[str, pd.Timestamp]) -> PricePoint:
        """Look up price at given date `when`. Look for the closest point in time if the
        exact point in time is not found.
        """
        return price_point(
            **self._create_price_args(),
            when=when,
            max_date_deviation_days=self.max_date_deviation_days,
        )

    def price_graph(self, monthsback: int = 6) -> tuple:
        """Display this symbol's price graph over the last monthsback months.

        Returns from_date, fig, and ax in order for subclass functions to add to the
        information and even the graph displayed here.
        """
        fig, ax = plt.subplots(figsize=(16, 8))
        hist = self.price_history().df

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
        things like SPICHA if SPICHA.SW is in the aliases. Ignores case.
        """
        candidates = [c.lower() for c in [self.name] + self.aliases]
        candidates += [c.split(".")[0] for c in candidates]
        return what.lower() in candidates
