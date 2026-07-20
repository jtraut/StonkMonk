"""Central configuration for the StonkMonk pick engine.

Everything tunable lives here so the scoring model, pick counts, and data
thresholds can be adjusted without hunting through the pipeline. Nothing in
here is hardcoded elsewhere.
"""

from __future__ import annotations

from pathlib import Path

# --- Paths -----------------------------------------------------------------

SCANNER_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCANNER_DIR.parent
DATA_DIR = REPO_ROOT / "data"
PICKS_DIR = DATA_DIR / "picks"
CACHE_DIR = SCANNER_DIR / ".cache"

LATEST_FILE = DATA_DIR / "latest.json"
INDEX_FILE = DATA_DIR / "index.json"
OUTCOMES_FILE = DATA_DIR / "outcomes.json"
TRACK_PERFORMANCE_FILE = DATA_DIR / "track_performance.json"

# --- Universe --------------------------------------------------------------

# Nasdaq Trader symbol directory (pipe-delimited). Market Category Q = Global
# Select Market, our free proxy for "big, liquid, Robinhood-tradable names".
NASDAQ_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
MARKET_CATEGORY = "Q"

# Liquidity floor: skip names whose average daily dollar volume is below this,
# so the scan doesn't spend time/requests on thin, un-tradable tickers.
MIN_AVG_DOLLAR_VOLUME = 5_000_000  # $5M/day

# --- Data fetch ------------------------------------------------------------

# How much daily history to pull per ticker. Need >200 sessions for a 200-day
# moving average plus a 52-week window with headroom.
HISTORY_PERIOD = "1y"
HISTORY_INTERVAL = "1d"

# yfinance is an unofficial scraper; treat every request as fallible.
BATCH_SIZE = 100          # tickers per yfinance batch download
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5  # base for exponential backoff
CACHE_TTL_HOURS = 20       # reuse same-day cache; a trading day is one run

# Fail the run rather than publish a thin/misleading day if too little of the
# universe returns usable data.
MIN_UNIVERSE_COVERAGE = 0.85  # 85%

# Minimum sessions of price history required to score a ticker at all.
MIN_HISTORY_ROWS = 200

# --- Signal parameters -----------------------------------------------------

SMA_FAST = 50
SMA_SLOW = 200
RSI_PERIOD = 14
ROC_PERIOD = 20            # rate-of-change lookback (sessions)
VOLUME_AVG_PERIOD = 20     # baseline for the volume-surge ratio
RANGE_WINDOW = 252         # ~52 weeks of sessions for high/low range

# --- Scoring weights -------------------------------------------------------

# Each signal is normalized to roughly [-1, 1] (bullish positive). The
# composite is a weighted sum, then rescaled to 0-100 for display. Weights
# need not sum to 1 — they are normalized at combine time.
SIGNAL_WEIGHTS = {
    "trend": 0.30,
    "momentum": 0.25,
    "volume_surge": 0.15,
    "range_position": 0.20,
    "earnings_surprise": 0.10,
}

# --- Selection -------------------------------------------------------------

BUY_COUNT = 3
SELL_COUNT_MAX = 3

# A caution pick must be at least this bearish (composite on the 0-100 scale,
# where 50 is neutral). This is what makes "up to 3" real: a day with no
# strongly bearish names returns fewer — or zero — cautions.
CAUTION_MAX_SCORE = 38  # composite must be <= this to qualify as caution
BUY_MIN_SCORE = 55      # a buy finalist should be at least mildly bullish

# How many scored names to persist in the shortlist for client-side
# re-ranking (Phase 3). Keep it bounded so the JSON stays small.
SHORTLIST_SIZE = 60

# --- LLM reasoning ---------------------------------------------------------

LLM_MODEL = "claude-haiku-4-5"  # cheap + fast; blurbs are short. Tune freely.
LLM_MAX_TOKENS = 200
LLM_TEMPERATURE = 0.4

# --- AI conviction picks (Phase 2, key-gated) -------------------------------

# Candidate pool for the AI pick pass: top-N scored tickers by composite
# score (algorithmic buys/cautions excluded so this is a separate idea
# source, not a rehash of the composite score).
AI_CANDIDATE_POOL_SIZE = 60
AI_PICK_COUNT_MAX = 3
AI_PICK_TEMPERATURE = 0.2  # lower than blurb generation - picks should be stable, not creative
AI_NEWS_HEADLINES_PER_TICKER = 3
# How many of the AI track's own past resolved outcomes to feed back into the
# prompt as in-context learning (see outcomes.load_recent_ai_outcomes).
AI_FEEDBACK_LOOKBACK = 10

# --- Outcome tracking (Phase 2) ---------------------------------------------

# Elapsed business days after which a pick's return is recorded (once, never
# recomputed). No market-holiday calendar - a documented approximation.
OUTCOME_5D_BDAYS = 5
OUTCOME_30D_BDAYS = 30
