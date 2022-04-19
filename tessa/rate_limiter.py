"""Rate Limiter -- makes sure we don't hit the APIs too often by making sure a minimum
amount of time has elapsed between calls to an API.

The goal is to never run into errors in the first place, b/c at least investing.com
takes substantial time until it allow-lists a blocked IP address again. That is also why
we can't use a library such das Tenacity here.
"""

import time
import pendulum

guards = {
    # Additional attributes that will be added dynamically are: last_call, wait_seconds
    "investing": {
        "initial_wait_seconds": 2,
    },
    "crypto": {
        "initial_wait_seconds": 1,
    },
}


def setup_guards() -> None:
    """Set up guards."""
    for guard in guards.values():
        guard["last_call"] = pendulum.parse("1900")
        guard["wait_seconds"] = guard["initial_wait_seconds"]
        # FIXME Can get wird of `initial_wait_seconds` if we don't end up implementing
        # the exponential back-off at some point.


def rate_limit(type_: str) -> None:
    """Do the actual rate limiting."""
    which_guard = "crypto" if type_ == "crypto" else "investing"
    guard = guards[which_guard]
    diff = (pendulum.now() - guard["last_call"]).total_seconds()
    if diff < guard["wait_seconds"]:
        time.sleep(guard["wait_seconds"] - diff)
    guard["last_call"] = pendulum.now()

    # FIXME The above is a very simple approach. We could also imagine having a variant
    # that gets called with the retrieval function to be called and all the arguments
    # and then also tests for a 429 error as shown below. In this case, we could get rid
    # of the `type_` parameter and use the function name as the key to the guard dict.

    # # Call the original function and return, increase wait_seconds exponentially if
    # # a 429 error is encountered:
    # try:
    #     res = func(*args, **kwargs)
    # except (requests.HTTPError, ConnectionError) as exc:
    #     if "429" in exc:
    #         guard["wait_seconds"] *= 2
    #     raise exc

    # guard["wait_seconds"] = guard["initial_wait_seconds"]  # Reset if no error


setup_guards()
