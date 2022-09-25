"""Rate Limiter -- makes sure we don't hit the APIs too often by waiting by default and
waiting exponentially if a 429 error is encountered.

The goal is to never run into errors in the first place, because some sites like
coingecko.com take substantial time until they allow-list a blocked IP address again.
That is also why we can't use a library such das Tenacity here.

Note that this module is no longer used by the package. But I left it in here anyway,
because it might come in handy for people who use the pycoingecko or some other library
in other ways than through this package.

Usage: Import the module and call `setup_guards()`.
"""

# pylint: disable=eval-used,exec-used,unused-import

import time
import requests
import pendulum

guards = {
    # Additional attributes that will be added dynamically are: last_call, wait_seconds
    "yahoo": {
        "func_name": "requests.post",
        "initial_wait_seconds": 0.2,
        "pattern": "yahoo.com",
    },
    "coingecko": {
        "func_name": "requests.Session.get",
        "initial_wait_seconds": 2.5,
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
            diff = (pendulum.now() - guard["last_call"]).total_seconds()
            if diff < guard["wait_seconds"]:
                time.sleep(guard["wait_seconds"] - diff)
            guard["last_call"] = pendulum.now()

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
        guard["last_call"] = pendulum.parse("1900")
        guard["wait_seconds"] = guard["initial_wait_seconds"]
        guard["func_orig"] = eval(guard["func_name"])
        exec(f"{guard['func_name']} = create_guard({guard['func_name']}, guard)")


# def reset_guards() -> None:
#     """Reset to the originals."""
#     for guard in guards.values():
#         exec(f"{guard['func_name']} = {guard['func_orig']}")
#         # Note that his doesn't work bc `func_orig` gets interpolated to a string
#         # representation, which in turn leads to a syntax error.
