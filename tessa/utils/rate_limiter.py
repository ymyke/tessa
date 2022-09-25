"""Rate Limiter -- makes sure we don't hit the APIs too often by making sure a minimum
amount of time has elapsed between calls to an API.

The goal is to never run into errors in the first place, b/c some sites take substantial
time until it allow-lists a blocked IP address again. That is also why we can't use a
library such das Tenacity here.
"""

# FIXME Move this to sources folder?

from dataclasses import dataclass
import datetime
import time
import pendulum


VERY_LONG_AGO = pendulum.parse("1900")


@dataclass
class RateLimiter:
    """Encapsulates state and stats of a rate limiter object."""

    wait_seconds: float
    """Enforce this amount of seconds between subsequent calls."""

    last_call: datetime.datetime = VERY_LONG_AGO
    """Keeps track of last call's timestamp."""

    count_all_calls: int = 0
    """Number of total calls."""

    count_limited_calls: int = 0
    """Number of calls that triggered some waiting."""

    def reset(self):
        """Reset state and stats."""
        self.last_call = VERY_LONG_AGO
        self.count_all_calls = self.count_limited_calls = 0

    def rate_limit(self):
        """Enforce the minimum wait time as specified in `wait_seconds`."""
        diff = (pendulum.now() - self.last_call).total_seconds()
        if diff < self.wait_seconds:
            time.sleep(self.wait_seconds - diff)
            self.count_limited_calls += 1
        self.last_call = pendulum.now()
        self.count_all_calls += 1
