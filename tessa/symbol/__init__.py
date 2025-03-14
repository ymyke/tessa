"""

# Working with Symbols

The main class is `tessa.symbol.symbol.Symbol`, which encapsulates all the information
and functionality around symbols. A `tessa.symbol.symbolcollection.SymbolCollection`
manages a collection of symbols including save and load functionality.

Example use:

```python
from tessa import Symbol, SymbolCollection
s1 = Symbol("MSFT")                 # will use "yahoo" as the default source
s1.price_latest()                   # get latest price
sc = SymbolCollection([s1])         # create collection
sc.add(Symbol("ethereum", source="coingecko"))       # add another symbol
sc.find_one("ethereum").price_graph(monthsback=6)    # graph of 6 past months
sc.save_yaml("my_symbols.yaml")     # save
```

`tessa.symbol.extended_symbol.ExtendedSymbol` shows how the `Symbol` class can be
extended.

"""

from .symbol import Symbol
from .extended_symbol import ExtendedSymbol
from .symbolcollection import SymbolCollection
