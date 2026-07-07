"""Outcome tracking, split by algorithmic vs. AI track.

Runs best-effort at the end of the daily scan: walks every past pick still
recent enough to have a 5- or 30-business-day return outstanding, records it
once (never recomputed), and aggregates both tracks into a small performance
summary for the Scoreboard view. Clearly unrealized/paper performance - see
CLAUDE.md Compliance notes.

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

Track = str  # "algorithmic" | "ai"


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
                }
    return existing


def record_outcomes() -> None:
    """Resolve any outstanding 5d/30d returns and persist the updated ledger."""
    entries = _collect_entries()
    today = _today()

    needs_price: set[str] = set()
    for entry in entries.values():
        elapsed = int(np.busday_count(entry["pick_date"], today))
        if entry["return_5d"] is None and elapsed >= config.OUTCOME_5D_BDAYS:
            needs_price.add(entry["ticker"])
        if entry["return_30d"] is None and elapsed >= config.OUTCOME_30D_BDAYS:
            needs_price.add(entry["ticker"])

    if not needs_price:
        log.info("Outcome tracking: no new returns due (%d tracked picks).", len(entries))
        _save_ledger(list(entries.values()))
        return

    log.info("Outcome tracking: fetching current prices for %d ticker(s).", len(needs_price))
    current_prices = data.fetch_current_prices(sorted(needs_price))

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

    log.info("Outcome tracking: resolved returns for %d ticker(s).", len(current_prices))
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


def _aggregate(entries: list[dict], track: Track) -> dict:
    track_entries = [e for e in entries if e["track"] == track]
    resolved_5d = [e["return_5d"] for e in track_entries if e["return_5d"] is not None]
    resolved_30d = [e["return_30d"] for e in track_entries if e["return_30d"] is not None]

    return {
        "track": track,
        "picks_count": len(track_entries),
        "avg_return_5d": round(sum(resolved_5d) / len(resolved_5d), 2) if resolved_5d else None,
        "avg_return_30d": round(sum(resolved_30d) / len(resolved_30d), 2) if resolved_30d else None,
        # Win rate is measured at the 5-day horizon, the first one that resolves.
        "win_rate": round(sum(1 for r in resolved_5d if r > 0) / len(resolved_5d), 2) if resolved_5d else None,
        "since": min((e["pick_date"] for e in track_entries), default=None),
    }


def write_track_performance() -> None:
    """Aggregate the ledger into the Scoreboard's per-track summary."""
    entries = _load_ledger()
    summary = [_aggregate(entries, "algorithmic"), _aggregate(entries, "ai")]
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.TRACK_PERFORMANCE_FILE.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    log.info("Wrote track performance: %s", {s["track"]: s["picks_count"] for s in summary})
