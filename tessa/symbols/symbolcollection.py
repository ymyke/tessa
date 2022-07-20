"""SymbolCollection class."""

from typing import Optional
import yaml
from . import Symbol


class SymbolCollection:
    """A collection of `Symbol`s."""

    def __init__(self, yaml_file: str):
        """Initialize with symbols loaded from `yaml_file`."""
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

    @staticmethod
    def load_yaml(yaml_file: str):
        """Load symbols from a YAML file."""
        with open(yaml_file, "r", encoding="utf-8") as stream:
            ymldict = yaml.safe_load(stream)
        return [Symbol(k, **(v or {})) for k, v in ymldict.items()]


# FIXME Add jurisdiction code here? (Or in some helper class or mixin?)
#
# Region mapping, some of these will be set up in setup
# FIXME Use https://github.com/flyingcircusio/pycountry or similar for this.
# region2jurisdictions = {
#     "South America": ["AR"],
#     "North America": ["US"],
#     "Switzerland": ["CH"],
#     "Europe": ["DE", "EU", "UK"],
#     "China": ["CN"],
#     "Other Asia": ["JP", "KR", "SG", "TW"],
#     "Other": ["US_tbd", "irrelevant", "several"],
# }
# region2tickers = defaultdict(list)
# juris2region = {}
# [...]
# Set up region2tickers:
# global juris2region  # pylint: disable=global-statement,invalid-name
# juris2region = {j: r for r, jlist in region2jurisdictions.items() for j in jlist}
# try:
#     for tci in tconfig:
#         region2tickers[juris2region[tci.jurisdiction]].append(tci.bloomberg)
# except KeyError as exc:
#     raise RuntimeError(
#         f"Region missing for jurisdiction {tci.jurisdiction}"
#         f" (ticker {tci.bloomberg})"
#     ) from exc
