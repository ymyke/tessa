"""SymbolCollection class."""

from typing import Optional
import yaml
from .symbol import Symbol

# FIXME Check Qortfolio and maybe add things here.

# FIXME The jurisdiction stuff could fit here.


class SymbolCollection:
    """A collection of `Symbol`s."""

    def __init__(self, yaml_file: str):
        self.yaml_file = yaml_file
        self.symbols = self.load_yaml(yaml_file)

    def find_one(self, what: str) -> Optional[Symbol]:
        """Find Symbol that matches query. Raises `ValueError` if there's more than 1
        match. Returns `None` if there's no match.
        """
        matches = [s for s in self.symbols if s.matches(what)]
        if len(matches) > 1:
            raise ValueError(f"Found several matching symbols for '{what}'")
        return matches[0] if matches else None

    @staticmethod
    def load_yaml(yaml_file: str):
        """Load symbols from a YAML file."""
        with open(yaml_file, "r", encoding="utf-8") as stream:
            ymldict = yaml.safe_load(stream)
        return [Symbol(k, v or {}) for k, v in ymldict.items()]
