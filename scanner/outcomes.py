"""Outcome tracking, split by algorithmic vs. AI track.

Runs best-effort at the end of the daily scan: walks every past pick still
recent enough to have a 5- or 30-business-day return outstanding, records it
once (never recomputed), and aggregates the ledger into three Scoreboard
cards - Buy, Caution, and AI Conviction. Buy and Caution both come from the
"algorithmic" ledger track (split by action, since they're opposite bets);
AI Conviction is its own track. Clearly unrealized/paper performance - see
CLAUDE.md Compliance notes.

Alongside those fixed-horizon returns, every tracked pick also gets a
mark-to-market ``return_all_time`` against today's current price - unlike
``return_5d``/``return_30d`` this is recomputed every run, so it reflects a
true since-inception performance number rather than a snapshot frozen at a
fixed checkpoint.

The ledger (``data/outcomes.json``) is separate from the daily
``data/picks/*.json`` snapshots, which stay immutable audit-trail entries.
Business-day counting uses ``numpy.busday_count`` (weekdays only, no market-
holiday calendar) - a documented approximation.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

import numpy as np

from . import config, data

log = logging.getLogger(__name__)

Track = str  # ledger track: "algorithmic" | "ai" (Scoreboard cards further split "algorithmic" into buy/caution)


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _load_ledger() -> list[dict]:
    if not config.OUTCOMES_FILE.exists():
        return []
    return json.loads(config.OUTCOMES_FILE.read_text(encoding="utf-8"))


def _save_ledger(entries: list[dict]) -> None:
    entries.sort(key=lambda e: (e["pick_date"], e["ticker"]), reverse=True)
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.OUTCOMES_FILE.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def _iter_picks(daily_run: dict):
    """Yield (ticker, action, price_at_pick, track) for every pick in a day's run."""
    for pick in daily_run.get("buys", []):
        yield pick["ticker"], pick["action"], pick.get("price_at_pick"), "algorithmic"
    for pick in daily_run.get("cautions", []):
        yield pick["ticker"], pick["action"], pick.get("price_at_pick"), "algorithmic"
    for pick in daily_run.get("ai_picks", []):
        yield pick["ticker"], pick["action"], pick.get("price_at_pick"), "ai"


def _collect_entries() -> dict[tuple, dict]:
    """Rebuild the full set of trackable entries from every persisted day.

    Keyed by (ticker, pick_date, track). Existing ledger entries (which may
    already carry resolved returns) take precedence over a fresh, blank one.
    """
    existing = {(e["ticker"], e["pick_date"], e["track"]): e for e in _load_ledger()}

    if not config.INDEX_FILE.exists():
        return existing

    dates = json.loads(config.INDEX_FILE.read_text(encoding="utf-8"))
    for date in dates:
        path = config.PICKS_DIR / f"{date}.json"
        if not path.exists():
            continue
        daily_run = json.loads(path.read_text(encoding="utf-8"))
        for ticker, action, price_at_pick, track in _iter_picks(daily_run):
            if price_at_pick is None:
                continue  # no anchor price, can't compute a return
            key = (ticker, date, track)
            if key not in existing:
                existing[key] = {
                    "ticker": ticker,
                    "pick_date": date,
                    "track": track,
                    "action": action,
                    "price_at_pick": price_at_pick,
                    "return_5d": None,
                    "return_30d": None,
                    "return_all_time": None,
                }
    return existing


def record_outcomes() -> None:
    """Resolve outstanding 5d/30d returns and refresh the all-time mark-to-market.

    Every tracked ticker needs a fresh current price each run for the
    all-time figure, so unlike the old threshold-gated fetch, this always
    hits the network when there's at least one tracked pick.
    """
    entries = _collect_entries()
    today = _today()

    all_tickers = sorted({entry["ticker"] for entry in entries.values()})
    if not all_tickers:
        log.info("Outcome tracking: no tracked picks yet.")
        _save_ledger(list(entries.values()))
        return

    log.info("Outcome tracking: fetching current prices for %d ticker(s).", len(all_tickers))
    current_prices = data.fetch_current_prices(all_tickers)

    for entry in entries.values():
        current = current_prices.get(entry["ticker"])
        if current is None:
            continue
        elapsed = int(np.busday_count(entry["pick_date"], today))
        entry_return = round((current - entry["price_at_pick"]) / entry["price_at_pick"] * 100, 2)
        if entry["return_5d"] is None and elapsed >= config.OUTCOME_5D_BDAYS:
            entry["return_5d"] = entry_return
        if entry["return_30d"] is None and elapsed >= config.OUTCOME_30D_BDAYS:
            entry["return_30d"] = entry_return
        entry["return_all_time"] = entry_return

    log.info("Outcome tracking: refreshed prices for %d ticker(s).", len(current_prices))
    _save_ledger(list(entries.values()))


def load_recent_ai_outcomes(limit: int) -> list[dict]:
    """Last ``limit`` resolved AI-track entries, most recent first.

    Used as the rolling in-context feedback fed into the AI pick prompt.
    """
    resolved = [
        e
        for e in _load_ledger()
        if e["track"] == "ai" and (e["return_5d"] is not None or e["return_30d"] is not None)
    ]
    resolved.sort(key=lambda e: e["pick_date"], reverse=True)
    return resolved[:limit]


def _aggregate(
    entries: list[dict],
    label: str,
    *,
    track: Track,
    action: str | None = None,
    invert_win: bool = False,
) -> dict:
    """Aggregate ledger entries into one Scoreboard card.

    ``label`` is the card identifier (buy / caution / ai), which is not
    always the same as the ledger's ``track`` field - buy and caution picks
    both live under the "algorithmic" track but get their own cards, since
    they're opposite bets and a blended average of the two wouldn't mean
    much. ``invert_win`` flips win-rate polarity for caution picks: a
    caution call is a "win" when the price actually fell, not rose.
    """
    track_entries = [
        e for e in entries if e["track"] == track and (action is None or e["action"] == action)
    ]
    resolved_5d = [e["return_5d"] for e in track_entries if e["return_5d"] is not None]
    resolved_30d = [e["return_30d"] for e in track_entries if e["return_30d"] is not None]
    resolved_all_time = [e["return_all_time"] for e in track_entries if e.get("return_all_time") is not None]

    if resolved_5d:
        # Win rate is measured at the 5-day horizon, the first one that resolves.
        wins = sum(1 for r in resolved_5d if (r < 0 if invert_win else r > 0))
        win_rate = round(wins / len(resolved_5d), 2)
    else:
        win_rate = None

    return {
        "track": label,
        "picks_count": len(track_entries),
        "avg_return_5d": round(sum(resolved_5d) / len(resolved_5d), 2) if resolved_5d else None,
        "avg_return_30d": round(sum(resolved_30d) / len(resolved_30d), 2) if resolved_30d else None,
        "avg_return_all_time": round(sum(resolved_all_time) / len(resolved_all_time), 2)
        if resolved_all_time
        else None,
        "win_rate": win_rate,
        "since": min((e["pick_date"] for e in track_entries), default=None),
    }


def write_track_performance() -> None:
    """Aggregate the ledger into the Scoreboard's three per-card summaries."""
    entries = _load_ledger()
    summary = [
        _aggregate(entries, "buy", track="algorithmic", action="buy"),
        _aggregate(entries, "ai", track="ai"),
        _aggregate(entries, "caution", track="algorithmic", action="caution", invert_win=True),
    ]
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.TRACK_PERFORMANCE_FILE.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    log.info("Wrote track performance: %s", {s["track"]: s["picks_count"] for s in summary})
