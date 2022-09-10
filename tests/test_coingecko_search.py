"""Test everything related to `coingecko_search` module.

Note that tests will hit the network and therefore will take a while to run.
"""

# pylint: disable=missing-function-docstring

from tessa.coingecko_search import coingecko_search
from tessa.search_result import SearchResult


def test_coingecko_search_returns_plausible_results():
    res = coingecko_search("whale")
    assert isinstance(res, SearchResult)
    assert len(res.buckets[0].symbols) > 1


def test_coingecko_search_returns_empty_result_for_non_existent_query():
    assert coingecko_search("non_existent_query").symbols == []
