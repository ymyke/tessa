"""An example of how to extend the Symbol class with more information and functionality.
"""

from typing import Optional, List, Union
from dataclasses import dataclass, field
from . import Symbol
from .geo import CountryName, j2r


# Customizations to jurisdiction2region (remove or adapt according to your needs):
j2r.jurisdiction2region.update(
    {
        "CH": "CH",
        "CN": "CN",
        "EU": "EU",
        "irrelevant": "OT",
        "several": "OT",
        "unknown": "OT",
    }
)
j2r.region2name.update(
    {
        "CH": "Switzerland",
        "CN": "China",
        "AS": "Asia sans China",
    }
)


@dataclass
class ExtendedSymbol(Symbol):
    """ExtendedSymbol class. Adds more information and functionality to the Symbol
    class.
    """

    description: Optional[str] = None
    """Informational only."""
    # FIXME A design alternative could be to move the `description` attribute to
    # `Symbol` itself, rename it to `info` so it can be used for arbitrary additional
    # informaton around a symbol such as a description or similar.

    country: Optional[CountryName] = "united states"
    """Country of HQ / listing."""

    watch: bool = False
    """Whether the ticker can produce alerts."""

    delisted: bool = False
    """Used to filter certain symbols from analysis."""

    jurisdiction: str = "US"
    """main jurisdiction of the underlying asset(s) (not of the title representing the
    asset); default US, other examples: CN, EU, several, irrelevant, unknown
    """

    isin: Optional[str] = None
    """Informational only."""

    strategy: Union[str, List[str]] = field(default_factory=list)
    """One strategy or a list of several strategies. Some strategies I use:
      - F&F: Fire & Forget (implies HoldForGrowth)
      - HoldForGrowth
      - HoldForStability: low growth expected, but also low risk
      - HoldForDiversification: titles I find important for diversification
      - EnterIf: consider starting a position if prices for this title fall
      - SellIf: consider selling if prices high and/or liquidity needed
      - Sold: earlier holding that was sold at some point
      - Quarterly: quarterly invest
    """

    strategy_comments: Optional[str] = None
    """Additional comments re strategy."""

    region: str = field(init=False)
    """Will be set automatically."""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.region = j2r.map_jurisdiction_to_region(self.jurisdiction)

    def get_strategy_string(self) -> str:
        """Return a nice string with the strategy including comments."""
        if isinstance(self.strategy, list):
            res = ", ".join(self.strategy)
        else:
            res = self.strategy
        if getattr(self, "strategy_comments", False):
            res += f" · {self.strategy_comments}"
        return res

    def price_graph(self, monthsback: int = 6) -> tuple:
        """Add some extra information to the price graph."""
        (from_date, fig, ax) = super().price_graph(monthsback)
        print(f"{self.name}")
        latestprice = self.price_latest().price
        print(f"Latest price: {latestprice:.2f}")
        hist = self.price_history()[0]
        maxprice = hist[hist.index > from_date].max().close
        print(f"Drop since max: {(latestprice - maxprice) / maxprice:2.0%}")
        return from_date, fig, ax
