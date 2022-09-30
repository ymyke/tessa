"""Test coingecko search.

Note that tests will hit the network and therefore will take a while to run.
"""

# pylint: disable=missing-function-docstring

import pytest
from tessa.search.coingecko import coingecko_search
from tessa.search import SearchResult


@pytest.mark.net
def test_coingecko_search_returns_plausible_results():
    res = coingecko_search("whale")
    assert isinstance(res, SearchResult)
    assert len(res.buckets[0].symbols) > 1


@pytest.mark.net
def test_coingecko_search_returns_empty_result_for_non_existent_query():
    assert coingecko_search("non_existent_query").symbols == []
