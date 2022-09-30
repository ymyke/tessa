"""Test the Coingecko API."""

# pylint: disable=missing-docstring

import pytest
from tessa.price import coingecko
from tessa.price.types import SymbolNotFoundError, CurrencyPreferenceNotFoundError


@pytest.mark.net
def test_api_returns_reasonable_data():
    df, crncy = coingecko.get_price_history("bitcoin", "CHF")
    assert df.shape[0] > 0
    assert crncy == "CHF"


@pytest.mark.net
def test_error_non_existent_currency_preference():
    with pytest.raises(CurrencyPreferenceNotFoundError) as excinfo:
        coingecko.get_price_history("ethereum", currency_preference="non-existent")
    assert "No currency preference found" in str(excinfo.value)


@pytest.mark.net
def test_error_non_existent_name():
    with pytest.raises(SymbolNotFoundError) as excinfo:
        coingecko.get_price_history("non-existent")
    assert "No symbol found" in str(excinfo.value)
