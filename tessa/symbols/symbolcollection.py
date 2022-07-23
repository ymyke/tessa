"""SymbolCollection class."""

from typing import Optional, Type
import yaml
from . import Symbol


class SymbolCollection:
    """A collection of `Symbol`s."""

    def __init__(self, yaml_file: str, symbol_class: Type[Symbol] = Symbol) -> None:
        """Initialize with symbols loaded from `yaml_file`. Use `symbol_class` to build
        extensions of `Symbol`.
        """
        self.symbol_class = symbol_class
        self.symbols = self.load_yaml(yaml_file)

    def __iter__(self) -> object:
        """Make class iterable directly."""
        return self.symbols.__iter__()

    def find_one(self, what: str) -> Optional[Symbol]:
        """Find Symbol that matches query. Raises `ValueError` if there's more than 1
        match. Returns `None` if there's no match.
        """
        matches = [s for s in self.symbols if s.matches(what)]
        if len(matches) > 1:
            raise ValueError(f"Found several matching symbols for '{what}'")
        return matches[0] if matches else None

    def load_yaml(self, yaml_file: str):
        """Load symbols from a YAML file."""
        with open(yaml_file, "r", encoding="utf-8") as stream:
            ymldict = yaml.safe_load(stream)
        return [self.symbol_class(k, **(v or {})) for k, v in ymldict.items()]
