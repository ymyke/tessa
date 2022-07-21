

These are internal notes that won't make much sense to anybody other than me...
-- ymyke





# Next up

- What about fx?
- Put the existing code and tests into subdirectories, e.g., price and search.
- Mark all tests that hit the net w/ @pytest.mark.net

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



## Other dependencies

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
- Would still need a wrapper/monkeypatching function in fignal to patch in the LNKD
  pricepoint.
- Use tessa in pypme for the investpy variants?
- Do we have a timezone issue? Do the different APIs return datetimes in different
  timezones and should the standardized?

