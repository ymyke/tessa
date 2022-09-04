
These are internal notes that won't make much sense to anybody other than me...
-- ymyke







# Todo

- Bug: symbols created from search objects from a search() call do not have the country
  set.
- Check all FIXMEs
- Add documentation (see below) / pdoc
- Compare to master and identify all changes to the price.* and search interface:
  - Adjust README accordingly.
  - Mention in release notes.
- Try pydantic for the Symbols/YAML reader?
- Add links to pdoc documentation to README and maybe toml file.
- Check if it works w Python 3.7.x
- Merge
- Release
- Update fignal, strela/dev, strela/prod and make sure they work.


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


# Interface-breaking updates

- Signatures of some of the price functions changed.
- Names of some of those functions changed.
- search return symbols now.
- PriceHistory, PricePoint.
- ((Check git log and/or compare branch to master))
- search functions now use investing_type instead of product(s). The types are now
  always singular rather than plural -- or sometimes this and sometimes that. But there
  are now type hints thanks to InvestingType. (75426954040673cfd6c4b982a12221819ab86e8b)
- In the main search function, the parameters are now called investing_countries and
  investing_types. (75426954040673cfd6c4b982a12221819ab86e8b)


# Terminology

- The right term is symbol, not ticker. Change this everywhere sometime.
- Symbol, not Asset, because an asset is one that is really owned. As long as it's not
  owned, it's just a symbol. (Maybe later use Asset instead of PortfolioAsset if I
  refactor fignal according to this new terminology.)
  - Symbol, Asset, Portfolio
