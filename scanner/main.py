"""Orchestrates the daily pick-generation pipeline end-to-end.

Universe build -> data fetch -> liquidity filter -> signal computation ->
composite scoring -> selection -> LLM reasoning -> persist. Fails loudly
(non-zero exit, nothing written) rather than publish a thin or partial day.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from . import config, data, llm, score, signals, universe
from .score import ScoredTicker

log = logging.getLogger(__name__)


def run() -> None:
    log.info("Starting StonkMonk daily scan.")

    universe_tickers = universe.fetch_universe()
    universe_by_symbol = {t.symbol: t for t in universe_tickers}
    symbols = list(universe_by_symbol)

    prices = data.fetch_prices(symbols)
    coverage = len(prices) / len(symbols)
    log.info("Price coverage: %d/%d symbols (%.1f%%).", len(prices), len(symbols), coverage * 100)
    if coverage < config.MIN_UNIVERSE_COVERAGE:
        raise RuntimeError(
            f"Universe coverage {coverage:.1%} is below the {config.MIN_UNIVERSE_COVERAGE:.0%} "
            "floor - aborting without publishing."
        )

    # Liquidity floor runs here, once volume data is available (see universe.py).
    liquid_symbols = [
        sym for sym, df in prices.items() if signals.avg_dollar_volume(df) >= config.MIN_AVG_DOLLAR_VOLUME
    ]
    log.info("%d/%d symbols clear the liquidity floor.", len(liquid_symbols), len(prices))

    # Quote snapshots are opportunistic and slow (one request per ticker), so
    # only fetch them for names that survived the liquidity floor.
    quotes = data.fetch_quotes(liquid_symbols)

    scored_inputs = []
    for sym in liquid_symbols:
        sig = signals.compute_signals(prices[sym], quotes.get(sym))
        if sig is None:
            continue
        ticker_info = universe_by_symbol[sym]
        quote = quotes[sym]
        scored_inputs.append((sym, ticker_info.name, quote.sector, signals.latest_price(prices[sym]), sig))

    scored = score.score_all(scored_inputs)
    buys, cautions = score.select(scored)
    log.info("Selected %d buy(s) and %d caution(s) from %d scored tickers.", len(buys), len(cautions), len(scored))

    reasoning = llm.generate_all(buys, cautions)

    today = datetime.now(timezone.utc).date().isoformat()
    daily_run = {
        "date": today,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "universe_size": len(symbols),
        "universe_coverage": round(coverage, 4),
        "buys": [_pick(s, "buy", reasoning) for s in buys],
        "cautions": [_pick(s, "caution", reasoning) for s in cautions],
        "shortlist": [_shortlist_entry(s) for s in scored[: config.SHORTLIST_SIZE]],
    }

    _persist(daily_run)
    data.save_manifest(config.CACHE_DIR / "run_manifest.json", coverage, len(symbols))
    log.info("Daily scan complete - wrote %s.", today)


def _pick(scored: ScoredTicker, action: str, reasoning: dict[str, str]) -> dict:
    return {
        "ticker": scored.ticker,
        "name": scored.name,
        "sector": scored.sector,
        "action": action,
        "price_at_pick": scored.price_at_pick,
        "signals": scored.signals.as_dict(),
        "composite_score": scored.composite_score,
        "reasoning": reasoning.get(scored.ticker, ""),
    }


def _shortlist_entry(scored: ScoredTicker) -> dict:
    return {
        "ticker": scored.ticker,
        "name": scored.name,
        "sector": scored.sector,
        "price_at_pick": scored.price_at_pick,
        "signals": scored.signals.as_dict(),
        "composite_score": scored.composite_score,
    }


def _persist(daily_run: dict) -> None:
    config.PICKS_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(daily_run, indent=2)
    (config.PICKS_DIR / f"{daily_run['date']}.json").write_text(payload, encoding="utf-8")
    config.LATEST_FILE.write_text(payload, encoding="utf-8")
    _update_index(daily_run["date"])


def _update_index(date: str) -> None:
    if config.INDEX_FILE.exists():
        dates = json.loads(config.INDEX_FILE.read_text(encoding="utf-8"))
    else:
        dates = []
    if date not in dates:
        dates.append(date)
    dates.sort(reverse=True)
    config.INDEX_FILE.write_text(json.dumps(dates, indent=2), encoding="utf-8")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        run()
    except Exception:
        log.exception("Daily scan failed - aborting without publishing.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
