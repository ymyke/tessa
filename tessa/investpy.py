"""`investpy`-related functions."""

import investpy


# FIXME Needs rate limiting as well.
# FIXME Add tests.


def search_asset(
    query: str, country: str = None, products: str = None, silent: bool = False
) -> dict:
    """Find asset on investpy."""
    return search_name_or_symbol(query, silent) | search_for_searchobjs(
        query, country, products, silent
    )


def search_name_or_symbol(query: str, silent: bool = False) -> dict:
    """Run query through all of the search functions and all the search_by options of
    investpy and return the results as a dict of type x search_by combinations. Also
    print out how many results were found per key.

    >>> from tessa.investpy import search_name_or_symbol
    >>> r = search_name_or_symbol("swiss")
    """
    # FIXME Add country and products here too for consistency reasons and filter
    # accordingly?
    # FIXME Rename types to products?
    types = [
        "certificates",
        "commodities",
        "bonds",
        "currency_crosses",
        "indices",
        "etfs",
        "stocks",
        "funds",
    ]
    bys = ["full_name", "name", "symbol"]
    res = {}
    for type_ in types:
        for by_ in bys:
            key = f"{type_}_by_{by_}"
            try:
                res[key] = getattr(investpy, "search_" + type_)(by=by_, value=query)
            except (RuntimeError, ValueError):
                continue
            if not silent:
                print(f"{key}: Found {res[key].shape[0]}")
    return res


def search_for_searchobjs(
    query: str, country: str = None, products: str = None, silent: bool = False
) -> dict:
    """Run query through `investpy.search_quotes`, which returns `SearchObj` objects and
    return the objects found as lists triaged into perfect and other matches. Also print
    out how many results were found per category.

    cf https://github.com/alvarobartt/investpy/issues/129#issuecomment-604048750

    - searches all countries if country == None
    - products: `indices`, `stocks`, `etfs`, `funds`, `commodities`, `currencies`,
      `crypto`, `bonds`, `certificates` and `fxfutures`, by default this parameter is
      set to `None` which means that no filter will be applied, and all product type
      quotes will be retrieved.

    >>> from tessa.investpy import search_for_searchobjs
    >>> r = search_for_searchobjs("soft")
    """
    # Search:
    query = query.lower()
    try:
        search_res = investpy.search_quotes(
            text=query,
            products=[products] if products else None,
            countries=[country] if country else None,
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
    res = {}
    for name, category in zip(
        ["perfect_searchobj_matches", "other_searchobj_matches"],
        [perfect_matches, other_matches],
    ):
        if category:
            res[name] = [x.__str__() for x in category]
            if not silent:
                print(f"{name}: Found {len(category)}")

    return res
