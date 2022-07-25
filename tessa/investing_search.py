"""Everything related to searching via `investpy`."""

import functools
import ast
from typing import Optional, Union
import pandas as pd
import investpy
from .freezeargs import freezeargs
from .rate_limiter import rate_limit
from .symbols import Symbol

PRODUCT2TYPE = {
    # FIXME Combine w/ the other valid_products lists here as well as VALID_TYPES in
    # tessa.investing; build a bidirectional map?
    "certificates": "certificate",
    "commodities": "commodity",
    "bonds": "bond",
    "currency_crosses": "currency_cross",
    "indices": "index",
    "etfs": "etf",
    "stocks": "stock",
    "funds": "fund",
}


def investing_search(
    query: str,
    countries: Optional[Union[list, str]] = None,
    products: Optional[Union[list, str]] = None,
) -> dict:
    """Find asset on investpy. This is the most generic function that simply combines
    the results of the 2 specific functions below.

    Note that the result is a dictionary with different categories of results. And
    results are either a dataframe or a list of search objects (as strings).

    Also check the docstrings of the specific functions `search_name_or_symbol` and
    `search_for_searchobjs` below for more info.

    Example calls:

    ```
    from tessa.investing_search import investing_search
    r1 = investing_search("AAPL")
    r2 = investing_search("AAPL", countries=["united states", "canada"], products="stocks")
    ```
    """
    return {
        **search_name_or_symbol(query, countries, products),
        **search_for_searchobjs(query, countries, products),
    }


def _dataframe_to_symbols(df: pd.DataFrame, product: str) -> list:
    """Convert a search result dataframe to a list of `Symbol`s.

    Unfortunately, investpy's dataframes are not well standardized. So we need to
    convert from the dataframe columns to Symbol attributes with a number of if
    statements here. See also `_mapping_dataframe_columns_to_symbol_attributes` at the
    end of this file for a complete list of how to map the different types.
    """
    symbols = []
    for _, row in df.iterrows():
        d = row.to_dict()
        type_ = PRODUCT2TYPE[product]
        args = {
            "type_": type_,
            "aliases": [],
        }
        if type_ != "currency_cross":
            args["country"] = d["country"]
        if type_ in ["currency_cross", "bond", "commodity"]:
            args["name"] = d["name"]
        else:
            args["name"] = d["symbol"]
        if type_ in ["etf", "fund", "certificate", "index"]:
            args["query"] = d["name"]
        args["aliases"].extend(
            set([d.get("name", None), d.get("full_name", None)])  # Make unique!
            - {args["name"]}  # Remove whatever was chosen as the name above
            - {None}  # Remove None if it was added above
        )
        symbols.append(Symbol(**args))
    return symbols


@freezeargs
@functools.lru_cache(maxsize=None)
def search_name_or_symbol(
    query: str,
    countries: Optional[Union[list, str]] = None,
    products: Optional[Union[list, str]] = None,
) -> dict:
    """Run query through all of the search functions and all the search_by options of
    `investpy` and return the results as a dict of product-search_by combinations. Also
    print out how many results were found per key.

    Args:

    - query: The query to search for.
    - countries: A list of countries to search in.
    - products: Any of `valid_products`.

    Both `countries` and `products` can be a list or a string. They can also be `None`,
    in which case all products or countries are searched.

    Example calls:

    ```
    from tessa.investing_search import search_name_or_symbol
    r1 = search_name_or_symbol("carbon")
    r2 = search_name_or_symbol(
        "carbon", countries=["united states", "switzerland"], products="etfs"
    )
    ```
    """
    rate_limit("investing")
    valid_products = [
        "certificates",
        "commodities",
        "bonds",
        "currency_crosses",
        "indices",
        "etfs",
        "stocks",
        "funds",
    ]
    valid_bys = ["full_name", "name", "symbol"]

    # Prepare input parameters (make sure countries and products are (empty) lists):
    query = query.lower()
    countries = [countries] if isinstance(countries, str) else countries
    if products is not None:
        products = [products] if isinstance(products, str) else products
        products = set(products) & set(valid_products)  # Only valid products
    else:
        products = valid_products

    # Search:
    res = {}
    for product in products:
        for by in valid_bys:  # pylint: disable=invalid-name
            try:
                df = getattr(investpy, "search_" + product)(by=by, value=query)
            except (RuntimeError, ValueError):
                continue
            if countries is not None:
                df = df[df.country.isin(countries)]
            if df.shape[0] > 0:
                res[f"investing_{product}_by_{by}"] = _dataframe_to_symbols(df, product)
    return res


