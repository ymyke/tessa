"""Everything related to search results, especially the `SearchResult` class."""

from __future__ import annotations
import functools
from typing import List, NamedTuple, Optional, Callable
import itertools
import re
from .symbol import Symbol

# ----- The predicates used to sort and bucketize results based on a query -----

# Each matches_* function takes a `query` and a `Symbol` and returns an int denoting the
# match, where lower numbers signify better matches but 0 (=falsy) signifies not match.

# FIXME Add these examples to the tests?


def matches_entire_name_or_alias(query: str, symbol: Symbol) -> int:
    """Try to match the complete name or one of the aliases completely. E.g.:
    `matches_entire_name_or_alias("eth", Symbol("ETH")) > 0`.
    """
    query = query.lower()
    if query == symbol.name.lower():
        return 1
    if any(query == x.lower() for x in symbol.aliases if x):
        return 2
    return 0


def matches_word_boundary(query: str, symbol: Symbol) -> int:
    """Try to match a complete word in name, aliases, or query. E.g.:
    `matches_word_boundary("eth", Symbol("ETHW", aliases=["PoW ETH"])) > 0`.
    """
    query = query.lower()
    pattern = re.compile(rf"(^|[^a-z0-9]){query}([^a-z0-9]|$)", re.IGNORECASE)
    if re.search(pattern, symbol.name):
        return 1
    if re.search(pattern, "|".join(symbol.aliases)):
        return 2
    if re.search(pattern, str(symbol.query)):
        return 3
    return 0


def matches_inanyway(query: str, symbol: Symbol) -> int:
    """Try to match anywhere in name, aliases, or query. E.g.:
    `matches_inanyway("eth", Symbol("TOGETHER")) > 0`.
    """
    query = query.lower()
    if query in symbol.name.lower():
        return 1
    if query in ("|".join(symbol.aliases)).lower():
        return 2
    if query in str(symbol.query).lower():
        return 3
    return 0


# ----- Everything related to bucketizing symbols -----

Bucket = NamedTuple("Bucket", [("name", str), ("symbols", List[Symbol])])


BUCKET_SPEC = [
    ("Matches entire name or alias ⭐", matches_entire_name_or_alias),
    ("Matches word boundary", matches_word_boundary),
    ("Matches in any way", matches_inanyway),
    # A bucket with the non-matches will be added by `bucketize`.
]


def bucketize(query: str, symbols: List[Symbol]) -> List[Bucket]:
    """Split a list of `Symbol`s into buckets based on how well a symbol matches the
    `query`.

    (We're not using `itertools.groupby` here bc we need empty lists for empty buckets,
    which `groupby` doesn't provide.)
    """
    buckets = []
    rest = symbols
    for name, matches_predicate in BUCKET_SPEC:
        matches_query_predicate = functools.partial(matches_predicate, query)
        hits = list(filter(matches_query_predicate, rest))
        rest = list(itertools.filterfalse(matches_query_predicate, rest))
        buckets.append(Bucket(name, hits))
    buckets.append(Bucket("Matches not (but was somehow still returned) 🤔", rest))
    return buckets


# ----- Sorting and removing duplicates -----


def create_sort_key_for_query(query: str) -> Callable:
    """Create a sort key function that classifies a `Symbol` based on `query`."""

    def symbol_sort_key(symbol: Symbol) -> int:
        """Cycle through the predicates in `BUCKET_SPEC` and use an offset to return an
        int based on the matching quality.
        """
        offset = 10
        for _, pred in BUCKET_SPEC:
            score = pred(query, symbol)
            if score > 0:
                return offset + score
            offset += 10
        return 999

    return symbol_sort_key


