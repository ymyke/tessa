"""Central types in tessa. To help with type hinting, type checking, and auto
suggestions from the IDE.

# FIXME Add documentation
"""

from typing import Literal

# FIXME Put this into sources folder or file. Remove this folder.

SourceType = Literal[
    "yahoo",
    "coingecko",
]
