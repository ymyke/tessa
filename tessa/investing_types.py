"""Helper functions to work with investpy's types.

investpy sometimes uses plurals and sometimes singulars for its types. Hence the
functions in this module help to simplify working with those types.
"""

PLURALS2SINGULARS = {
    "certificates": "certificate",
    "commodities": "commodity",
    "bonds": "bond",
    "currency_crosses": "currency_cross",
    "indices": "index",
    "etfs": "etf",
    "stocks": "stock",
    "funds": "fund",
    # "crypto" is also a valid type but tessa uses pycoingecko for crypto. investpy's
    # `search_quotes` can also return "currencies" and "fxfutures" but we'll ignore
    # those, so they are not included in the list above.
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


def ensure_singular(type_: str) -> str:
    """Make sure `type_` is in its singular form."""
    if type_ in PLURALS2SINGULARS.values():  # singular already?
        return type_
    return PLURALS2SINGULARS[type_]
