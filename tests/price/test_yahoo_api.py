"""Test the Yahoo API."""

# pylint: disable=missing-docstring

import pytest
from tessa.price import yahoo


@pytest.mark.parametrize(
    "query, expected_currency",
    [
        ("TSLA", "USD"),
        ("SPICHA.SW", "CHF"),
        ("ZAL.DE", "EUR"),
    ],
)
@pytest.mark.net
def test_api_returns_reasonable_data(query: str, expected_currency: str):
    # FIXME Why does this test take so long?
    old_start_from = yahoo.START_FROM
    yahoo.START_FROM = "2022-01-01"
    df, crncy = yahoo.get_price_history(query)
    assert df.shape[0] > 0
    assert crncy == expected_currency
    yahoo.START_FROM = old_start_from


@pytest.mark.net
def test_non_existing_query_raises():
    with pytest.raises(Exception):
        yahoo.get_price_history("thisshouldntexistreally")
