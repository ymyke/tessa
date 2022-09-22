# Symbols.yaml specification

## Keys and attributes

Explained with an example:

```yaml
SPICHA: # The entry's key; your name for this symbol
  query: SPICHA.SW  # The symbol/query to be used by tessa
  type: stock   # Anything tessa "understands", e.g. stock, crypto, etf, ...
  aliases: [ETF SPI, SPICHA.SW] # Opt. list of aliases this ticker shall be found under
```

- Note that price information is retrieved using the tessa package. So the attributes
  `query` and `type_` are used to build queries for tessa.
- The `aliases` attribute is optional; the `lookup` function will also try and find
  matches in that list.
- If an entry has no `query` attribute, it will be set to the entry's key.
- If an entry has no `type_` attribute, it will be set to the default type (usually
  "stock").

This implies that a minimal entry can look like this:

```yaml
MSFT:
  # Just the key; all of these are then set automatically:
  # query: MSFT
  # type: stock
```

## More examples

See `docs/example_symbols.yaml` file.


## Additional attributes

You can use arbitrary additional attributes for whatever use cases make sense for you
and to further extend functionality. Some examples of what I use:

```yaml
AAPL:
  description: yada   # informational only
  isin: US0378331005  # informational only
  watch: True     # whether the ticker can produce alerts; default False
  delisted: True  # used to filter certain symbols from analysis; default False
  strategy: F&F   # one strategy or list of several strategies; default NoStrategy
      # possible strategies:
      # - F&F – Fire & Forget (implies HoldForGrowth)
      # - HoldForGrowth
      # - HoldForStability – low growth expected, but also low risk
      # - HoldForDiversification – titles I find important for diversification
      # - EnterIf – consider starting a position if prices for this title fall
      # - SellIf – consider selling if prices high and/or liquidity needed
      # - Sold – earlier holding that was sold at some point
      # - Quarterly
  strategy_comments: yada  # comments re strategy
  jurisdiction: CN  # main jurisdiction of the underlying asset(s) 
  # (not of the title representing the asset); default US, other examples: CN, several, 
  # irrelevant, EU


## Misc notes

- The syntax could later be extended to support different retrieval services; somehow
  like this:

```yaml
retriever:
    service: tessa
    query: SPICHA.SW
    type_: stock
```

