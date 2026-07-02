# StonkMonk — Full Spec

> This document is the full spec: architecture, data model, pipeline, and
> phased roadmap. `CLAUDE.md` is the short orientation file that points back
> here.

## What it is

A daily stock picker for the Nasdaq Global Select Market (Robinhood's tradable
universe is close enough to this that it's used as the default scope — see
Universe below). Each trading day it produces a short, ranked list of **buy**
candidates and **up to** a smaller number of **sell/caution** candidates, each
with a plain-English reasoning blurb grounded in the actual computed signals
(momentum, technicals, volume, valuation where available). The "up to" on the
sell side is deliberate: some days there just isn't a strong sell signal
anywhere in the universe, and the list should say so rather than force a
count.

The project has two faces:

1. **A public live demo** — a static site on GitHub Pages, refreshed once
   per trading day by a GitHub Actions cron job, showing default picks with
   no login and no API key required from visitors.
2. **A personal, run-it-yourself version** — same codebase, run locally (or
   via a manual Actions dispatch) with your own preferences and your own
   AI key, same BYO-key philosophy as Couchworthy.

A **watchlist** (tickers you add yourself, independent of the daily picks)
and a **picks history** (so you can catch up on days you missed) are both
first-class, not afterthoughts.

**This app never places trades or connects to a brokerage account.** It is
informational only. See Compliance below — this is a permanent constraint,
not a Phase 1 shortcut.

## Decisions already made

- **Stack:** Python for the quantitative pick-generation engine (pandas,
  yfinance, pandas-ta or equivalent); React (Vite) + TypeScript (strict) +
  Tailwind for the frontend, same as Couchworthy. No always-on server for the
  public demo — GitHub Actions + committed JSON + GitHub Pages is the whole
  backend for Phase 1.
