"""
# Searching symbols

Main function is `tessa.search.search.search`, which will return a
`tessa.search.search_result.SearchResult`, offering all kinds of useful functionality.

Example use:

```python
from tessa import search

>>> r = search("botto")
>>> r.filter(source="coingecko").symbols
```

(Note that the filter currently doesn't make much sense because coingecko is the only
search source currently with Yahoo Finance disabled.)

"""

from .search_result import SearchResult
from .search import search
