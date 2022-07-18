"""Symbol class."""

import datetime
from typing import Tuple, Union
import pandas as pd
import yaml
import matplotlib.pyplot as plt
import seaborn as sns
from .. import price_history

pd.plotting.register_matplotlib_converters()

# FIXME Add more relevant things from tickerconfig.


class Symbol:
    """Symbol class. Encapsulates all the relevant information around a financial symbol
    and some functionality to get price information, display graphs, etc.
    """

    # pylint: disable=no-member

    # This attributes will be set if the attribute is not set at all:
    defaults = {
        "type": "stock",  # FIXME Introduce DEFAULT_TYPE
        "country": "united states",  # FIXME Introduce DEFAULT_COUNTRY
        # FIXME Code ends up adding country to types where it doesn't make sense. This
        # isn't a problem from from a code perspective, because the country attribute is
        # not used in those cases. But it's not very nice when a user looks at a
        # Symbol's attributes.
        "watch": False,
        "delisted": False,
        "strategy": "NoStrategy",
        "jurisdiction": "US",
    }  # FIXME Remove some of these?

    def __init__(self, name: str, data: dict) -> None:
        # Set attributes to whatever we get:
        self.__dict__.update(data)
        # Set default values:
        for k, v in self.defaults.items():
            self.__dict__.setdefault(k, v)
        self.__dict__.setdefault("name", name)
        if "query" not in data:
            self.query = name

        # FIXME Not sure that I like that the initiator causes the price history to be
        # loaded automatically. In fignal it's useful that the Tickerconfig can be
        # loaded w/ hitting the net.
        self.today, self.todayprice, self.currency = self.latest_price()
        self.currency = self.currency and self.currency.upper()

    def p(self):
        """Convenience method to print the symbol."""
        print(str(self))

    def latest_price(self) -> Tuple[pd.Timestamp, float, str]:
        """Return the latest close price. Returns a tuple of timestamp, price and
        currency. Note that this relies on caching happening on lower levels to be
        efficient.
        """
        df, currency = self.price_history()
        return (df.iloc[-1].name, float(df.iloc[-1]["close"]), currency)

    def price_history(self) -> Tuple[pd.DataFrame, str]:
        """Return a tuple of the full price history as a DataFrame of dates and close
        prices and the currency.
        """
        args = {}
        if isinstance(self.query, dict):  # searchobj case
            args["query"] = str(self.query)
            args["type_"] = "searchobj"
        else:
            args["query"] = self.query
            args["type_"] = self.type
        if "country" in self.__dict__:
            args["country"] = self.country
        return price_history(**args)

    def lookup_price(self, date: Union[str, pd.Timestamp]):
        """Look up price at given date."""
        return self.price_history()[0].loc[date]

    def pricegraph(self, monthsback=6):
        """Display this symbol's price graph over the last monthsback months.

        Returns from_date, fig, and ax in order for subclass functions to add to the
        information and even the graph displayed here.
        """
        fig, ax = plt.subplots(figsize=(16, 8))
        hist = self.price_history()[0]

        # Calc start date:
        from_date = datetime.date.today() - pd.offsets.DateOffset(months=monthsback)
        from_date = from_date.strftime("%Y-%m-%d")

        # Plot the prices:
        sns.lineplot(ax=ax, data=hist.loc[from_date:, "close"], marker="o").set(
            title=self.name
        )

        # Print some stats:
        # FIXME Leave this to an outside subclass?
        print(f"{self.name}")
        print(f"Latest price: {self.todayprice:.2f}")
        maxprice = hist[hist.index > from_date].max().close
        print(f"Drop since max: {(self.todayprice - maxprice) / maxprice:2.0%}")

        return from_date, fig, ax

    def get_strategy(self) -> str:
        """Return strategy for this symbol. To be overridden in derived classes."""
        # FIXME Fix. // Make this generic or leave to subclass?
        return "NoStrategy"

    # FIXME Should the class methods rather be implemented as a separate class such as
    # SymbolCollection?

    @classmethod
    def load_yaml(cls, yaml_file: str):
        """Load symbols from a YAML file."""
        with open(yaml_file, "r", encoding="utf-8") as stream:
            ymldict = yaml.safe_load(stream)
        return [Symbol(k, v or {}) for k, v in ymldict.items()]
