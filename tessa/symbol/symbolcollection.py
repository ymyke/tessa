"""SymbolCollection class."""

from typing import Optional, Type, Union, List
import yaml
from . import Symbol


class SymbolCollection:
    """A collection of `Symbol`s."""

    def __init__(self, symbol_class: Type[Symbol] = Symbol) -> None:
        """Use `symbol_class` to create extensions of `Symbol`."""
        self.symbol_class = symbol_class
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

    def find_one(self, what: str) -> Optional[Symbol]:
        """Find Symbol that matches query. Raises `ValueError` if there's more than 1
        match. Returns `None` if there's no match.
        """
        matches = [s for s in self.symbols if s.matches(what)]
        if len(matches) > 1:
            raise ValueError(f"Found several matching symbols for '{what}'")
        return matches[0] if matches else None

    def load_yaml(self, yaml_file: str) -> None:
        """Load symbols from a YAML file."""
        with open(yaml_file, "r", encoding="utf-8") as stream:
            ymldict = yaml.safe_load(stream)
        self.symbols = [self.symbol_class(k, **(v or {})) for k, v in ymldict.items()]

    def to_yaml(self) -> str:
        """Return a YAML representation of all symbols."""
        return "".join([s.to_yaml() for s in self.symbols])

    def save_yaml(self, yaml_file: str) -> None:
        """Save symbols to a YAML file."""
        with open(yaml_file, "w", encoding="utf-8") as stream:
            stream.write(self.to_yaml())
