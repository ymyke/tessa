"""SymbolCollection class."""

from __future__ import annotations
from typing import Optional, Type, Union, List
import collections
import yaml
from . import Symbol


class SymbolCollection:
    """A collection of `Symbol`s. A `Symbol`'s name is treated as a key in a collection
    and this class enforces as much in the `add` method.
    """

    symbols: List[Symbol]
    """The `Symbol`s in the collection."""

    def __init__(self, symbols: Optional[List[Symbol]] = None) -> None:
        """Initializer. Use `symbols` to add symbols immediately and/or use `add` method
        later.
        """
        self.symbols = []
        if symbols is not None:
            self.add(symbols)

    def __iter__(self) -> object:
        """Make class iterable directly."""
        return self.symbols.__iter__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} with {len(self.symbols)} symbols"

    def add(self, symbols: Union[Symbol, List[Symbol]]) -> SymbolCollection:
        """Add symbols to the collection. Ensure names are unique."""
        if not isinstance(symbols, list):
            symbols = [symbols]
        if not all(isinstance(x, Symbol) for x in symbols):
            raise ValueError("Please only add Symbol types to a SymbolCollection.")
        all_names = [s.name for s in self.symbols + symbols]
        duplicates = [k for k, v in collections.Counter(all_names).items() if v > 1]
        if duplicates:
            raise ValueError(
                f"Duplicate names ({', '.join(duplicates)}). "
                "Please make sure each name is only used once."
            )
        self.symbols.extend(symbols)
        return self

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
        new_symbols = [which_class(k, **(v or {})) for k, v in ymldict.items()]
        self.add(new_symbols)

    def to_yaml(self) -> str:
        """Return a YAML representation of all symbols."""
        return "".join([s.to_yaml() for s in self.symbols])

    def save_yaml(self, yaml_file: str) -> None:
        """Save symbols to a YAML file."""
        with open(yaml_file, "w", encoding="utf-8") as stream:
            stream.write(self.to_yaml())
