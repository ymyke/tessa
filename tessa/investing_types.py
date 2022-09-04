"""Helper functions to work with investpy's types.

Defines type `InvestingType` that lists all possible types that can be used.

investpy sometimes uses plurals and sometimes singulars for its types. Hence the
functions in this module help to simplify working with those types.

Notes:

- "crypto" is also a valid type but tessa uses pycoingecko for crypto. So crypto gets
  ignored here.
- investpy's `search_quotes` can also return "currencies" and "fxfutures" but we'll
  ignore those, because investpy doesn't offer any price history retrieval for those.
"""

from typing import Literal, Optional, Union, List, TypeVar


T = TypeVar("T")
ListOrItemOptional = Optional[Union[List[T], T]]

InvestingType = Literal[
    "certificate",
    "commodity",
    "bond",
    "currency_cross",
    "index",
    "etf",
    "stock",
    "fund",
]


PLURALS2SINGULARS = {
    "certificates": "certificate",
    "commodities": "commodity",
    "bonds": "bond",
    "currency_crosses": "currency_cross",
    "indices": "index",
    "etfs": "etf",
    "stocks": "stock",
    "funds": "fund",
}


def get_plurals() -> list:
    """Get all types in plural form."""
    return PLURALS2SINGULARS.keys()


def get_singulars() -> list:
    """Get all types in singular form."""
    return PLURALS2SINGULARS.values()


def is_valid(type_: str) -> bool:
    """Check if a `type_` is valid; either in singular or plural form."""
    return type_ in PLURALS2SINGULARS or type_ in PLURALS2SINGULARS.values()


def singularize(type_: str) -> str:
    """Make sure `type_` is in its singular form."""
    if type_ in PLURALS2SINGULARS.values():  # singular already?
        return type_
    return PLURALS2SINGULARS[type_]


def pluralize(type_: str) -> str:
    """Make sure `type_` is in its plural form."""
    for k, v in PLURALS2SINGULARS.items():
        if v == type_:
            return k
    # Will just return what it has received, even if the type_ is not even contained in
    # PLURALS2SINGULARS:
    return type_


def pluralize_list(types: List[str]) -> List[str]:
    """Pluralize an entire list."""
    return [pluralize(x) for x in types]
