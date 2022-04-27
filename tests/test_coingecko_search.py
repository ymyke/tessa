"""Test everything related to `coingecko_search` module.

Note that tests will hit the network and therefore will take a while to run.
"""

# pylint: disable=use-implicit-booleaness-not-comparison

from tessa import coingecko_search


def test_coingecko_search():
    """It returns the correct result."""
    res = coingecko_search("whale")
    assert isinstance(res, dict)
    assert len(res) == 4
    assert len(res["perfect_symbol"]) > 1


def test_coingecko_search_non_existent_query():
    """It returns an empty dict if the query doesn't exist."""
    assert coingecko_search("non_existent_query") == {}
