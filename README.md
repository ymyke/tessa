
# tessa – a package for asset identity & information access

tessa is a small package to help you easily search asset identifiers (e.g., tickers) and
retrieve (currently price) information for assets in different categories such stocks,
crypto, etfs, etc.

tessa builds on investpy and pycoingecko and offers a simplified and somewhat unified
interface. This applies especially to investpy, which for some reason has different ways
of finding assets and accessing the respective data.

Why these two packages? [investpy](https://github.com/alvarobartt/investpy) offers
high-quality data for most categories from [investing.com](https://www.investing.com/).
However, investing.com lacks on the crypto side, so crypto data is retrieved using
[pycoingecko](https://github.com/man-c/pycoingecko) from
[Coingecko](https://www.coingecko.com/)'s API.

Furthermore, tessa makes sure to be nice to the sites being accessed and tries to
prevent users from being blocked by 429 rate limiting errors by 1) caching results upon
retrieval and 2) keeping track of request timestamps and waiting appropriate amounts of
time if necessary.


# How to use

FIXME


# How to install

FIXME


# Prerequisites

See `pyproject.toml`. Major prerequisites are the `investpy` and `pycoingecko` packages.


# Future Work

This if an initial version. There are a number of ideas on how to extend. Please leave
your suggestions and comments in the [Issues
section](https://github.com/ymyke/tessa/issues).
