"""Test the SearchResult class."""

# pylint: disable=missing-function-docstring

from tessa.search_result import (
    SearchResult,
    matches_entire_name_or_alias,
    matches_word_boundary,
    matches_inanyway,
)
from tessa import Symbol


def test_matches_predicates():
    assert matches_entire_name_or_alias("eth", Symbol("ETH")) > 0
    assert matches_word_boundary("eth", Symbol("ETHW", aliases=["PoW ETH"])) > 0
    assert matches_inanyway("eth", Symbol("TOGETHER")) > 0
    assert matches_inanyway("et h", Symbol("TOGETHER")) == 0


def test_init_with_empty_list():
    res = SearchResult("q", [])
    assert res.query == "q"
    assert res.symbols == []
    assert all(b.symbols == [] for b in res.buckets)


def test_add_symbols():
    res = SearchResult("q", [Symbol("A")])
    res.add_symbols([Symbol("B")])
    assert len(res.symbols) == 2


def test_remove_duplicates():
    symbols = [Symbol(x) for x in "ABBBCBB"]
    res = SearchResult("q", symbols)
    assert [s.name for s in res.symbols] == ["A", "B", "C"]
    symbols[-1].type_ = "zzz"
    res = SearchResult("q", symbols)
    assert [s.name for s in res.symbols] == ["A", "B", "C", "B"]


def test_sort_and_bucketize():
    symbol_ranking_specs = [
        # name, type, query, country, aliases, expected_bucket_lengths
        ("AAA", "", "", "", [], [1, 0, 0, 0]),  # perfect match on name
        ("x1", "", "", "", ["aaa"], [2, 0, 0, 0]),  # perfect match on alias
        ("x2", "", "...aaa...", "", [], [2, 1, 0, 0]),  # word bounadary match
        ("xxaaaxxx", "", "", "", [], [2, 1, 1, 0]),  # anywhere match
        ("x", "", "", "", [], [2, 1, 1, 1]),  # no match
    ]
    res = SearchResult("aaa", [])
    for spec in symbol_ranking_specs:
        symbol_spec = spec[:-1]
        expected_bucket_lengths = spec[-1]
        res.add_symbols([Symbol(*symbol_spec)])
        assert [len(b.symbols) for b in res.buckets] == expected_bucket_lengths


def test_filtering():
    def names_as_set(sr: SearchResult) -> set:  # pylint: disable=invalid-name
        return set(s.name for s in sr.symbols)

    symbol_specs = [
        # name, type, query, country, aliases
        ("A", "stock", "", "switzerland", []),
        ("B", "fund", "", "switzerland", []),
        ("C", "stock", "", "spain", []),
        ("D", "etf", "", "france", []),
    ]
    res = SearchResult("q", [Symbol(*spec) for spec in symbol_specs])
    assert names_as_set(res) == set("ABCD")
    assert names_as_set(res.filter(country="switzerland")) == set("AB")
    assert names_as_set(res.filter(type_="stock")) == set("AC")
    assert names_as_set(res.filter(country="nowhere")) == set()
    assert names_as_set(res.filter(country="spain", type_="stock")) == set("C")
    assert names_as_set(res.filter(type_="stock").filter(country="spain")) == set("C")
    assert names_as_set(res.filter(country="nowhere").filter(type_="nothing")) == set()


def test_filter_history_gets_updated():
    res = SearchResult("q", [])
    assert res.filter_history == []
    assert res.filter(country="x").filter(type_="y").filter_history == [
        "country=x",
        "type_=y",
    ]
