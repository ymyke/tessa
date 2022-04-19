"""Rate Limiter -- makes sure we don't hit the APIs too often by waiting by default and
waiting exponentially if a 429 error is encountered.

The goal is to never run into errors in the first place, b/c at least investing.com
takes substantial time until it allow-lists a blocked IP address again. That is also why
we can't use a library such das Tenacity here.
"""

# FIXME Keep it as a tool that people can import when they use the coingecko or investpy
# libraries in other ways than through this package?

# pylint: disable=eval-used,exec-used,unused-import

import atexit
import time
import requests
import pendulum as pdl

guards = {
    # Additional attributes that will be added dynamically are: last_call, wait_seconds
    "investing": {
        "func_name": "requests.post",
        "initial_wait_seconds": 2,
        "pattern": "investing.com",
    },
    "coingecko": {
        "func_name": "requests.Session.get",
        "initial_wait_seconds": 1,
        "pattern": "coingecko.com",
    },
}


def create_guard(func: callable, guard: dict) -> callable:
    """Create a guard."""

    def guarded_func(*args, **kwargs):

        # If the call is for the url pattern, check if the last call was long enough in
        # the past and wait, if not:
        if any(
            guard["pattern"] in x
            for x in args + tuple(kwargs.values())
            if isinstance(x, str)
        ):
            diff = (pdl.now() - guard["last_call"]).total_seconds()
            if diff < guard["wait_seconds"]:
                time.sleep(guard["wait_seconds"] - diff)
            guard["last_call"] = pdl.now()

        # Call the original function and return, increase wait_seconds exponentially if
        # a 429 error is encountered:
        try:
            res = func(*args, **kwargs)
        except (requests.HTTPError, ConnectionError) as exc:
            if "429" in exc:
                guard["wait_seconds"] *= 2
            raise exc

        guard["wait_seconds"] = guard["initial_wait_seconds"]  # Reset if no error
        return res

    return guarded_func


def setup_guards() -> None:
    """Set up guards."""
    for guard in guards.values():
        guard["last_call"] = pdl.parse("1900")
        guard["wait_seconds"] = guard["initial_wait_seconds"]
        guard["func_orig"] = eval(guard["func_name"])
        exec(f"{guard['func_name']} = create_guard({guard['func_name']}, guard)")


def reset_guards() -> None:
    """Reset to the originals."""
    for guard in guards.values():
        exec(f"{guard['func_name']} = {guard['func_orig']}")
        # FIXME This doesn't work bc `func_orig` gets interpolated to a string
        # representation, which in turn leads to a syntax error.


# FIXME Better remove this here and call these from __init__?
# FIXME Also, remove the code and have consumers call `setup_guards` explicitly.
setup_guards()
atexit.register(reset_guards)