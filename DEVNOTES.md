# Next up

- Add tests
- Make it work with fignal
- Make it work for the needs of the users on investpy
- Add the lenient version // add tickerconfig
  - price_history_magic
    - SearchObj? -> Use that
    - Look up in config
    - No country given?
      - Try stock / "united states"
      - Try crypto
    - Country given?
      - Try stock, etfs, funds, bonds, ...
- Add helper functions to get the searchobj
- What about fx?
- Fix the fixmes


# QQ:

- Rename helper functions to "dataframify_investpy" etc.?
- Related: Put everything coingecko/investing into separate modules?
- Add a more lenient `price_history` function? (Make this function as simple and
straightforward as possible and then add another function that is as lenient and
forgiving as possible and tries to assume reasonable defaults wherever possible. I.e.,
set country to us if undefined or cycle through types if none given.) (E.g., would try to resolve an unknown crypto ticker using something like symbol_to_id or so...)


# Asset factory

def create_asset(str or spec):
    # Should maybe have some default spec that simply assumes vanilla stock.


a = create_asset("SLICHA.SW")
a.price_history()

# What namespaces/types do we have?

- investpy ==> searchobj (as str or as dict)
  - query (can get type implicitly)
- coingecko ==> crypto
  - query, type
- investing/stock
- investing/fund
- investing/etf
- investing/crypto
- investing/bond
- investing/index
- investing/certificate
  - query, type, sometimes country

=> Work with a type hint in the investing cases? But otherwise try through all the
types?

# Asset v TCI

Asset:
    ticker, today, todayprice

    latest_stableprice
    price_history
    get_strategy
    lookup_price
    pricegraph

TickerConfigItem:
    (type, country, watch, delisted, strategy, jurisdiction)
    type, country, bloomberg, investpy, aliases

    matches
    get_strategy_string
    is_investpy_direct


# Functionality

- Calls:
  - price_history(asset_spec, target_currency)
    - w/o target_currency: simply return whatever we get along with the currency?
  - price_point(asset_spec, date, target_currency)
    - return effective date, price, currency
  - price_latest(asset_spec, target_currency)
    - return effective date, price, currency
  - exchange -- should be a separate function 
  - BTW, should target_currency be more like an asset_spec for the target?
    - Or is fiat enough? Or is there a need for something like history("BTC", "ETH"),
      i.e. retrieving the price of "BTC" in "ETH"?
  - Or: Make this oo? asset.price_history, asset.price_point, asset.price_latest,
    asset.convert_to(asset) -- Then we'd have an asset directory.
- Should this be more generic?
  - history(asset_spec, return_spec)
    - asset_spec example: sren.sw, public stock, bloombergticker, switzerland
    - asset_spec example: metaportal-gaming-index, crypto, coingeckosymbol
      - Is bloombergticker and coingeckosymbol a type or a namespace? I think rather a
        namespace.
    - return_spec example: price, chf
  - => no, this is too generic.
- Should there also be verbose variants that return all kind of additional information?
- Give hints re asset characteristics such as type or country etc. -- or try to get them
  from a central directory if nothing given.
- Get any asset price in any arbitrary currency.
  - No need for fx? (Or fx only as a helper method?)
  - Might need "routing", i.e., exchange information over several hops whenever there is
    no immediate exchange available between two assets? Could become complex to resolve.
- Should there be finer-grained time resolution for things such as crypto?

# The case for a "Asset identity & information access" layer

- alerts.py uses the models to access the right `price_history` function depending on
  the asset type. -> Need some abstraction layer there? Something better than
  `api.ticker` today?
- Tickerconfig: Is used in both finalerts and fignal. 
  - What should this be in the future? Something central somewhere?
  - Also add crypto to it? (Including the coingecko symbols?)
  - Or would this be some kind of generic price access layer that contains everything in
    the `api` folder as well as the tickerconfig?
  - Could also take care of other stuff: SearchObj, rate limiting detection / caching /
    sleeping, aux functions to search for tickers etc.
  - Tickerconfig would have to be extensible. Would have just the minimum information
    required to uniquely identify an asset but would be lenient enough to allow storing
    of arbitrary additional attributes like `strategy` or `comments` that can be used in
    "higher levels" such as Fignal.
- Would this also include the base classes Asset, PublicEquityAsset, CryptoAsset, etc.?


# Other dependencies

- What about MetricHistory? -- I guess this is part of alerts? Or should this be another
  separate package? If so, why? -- Or should the whole thing be a library and alerts,
  ticker, metric history etc. be packages within it? -- Would MetricHistory be a
  glorified / persistent cache for tessa?


