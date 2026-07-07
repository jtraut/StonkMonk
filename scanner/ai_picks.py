"""AI conviction picks (Phase 2, key-gated) - a separate idea source from the
composite-score selection in ``score.py``.

If an Anthropic API key is configured, the model is shown the full scored
candidate pool (minus tickers already selected as algorithmic buys/cautions),
fresh headlines per candidate, and a rolling summary of the AI track's own
past resolved outcomes, then asked to pick 1-3 high-conviction buys via a
structured tool call. Grounded strictly in the signals/headlines it's given -
never free-floating model judgment. No key, or any failure along the way
(missing package, API error, empty/invalid response), means this step is
skipped entirely and the day is algo-only, exactly like Phase 1's fallback
philosophy in ``llm.py``.
"""

from __future__ import annotations

import logging

from . import config, data, outcomes
from .score import ScoredTicker

log = logging.getLogger(__name__)

_TOOL_NAME = "submit_ai_picks"


def generate_ai_picks(
    scored: list[ScoredTicker],
    excluded: set[str],
    api_key: str | None,
) -> list[dict]:
    """Return 0-``config.AI_PICK_COUNT_MAX`` AI conviction pick dicts, shaped like ``Pick``."""
    if not api_key:
        return []

    candidates = [s for s in scored if s.ticker not in excluded][: config.AI_CANDIDATE_POOL_SIZE]
    if not candidates:
        return []

    try:
        news = data.fetch_news([s.ticker for s in candidates], config.AI_NEWS_HEADLINES_PER_TICKER)
        feedback = outcomes.load_recent_ai_outcomes(config.AI_FEEDBACK_LOOKBACK)
        raw_picks = _call_model(candidates, news, feedback, api_key)
    except Exception as exc:
        log.warning("AI conviction pick generation failed, skipping for today: %s", exc)
        return []

    by_ticker = {s.ticker: s for s in candidates}
    out: list[dict] = []
    for raw in raw_picks[: config.AI_PICK_COUNT_MAX]:
        ticker = raw.get("ticker")
        reasoning = raw.get("reasoning")
        scored_ticker = by_ticker.get(ticker)
        if scored_ticker is None or not reasoning:
            log.warning("Dropping invalid AI pick %r (not in candidate set or missing reasoning).", raw)
            continue
        out.append(_shape_pick(scored_ticker, reasoning, news.get(ticker, [])))
    return out


def _shape_pick(scored: ScoredTicker, reasoning: str, news_context: list[str]) -> dict:
    return {
        "ticker": scored.ticker,
        "name": scored.name,
        "sector": scored.sector,
        "action": "buy",
        "ai_pick": True,
        "price_at_pick": scored.price_at_pick,
        "signals": scored.signals.as_dict(),
        "composite_score": None,  # not score-selected - see spec's Pick shape
        "reasoning": reasoning,
        "news_context": news_context,
    }


def _call_model(
    candidates: list[ScoredTicker],
    news: dict[str, list[str]],
    feedback: list[dict],
    api_key: str,
) -> list[dict]:
    import anthropic  # imported lazily so a missing/no-key env never blocks the pipeline

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=config.LLM_MODEL,
        max_tokens=1024,
        temperature=config.AI_PICK_TEMPERATURE,
        tools=[_TOOL_SCHEMA],
        tool_choice={"type": "tool", "name": _TOOL_NAME},
        messages=[{"role": "user", "content": _build_prompt(candidates, news, feedback)}],
    )
    for block in response.content:
        if block.type == "tool_use" and block.name == _TOOL_NAME:
            return block.input.get("picks", [])
    raise ValueError("model did not return a submit_ai_picks tool call")


_TOOL_SCHEMA = {
    "name": _TOOL_NAME,
    "description": "Submit 1-3 high-conviction AI buy picks chosen from the given candidates.",
    "input_schema": {
        "type": "object",
        "properties": {
            "picks": {
                "type": "array",
                "maxItems": config.AI_PICK_COUNT_MAX,
                "items": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Must be one of the candidate tickers given."},
                        "reasoning": {
                            "type": "string",
                            "description": "1-3 sentence plain-English thesis grounded in the given signals/headlines.",
                        },
                    },
                    "required": ["ticker", "reasoning"],
                },
            }
        },
        "required": ["picks"],
    },
}


def _build_prompt(candidates: list[ScoredTicker], news: dict[str, list[str]], feedback: list[dict]) -> str:
    candidates_block = "\n".join(_candidate_line(s, news.get(s.ticker, [])) for s in candidates)
    feedback_block = _feedback_block(feedback)

    return (
        "You are the AI conviction-pick track of a stock-scanning tool. Your job is to find "
        "genuinely high-conviction buy ideas, independent of the tool's own composite technical "
        "score - not to rank the candidates by the score you're shown.\n\n"
        f"Candidates (already cleared a liquidity filter; each signal is roughly -1 to 1, "
        f"positive = bullish):\n{candidates_block}\n\n"
        f"Your own track record so far (in-context feedback, not fine-tuning):\n{feedback_block}\n\n"
        f"Pick between 1 and {config.AI_PICK_COUNT_MAX} of the candidates above as high-conviction "
        "buys. You may pick fewer if nothing stands out - do not pad the list. Ground each pick "
        "strictly in the computed signals and/or headlines given for it; do not invent news, "
        "numbers, or rumors not provided above, and do not give financial advice. Call the "
        f"{_TOOL_NAME} tool with your selections."
    )


def _candidate_line(scored: ScoredTicker, headlines: list[str]) -> str:
    sector_bit = f", sector: {scored.sector}" if scored.sector else ""
    headline_bit = "; ".join(headlines) if headlines else "no recent headlines"
    return (
        f"- {scored.ticker} ({scored.name}{sector_bit}) - composite score {scored.composite_score}/100, "
        f"signals: {scored.signals.as_dict()}. Recent headlines: {headline_bit}"
    )


def _feedback_block(feedback: list[dict]) -> str:
    if not feedback:
        return "No resolved AI-track picks yet - this may be one of the first."
    lines = []
    for entry in feedback:
        parts = [f"{entry['ticker']} picked {entry['pick_date']}"]
        if entry.get("return_5d") is not None:
            parts.append(f"5d return {entry['return_5d']:+.2f}%")
        if entry.get("return_30d") is not None:
            parts.append(f"30d return {entry['return_30d']:+.2f}%")
        lines.append("- " + ", ".join(parts))
    return "\n".join(lines)
