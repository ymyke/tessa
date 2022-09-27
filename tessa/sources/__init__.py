"""

# Managing different data sources

A `tessa.sources.sources.Source` ties together all the functionality and state related
to a source such as Yahoo or Coingecko.

`tessa.sources.rate_limiter.RateLimiter` takes care of rate limiting for a source.

All known sources are specified in `tessa.sources.sources_directory`.

"""

from .sourcetype import SourceType
from .sources import Source, get_source, get_all_sources, reset_rate_limiters