# Low prio stuff

- Would still need a wrapper/monkeypatching function in fignal to patch in the LNKD
  pricepoint.
- Use tessa in pypme for the investpy variants?
- Do we have a timezone issue? Do the different APIs return datetimes in different
  timezones and should the standardized?
- investpy calls get split into a series of requests. See below. Is that a problem?


```python
('https://www.investing.com/instruments/HistoricalDataAjax',)
{'headers': {'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/540.0 (KHTML,like Gecko) Chrome/9.1.0.0 Safari/540.0', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'text/html', 'Accept-Encoding': 'gzip, deflate', 'Connection': 'keep-alive'}, 'data': {'curr_id': 6408, 'smlID': '92251770', 'header': 'AAPL Historical Data', 'st_date': '01/01/1900', 'end_date': '01/01/1919', 'interval_sec': 'Daily', 'sort_col': 'date', 'sort_ord': 'DESC', 'action': 'historical_data'}}
('https://www.investing.com/instruments/HistoricalDataAjax',)
{'headers': {'User-Agent': 'Mozilla/5.0 (Windows; Windows NT 6.1; rv:2.0b2) Gecko/20100720 Firefox/4.0b2', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'text/html', 'Accept-Encoding': 'gzip, deflate', 'Connection': 'keep-alive'}, 'data': {'curr_id': 6408, 'smlID': '21131786', 'header': 'AAPL Historical Data', 'st_date': '01/02/1919', 'end_date': '01/02/1938', 'interval_sec': 'Daily', 'sort_col': 'date', 'sort_ord': 'DESC', 'action': 'historical_data'}}
('https://www.investing.com/instruments/HistoricalDataAjax',)
{'headers': {'User-Agent': 'Mozilla/5.0 (X11; U; SunOS sun4u; en-US; rv:1.9b5) Gecko/2008032620 Firefox/3.0b5', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'text/html', 'Accept-Encoding': 'gzip, deflate', 'Connection': 'keep-alive'}, 'data': {'curr_id': 6408, 'smlID': '47294602', 'header': 'AAPL Historical Data', 'st_date': '01/03/1938', 'end_date': '01/03/1957', 'interval_sec': 'Daily', 'sort_col': 'date', 'sort_ord': 'DESC', 'action': 'historical_data'}}
('https://www.investing.com/instruments/HistoricalDataAjax',)
{'headers': {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1b3) Gecko/20090305 Firefox/3.1b3 GTB5', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'text/html', 'Accept-Encoding': 'gzip, deflate', 'Connection': 'keep-alive'}, 'data': {'curr_id': 6408, 'smlID': '48552973', 'header': 'AAPL Historical Data', 'st_date': '01/04/1957', 'end_date': '01/04/1976', 'interval_sec': 'Daily', 'sort_col': 'date', 'sort_ord': 'DESC', 'action': 'historical_data'}}
('https://www.investing.com/instruments/HistoricalDataAjax',)
{'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'text/html', 'Accept-Encoding': 'gzip, deflate', 'Connection': 'keep-alive'}, 'data': {'curr_id': 6408, 'smlID': '40542120', 'header': 'AAPL Historical Data', 'st_date': '01/05/1976', 'end_date': '01/05/1995', 'interval_sec': 'Daily', 'sort_col': 'date', 'sort_ord': 'DESC', 'action': 'historical_data'}}
('https://www.investing.com/instruments/HistoricalDataAjax',)
{'headers': {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.11 Safari/534.16', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'text/html', 'Accept-Encoding': 'gzip, deflate', 'Connection': 'keep-alive'}, 'data': {'curr_id': 6408, 'smlID': '50407384', 'header': 'AAPL Historical Data', 'st_date': '01/06/1995', 'end_date': '01/06/2014', 'interval_sec': 'Daily', 'sort_col': 'date', 'sort_ord': 'DESC', 'action': 'historical_data'}}
('https://www.investing.com/instruments/HistoricalDataAjax',)
{'headers': {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.36 Safari/525.19', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'text/html', 'Accept-Encoding': 'gzip, deflate', 'Connection': 'keep-alive'}, 'data': {'curr_id': 6408, 'smlID': '19308678', 'header': 'AAPL Historical Data', 'st_date': '01/07/2014', 'end_date': '04/16/2022', 'interval_sec': 'Daily', 'sort_col': 'date', 'sort_ord': 'DESC', 'action': 'historical_data'}}
```