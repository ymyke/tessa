

These are internal notes that won't make much sense to anybody other than me...
-- ymyke





# Next up

- Add new folders and subpackages:
  - tessa.price (same in tests)
  - tessa.search (same in tests)
  - tessa.utils? <- rate limiters? also freezeargs?
    - also investing_types in here?
- Put the existing code and tests into subdirectories, e.g., price and search.
- Mark all tests that hit the net w/ @pytest.mark.net
- Fix FIXMEs.


# Some day

- Add some Literal type for "stock", "etf" etc. that can be used for type hints,
  autocomplete suggestions, and type checking in price.py (and elsewhere?). (List of
  types: ["crypto", "stock", "etf", "fund", "crypto", "bond", "index", "certificate",
  "currency_cross", "searchobj"])


# Equality of symbols

type_ + query + country ⇒ equality
vs
name

in search results:
- same name → can be different symbols
- different type_ + query + country → different symbols, but can have same name
- same type_ + query + country / different name → same symbols


in SymbolCollection, if loaded from yaml:
- same name → not possible
- same type_ + query + country / different name → don't care


⇒ SearchResult is not a subclass of SymbolCollection bc it has different invariants.
⇒ Which invariants does SymbolCollection really have and impose?


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


