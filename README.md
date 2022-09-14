
# tessa – simple, hassle-free access to price information of financial assets 📉🤓📈

tessa is a Python library to help you **easily search asset identifiers** (e.g.,
tickers) and **retrieve price information** for assets in different categories such as
stocks, crypto, etfs, etc. It takes care of the different APIs, caching, rate limiting,
and other hassles.

tessa builds on investpy and pycoingecko and offers **a simplified and unified
interface**. This applies especially to investpy, which for some reason has different
ways of finding assets and accessing the respective data.

Why these two packages? [investpy](https://github.com/alvarobartt/investpy) offers
high-quality data for most categories from [investing.com](https://www.investing.com/).
However, investing.com lacks on the crypto side, so crypto data is retrieved using
[pycoingecko](https://github.com/man-c/pycoingecko) from
[Coingecko](https://www.coingecko.com/)'s API.

Importantly, tessa makes sure to be nice to the sites being accessed and tries to
**prevent users from being blocked by 429 rate limiting errors** by 1) caching results upon
retrieval and 2) keeping track of request timestamps and waiting appropriate amounts of
time if necessary.

Finally, tessa provides functionality to **manage collections of symbols**, store and
load them, and extend their functionality.


## FIXME

- Use case: search for some symbol/ticker, pick one, use the Symbol object directly to
  retrieve price information, print YAML from symbol, add several symbols to a
  SymbolCollection, store yaml in symbols.yaml file, load the file as a
  SymbolCollection. Do some analysis on the symbols. (Maybe even load a yaml file, find
  some more symbols, add those symbols to the collection, save the collection.)
- Existing use cases in README which access price.* functions directly should be rather
  lower prio in the future. Only keep as illustrations of how things work under the
  hood?
- Maybe the fact that the price functions now return PricePoint and PriceHistory types?
- ((Maybe provide a comprehensive jupyter notebook as documentation?))





## Main submodules FIXME

symbol, search, price

FIXME Needs new architecture in file system first.


## How to use


FIXME Continue here somehow


## Main functions

- `search`: Search for an asset in all sources and types.
- `price_history`: Retrieve the full history of an asset as a dataframe.
- `price_point_strict`: Get an asset's price at a certain point in time. Fail if no
  price found.
- `price_point`: Same, but find the nearest price if the given point in time has no
  price.
- `price_latest`: Get an asset's latest price.

## How to use the `price_*` functions directly

FIXME: Does this still make sense? Remove the search examples, since they should be used
differently now. 

FIXME: Put this elsewhere? E.g., in price/__init__? -- or to the different price
functions to which the examples fit?

FIXME Remove types_ and countries from seach functions as they are no longer supported.

```python
>>> from tessa import price_history, search, price_point, price_latest

# Ex 1, easy – Get straightforward price information:
>>> df, currency = price_history("AAPL", "stock", "united states")
>>> price_point("SAPG", "stock", "2015-12-25", "germany" )
# (Will return price at 2015-12-23.)
>>> price_point_strict("SAPG", "stock", "2015-12-25", "germany" )
# (Will raise a KeyError.)
>>> price_latest("ethereum", "crypto")

# Ex 2, medium – Find ticker and get price information for some 
# lesser-known stock, e.g. the original Roche:
>>> res = search("roche", countries="switzerland")
    2 of investing_stocks_by_full_name
    2 of investing_stocks_by_name
    1 of investing_funds_by_name
    ...
>>> res["investing_stocks_by_name"]
# -> Ticker is ROG
df, currency = price_history("ROG", "stock", country="switzerland")

# Ex 3, medium – Find Coingecko id and get price information for a
# more obscure token:
>>> res = search("jenny")
    1 of coingecko_other_symbol
    2 of coingecko_other_name
>>> res["coingecko_other_name"]
# ...
>>> df, currency = price_history("jenny-metaverse-dao-token", "crypto")

# Ex 4, medium – Find an ETF:
>>> res = search("carbon")
# ...
>>> res["investing_etfs_by_full_name"]
# ...
>>> df, currency = price_history("VanEck Vectors Low Carbon Energy", "etf", "united states")

# Ex 5, medium – Search in a selection of countries and products:
>>> res = search("renewable", countries=["united states", "canada", "mexico"], products=["etfs", "funds", "indices"])
# ...

# Ex 6, advanced – Find a stock that is not (yet?) exposed on investpy:
>>> price_history("PINS", "stock", "united states")
# Produces an error
>>> res = search("pinterest")
    2 of investing_searchobj_other
>>> res["investing_searchobj_other"]
['{"id_": 1127189, "name": "Pinterest Inc", "symbol": "PINS", "country": "united states", "tag": "/equities/pinterest-inc", "pair_type": "stocks", "exchange": "NYSE"}',
 '{"id_": 1177341, "name": "Pinterest Inc", "symbol": "PINS-RM", "country": "russia", "tag": "/equities/pinterest-inc?cid=1177341", "pair_type": "stocks", "exchange": "Moscow"}']
 >>> df, currency = price_history(res["investing_searchobj_other"][0], "searchobj")
 # ...
```


## How to install

pip install tessa


## Prerequisites

See `pyproject.toml`. Major prerequisites are the `investpy` and `pycoingecko` packages.


## Future Work

This if an initial version. There are a number of ideas on how to extend. Please leave
your suggestions and comments in the [Issues
section](https://github.com/ymyke/tessa/issues).
