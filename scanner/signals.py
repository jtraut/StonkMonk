"""Deterministic signal computation — no AI anywhere in here.

Given a ticker's daily OHLCV history (and an optional quote snapshot), compute
a small, explicit, inspectable set of signals, each normalized to roughly
[-1, 1] where positive is bullish. This is the part most likely to get tuned
over time, so it's kept deliberately simple and readable.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from . import config
from .data import QuoteSnapshot


@dataclass
class Signals:
    """Normalized signal set for one ticker. Each value is ~[-1, 1]."""

    trend: float
    momentum: float
    volume_surge: float
    range_position: float
    earnings_surprise: float | None = None

    def as_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items()}


def _clip(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _rsi(close: pd.Series, period: int) -> float:
    """Classic Wilder RSI, returning the latest value in [0, 100]."""
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    latest = rsi.iloc[-1]
    if pd.isna(latest):
        return 50.0
    return float(latest)


def _trend_signal(close: pd.Series) -> float:
    """Price vs. fast/slow SMAs and their relationship.

    Bullish when price is above both moving averages and the fast MA is above
    the slow (a "golden" configuration); bearish in the mirror case.
    """
    sma_fast = close.rolling(config.SMA_FAST).mean().iloc[-1]
    sma_slow = close.rolling(config.SMA_SLOW).mean().iloc[-1]
    price = close.iloc[-1]
    if pd.isna(sma_fast) or pd.isna(sma_slow) or sma_slow == 0:
        return 0.0

    above_fast = 1.0 if price > sma_fast else -1.0
    above_slow = 1.0 if price > sma_slow else -1.0
    # Fast-vs-slow separation, scaled: a 5% gap saturates the component.
    sep = _clip((sma_fast - sma_slow) / sma_slow / 0.05)
    return _clip(0.35 * above_fast + 0.35 * above_slow + 0.30 * sep)


def _momentum_signal(close: pd.Series) -> float:
    """Blend of RSI (centered at 50) and N-day rate of change."""
    rsi = _rsi(close, config.RSI_PERIOD)
    # Map RSI 0..100 -> -1..1, centered at 50.
    rsi_component = _clip((rsi - 50) / 30)

    roc_period = config.ROC_PERIOD
    if len(close) > roc_period and close.iloc[-roc_period - 1] != 0:
        roc = (close.iloc[-1] / close.iloc[-roc_period - 1]) - 1.0
        # A 15% move over the window saturates the component.
        roc_component = _clip(roc / 0.15)
    else:
        roc_component = 0.0

    return _clip(0.55 * rsi_component + 0.45 * roc_component)


def _volume_surge_signal(close: pd.Series, volume: pd.Series) -> float:
    """Recent volume relative to its baseline, signed by the day's direction.

    A volume spike is only bullish if price also rose; a spike on a down day is
    distribution, i.e. bearish.
    """
    avg_vol = volume.rolling(config.VOLUME_AVG_PERIOD).mean().iloc[-1]
    latest_vol = volume.iloc[-1]
    if pd.isna(avg_vol) or avg_vol == 0:
        return 0.0

    ratio = latest_vol / avg_vol
    # ratio 1.0 -> 0 magnitude; 2.5x -> saturates.
    magnitude = _clip((ratio - 1.0) / 1.5, 0.0, 1.0)

    direction = 0.0
    if len(close) >= 2 and close.iloc[-2] != 0:
        day_change = (close.iloc[-1] / close.iloc[-2]) - 1.0
        direction = 1.0 if day_change >= 0 else -1.0
    return _clip(magnitude * direction)


def _range_position_signal(close: pd.Series) -> float:
    """Where price sits in its 52-week range, mapped to [-1, 1].

    Near the 52-week high is bullish (breakout/strength); near the low is
    bearish. 0.5 (mid-range) maps to 0.
    """
    window = close.tail(config.RANGE_WINDOW)
    hi = window.max()
    lo = window.min()
    price = close.iloc[-1]
    if pd.isna(hi) or pd.isna(lo) or hi == lo:
        return 0.0
    pos = (price - lo) / (hi - lo)  # 0..1
    return _clip((pos - 0.5) * 2.0)


def _earnings_signal(snapshot: QuoteSnapshot | None) -> float | None:
    """Normalize an earnings surprise percentage, if we have one."""
    if snapshot is None or snapshot.earnings_surprise_pct is None:
        return None
    if math.isnan(snapshot.earnings_surprise_pct):
        return None
    # A 10% surprise saturates the component.
    return _clip(snapshot.earnings_surprise_pct / 10.0)


def compute_signals(
    prices: pd.DataFrame,
    snapshot: QuoteSnapshot | None = None,
) -> Signals | None:
    """Compute the full signal set for one ticker.

    Returns ``None`` when there isn't enough clean history to score the name.
    """
    if prices is None or "Close" not in prices.columns:
        return None
    close = prices["Close"].dropna()
    volume = prices["Volume"].dropna() if "Volume" in prices.columns else pd.Series(dtype=float)
    if len(close) < config.MIN_HISTORY_ROWS:
        return None

    return Signals(
        trend=_trend_signal(close),
        momentum=_momentum_signal(close),
        volume_surge=_volume_surge_signal(close, volume),
        range_position=_range_position_signal(close),
        earnings_surprise=_earnings_signal(snapshot),
    )


def latest_price(prices: pd.DataFrame) -> float | None:
    if prices is None or "Close" not in prices.columns:
        return None
    close = prices["Close"].dropna()
    if close.empty:
        return None
    return round(float(close.iloc[-1]), 2)


def avg_dollar_volume(prices: pd.DataFrame, window: int = config.VOLUME_AVG_PERIOD) -> float:
    """Average daily dollar volume over the recent window, for liquidity gating."""
    if prices is None or "Close" not in prices.columns or "Volume" not in prices.columns:
        return 0.0
    tail = prices.tail(window)
    dollar = (tail["Close"] * tail["Volume"]).dropna()
    if dollar.empty:
        return 0.0
    return float(dollar.mean())
