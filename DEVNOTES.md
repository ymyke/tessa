

These are internal notes that won't make much sense to anybody other than me...
-- ymyke


# Additional tests?

```python
@pytest.mark.parametrize(
    "ticker, at_date, exp_close",
    [
        ("BTC", "11/10/2019", 8809.78367388588),
        ("ETH", "11/05/2019", 185.76433086001398),
        ("LTC", "11/03/2019", 58.35754576168543),
    ],
)
@pytest.mark.enable_socket
def test_coingecko_crypto(ticker, at_date, exp_close):
    res = api.coingecko.crypto_lookup_price(ticker, at_date, "USD")
    assert res == exp_close
```

```python
@pytest.mark.parametrize(
    "currencypair, from_date, to_date, exp_close",
    [
        ("USD/CHF", "01/01/2015", "02/01/2015", 0.994),
        ("USD/CHF", "12/06/2018", "13/06/2018", 0.9868),
        ("USD/CHF", "29/03/2020", "30/03/2020", 0.9583),
        ("EUR/CHF", "01/01/2015", "02/01/2015", 1.2031),
        ("EUR/CHF", "12/06/2018", "13/06/2018", 1.159),
        ("EUR/CHF", "29/03/2020", "30/03/2020", 1.0587),
    ],
)
@pytest.mark.enable_socket
def test_investing_fx(currencypair, from_date, to_date, exp_close):
    res = investpy.get_currency_cross_historical_data(
        currency_cross=currencypair, from_date=from_date, to_date=to_date, as_json=True
    )
    elem = json.loads(res)["historical"][0]
    assert elem["date"] in [from_date, to_date]
    assert elem["Currency"] == "CHF"
    assert elem["close"] == exp_close
```

```python
@pytest.mark.parametrize(
    "ticker, country, from_date, to_date, exp_close",
    [
        ("AAPL", "united states", "01/01/2020", "02/01/2020", 75.09),
        ("SRENH", "switzerland", "20/12/2019", "21/12/2019", 109.7),
        ("ZALG", "germany", "15/05/2018", "16/05/2018", 43.81),
        # Interesting: The first 2 calls return just 1 row,
        # whereas the last call returns 2.
    ],
)
@pytest.mark.enable_socket
def test_investpy_stock(ticker, country, from_date, to_date, exp_close):
    res = investpy.get_stock_historical_data(
        stock=ticker, country=country, from_date=from_date, to_date=to_date
    )
    assert res.Close[-1] == exp_close
```

```python


def test_investpy_stock_noticker():
    with pytest.raises(RuntimeError):
        investpy.get_stock_historical_data(
            stock="SREN.SW",
            country="switzerland",
            from_date="01/01/2020",
            to_date="02/01/2020",
        )

@pytest.mark.parametrize(
    "ticker, country, from_date, to_date, exp_close",
    [
        ("UBS SLI CHF A-dis", "switzerland", "20/12/2019", "21/12/2019", 168.48),
        ("UBS MSCI Emerging Markets", "switzerland", "05/05/2020", "06/05/2020", 87.65),
        (
            "iShares S&P 500 CHF Hedged",
            "switzerland",
            "15/05/2018",
            "16/05/2018",
            47.86,
        ),
    ],
)
@pytest.mark.enable_socket
def test_investpy_etf(ticker, country, from_date, to_date, exp_close):
    res = investpy.get_etf_historical_data(
        etf=ticker, country=country, from_date=from_date, to_date=to_date
    )
    assert res.Close[-1] == exp_close


def test_investpy_etf_noticker():
    with pytest.raises(RuntimeError):
        investpy.get_etf_historical_data(
            etf="SREN.SW",
            country="switzerland",
            from_date="01/01/2020",
            to_date="02/01/2020",
        )

@pytest.mark.skip(reason="Currently not working. Would need to use SearchObj I think.")
@pytest.mark.parametrize(
    "ticker, country, from_date, to_date, exp_close",
    [
        (
            "Ubs (lux) Equity Fund - China Opportunity (usd) P-mdist",
            "luxembourg",
            "23/07/2020",
            "24/07/2020",
            236.83,
        )
    ],
)
@pytest.mark.enable_socket
def test_investpy_fund(ticker, country, from_date, to_date, exp_close):
    res = investpy.get_fund_historical_data(
        fund=ticker, country=country, from_date=from_date, to_date=to_date
    )
    assert res.Close[-1] == exp_close


@pytest.mark.enable_socket
def test_investpy_fund_noticker():
    with pytest.raises(RuntimeError):
        investpy.get_fund_historical_data(
            fund="SREN.SW",
            country="switzerland",
            from_date="01/01/2020",
            to_date="02/01/2020",
        )


```

Also something for currency_cross?
Need to add a test that tests the scanning functionality in the df?



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

