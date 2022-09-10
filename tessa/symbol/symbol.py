"""Symbol class."""

from typing import Union, Optional, ClassVar
from dataclasses import dataclass, field
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .. import price_history, price_latest, price_point
from ..price import PricePoint, PriceHistory

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
    - The `tessa.price` functions are used to get the actual price information, and they
      have a  `currency_preference` argument. This argument is not exposed explicitly by
      `Symbol` but if you need, you can set a preference by setting the
      `_currency_preference` attribute.
    """

    name: str
    type_: str = "stock"
    query: Optional[str] = None
    country: Optional[str] = "united states"
    aliases: list[str] = field(default_factory=list)

    # Class variables:
    _currency_preference: ClassVar[str] = "USD"
    """Use this to set the preferred currency to get price information in.

    This is no guarantee and you should always double-check the currency that gets
    returned by any of the `price_*` methods in actuality. This is also the reason why
    this feature is slightly hidden behind an underscore.

    Since this is a class variable, you can set your preference once for all objects.
    """

    # Private variables:
    __querytype: str = field(init=False)

    def __post_init__(self) -> None:
        """Re/set some attributes."""
        if self.query is None:
            self.query = self.name
        self.__querytype = "searchobj" if isinstance(self.query, dict) else self.type_
        if self.__querytype == "crypto":  # Reset country default
            self.country = None

    def __repr__(self) -> str:
        """Special repr method that puts the `query` to the end and leaves out private
        attributes so a Symbol can be built directly from the repr output.
        """
        attributes = []
        for attrib_name in ["name", "type_", "country", "aliases", "query"]:
            attrib = getattr(self, attrib_name, None)
            value = f"'{attrib}'" if isinstance(attrib, str) else attrib
            attributes.append(f"{attrib_name}={value}")
        return f"Symbol({', '.join(attributes)})"

    def __str__(self) -> str:
        txt = f"Symbol {self.name} of type {self.type_}"
        if getattr(self, "country", None):
            txt += f" ({self.country})"
        return txt

    def p(self) -> None:
        """Convenience method to print the symbol."""
        print(str(self))

    def to_yaml(self) -> str:
        """Return a YAML representation of this symbol."""
        return f"""
{self.name}:
    query: {self.query}
    aliases: [{", ".join(self.aliases)}]
    type_: {self.type_}
    country: {self.country}
"""

    def currency(self) -> str:
        """Return currency for this symbol."""
        currency = self.price_latest().currency
        return currency and currency.upper()

    def _create_price_args(self) -> dict:
        """Create a dictionary of arguments that work with tessa's price functions."""
        args = {
            "query": str(self.query),
            "type_": self.__querytype,
            "currency_preference": self._currency_preference,
        }
        if self.country is not None and self.__querytype != "searchobj":
            args["country"] = self.country
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
        return price_point(**self._create_price_args(), when=when)

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
