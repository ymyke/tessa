"""SymbolCollection class."""

from typing import Optional, Type, Union, List
import yaml
from . import Symbol


class SymbolCollection:
    """A collection of `Symbol`s.

    Note that `SymbolCollection` does not enforce any uniqueness or similar of symbols
    or symbol attributes (especially names) in the collection. The YAML syntax, however,
    prescribes that keys need to be unique. Therefore, `yaml.safe_load` silently
    overwrites duplicate keys (case sensitive). The `matches` method in `Symbol` on the
    other hand ignores case. Thus, while you can't have two "ETH" keys/names, you can
    have two symbols with names "BTC" and "btc" respectively.
    """

    symbols: List[Symbol]
    """The `Symbol`s in the collection."""

    def __init__(self) -> None:
        """Initializer"""
        self.symbols = []

    def __iter__(self) -> object:
        """Make class iterable directly."""
        return self.symbols.__iter__()

    def add(self, what: Union[Symbol, List[Symbol]]) -> None:
        """Add `what` to the collection."""
        if isinstance(what, list):
            self.symbols.extend(what)
        else:
            self.symbols.append(what)
        # FIXME Should this return self to make it chainable?

    def find_one(self, what: str) -> Optional[Symbol]:
        """Find exactly one `Symbol` that matches the query. Raises `ValueError` if
        there's more than 1 match. Returns `None` if there's no match.
        """
        matches = self.find(what)
        if len(matches) > 1:
            raise ValueError(f"Found several matching symbols for '{what}'")
        return matches[0] if matches else None

    def find(self, what: str) -> List[Symbol]:
        """Find all `Symbol`s that match the query."""
        return [s for s in self.symbols if s.matches(what)]

    def load_yaml(self, yaml_file: str, which_class: Type[Symbol] = Symbol) -> None:
        """Load symbols from a YAML file.

        - `yaml_file`: Name/path of file to load.
        - `which_class`: The class to be instantiated, can be used to instatiate
          subclasses of `Symbol`.
        """
        with open(yaml_file, "r", encoding="utf-8") as stream:
            ymldict = yaml.safe_load(stream)
        self.symbols = [which_class(k, **(v or {})) for k, v in ymldict.items()]

    def to_yaml(self) -> str:
        """Return a YAML representation of all symbols."""
        return "".join([s.to_yaml() for s in self.symbols])

    def save_yaml(self, yaml_file: str) -> None:
        """Save symbols to a YAML file."""
        with open(yaml_file, "w", encoding="utf-8") as stream:
            stream.write(self.to_yaml())
