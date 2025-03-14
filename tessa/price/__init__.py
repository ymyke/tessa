"""
# Retrieving price information

Main functions:

- `tessa.price.price.price_history`: Retrieve the full history of an asset as a
  dataframe.
- `tessa.price.price.price_point_strict`: Get an asset's price at a certain point in
  time. Fail if no price found.
- `tessa.price.price.price_point`: Same, but find the nearest price if the given point
  in time has no price.
- `tessa.price.price.price_latest`: Get an asset's latest price.


Example use:

```python
>>> from tessa import price_history, price_point, price_point_strict, price_latest

>>> df, currency = price_history("AAPL")

>>> price_point("AAPL", "2015-01-01")           # will return price at 2014-12-31

>>> price_point_strict("AAPL", "2015-01-01")    # will raise a KeyError

>>> price_latest("ethereum", source="coingecko", currency_preference="CHF")

>>> price_latest("ETH-EUR", source="yahoo")

>>> price_latest("ethereum", source="yahoo")    # error b/c symbol not found on yahoo

>>> price_latest("ETH-EUR", source="coingecko") # error b/c symbol not found on coingecko

```

"""

from .types import PriceHistory, PricePoint
from .price import (
    price_history,
    price_point,
    price_point_strict,
    price_latest,
)
