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
