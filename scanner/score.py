"""Composite scoring and selection.

Combines the normalized signals into a single 0-100 composite (50 = neutral),
then selects the top-N buys and up-to-N cautions. The "up to" is enforced by a
bearish threshold: a day with no strongly bearish names returns fewer, or zero,
cautions rather than padding the list.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import config
from .signals import Signals


@dataclass
class ScoredTicker:
    ticker: str
    name: str
    sector: str | None
    price_at_pick: float | None
    signals: Signals
    composite_score: float  # 0-100, 50 = neutral


def composite(signals: Signals) -> float:
    """Weighted blend of signals -> 0-100 (50 neutral).

    Signals absent for a ticker (e.g. no earnings surprise) are dropped and the
    remaining weights renormalized, so a missing signal is neutral rather than
    penalizing.
    """
    weights = config.SIGNAL_WEIGHTS
    total_weight = 0.0
    acc = 0.0
    values = signals.as_dict()
    for key, weight in weights.items():
        val = values.get(key)
        if val is None:
            continue
        acc += weight * val
        total_weight += weight
    if total_weight == 0:
        return 50.0
    normalized = acc / total_weight  # back into [-1, 1]
    return round(50.0 + normalized * 50.0, 1)


def score_all(scored_inputs) -> list[ScoredTicker]:
    """Compute composites for a list of (ticker, name, sector, price, signals)."""
    out: list[ScoredTicker] = []
    for ticker, name, sector, price, signals in scored_inputs:
        out.append(
            ScoredTicker(
                ticker=ticker,
                name=name,
                sector=sector,
                price_at_pick=price,
                signals=signals,
                composite_score=composite(signals),
            )
        )
    out.sort(key=lambda s: s.composite_score, reverse=True)
    return out


def select(scored: list[ScoredTicker]):
    """Return (buys, cautions) per the config thresholds and counts."""
    ranked = sorted(scored, key=lambda s: s.composite_score, reverse=True)

    buys = [s for s in ranked if s.composite_score >= config.BUY_MIN_SCORE][: config.BUY_COUNT]

    # Cautions: most bearish first, only those clearing the bearish threshold.
    bearish = sorted(scored, key=lambda s: s.composite_score)
    cautions = [s for s in bearish if s.composite_score <= config.CAUTION_MAX_SCORE][
        : config.SELL_COUNT_MAX
    ]

    return buys, cautions
