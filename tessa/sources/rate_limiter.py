"""Rate Limiter -- makes sure we don't hit the APIs too often by making sure a minimum
amount of time has elapsed between calls to an API.

The goal is to never run into errors in the first place, b/c some sites take substantial
time until it allow-lists a blocked IP address again. That is also why we can't use a
library such das Tenacity here.
"""

from dataclasses import dataclass
import datetime
import time
import pendulum


VERY_LONG_AGO = pendulum.parse("1900")
INITIAL_BACK_OFF_TIME = 10


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

    back_off_time: int = INITIAL_BACK_OFF_TIME
    """Number of seconds to wait after a rate limit hit."""

    def reset_back_off(self):
        """Reset back-off time to initial value."""
        self.back_off_time = INITIAL_BACK_OFF_TIME

    def reset(self):
        """Reset state and stats."""
        self.last_call = VERY_LONG_AGO
        self.count_all_calls = self.count_limited_calls = 0
        self.reset_back_off()

    def rate_limit(self):
        """Enforce the minimum wait time as specified in `wait_seconds`."""
        diff = (pendulum.now() - self.last_call).total_seconds()
        if diff < self.wait_seconds:
            time.sleep(self.wait_seconds - diff)
            self.count_limited_calls += 1
        self.last_call = pendulum.now()
        self.count_all_calls += 1

    def back_off(self):
        """Back off exponentially."""
        time.sleep(self.back_off_time)
        self.back_off_time *= 2
