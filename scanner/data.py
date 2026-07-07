"""Market-data fetch layer — isolated so it can be swapped wholesale.

Everything Yahoo/yfinance-specific lives here. If yfinance reliability ever
forces a move to Finnhub/Polygon/Alpha Vantage, this is the one file to
rewrite; the rest of the pipeline only sees the returned pandas frames and the
``QuoteSnapshot`` shape.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import pandas as pd

from . import config

log = logging.getLogger(__name__)


@dataclass
class QuoteSnapshot:
    """Lightweight per-ticker fundamentals we opportunistically capture.

    All fields are optional — yfinance frequently omits them, and the pipeline
    must not depend on any single one being present.
    """

    sector: str | None = None
    market_cap: float | None = None
    earnings_surprise_pct: float | None = None


@dataclass
class FetchResult:
    """OHLCV history + optional quote metadata per ticker."""

    prices: dict[str, pd.DataFrame] = field(default_factory=dict)
    quotes: dict[str, QuoteSnapshot] = field(default_factory=dict)

    @property
    def coverage(self) -> float:
        return 0.0


def _cache_path(period: str, interval: str):
    config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return config.CACHE_DIR / f"ohlcv_{period}_{interval}.parquet"


def _cache_is_fresh(path) -> bool:
    if not path.exists():
        return False
    age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
    return age < timedelta(hours=config.CACHE_TTL_HOURS)


def fetch_prices(
    symbols: list[str],
    *,
    use_cache: bool = True,
) -> dict[str, pd.DataFrame]:
    """Download daily OHLCV for ``symbols`` with batching, retry, and caching.

    Returns a dict of symbol -> DataFrame (columns: Open/High/Low/Close/Volume).
    Symbols that fail to return usable data are simply absent from the dict;
    the caller decides whether coverage is high enough to proceed.
    """
    import yfinance as yf  # imported lazily so config-only imports stay cheap

    cache_path = _cache_path(config.HISTORY_PERIOD, config.HISTORY_INTERVAL)
    if use_cache and _cache_is_fresh(cache_path):
        log.info("Using cached OHLCV: %s", cache_path)
        cached = pd.read_parquet(cache_path)
        return _split_multi(cached, symbols)

    frames: dict[str, pd.DataFrame] = {}
    batches = [symbols[i : i + config.BATCH_SIZE] for i in range(0, len(symbols), config.BATCH_SIZE)]
    log.info("Fetching OHLCV for %d symbols in %d batches.", len(symbols), len(batches))

    for bi, batch in enumerate(batches, start=1):
        raw = _download_batch(yf, batch)
        if raw is None:
            log.warning("Batch %d/%d returned nothing after retries.", bi, len(batches))
            continue
        frames.update(_split_batch(raw, batch))
        log.info("Batch %d/%d done — %d cumulative symbols.", bi, len(batches), len(frames))

    if use_cache and frames:
        _write_cache(frames, cache_path)

    return frames


def _download_batch(yf, batch: list[str]):
    """One batch download with exponential backoff."""
    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            data = yf.download(
                tickers=batch,
                period=config.HISTORY_PERIOD,
                interval=config.HISTORY_INTERVAL,
                group_by="ticker",
                auto_adjust=True,
                threads=True,
                progress=False,
            )
            if data is not None and not data.empty:
                return data
            log.warning("Empty batch response (attempt %d).", attempt)
        except Exception as exc:  # yfinance raises a grab-bag of errors
            log.warning("Batch download failed (attempt %d): %s", attempt, exc)
        if attempt < config.MAX_RETRIES:
            time.sleep(config.RETRY_BACKOFF_SECONDS * attempt)
    return None


def _split_batch(data: pd.DataFrame, batch: list[str]) -> dict[str, pd.DataFrame]:
    """Split a multi-ticker yfinance frame into per-symbol frames."""
    out: dict[str, pd.DataFrame] = {}
    single = len(batch) == 1
    for sym in batch:
        try:
            if single:
                df = data.copy()
            else:
                if sym not in data.columns.get_level_values(0):
                    continue
                df = data[sym].copy()
        except (KeyError, TypeError):
            continue
        df = df.dropna(how="all")
        if df.empty or "Close" not in df.columns:
            continue
        out[sym] = df
    return out


def _split_multi(cached: pd.DataFrame, symbols: list[str]) -> dict[str, pd.DataFrame]:
    """Reconstruct per-symbol frames from the flattened cache layout."""
    out: dict[str, pd.DataFrame] = {}
    wanted = set(symbols)
    for sym, group in cached.groupby("symbol"):
        if sym not in wanted:
            continue
        df = group.drop(columns=["symbol"]).set_index("Date")
        out[sym] = df
    return out


def _write_cache(frames: dict[str, pd.DataFrame], path) -> None:
    """Flatten per-symbol frames into a single tagged parquet for caching."""
    parts = []
    for sym, df in frames.items():
        part = df.reset_index()
        # Normalize the datetime index column name to "Date".
        first = part.columns[0]
        if first != "Date":
            part = part.rename(columns={first: "Date"})
        part["symbol"] = sym
        parts.append(part)
    if not parts:
        return
    combined = pd.concat(parts, ignore_index=True)
    combined.to_parquet(path)
    log.info("Wrote OHLCV cache: %s (%d rows)", path, len(combined))


def fetch_quotes(symbols: list[str]) -> dict[str, QuoteSnapshot]:
    """Best-effort per-ticker fundamentals (sector, market cap, surprise).

    Uses yfinance's per-ticker ``.info`` which is slow and flaky, so this is
    intentionally best-effort: any failure yields an empty snapshot rather than
    aborting. Callers must tolerate missing fields.
    """
    import yfinance as yf

    out: dict[str, QuoteSnapshot] = {}
    for sym in symbols:
        snap = QuoteSnapshot()
        try:
            info = yf.Ticker(sym).info or {}
            snap.sector = info.get("sector")
            snap.market_cap = info.get("marketCap")
            # yfinance sometimes exposes an earnings-surprise-ish field.
            eps_actual = info.get("epsCurrentYear")
            eps_est = info.get("epsForward")
            if eps_actual and eps_est:
                snap.earnings_surprise_pct = (eps_actual - eps_est) / abs(eps_est) * 100
        except Exception as exc:
            log.debug("Quote fetch failed for %s: %s", sym, exc)
        out[sym] = snap
    return out


def fetch_news(symbols: list[str], limit: int) -> dict[str, list[str]]:
    """Best-effort recent headline titles per ticker, for AI-pick grounding.

    ``yf.Ticker(sym).news`` shape has changed across yfinance versions (a
    flat ``{"title": ...}`` dict, or a newer ``{"content": {"title": ...}}``
    nesting) - handle both defensively. Any failure yields an empty list for
    that symbol rather than aborting; callers must tolerate thin coverage.
    """
    import yfinance as yf

    out: dict[str, list[str]] = {}
    for sym in symbols:
        titles: list[str] = []
        try:
            items = yf.Ticker(sym).news or []
            for item in items:
                content = item.get("content", item) if isinstance(item, dict) else {}
                title = content.get("title")
                if title:
                    titles.append(title)
                if len(titles) >= limit:
                    break
        except Exception as exc:
            log.debug("News fetch failed for %s: %s", sym, exc)
        out[sym] = titles
    return out


def fetch_current_prices(symbols: list[str]) -> dict[str, float]:
    """Latest close price for a small, arbitrary set of tickers.

    Used by outcome tracking (a handful of aging past picks, not the daily
    universe scan) - a single lightweight download, no caching, no retries.
    Symbols that fail to return usable data are simply absent from the dict.
    """
    import yfinance as yf

    if not symbols:
        return {}

    out: dict[str, float] = {}
    try:
        raw = yf.download(
            tickers=symbols,
            period="5d",
            interval="1d",
            group_by="ticker",
            auto_adjust=True,
            threads=True,
            progress=False,
        )
    except Exception as exc:
        log.warning("Current-price fetch failed for %d symbols: %s", len(symbols), exc)
        return out

    if raw is None or raw.empty:
        return out

    single = len(symbols) == 1
    for sym in symbols:
        try:
            df = raw.copy() if single else raw[sym]
        except (KeyError, TypeError):
            continue
        if "Close" not in df.columns:
            continue
        close = df["Close"].dropna()
        if close.empty:
            continue
        out[sym] = round(float(close.iloc[-1]), 2)
    return out


def save_manifest(path, coverage: float, universe_size: int) -> None:
    """Persist a tiny run manifest for debugging cache/coverage issues."""
    config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now().isoformat(),
                "coverage": coverage,
                "universe_size": universe_size,
            },
            indent=2,
        )
    )
