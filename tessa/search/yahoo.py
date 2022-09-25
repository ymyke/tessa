"""Get Yahoo Finance search results via scraping."""

from typing import List
import pandas as pd
from bs4 import BeautifulSoup
import requests
from .. import Symbol
from ..search import SearchResult
from .. import sources

NUM_PER_PAGE = 1000
URL_BLUEPRINT = "https://finance.yahoo.com/lookup/all?s={}&t=A&b={}&c=" + str(
    NUM_PER_PAGE
)


def create_headers(url: str) -> dict:
    return {
        "authority": "finance.yahoo.com",
        "method": "GET",
        "path": url,
        "scheme": "https",
        "accept": "text/html,application/xml;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "referer": "https://finance.yahoo.com/",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0;)",
    }


def get_tables(query: str, offset: int) -> List[pd.DataFrame]:
    """Retrieve search page for query and at offset, parse all the tables into
    dataframes and return that list.
    """
    sources.get_source("yahoo").rate_limiter.rate_limit()
    url = URL_BLUEPRINT.format(query, str(offset))
    page = requests.get(url, headers=create_headers(url))
    soup = BeautifulSoup(page.content, "lxml")
    return [pd.read_html(str(table))[0] for table in soup.find_all("table")]


def get_search_results(query: str) -> pd.DataFrame:
    """Get all search results as a dataframe. Returns an empty dataframe if there are no
    results.
    """
    offset = 0
    df = pd.DataFrame()
    tables = get_tables(query, offset)
    while len(tables) == 1:
        df = pd.concat([df, tables[0]])
        offset += NUM_PER_PAGE
        tables = get_tables(query, offset)

    if len(tables) > 1:
        raise RuntimeError(
            "Yahoo returned more than one table on the search "
            "results page, which is unexpected. Please investigate and/or "
            "submit an issue at github/tessa."
        )

    return df.reset_index(drop=True)


def dataframe_to_symbols(df: pd.DataFrame) -> List[Symbol]:
    """Convert a search result dataframe to a list of `Symbol`s."""
    symbols = []
    for _, row in df.iterrows():
        d = row.to_dict()
        args = {
            "name": d["Symbol"],
            "source": "yahoo",
            "aliases": [d["Name"]],
        }
        symbol = Symbol(**args)
        # FIXME Not the optimal solution bc adding attributes that are unknown to the
        # dataclass Symbol. Add type and exchange as optional attributes to Symbol? Or
        # add a mixin like YahooSymbol or TypedSymbol or so??
        symbol.type = d["Type"]
        symbol.exchange = d["Exchange"]
        symbols.append(symbol)
    return symbols


def yahoo_search(query: str) -> SearchResult:
    """Search on Yahoo Finance."""
    return SearchResult(
        query=query, symbols=dataframe_to_symbols(get_search_results(query))
    )