def _searchobj_to_symbols(objs: list) -> list:
    """Convert a list of investpy search objects to a list of `Symbol`s."""
    symbols = []
    for obj in objs:
        try:
            symbols.append(
                Symbol(
                    name=obj.symbol,
                    type_=PRODUCT2TYPE[obj.pair_type],
                    query=ast.literal_eval(str(obj).replace("null", "None")),
                    aliases=[obj.name],
                    country=obj.country,
                )
            )
        except KeyError:
            # PRODUCT2TYPE mapping above can fail with certain SearchObj types (e.g.,
            # cryptos, currencies); we'll simply ignore these.
            continue
    return symbols


@freezeargs
@functools.lru_cache(maxsize=None)
def search_for_searchobjs(
    query: str,
    countries: Optional[Union[list, str]] = None,
    products: Optional[Union[list, str]] = None,
) -> dict:
    """Run query through `investpy.search_quotes`, which returns `SearchObj` objects and
    return the objects found as lists triaged into perfect and other matches. Also print
    out how many results were found per category.

    cf https://github.com/alvarobartt/investpy/issues/129#issuecomment-604048750

    Args:

    - query: The query to search for.
    - countries: A list of countries to search in.
    - products: Any of `valid_products`.

    Both `countries` and `products` can be a list or a string. They can also be `None`,
    in which case all products or countries are searched.

    Example calls:

    ```
    from tessa.investing_search import search_for_searchobjs
    r1 = search_for_searchobjs("soft")
    r2 = search_for_searchobjs("carbon", products=["etfs", "funds"])
    ```
    """
    rate_limit("investing")
    valid_products = [
        "indices",
        "stocks",
        "etfs",
        "funds",
        "commodities",
        "currencies",
        "cryptos",
        "bonds",
        "certificates",
        "fxfutures",
    ]

    # Prepare input parameters:
    query = query.lower()
    countries = [countries] if isinstance(countries, str) else countries
    if products is not None:
        if isinstance(products, str):
            products = [products]
        products = list(set(products) & set(valid_products))  # Only valid products
        products = products or None  # If empty, set to None

    # Search:
    try:
        search_res = investpy.search_quotes(
            text=query,
            products=products,
            countries=countries,
        )
    except (ValueError, RuntimeError):
        return {}

    # search_quotes sometimes returns just the SearchObj itself, but we always want a
    # list:
    if not isinstance(search_res, list):
        search_res = [search_res]

    # Triage:
    perfect_matches = [
        x for x in search_res if x.symbol.lower() == query or x.name.lower() == query
    ]
    other_matches = set(search_res) - set(perfect_matches)
    return {
        category_name: _searchobj_to_symbols(category_matches)
        for category_name, category_matches in zip(
            ["investing_searchobj_perfect", "investing_searchobj_other"],
            [perfect_matches, other_matches],
        )
        if category_matches
    }


# FIXME Have some separate module for all those mappings?
# FIXME Keep in mind that we can now access everything from the returned objects. So we
# can adjust some or all of the examples in the readme. Maybe keep the old ones around
# somewhere bc they show how everything works under the hood?


# -----·-----

# Specification of how to map the dataframe columns investpy returns to the Symbol
# attributes tessa uses. (_dataframe_to_symbols is coded according to this
# specification.):
#
# _mapping_dataframe_columns_to_symbol_attributes = {
#     "etf": {
#         "name": "symbol",
#         "query": "name",
#         "aliases": ["full_name", "name"],
#         "country": "country",
#         "type_": "literal:etf",
#     },
#     "stock": {
#         "name": "symbol",
#         "aliases": [
#             "full_name",
#             "name",
#         ],
#         "country": "country",
#         "type_": "literal:stock",
#     },
#     "fund": {
#         "name": "symbol",
#         "query": "name",
#         "aliases": ["name"],
#         "country": "country",
#         "type_": "literal:fund",
#     },
#     "index": {
#         "name": "symbol",
#         "query": "name",
#         "aliases": ["full_name", "name"],
#         "country": "country",
#         "type_": "literal:index",
#     },
#     "certificate": {
#         "name": "symbol",
#         "query": "name",
#         "aliases": ["full_name", "name"],
#         "country": "country",
#         "type_": "literal:certificate",
#     },
#     "currency_cross": {
#         "name": "name",
#         "aliases": ["full_name"],
#         "country": "currency_cross",
#     },
#     "bond": {
#         "name": "name",
#         "aliases": ["full_name"],
#         "country": "country",
#         "type_": "literal:bond",
#     },
#     "commodity": {
#         "name": "name",
#         "aliases": ["full_name"],
#         "country": "country",
#         "type_": "literal:commodity",
#     },
# }
