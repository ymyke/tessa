"""An example of how to extend the Symbol class with more information and functionality.
"""

from typing import Optional, List, Union
from dataclasses import dataclass, field
from . import Symbol


@dataclass
class ExtendedSymbol(Symbol):
    """ExtendedSymbol class. Adds more information and functionality to the Symbol
    class.
    """

    description: Optional[str] = None
    watch: bool = False
    delisted: bool = False
    jurisdiction: str = "US"
    isin: Optional[str] = None
    strategy: Union[str, List[str]] = field(default_factory=list)
    strategy_comments: Optional[str] = None

    # You can also overwrite defaults from Symbol here, like so:
    # country: str = "switzerland"

    def get_strategy_string(self) -> str:
        """Return a nice string with the strategy including comments."""
        if isinstance(self.strategy, list):
            res = ", ".join(self.strategy)
        else:
            res = self.strategy
        if getattr(self, "strategy_comments", False):
            res += f" · {self.strategy_comments}"
        return res

    def pricegraph(self, monthsback: int = 6) -> tuple:
        """Add some extra information to the pricegraph."""
        (from_date, fig, ax) = super().pricegraph(monthsback)
        print(f"{self.name}")
        print(f"Latest price: {self.today_price():.2f}")
        hist = self.price_history()[0]
        maxprice = hist[hist.index > from_date].max().close
        print(f"Drop since max: {(self.today_price() - maxprice) / maxprice:2.0%}")
        return from_date, fig, ax
