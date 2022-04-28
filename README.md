
# tessa

**Find financial assets and get their price history without worrying about different
APIs or rate limiting.**

tessa is a small package to help you **easily search asset identifiers** (e.g., tickers) and
**retrieve price information** for assets in different categories such as stocks,
crypto, etfs, etc.

tessa builds on investpy and pycoingecko and offers **a simplified and somewhat unified
interface**. This applies especially to investpy, which for some reason has different ways
of finding assets and accessing the respective data.

Why these two packages? [investpy](https://github.com/alvarobartt/investpy) offers
high-quality data for most categories from [investing.com](https://www.investing.com/).
However, investing.com lacks on the crypto side, so crypto data is retrieved using
[pycoingecko](https://github.com/man-c/pycoingecko) from
[Coingecko](https://www.coingecko.com/)'s API.

Importantly, tessa makes sure to be nice to the sites being accessed and tries to
**prevent users from being blocked by 429 rate limiting errors** by 1) caching results upon
retrieval and 2) keeping track of request timestamps and waiting appropriate amounts of
time if necessary.


# Usage examples

```python
>>> from tessa import price_history, investing_search, coingecko_search

# Ex 1, easy – Get price information for a well-known stock:
>>> df, currency = price_history("AAPL", "stock", "united states")

# Ex 2, easy – Get price information for a well-known crypto asset:
>>> df, currency = price_history(type_="crypto", query="ethereum")

# Ex 3, medium – Find ticker and get price information for some 
# lesser-known stock, e.g. the original Roche:
>>> res = investing_search("roche", "switzerland")
stocks_by_full_name: Found 2
stocks_by_name: Found 2
funds_by_name: Found 1
other_searchobj_matches: Found 5
>>> res["stocks_by_name"]
# -> Ticker is ROG
df, currency = price_history("ROG", "stock", country="switzerland")

# Ex 4, medium – Find Coingecko id and get price information for a
# more obscure token:
>>> res = coingecko_search("jenny")
other_symbol: Found 1
other_name: Found 2
>>> res["other_name"]
# ...
>>> df, currency = price_history("jenny-metaverse-dao-token", "crypto")

# Ex 5, medium – Find an ETF:
>>> res = investing_search("carbon")
# ...
>>> res["etfs_by_full_name"]
# ...
>>> df, currency = price_history("VanEck Vectors Low Carbon Energy", "etf", "united states")

# Ex 6, medium – Search in a selection of countries and products:
>>> res = investing_search("renewable", countries=["united states", "canada", "mexico"], products=["etfs", "funds", "indices"])
# ...

# Ex 7, advanced – Find a stock that is not (yet?) exposed on investpy:
>>> price_history("PINS", "stock", "united states")
# Produces an error
>>> res = investing_search("pinterest")
other_searchobj_matches: Found 2
>>> res["other_searchobj_matches"]
['{"id_": 1127189, "name": "Pinterest Inc", "symbol": "PINS", "country": "united states", "tag": "/equities/pinterest-inc", "pair_type": "stocks", "exchange": "NYSE"}',
 '{"id_": 1177341, "name": "Pinterest Inc", "symbol": "PINS-RM", "country": "russia", "tag": "/equities/pinterest-inc?cid=1177341", "pair_type": "stocks", "exchange": "Moscow"}']
 >>> df, currency = price_history(res["other_searchobj_matches"][0], "searchobj")
```


# How to install

FIXME


# Prerequisites

See `pyproject.toml`. Major prerequisites are the `investpy` and `pycoingecko` packages.


# Future Work

This if an initial version. There are a number of ideas on how to extend. Please leave
your suggestions and comments in the [Issues
section](https://github.com/ymyke/tessa/issues).
