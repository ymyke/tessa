"""Test the Coingecko API."""

# pylint: disable=missing-docstring

import pytest
from tessa.price import coingecko


@pytest.mark.net
def test_api_returns_reasonable_data():
    df, crncy = coingecko.get_price_history("bitcoin", "CHF")
    assert df.shape[0] > 0
    assert crncy == "CHF"


@pytest.mark.net
def test_error_non_existent_currency_preference():
    with pytest.raises(ValueError) as excinfo:
        coingecko.get_price_history("ethereum", currency_preference="non-existent")
        assert "invalid vs_currency" in excinfo


@pytest.mark.net
def test_error_non_existent_name():
    with pytest.raises(ValueError) as excinfo:
        coingecko.get_price_history("non-existent")
        assert "Could not find coin with the given id" in excinfo
