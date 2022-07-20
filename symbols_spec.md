# Symbols.yaml specification

## Keys and attributes

Explained with an example:

```yaml
SPICHA: # The entry's key; your name for this symbol
  query: SPICHA.SW  # The symbol/query to be used by tessa
  type: stock   # Anything tessa "understands", e.g. stock, crypto, etf, ...
  country: switzerland  # Only where necessary, e.g. not with type crypto
  aliases: [ETF SPI, SPICHA.SW] # Opt. list of aliases this ticker shall be found under
```

- Note that price information is retrieved using the tessa package. So the attributes
  `query`, `type`, and `country` are used to build queries for tessa.
- The `aliases` attribute is optional; the `lookup` function will also try and find
  matches in that list.
- If an entry has no `query` attribute, it will be set to the entry's key.
- If an entry has no `type` attribute, it will be set to the default type (usually
  "stock").
- An entry's country will be set to the default country (usually "united states") if no
  country is given (and unless a country doesn't make sense for the type of symbol or
  query).

This implies that a minimal entry can look like this:

```yaml
MSFT:
  # Just the key; all of these are then set automatically:
  # query: MSFT
  # type: stock
  # country: united states
```

- Internal attribute `_querytype` is the actual type sent to tessa's price retrieval
  functions and will be derived from `query` and `type_`.


## More examples

```yaml
CHINAOPPTY:
  type: fund
  aliases: [ UECOPMD:LX, Ubs-ChinaOppoPU ]
  query:  # This is an investpy SearchObj in this case; use tessa.search to find these
    {
      "id_": 1160209,
      "name": "Ubs (lux) Equity Fund - China Opportunity (usd) P-mdist",
      "symbol": "0P000159H2",
      "country": "luxembourg",
      "tag": "/funds/lu1152091168",
      "pair_type": "funds",
      "exchange": "Luxembourg",
    }
  country: luxembourg
ETH:
  type: crypto
  query: ethereum
JENNY:
  type: crypto
  query: jenny-metaverse-dao-token  # Use tessa.search to find the right query
```


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

Questions around this: FIXME
- Keep jurisdiction; does this really make sense?
- What about the attributes that get some default value (e.g., watch, delisted,
  strategy)? Should there be some support here for that or is this left for possible
  extensions? -- Some of these then also need functionality, so they need extension code
  anyway.


## Misc notes

- The syntax could later be extended to support different retrieval services; somehow
  like this:

```yaml
retriever:
    service: tessa
    query: SPICHA.SW
    type_: stock
    country: switzerland
```