def remove_duplicates(symbols: List[Symbol]) -> List[Symbol]:
    """Return a list in which every `Symbol` is unique. Two symbols are considered
    equivalent if they match in `type_`, `country`, and `query`. Regardless of whether
    their names are the same or different.

    Note further that several symbols can have the same name but still be considered
    different if they differ in any of `type_`, `country`, or `query`.
    """
    # FIXME Will this remove_duplicates function have a different definition of equality
    # than the SymbolCollection class? -- If so, rightly so? Or is this an issue?
    equality_key = lambda symbol: str((symbol.type_, symbol.country, symbol.query))
    return [k for k, _ in itertools.groupby(sorted(symbols, key=equality_key))]


# ----- The SearchResult class -----


class SearchResult:
    """Manages a search result consisting of a list of `Symbol`s. Removes duplicates,
    bucketizes, sorts and offers methods to filter and print statistics.

    (Design note: `SearchResult` has no relationship with `SymbolCollection` because the
    purposes of the two classes are very different and because they have different
    equality definitions for symbols.)

    Example usage:

    ```
    from tessa import search
    r = search("pins")
    # Review results:
    r.p()
    # Get the 1 symbol in US in the best bucket (i.e., bucket 0):
    s = r.filter(country="united states").buckets[0].symbols[0]
    s.price_latest()
    ```
    """

    query: str
    """The query that produced the results here."""

    symbols: List[Symbol]
    """List of symbols in this result. Always deduplicated and sorted."""

    buckets: List[Bucket]
    """List of buckets after bucketizing the symbols."""

    filter_history: List[str]
    """The filters that have been applied to get to this result."""

    def __init__(self, query: str, symbols: List[Symbol]):
        self.query = query
        self.buckets = []
        self.filter_history = []
        self.symbols = []
        self.add_symbols(symbols)

    def add_symbols(self, symbols: List[Symbol]) -> SearchResult:
        """Add symbols. Removes duplicates, sorts, and bucketizes after adding."""
        self.symbols.extend(symbols)
        self.symbols = remove_duplicates(self.symbols)
        self.symbols.sort(key=create_sort_key_for_query(self.query))
        self.buckets = bucketize(self.query, self.symbols)
        return self

    def filter(
        self, country: Optional[str] = None, type_: Optional[str] = None
    ) -> SearchResult:
        """Filter for country or type and return a new `SearchResult` with the results
        after filtering. Also updates the filter history.
        """
        # FIXME Use InvestingType or TessaType for type_.
        symbols = self.symbols
        filters = []
        if country:
            symbols = [
                s for s in symbols if s.country and s.country.lower() == country.lower()
            ]
            filters.append(f"country={country}")
        if type_:
            symbols = [s for s in symbols if s.type_ == type_]
            filters.append(f"type_={type_}")
        newres = SearchResult(self.query, symbols)
        newres.filter_history = self.filter_history + filters
        return newres

    def __str__(self) -> str:
        """Return summary."""
        out = ""

        def s(line: str = "", indent=False) -> None:
            nonlocal out
            indent_str = "  " if indent else ""
            out += indent_str + line + "\n"

        s(f"Search results for query '{self.query}'")
        if len(self.filter_history) > 0:
            s("With filters: " + ", ".join(self.filter_history))
        s()
        for i, b in enumerate(self.buckets):
            s(f"Bucket {i}: {b.name}")
            countries = set(s.country for s in b.symbols) - {None}
            types = set(s.type_ for s in b.symbols)

            if len(b.symbols) == 0:
                s("No hits", indent=True)
            else:
                s(
                    f"{len(b.symbols)} hits, {len(types)} types, "
                    f"{len(countries)} countries",
                    indent=True,
                )
                if len(b.symbols) in range(1, 6):
                    s("Hits: " + ", ".join([s.name for s in b.symbols]), indent=True)
                if len(types) in range(1, 6):
                    s("Types: " + ", ".join(types), indent=True)
                if len(countries) in range(1, 6):
                    s("Countries: " + ", ".join(countries), indent=True)
            s()
        return out

    def p(self) -> None:
        """Convenience method to print str rep."""
        print(self)

    # FIXME Use the TessaType or whatever it is called for the filter (and maybe
    # elsewhere)
