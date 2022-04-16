"""Makes sure we don't hit the APIs too often. Also checks for corresponding errors.

The goal is to never run into errors in the first place, bc at least investing takes
substantial time until it allow-lists a blocked IP address again. That is also why we
can't use a library such das Tenacity here. 

Errors: Definitely 429. Maybe also 503, 504?

Coingecko API: 4.2 Rate limit for the CoinGecko API is 8 calls each second per Internet
Protocol ("IP") address, although such rate limit may be varied by CoinGecko at any time
in its sole discretion without notice or reference to you or any Users. You agree not to
exceed or circumvent (or make any attempts thereto) the aforesaid rate limitation,
limitations on the calls and use of CoinGecko API as may be implemented by CoinGecko
from time to time in its sole discretion (without any notice or reference to you), or
otherwise use the CoinGecko API in a manner that can be anticipated to exceed reasonable
request volume, constitute excessive or abusive usage, or otherwise fail to comply or is
inconsistent with any part of this API Terms, the API Documentation, our Privacy Policy,
our Website Terms of Use, or the limitations of your selected usage plan.
https://www.coingecko.com/en/api_terms
"""

# pylint: disable=eval-used,exec-used,unused-import

# FIXME:
# - Use status codes from requests package.
# - Get wait time from response headers. (x-quota-resets-on or retry-after or ...?)
# - Check url

import atexit
import time
import requests
import pendulum as pdl

hooks = {
    "investing": {
        "func_name": "requests.post",
        "wait_seconds": 2,
        "pattern": "investing.com",
    },
    "coingecko": {
        "func_name": "requests.Session.get",
        "wait_seconds": 1,
        "pattern": "coingecko.com",
    },
}


def create_guard(func: callable, hook: dict) -> callable:
    def guard(*args, **kwargs):

        # If the call is for the url pattern, check if the last call was long enough in
        # the past and wait, if not:
        if any(
            hook["pattern"] in x
            for x in args + tuple(kwargs.values())
            if isinstance(x, str)
        ):
            diff = (pdl.now() - hook["last_call"]).total_seconds()
            if diff < hook["wait_seconds"]:
                time.sleep(hook["wait_seconds"] - diff)
            hook["last_call"] = pdl.now()
        
        # Call the original function and return:
        return func(*args, **kwargs)

    return guard


def reset_functions():
    """Reset to the originals."""
    for hook in hooks.values():
        exec(f"{hook['func_name']} = {hook['orig_func']}")


# Code that gets executed when the module gets loaded:


for hook in hooks.values():
    hook["last_call"] = pdl.parse("1900")
    hook["func_orig"] = eval(hook["func_name"])
    exec(f"{hook['func_name']} = create_guard({hook['func_name']}, hook)")


atexit.register(reset_functions)


# investpy 429:

# ConnectionError                           Traceback (most recent call last)
# c:\code\tessa\x.py in <cell line: 4>()
#       20 while True:
#       21     print(".", end="")
# ----> 22     investpy.get_currency_cross_historical_data(
#       23         "USD/CHF",
#       24         from_date="01/01/2015",
#       25         to_date=datetime.now().strftime("%d/%m/%Y"),
#       26         as_json=True,
#      27     )

# File C:\code\tessa\.venv\lib\site-packages\investpy\currency_crosses.py:674, in get_currency_cross_historical_data(currency_cross, from_date, to_date, as_json, order, interval)
#     671 req = requests.post(url, headers=head, data=params)
#     673 if req.status_code != 200:
# --> 674     raise ConnectionError(
#     675         "ERR#0015: error " + str(req.status_code) + ", try again later."
#     676     )
#     678 if not req.text:
#     679     continue

# ConnectionError: ERR#0015: error 429, try again later.


# Coingecko 429:

# ---------------------------------------------------------------------------
# HTTPError                                 Traceback (most recent call last)
# c:\code\tessa\x.py in <cell line: 3>()
#       19 while True:
#       20     print(".", end="")
# ----> 21     prices = CoinGeckoAPI().get_coin_market_chart_by_id(
#       22             id="bitcoin",
#       23             vs_currency="chf",
#       24             days="max",
#       25             interval="daily",
#       26         )

# File C:\code\tessa\.venv\lib\site-packages\pycoingecko\utils.py:12, in func_args_preprocessing.<locals>.input_args(*args, **kwargs)
#       9 # check in *args for lists and booleans
#      10 args = [arg_preprocessing(v) for v in args]
# ---> 12 return func(*args, **kwargs)

# File C:\code\tessa\.venv\lib\site-packages\pycoingecko\api.py:169, in CoinGeckoAPI.get_coin_market_chart_by_id(self, id, vs_currency, days, **kwargs)
#     166 api_url = '{0}coins/{1}/market_chart?vs_currency={2}&days={3}'.format(self.api_base_url, id, vs_currency, days)
#     167 api_url = self.__api_url_params(api_url, kwargs, api_url_has_params=True)
# --> 169 return self.__request(api_url)

# File C:\code\tessa\.venv\lib\site-packages\pycoingecko\api.py:29, in CoinGeckoAPI.__request(self, url)
#      26     raise
#      28 try:
# ---> 29     response.raise_for_status()
#      30     content = json.loads(response.content.decode('utf-8'))
#      31     return content

# File C:\code\tessa\.venv\lib\site-packages\requests\models.py:960, in Response.raise_for_status(self)
#     957     http_error_msg = u'%s Server Error: %s for url: %s' % (self.status_code, reason, self.url)
#     959 if http_error_msg:
# --> 960     raise HTTPError(http_error_msg, response=self)

# HTTPError: 429 Client Error: Too Many Requests for url: https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=chf&days=max&interval=daily
