"""`freezeargs` decorator."""

import functools
from frozendict import frozendict

def freezeargs(func: callable) -> callable:
    """Transform mutable dictionary into immutable useful to be compatible with cache.

    Based on:
    https://stackoverflow.com/questions/6358481/using-functools-lru-cache-with-dictionary-arguments
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        return func(
            *[frozendict(x) if isinstance(x, dict) else x for x in args],
            **{
                k: frozendict(v) if isinstance(v, dict) else v
                for k, v in kwargs.items()
            },
        )

    wrapped.cache_info = func.cache_info
    wrapped.cache_clear = func.cache_clear
    return wrapped

