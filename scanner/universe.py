"""Universe build: fetch and filter the Nasdaq Global Select Market list.

Pulls Nasdaq Trader's pipe-delimited symbol directory, keeps Market Category
Q (Global Select), and drops test issues and ETFs. Liquidity filtering happens
later in the pipeline once we have volume data.
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass

import requests

from . import config

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class UniverseTicker:
    symbol: str
    name: str


def _clean_symbol(symbol: str) -> str:
    """Normalize a Nasdaq symbol to the form yfinance expects.

    Nasdaq uses ``.`` for share classes and ``$`` for preferreds/units;
    yfinance expects ``-`` for classes (e.g. BRK.B -> BRK-B). Symbols with
    ``$`` are preferreds/warrants/units we don't want in Phase 1.
    """
    return symbol.strip().replace(".", "-")


def fetch_universe(session: requests.Session | None = None) -> list[UniverseTicker]:
    """Return the filtered Global Select universe.

    Raises on network/parse failure — an empty or broken universe should abort
    the run, not silently publish nothing.
    """
    sess = session or requests.Session()
    log.info("Fetching Nasdaq symbol directory: %s", config.NASDAQ_LISTED_URL)
    resp = sess.get(config.NASDAQ_LISTED_URL, timeout=30)
    resp.raise_for_status()
    text = resp.text

    tickers = parse_nasdaq_listed(text)
    if not tickers:
        raise RuntimeError("Universe came back empty after filtering — aborting.")
    log.info("Universe: %d Global Select tickers after filtering.", len(tickers))
    return tickers


def parse_nasdaq_listed(text: str) -> list[UniverseTicker]:
    """Parse the pipe-delimited nasdaqlisted.txt content.

    Columns: Symbol | Security Name | Market Category | Test Issue |
    Financial Status | Round Lot Size | ETF | NextShares. The final line is a
    ``File Creation Time`` footer, not a record.
    """
    reader = io.StringIO(text)
    header = reader.readline().rstrip("\n").split("|")
    try:
        i_symbol = header.index("Symbol")
        i_name = header.index("Security Name")
        i_category = header.index("Market Category")
        i_test = header.index("Test Issue")
        i_etf = header.index("ETF")
    except ValueError as exc:  # header shape changed under us
        raise RuntimeError(f"Unexpected nasdaqlisted.txt header: {header}") from exc

    out: list[UniverseTicker] = []
    seen: set[str] = set()
    for line in reader:
        line = line.rstrip("\n")
        if not line or line.startswith("File Creation Time"):
            continue
        cols = line.split("|")
        if len(cols) <= max(i_symbol, i_name, i_category, i_test, i_etf):
            continue

        if cols[i_category].strip() != config.MARKET_CATEGORY:
            continue
        if cols[i_test].strip() == "Y":
            continue
        if cols[i_etf].strip() == "Y":
            continue

        raw_symbol = cols[i_symbol].strip()
        # Skip preferreds/warrants/units and any non-common share notation.
        if "$" in raw_symbol or raw_symbol == "":
            continue

        symbol = _clean_symbol(raw_symbol)
        if symbol in seen:
            continue
        seen.add(symbol)
        out.append(UniverseTicker(symbol=symbol, name=cols[i_name].strip()))

    return out