- **Universe / data source:** Nasdaq Global Select Market, sourced from
  Nasdaq Trader's symbol directory
  (`https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt`), filtered
  to `Market Category = Q` (Q = Global Select, G = Global Market, S = Capital
  Market — Q is the highest tier and the closest free proxy for "big, liquid,
  Robinhood-tradable names"). There is no public Robinhood API for US equities
  to check tradability directly, so this is a documented approximation, not a
  guarantee every pick is on Robinhood. Broadening to NYSE (`otherlisted.txt`)
  for closer parity is a Phase 4 option.
- **Market data:** `yfinance` (free, no key, no signup). It's an unofficial
  wrapper around Yahoo endpoints — it will occasionally rate-limit, change
  shape, or need a version bump. Cache aggressively (once per trading day is
  enough), fail loudly and skip the day's publish rather than publish partial
  or stale data, and keep the fetch layer (`scanner/data.py`) isolated so
  swapping in a paid API (Finnhub, Polygon, Alpha Vantage) later is a
  one-file change.
- **AI:** Anthropic/OpenAI, used only to turn already-computed signals into a
  short "why this pick" blurb — never to invent the numbers themselves. Two
  key-handling paths:
  - **Public demo:** your own API key stored as a GitHub Actions secret,
    used only by the scheduled workflow server-side. Never shipped to the
    browser.
  - **Personal/local runs:** BYO-key, entered locally, same pattern as
    Couchworthy's client-side key storage.
  - The scoring and ranking itself is fully deterministic and works with
    zero AI calls — the LLM layer is additive, exactly like Couchworthy's
    "deterministic parser first, LLM blurb layer on top."
- **Default pick counts:** 5 buy picks, up to 5 sell/caution picks (0–5,
  varies by day). Both numbers are a config constant, not hardcoded — trivial
  to change.
- **Sell framing:** Because there's no brokerage connection, the app has no
  idea what you actually own. "Sell" candidates are framed as **"Caution /
  Consider Trimming"** — bearish-signal names worth a second look — not "you
  own this, sell it." Copy in the UI should reflect that explicitly.
- **Storage:** Daily picks persist as committed JSON in the repo
  (`data/picks/YYYY-MM-DD.json` + `data/latest.json` pointer). This doubles
  as the history feature and the audit trail — every past pick, its entry
  price, its date, and its reasoning are just files in git, no database
  needed for Phase 1. Watchlist is client-side (localStorage), matching
  Couchworthy's storage pattern.
- **No trade execution, ever.** Out of scope permanently, not just for MVP.

## Key technical notes

- **Nasdaq symbol directory format:** pipe-delimited, columns include
  `Symbol | Security Name | Market Category | Test Issue | Financial Status |
  Round Lot Size | ETF | NextShares`. Filter out `Test Issue = Y` and
  `ETF = Y` (picks should be single names, not funds, at least for Phase 1).
- **yfinance reliability:** treat every fetch as fallible. Batch requests,
  add retry/backoff, and cap the run — if fewer than some threshold (e.g.
  90%) of the universe returns usable data, fail the run rather than publish
  a thin/misleading day. Log what was skipped.
- **GitHub Actions scheduling:** cron-triggered workflows auto-disable after
  60 days with zero repo activity. Since this workflow commits data daily,
  it's self-sustaining as long as it's running — but if it ever silently
  fails for 60+ days (e.g. yfinance breaks and every run aborts before
  committing), the schedule itself will get disabled with no alert in the
  Actions tab. Worth a lightweight health check (e.g. a badge or a "last
  successful run" timestamp on the demo site) so this failure mode is visible
  instead of silent.
- **Browser can't call yfinance directly** (it's a server-side Python
  library scraping HTML, not a CORS-friendly JSON API). Two different data
  paths exist by design:
  - Daily picks: Python + yfinance, runs in GitHub Actions, output is
    static JSON the frontend just fetches.
  - Watchlist "live" price refresh (Phase 2+): needs a browser-callable
    quote API (e.g. Finnhub or Twelve Data free tier, both support
    client-side calls with a user-supplied key) — a separate, optional,
    BYO-key feature, not the same pipeline as the daily scan.
- **Attribution / compliance footer:** required on every page — "Educational
  use only. Not financial advice. Data via Yahoo Finance (yfinance) and
  Nasdaq Trader. Not affiliated with or endorsed by Robinhood, Nasdaq, or
  Yahoo." Also disclose that picks are algorithmic and unverified, and that
  past performance shown in the history view is not a guarantee of anything.

## Pick generation pipeline (runs once per trading day, in Actions)

1. **Universe build** — pull/refresh `nasdaqlisted.txt`, filter to Market
   Category `Q`, drop test issues and ETFs, apply a basic liquidity floor
   (avg dollar volume) so the scan doesn't burn time/requests on illiquid
   names.
2. **Data fetch** — pull recent daily OHLCV (roughly 6–12 months) and a
   quote snapshot per ticker via yfinance, with retry/backoff and caching so
   a rerun same-day doesn't refetch everything.
3. **Signal computation (deterministic, no AI)** — compute a small, explicit
   set of signals per ticker: trend (moving-average relationship), momentum
   (RSI, rate of change), volume surge vs. average, 52-week range position,
   and (where available) recent earnings surprise. Combine into a single
   bullish/bearish composite score per ticker. Keep the formula simple and
   inspectable — this is the part most likely to get tuned over time (see
   Open Decisions).
4. **Selection** — top N by bullish score → buy list (default N=5). Names
   clearing a minimum bearish-signal threshold, up to N → sell/caution list
   (default N=5, can be fewer or zero). The threshold is what makes "up to
   X" real — a weak-signal day should return fewer sell candidates, not pad
   the list.
5. **LLM reasoning pass** — for each finalist only (not the whole universe,
   to keep AI calls/cost small), send the computed numbers to
   Anthropic/OpenAI and ask for a 1–3 sentence plain-English "why," grounded
   strictly in the provided signals.
6. **Persist** — write `data/picks/YYYY-MM-DD.json` (full snapshot: ticker,
   name, sector, action, entry price, entry date, signal values, composite
   score, blurb) and update `data/latest.json`. Commit both.
7. **(Phase 2+) Outcome tracking** — a lightweight follow-up step records
   current price against still-recent past picks so the history/track-record
   view can show "pick price → today," clearly labeled as unrealized/paper
   performance only.

## Frontend (React + Vite + TS + Tailwind, static)

- **Today view** — Buy cards (up to 5) and Caution cards (0–5), each with
  ticker, price at pick time, sector, one-line reasoning, expandable detail
  (the underlying signal values), and an "Add to Watchlist" action.
- **History view** — date picker or scrollable list over `data/picks/*.json`
  (an index file listing available dates avoids fetching a full directory
  listing from a static host), so a user who was away for a few days can
  scan what they missed.
- **Watchlist view** — user-managed ticker list (localStorage), independent
  of the daily picks; shows last-known price from the daily scan if the
  ticker happens to be in the Global Select universe, plus (Phase 2+) a
  live-quote refresh via a separate BYO-key browser-callable API.
- **Preferences (Phase 3)** — sector excludes, min market cap, risk
  tilt (momentum vs. value weighting), custom pick counts. Because the daily
  JSON can include the full scored shortlist (not just the top N), the
  public demo can re-rank/filter **client-side** against preferences without
  needing any backend — the static-site constraint stays intact even with
  personalization.

## Data model (illustrative shapes, not final types)

```
DailyRun {
  date: string            // YYYY-MM-DD
  generated_at: string    // ISO timestamp
  universe_size: number
  universe_coverage: number  // % of universe with usable data this run
  buys: Pick[]
  cautions: Pick[]
  shortlist: ScoredTicker[]  // full scored set, for client-side re-ranking
}

Pick {
  ticker: string
  name: string
  sector: string
  action: "buy" | "caution"
  price_at_pick: number
  signals: { trend, momentum, volume_surge, range_position, earnings_surprise? }
  composite_score: number
  reasoning: string        // LLM blurb, grounded in `signals`
}

WatchlistItem {
  ticker: string
  added_at: string
  note?: string
}

UserPreferences {           // client-side only, Phase 3
  excluded_sectors: string[]
  min_market_cap?: number
  risk_tilt: "momentum" | "balanced" | "value"
  buy_count: number
  sell_count_max: number
}
```

## Repo layout (proposed)

```
scanner/            # Python: the daily pick-generation engine
  universe.py        # Nasdaq symbol directory fetch + filter
  data.py             # yfinance fetch/cache layer (isolated, swappable)
  signals.py          # deterministic technical/momentum signal computation
  score.py            # composite scoring + selection (top N buy / up-to-N caution)
  llm.py               # reasoning blurb generation (Anthropic/OpenAI)
  main.py              # orchestrates the above, writes data/ output
  requirements.txt
data/
  latest.json
  picks/YYYY-MM-DD.json
  index.json           # list of available dates, for the History view
web/                 # Vite + React + TS + Tailwind, static frontend
  src/lib/types.ts
  src/lib/storage.ts    # watchlist + preferences (localStorage)
  src/components/       # TodayView, HistoryView, WatchlistView, PreferencesDrawer
.github/workflows/
  daily-scan.yml        # cron: run scanner, commit data/
  deploy-pages.yml       # build web/, publish to GitHub Pages
```

## Phased roadmap

**Phase 1 — MVP (public demo works end to end)**
Universe build, yfinance fetch, deterministic signal scoring, top-5 buy /
up-to-5 caution selection, LLM reasoning blurbs (via Actions secret key),
daily JSON commit, static frontend with Today + History views, GitHub Pages
deploy, compliance footer.

**Phase 2 — Watchlist + track record**
Client-side watchlist (add/remove, localStorage), browser-callable live
quote refresh for watchlisted tickers (separate BYO-key API), outcome
tracking on past picks (price then vs. now, clearly labeled as unrealized).

**Phase 3 — Personalization**
Preferences panel (sector excludes, risk tilt, custom counts), client-side
re-ranking of the full daily shortlist against preferences, BYO-key local
run mode for a fully custom on-demand scan (via `workflow_dispatch` inputs
or local CLI).

**Phase 4 — Expansion**
Broaden universe toward full Robinhood parity (NYSE via `otherlisted.txt`),
notifications/alerts (needs a small external service — Actions alone can't
push to a phone), backtesting the scoring methodology against history,
optional accounts/cross-device sync for preferences and watchlist.

## Compliance (permanent, not a phase)

- No trade execution, no brokerage connection, ever.
- Every view carries a visible "not financial advice, educational only"
  disclaimer.
- Reasoning blurbs must be grounded in the computed signals passed to the
  LLM — no free-floating claims about news, rumors, or non-computed factors.
- Track-record/performance views must be clearly labeled unrealized/paper
  and must not imply guaranteed or typical results.

## Open decisions to revisit

- Exact indicator set and scoring weights — start simple, expect to tune
  once there's a few weeks of history to look back on.
- Universe scope: stay Nasdaq Global Select only, or broaden sooner for
  closer Robinhood parity?
- Paid data API upgrade path if/when yfinance reliability becomes a real
  blocker (Finnhub, Polygon, Alpha Vantage are the likely candidates).
- Notification delivery mechanism for Phase 4 (email via a free transactional
  service is the simplest; push needs more infrastructure).
