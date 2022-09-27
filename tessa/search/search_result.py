"""Everything related to search results, especially the `SearchResult` class."""

from __future__ import annotations
import functools
from typing import List, NamedTuple, Callable
import itertools
import re
from ..symbol import Symbol

# ----- The predicates used to sort and bucketize results based on a query -----

# Each matches_* function takes a `query` and a `Symbol` and returns an int denoting the
# match, where lower numbers signify better matches but 0 (=falsy) signifies not match.


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
"""A bucket is a set of results of a certain quality level in a larger search result. A
bucket has a name and a list of symbols that belong into that bucket.
"""


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
    """Return a list in which every symbol is unique. Two symbols are considered
    equivalent if they match in `query` and `source`. Regardless of whether their names
    are the same or different.

    Note further that several symbols can have the same name but still be considered
    different if they differ in any of `query` or `source`.
    """
    equality_key = lambda symbol: str((symbol.source, symbol.query))
    return [k for k, _ in itertools.groupby(sorted(symbols, key=equality_key))]


# ----- The SearchResult class -----


class SearchResult:
    """Manages a search result consisting of a list of `Symbol`s. Removes duplicates,
    bucketizes, sorts and offers methods to filter and print statistics.

    (Design note 1: `SearchResult` has no relationship with `SymbolCollection` because
    the purposes of the two classes are very different and because they have different
    equality definitions for symbols.

    Design note 2: `SearchResult` and `SymbolCollection` have different definitions of
    equality between symbols: `SearchResult` considers 2 symbols to be equal if they are
    equal in `query` and `source`, regardless of whether they have the same name or not.
    A `SymbolCollection` does not have a definition of equality, but it does enforce
    that names are unique.)

    Example use:

    ```python
    from tessa import search
    r = search("harmony")

    # Review results:
    r.p()

    # Get the 1 symbol from source "coingecko" in the best bucket (i.e., bucket 0):
    s = r.filter(source="coingecko").buckets[0].symbols[0]
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

    def filter(self, **kwargs) -> SearchResult:
        """Filter for arbitrary attribute-value-pairs (e.g., `source="coingecko"` or
        `exchange="ebs"`) and return a new `SearchResult` with the results after the
        filtering. Also updates the filter history.
        """
        symbols = []
        for s in self.symbols:
            if all(getattr(s, k, "DOESNOTEXISTEVER") == v for k, v in kwargs.items()):
                symbols.append(s)
        newres = SearchResult(self.query, symbols)
        newres.filter_history = self.filter_history + [
            f"{k}={v}" for k, v in kwargs.items()
        ]
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
            sources = set(s.source for s in b.symbols)

            if len(b.symbols) == 0:
                s("No hits", indent=True)
            else:
                s(
                    f"{len(b.symbols)} hits, {len(sources)} sources",
                    indent=True,
                )
                if len(b.symbols) in range(1, 6):
                    s("Hits: " + ", ".join([s.name for s in b.symbols]), indent=True)
                if len(sources) in range(1, 6):
                    s("Sources: " + ", ".join(sources), indent=True)
            s()
        return out

    def p(self) -> None:
        """Convenience method to print str rep."""
        print(self)
