"""
# Searching symbols

Main function is `tessa.search.search.search`, which will return a
`tessa.search.search_result.SearchResult`, offering all kinds of useful functionality.

Example use:

```python
from tessa import search

>>> r = search("roche")                 # search
>>> r.p()                               # print result statistics
>>> r.filter(exchange="EBS").symbols    # filter and get list of resulting symbols

>>> r = search("jenny")                 # another search
>>> r.filter(source="coingecko").symbols # filter for source (i.e., yahoo or coingecko)

>>> r = search("carbon")                # yet another search
>>> r.filter(source="yahoo", type="ETF").symbols # filter for source and type
```

"""

from .search_result import SearchResult
from .search import search
