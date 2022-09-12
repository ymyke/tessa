"""Helper functions to work with investpy's types.

The most important functions are `get_enabled_investing_types`,
`set_enabled_investing_types`, and the context manager / decorator
`set_enabled_investing_types_temporarily`.

investpy sometimes uses plurals and sometimes singulars for its types. Hence the
functions in this module help to simplify working with those types.

Notes:

- "crypto" is also a valid type but tessa uses pycoingecko for crypto. So crypto gets
  ignored here.
- investpy's `search_quotes` can also return "currencies" and "fxfutures" but we'll
  ignore those, because investpy doesn't offer any price history retrieval for those.
"""

import contextlib
from typing import List, Final

_ENABLED_TYPES = [
    "certificate",
    "commodity",
    "bond",
    "currency_cross",
    "index",
    "etf",
    "stock",
    "fund",
]
"""Use `get_enabled_investing_types` and `set_enabled_investing_types` to manage
these.
"""

_PLURALS2SINGULARS: Final[dict] = {
    "certificates": "certificate",
    "commodities": "commodity",
    "bonds": "bond",
    "currency_crosses": "currency_cross",
    "indices": "index",
    "etfs": "etf",
    "stocks": "stock",
    "funds": "fund",
}


def get_enabled_investing_types() -> List[str]:
    """Return the types that are enabled for investing search functions."""
    return _ENABLED_TYPES


def set_enabled_investing_types(types: List[str]) -> None:
    """Set the types that are enabled for investing search functions. Use this to make
    searching more efficient in case you are only interested in certain types (e.g.,
    stock, etf, fund).
    """
    if any(x not in get_plurals() + get_singulars() for x in types):
        raise ValueError(f"Invalid type(s). Supported types are {get_singulars()}")
    global _ENABLED_TYPES  # pylint: disable=global-statement
    _ENABLED_TYPES = types


class set_enabled_investing_types_temporarily(  # pylint: disable=invalid-name
    contextlib.ContextDecorator
):
    """A context manager that sets the investing types and resets them when the context
    exits. Can be used both in a `with`-statement or as a function decorator.
    """

    def __init__(self, types: List[str]):
        self.types = types
        self.old_types = get_enabled_investing_types()

    def __enter__(self):
        set_enabled_investing_types(self.types)

    def __exit__(self, ext_type, ex_value, ex_traceback):
        set_enabled_investing_types(self.old_types)


def get_plurals() -> list:
    """Get all types in plural form."""
    return list(_PLURALS2SINGULARS)


def get_singulars() -> list:
    """Get all types in singular form."""
    return list(_PLURALS2SINGULARS.values())


def is_valid(type_: str) -> bool:
    """Check if a `type_` is valid; either in singular or plural form."""
    return type_ in get_plurals() + get_singulars()


def singularize(type_: str) -> str:
    """Make sure `type_` is in its singular form."""
    if type_ in get_singulars():  # singular already?
        return type_
    return _PLURALS2SINGULARS[type_]


def pluralize(type_: str) -> str:
    """Make sure `type_` is in its plural form."""
    for k, v in _PLURALS2SINGULARS.items():
        if v == type_:
            return k
    # Will just return what it has received, even if the type_ is not even contained in
    # _PLURALS2SINGULARS:
    return type_


def pluralize_list(types: List[str]) -> List[str]:
    """Pluralize an entire list."""
    return [pluralize(x) for x in types]
