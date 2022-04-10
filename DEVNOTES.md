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
- Should this be more generic?
  - history(asset_spec, return_spec)
    - asset_spec example: sren.sw, public stock, bloombergticker, switzerland
    - asset_spec example: metaportal-gaming-index, crypto, coingeckosymbol
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
- Tickerconfig: I used in both finalerts and fignal. 
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

# Caching / rate limiting strategies

- requests_cache
- own caching, like in fx
  - Why did I do this in the first place? => Bc it doesn't seem to work w investpy, at least not with the currency_cross function.
- function-level caching w/ the corresponding fixtures -> Would be the best way I think
- always get big chunks, even if smaller chunks requested -- in order to hit the api
  fewer times
- how often to check if there is new information available? (e.g., in long-running
  applications that run for hours or days where a call to a date w/o data now can lead
  to a call w/ data at some point in the future (still during runtime))
    -> Simply use expiration in requests_cache?
- maybe even make a full replica of things?

# Other dependencies

- What about MetricHistory? -- I guess this is part of alerts? Or should this be another
  separate package? If so, why? -- Or should the whole thing be a library and alerts,
  ticker, metric history etc. be packages within it? -- Would MetricHistory be a
  glorified / persistent cache for tessa?


# Low prio stuff

- Would still need a wrapper/monkeypatching function in fignal to patch in the LNKD
  pricepoint.
- Use tessa in pypme for the investpy variants?