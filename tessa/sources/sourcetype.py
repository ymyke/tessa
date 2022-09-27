"""`SourceType` is a literal type with all known sources; used for type hinting and to
support autocomplete suggestions.
"""

from typing import Literal

SourceType = Literal[
    "yahoo",
    "coingecko",
]
