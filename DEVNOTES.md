

These are internal notes that won't make much sense to anybody other than me...
-- ymyke





# Next up

- Make it work with fignal
- What about fx?


# QQ:

- Add a more lenient `price_history` function? (Make this function as simple and
straightforward as possible and then add another function that is as lenient and
forgiving as possible and tries to assume reasonable defaults wherever possible. I.e.,
set country to us if undefined or cycle through types if none given.) (E.g., would try
to resolve an unknown crypto ticker using something like symbol_to_id or so...)


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


# More lenient version?

- price_history_magic
  - SearchObj? -> Use that
  - Look up in config / directory
  - No country given?
    - Try stock / "united states"
    - Try crypto
  - Country given?
    - Try stock, etfs, funds, bonds, ...


# The case for a "Asset identity & information access" layer for fignal

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


## Asset v TCI

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


## Asset factory

def create_asset(str or spec):
    # Should maybe have some default spec that simply assumes vanilla stock.


a = create_asset("SLICHA.SW")
a.price_history()


## Other dependencies

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

