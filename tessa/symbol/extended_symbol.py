"""An example of how to extend the Symbol class with more information and functionality.
"""

from typing import Optional, List, Union
from dataclasses import dataclass, field
from . import Symbol
from . import jurisdiction2region as j2r

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
    # FIXME A design alternative could be to move the `description` attribute to
    # `Symbol` itself, rename it to `info` so it can be used for arbitrary additional
    # informaton around a symbol such as a description or similar.
    watch: bool = False
    delisted: bool = False
    jurisdiction: str = "US"
    isin: Optional[str] = None
    strategy: Union[str, List[str]] = field(default_factory=list)
    strategy_comments: Optional[str] = None
    region: str = field(init=False)

    # You can also overwrite defaults from Symbol here, like so:
    # country: str = "switzerland"

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

    def pricegraph(self, monthsback: int = 6) -> tuple:
        """Add some extra information to the pricegraph."""
        (from_date, fig, ax) = super().pricegraph(monthsback)
        print(f"{self.name}")
        print(f"Latest price: {self.today_price():.2f}")
        hist = self.price_history()[0]
        maxprice = hist[hist.index > from_date].max().close
        print(f"Drop since max: {(self.today_price() - maxprice) / maxprice:2.0%}")
        return from_date, fig, ax
