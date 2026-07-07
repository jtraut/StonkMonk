"""LLM reasoning-blurb generation — the only place AI touches the pipeline.

Turns already-computed signals into a short, plain-English "why" for each
finalist (buy or caution). Scoring is 100% deterministic upstream; the LLM
never invents numbers, only narrates ones it's given. If no API key is
configured, the `anthropic` package isn't installed, or the call fails for
any reason, every blurb falls back to a deterministic template so the
pipeline never blocks on AI availability.
"""

from __future__ import annotations

import logging
import os

from . import config
from .score import ScoredTicker

log = logging.getLogger(__name__)

_SIGNAL_LABELS = {
    "trend": "trend",
    "momentum": "momentum",
    "volume_surge": "volume",
    "range_position": "52-week range position",
    "earnings_surprise": "earnings surprise",
}

# Sentence per signal, keyed by (signal name, is_bullish). Used by the
# deterministic fallback when no LLM call is available or one fails.
_FALLBACK_TEMPLATES = {
    "trend": {
        True: "{ticker} is trading above its short- and long-term moving averages, a bullish trend configuration.",
        False: "{ticker} is trading below its short- and long-term moving averages, a bearish trend configuration.",
    },
    "momentum": {
        True: "Momentum is positive, with RSI and recent price action both pointing up.",
        False: "Momentum is negative, with RSI and recent price action both pointing down.",
    },
    "volume_surge": {
        True: "Volume has surged well above its recent average on an up day, suggesting accumulation.",
        False: "Volume has surged well above its recent average on a down day, suggesting distribution.",
    },
    "range_position": {
        True: "The stock is trading near its 52-week high, showing relative strength.",
        False: "The stock is trading near its 52-week low, showing relative weakness.",
    },
    "earnings_surprise": {
        True: "The most recent earnings came in above estimates.",
        False: "The most recent earnings came in below estimates.",
    },
}

# Below this magnitude a signal is too close to neutral to anchor a sentence on.
_FALLBACK_MAGNITUDE_FLOOR = 0.1


def generate_reasoning(scored: ScoredTicker, action: str) -> str:
    """Return a 1-3 sentence reasoning blurb for one finalist.

    ``action`` is "buy" or "caution" — frames the prompt/fallback only, never
    changes the underlying signals.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        try:
            return _llm_reasoning(scored, action, api_key)
        except Exception as exc:
            log.warning("LLM reasoning failed for %s, using fallback: %s", scored.ticker, exc)
    return _fallback_reasoning(scored, action)


def generate_all(buys: list[ScoredTicker], cautions: list[ScoredTicker]) -> dict[str, str]:
    """Generate reasoning blurbs for every finalist, keyed by ticker."""
    out: dict[str, str] = {}
    for s in buys:
        out[s.ticker] = generate_reasoning(s, "buy")
    for s in cautions:
        out[s.ticker] = generate_reasoning(s, "caution")
    return out


def _llm_reasoning(scored: ScoredTicker, action: str, api_key: str) -> str:
    import anthropic  # imported lazily so a missing/no-key env never blocks the pipeline

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=config.LLM_MODEL,
        max_tokens=config.LLM_MAX_TOKENS,
        temperature=config.LLM_TEMPERATURE,
        messages=[{"role": "user", "content": _build_prompt(scored, action)}],
    )
    text = "".join(block.text for block in response.content if block.type == "text").strip()
    if not text:
        raise ValueError("empty LLM response")
    return text


def _build_prompt(scored: ScoredTicker, action: str) -> str:
    values = scored.signals.as_dict()
    signal_block = "\n".join(f"- {_SIGNAL_LABELS[k]}: {v:.2f}" for k, v in values.items() if v is not None)
    verb = "a potential buy" if action == "buy" else "a caution / consider-trimming candidate"
    sector_bit = f" in the {scored.sector} sector" if scored.sector else ""

    return (
        f"You are writing a short, plain-English blurb for a stock scanner. "
        f"{scored.ticker} ({scored.name}){sector_bit} is flagged as {verb} with a composite "
        f"score of {scored.composite_score}/100 (50 is neutral).\n\n"
        f"Computed signals (each roughly -1 to 1, positive = bullish):\n"
        f"{signal_block}\n\n"
        "Write 1-3 sentences explaining why, grounded strictly in these signals. "
        "Do not mention news, rumors, or anything not in the numbers above. "
        "Do not give financial advice or tell the reader to buy or sell — describe "
        "what the signals show. Plain English, no jargon dump."
    )


def _fallback_reasoning(scored: ScoredTicker, action: str) -> str:
    """Deterministic template used when the LLM path is unavailable or fails.

    Narrates the single strongest-magnitude signal so a blurb is always
    present, without ever inventing information the signals don't support.
    """
    values = scored.signals.as_dict()
    present = {k: v for k, v in values.items() if v is not None}
    if not present:
        return _generic_fallback(scored, action)

    top_key, top_val = max(present.items(), key=lambda kv: abs(kv[1]))
    if abs(top_val) < _FALLBACK_MAGNITUDE_FLOOR:
        return _generic_fallback(scored, action)

    sentence = _FALLBACK_TEMPLATES[top_key][top_val > 0].format(ticker=scored.ticker)
    return f"{sentence} Composite score: {scored.composite_score}/100."


def _generic_fallback(scored: ScoredTicker, action: str) -> str:
    verb = "a potential buy" if action == "buy" else "a caution / consider-trimming candidate"
    return (
        f"{scored.ticker} is flagged as {verb} based on its composite signal score "
        f"of {scored.composite_score}/100, though no single signal stands out strongly."
    )
