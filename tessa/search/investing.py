"""Everything related to searching via `investpy`."""

import ast
import functools
import itertools
import random
from typing import List

import investpy
import pandas as pd

from .. import investing_types as itypes
from .. import rate_limiter
from ..freezeargs import freezeargs
from . import SearchResult
from ..symbol import Symbol


def investing_search(query: str, silent: bool = False) -> SearchResult:
    """Find asset on investpy. This is the most generic function that simply combines
    the results of the 2 specific functions below. Returns a combined `SearchResult`.
    """
    res = search_name_or_symbol(query, silent)
    res.add_symbols(search_for_searchobjs(query).symbols)
    return res


def _dataframe_to_symbols(df: pd.DataFrame, input_type: str) -> List[Symbol]:
    """Convert a search result dataframe to a list of `Symbol`s.

    Unfortunately, investpy's dataframes are not well standardized. So we need to
    convert from the dataframe columns to Symbol attributes with a number of `if`
    statements here. See also `_mapping_dataframe_columns_to_symbol_attributes` at the
    end of this file for a complete list of how to map the different types.
    """
    symbols = []
    for _, row in df.iterrows():
        d = row.to_dict()
        type_ = itypes.singularize(input_type)
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
            (
                {d.get("name", None), d.get("full_name", None)}  # Make unique!
                | {d.get("isin", None)}
            )
            - {args["name"]}  # Remove whatever was chosen as the name above
            - {None, ""}  # Remove None and empty string if it was added above
        )
        symbols.append(Symbol(**args))
    return symbols


@freezeargs
@functools.lru_cache(maxsize=None)
def _investpy_search_for_type(
    type_: str, by_: str, query: str, silent: bool
) -> List[Symbol]:
    """Small wrapper so results can be cached in an easy and finegrained way
    using functools.
    """
    if not silent:
        print(random.choice("☕🥱😴💤🛌🦥🕰️🐌🐛🪱🐢"), end="")
    rate_limiter.rate_limit("investing_search")
    try:
        df = getattr(investpy, "search_" + type_)(by=by_, value=query)
    except (RuntimeError, ValueError):
        return []
    return _dataframe_to_symbols(df, type_)


def search_name_or_symbol(query: str, silent: bool = False) -> SearchResult:
    """Run query through all of the search functions and all the search_by options of
    `investpy` and return the results as a `SearchResult`.
    """

    which_types = itypes.pluralize_list(itypes.get_enabled_investing_types())
    which_bys = ["full_name", "name", "symbol"]

    # Print some search stats and advise:
    if not silent:
        estimated_time = (
            len(which_types)
            * len(which_bys)
            * rate_limiter.original_guards["investing_search"]["wait_seconds"]
        )
        print(f"This search could take up to about {estimated_time} seconds.")
        if estimated_time > 10:
            print(
                "Consider using tessa.set_enabled_investing_types() to reduce the "
                "number of investing types to the necessary minimum. (Currently "
                f"enabled: {itypes.get_enabled_investing_types()})"
            )

    # Search:
    res = SearchResult(query=query.lower(), symbols=[])
    for type_, by_ in itertools.product(which_types, which_bys):
        res.add_symbols(_investpy_search_for_type(type_, by_, query, silent))

    if not silent:
        print("\n\n")
    return res


def _searchobj_to_symbols(objs: list) -> list:
    """Convert a list of investpy search objects to a list of `Symbol`s."""
    symbols = []
    for obj in objs:
        symbols.append(
            Symbol(
                name=obj.symbol,
                type_=(
                    itypes.singularize(obj.pair_type)
                    if itypes.is_valid(obj.pair_type)
                    else obj.pair_type
                    # Search objects can have certain types (e.g., currencies) that we
                    # don't "officially" support in symbols. We simply pass these
                    # through since they are nevertheless accessible.
                ),
                query=ast.literal_eval(str(obj).replace("null", "None")),
                aliases=[obj.name],
                country=obj.country,
            )
        )
    return symbols


@freezeargs
@functools.lru_cache(maxsize=None)
def _investpy_search_for_search_quotes(query: str) -> List[Symbol]:
    """Small wrapper so results can be cached in an easy and finegrained way using
    functools.
    """
    rate_limiter.rate_limit("investing_search")
    try:
        search_res = investpy.search_quotes(query)
    except (ValueError, RuntimeError):
        return []
    # search_quotes sometimes returns just a SearchObj, but we always want a list:
    if not isinstance(search_res, list):
        search_res = [search_res]
    return _searchobj_to_symbols(search_res)


def search_for_searchobjs(query: str) -> SearchResult:
    """Run query through `investpy.search_quotes`, convert the `SearchObj` objects found
    into `Symbol`s and return those as a `SearchResult`.

    See also https://github.com/alvarobartt/investpy/issues/129#issuecomment-604048750
    """
    symbols = _investpy_search_for_search_quotes(query)
    # Crypto is done exclusively via coingecko, so we filter symbols of that type here:
    symbols = [s for s in symbols if s.type_ != "cryptos"]
    return SearchResult(query=query, symbols=symbols)


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
