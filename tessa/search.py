"""Unified search."""

from typing import Optional, Union
from .investing_search import investing_search
from .coingecko_search import coingecko_search


def search(
    query: str,
    countries: Optional[Union[list, str]] = None,
    products: Optional[Union[list, str]] = None,
    silent: bool = False,
) -> dict:
    """Unified search function.

    Args:

    - query: The string to search for.
    - silent: No print output if True.

    Optional/situational args:

    - countries: One or a list of countries to search in.
    - products: One or a list of products to search for. Options are ["bonds",
      "certificates", "commodities", "cryptos", "currencies", "currency_crosses",
      "etfs", "funds", "fxfutures", "indices", "stocks"].

    Both `countries` and `products` will only be used for the searches on investing.
    They can be a list or a string. They can also be `None`, in which case all products
    or countries are searched.

    Returns:

    - dict of finds in different categories.

    Example calls:

    ```
    from tessa import search
    r1 = search("soft")
    r2 = search("carbon", products=["etfs", "funds"])
    r3 = search("btc")
    ```
    """
    res = investing_search(
        query, products=products, countries=countries
    ) | coingecko_search(query)
    if not silent:
        for k, v in res.items():
            num = len(v) if isinstance(v, list) else v.shape[0]
            print(f"{num:5d} of {k}")
    return res
