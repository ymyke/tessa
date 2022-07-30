
These are internal notes that won't make much sense to anybody other than me...
-- ymyke







# Todo

- Bug: symbols created from search objects from a search() call do not have the country
  set.
- Use Symbol and SymbolCollection 
  - in alerts and see how this goes.
  - in fignal.
- Add documentation (see below)
- Find diffs to master (see below)
- Release

# To be documented

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

How to:
- Try: https://pdoc3.github.io/pdoc/doc/pdoc/#pdoc&gsc.tab=0 -- or rather pdoc
- https://docs.python-guide.org/writing/documentation/ -> sphinx + readthedocs
- https://realpython.com/documenting-python-code/ -- generisches blabla


# Interface-breaking updates

- Signatures of some of the price functions changed.
- Names of some of those functions changed.
- search return symbols now.
- PriceHistory, PricePoint.
- ((Check git log and/or compare branch to master))

# Misc notes & later todos

- Compare to master and identify all changes to the price.* and search interface:
  - Adjust README accordingly.
  - Mention in release notes.
- Fix the FIXMEs.

# Changes to fignal

- Some logic has changed in how Symbols are matched.
- Use the new symbols file. (Make sure there are no new symbols in tickerconfig that are
  not yet in symbols.yaml)
- Got rid of todayprice in Symbol. Use latest_price instead. -- A number of changes
  needed in fignal bc todayprice is used often.
- What about PublicEquityAssetMixin and CryptoAssetMixin -- which parts are still
  needed? -- Most of it seems not necessary bc the new, generalized symbols can do it
  all.

# Things to consider in fignal

- Will Portfolio class be a subclass of SymbolCollection?
- Will (Portfolio)Assets be a subclass of Symbol or will they just have a symbol
  (composition)? -> Maybe preference for composition (which should according to
  literature be the preference in general).
- Should more things in fignal be value objects? E.g. dates, currencies, prices, ...?



# Misc

- The right term is symbol, not ticker. Change this everywhere sometime.
- Symbol, not Asset, because an asset is one that is really owned. As long as it's not
  owned, it's just a symbol. (Maybe later use Asset instead of PortfolioAsset if I
  refactor fignal according to this new terminology.)
  - Symbol, Asset, Portfolio


