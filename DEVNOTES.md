

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


