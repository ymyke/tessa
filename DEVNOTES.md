

These are internal notes that won't make much sense to anybody other than me...
-- ymyke






# Change notes that were specific for investpy

- In the main search function, the parameters are now called investing_countries and
  investing_types. (75426954040673cfd6c4b982a12221819ab86e8b)
- search functions now use investing_type instead of product(s). The types are now
  always singular rather than plural -- or sometimes this and sometimes that. But there
  are now type hints thanks to InvestingType. (75426954040673cfd6c4b982a12221819ab86e8b)


## MetricHistory

- What about MetricHistory? -- I guess this is part of alerts? Or should this be another
  separate package? If so, why? -- Or should the whole thing be a library and alerts,
  ticker, metric history etc. be packages within it? -- Would MetricHistory be a
  glorified / persistent cache for tessa?


# Overall package architecture

A) tessa + strela + lobmys + oiloftrop?
- tessa makes a lot of sense standalone
- lobmys only to some (pretty limited) extent
- oiloftrop also very limited
- strela yes, but it will have strong dependencies for both tessa and lobmys
- would be 4 different packages with the related pain of maintaining

B) tessa (everything else in tessa) ⭐
- lower maintenance overhead
- but harder to make compatible w/ different environments bc package has more and more
  dependencies? E.g., still possible to make work w Python 3.7.13 for Google Colab?
- need to bump versions even if only certain sub-packages change
- consumers need to install everything even if they only need parts of it
- quite some complexity in the package due to the (unpackaged) files that are needed:
  - symbols.yaml
  - state file(s) for strela

B1) Installing subpackages an option?
https://stackoverflow.com/questions/45324189/python-install-sub-package-from-package
https://stackoverflow.com/questions/1675734/how-do-i-create-a-namespace-package-in-python
https://dev.to/bastantoine/discovering-python-namespace-packages-4gi3

C) tessa + strela ⭐⭐
- Let's go with this for the time being in separate `add-symbols` branch.

D) tessa + strela + lobmys/oiloftrop combined
- because tessa makes a lot of sense as a standalone package.

Note:
- Should tessa return a Symbol instead of the (dataframe, currency) tuple? The Symbol
  could then also take care of the caching and some other things. This would make a
  strong case for B or C.
  - The tessa.search would return Symbols.
  - Symbols could turn themselves into yaml entries and back from yaml entries into
    Symbols.
- There's also pypme, but that one will definitely remain independent.


# Low prio stuff

- Make sure we use pd.Dataframe vs Dataframe consistently.
- Use tessa in pypme for the investpy variants?
- Do we have a timezone issue? Do the different APIs return datetimes in different
  timezones and should the standardized?


# Some more investpy-specific tests that could be added


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


