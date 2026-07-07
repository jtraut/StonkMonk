# StonkMonk

A daily stock picker for the Nasdaq Global Select Market. Every trading day, a
GitHub Actions cron job scans the universe, computes deterministic technical
signals, ranks them into a small **buy** list and an up-to-5 **caution /
consider trimming** list, and asks an LLM to write a plain-English "why" for
each pick — grounded strictly in the computed signals, never inventing news
or rumors.

**StonkMonk never places trades or connects to a brokerage account.** It is
informational and educational only.

## Live demo

**https://jtraut.github.io/StonkMonk/**

Public, no-login, static site. Refreshed automatically on trading days.

## Tech stack

**Pick engine (`scanner/`)** — Python
- [pandas](https://pandas.pydata.org/) / [numpy](https://numpy.org/) — signal math
- [yfinance](https://github.com/ranaroussi/yfinance) — OHLCV + quote data (unofficial Yahoo Finance scraper)
- [pyarrow](https://arrow.apache.org/docs/python/) — Parquet OHLCV cache
- [requests](https://requests.readthedocs.io/) — Nasdaq symbol directory fetch
- [anthropic](https://github.com/anthropics/anthropic-sdk-python) (Claude Haiku 4.5) — reasoning blurbs, with a deterministic template fallback if no API key/library is present; also powers the key-gated AI conviction pick pass (`ai_picks.py`), skipped entirely with no key

**Frontend (`web/`)** — static site, no backend
- [React 19](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/) (strict)
- [Vite 8](https://vite.dev/)
- [Tailwind CSS v4](https://tailwindcss.com/)
- Reads static JSON (`data/*.json`) directly — no API server, no database
- Optional live watchlist prices via [Finnhub](https://finnhub.io/)'s free-tier `/quote` endpoint, called directly from the browser with a user-supplied key (BYO-key, stored in localStorage only) — separate from the daily scan's yfinance pipeline

**CI/CD** — GitHub Actions
- `daily-scan.yml` — runs the scanner on a schedule (weekdays, cron) or on demand, commits the day's picks back to `data/`
- `deploy-pages.yml` — builds `web/` and publishes to GitHub Pages, triggered by pushes to `web/`/`data/` or by a successful scan
- GitHub Pages, `Source: GitHub Actions`

## Repo layout

```
scanner/            # Python pick-generation engine
  universe.py          # Nasdaq Global Select universe build
  data.py              # yfinance OHLCV + quote/news fetch, caching
  signals.py           # deterministic technical signal computation
  score.py             # composite scoring + buy/caution selection
  llm.py               # LLM reasoning blurbs (Anthropic), deterministic fallback
  ai_picks.py          # AI conviction picks (Phase 2, key-gated, news-grounded)
  outcomes.py          # outcome tracking, split by algorithmic/AI track
  main.py              # orchestrates the full pipeline, persists JSON
  config.py            # all tunable constants
  requirements.txt
data/
  latest.json          # most recent day's picks (DailyRun)
  index.json           # list of available dates, for History view
  picks/YYYY-MM-DD.json
  outcomes.json        # per-pick 5d/30d return ledger, by track
  track_performance.json  # aggregated algo vs. AI stats, for the Scoreboard view
web/                 # Vite + React + TS + Tailwind static frontend
  src/lib/             # types, localStorage watchlist, JSON fetch helpers, Finnhub live-quote client
  src/components/      # Header, TodayView, HistoryView, ScoreboardView, PickCard, WatchlistSidebar, ComplianceFooter
  public/data/         # synced copy of root data/, served by Vite as static files
.github/workflows/
  daily-scan.yml
  deploy-pages.yml
```

See `stonkmonk-spec.md` for the full spec, data model, and phased roadmap.

## Running locally

### Scanner (Python)

```bash
pip install -r scanner/requirements.txt

# Optional — enables real LLM reasoning blurbs. Without it, every pick gets a
# deterministic templated blurb instead (the pipeline never blocks on this).
export ANTHROPIC_API_KEY=sk-ant-...

# Run from the repo root (scanner is an implicit namespace package):
python -m scanner.main
```

This fetches the whole Nasdaq Global Select universe via yfinance (~1,400+
tickers), so a full run takes a couple of minutes. It writes/updates
`data/latest.json`, `data/index.json`, and `data/picks/<today>.json` — or
fails loudly with a non-zero exit and writes nothing if too much of the
universe comes back empty (see `config.MIN_UNIVERSE_COVERAGE`).

### Frontend (Vite + React)

```bash
cd web
npm install

# The frontend serves data/ as static files from web/public/data — sync the
# root data/ directory in before running dev/build:
rm -rf public/data && cp -r ../data public/data

npm run dev       # http://localhost:5173
npm run build     # production build to web/dist
npm run preview   # serve the production build locally
```

`vite.config.ts` sets `base: '/StonkMonk/'` to match the GitHub Pages project
URL — if you fork this to a different repo name, update that (and re-sync
`public/data`).

## Compliance

Educational use only. Not financial advice. Data via Yahoo Finance
(yfinance) and Nasdaq Trader. Not affiliated with or endorsed by Robinhood,
Nasdaq, or Yahoo. Buy/caution picks are generated algorithmically from
computed technical signals and are not reviewed by a human before
publishing. AI conviction picks (badged "AI Pick," when present) are an
experimental, model-judgment layer — closer to a judgment call than a
formula, not score-selected, and carry higher variance. Track-record/
Scoreboard figures are unrealized/paper performance only, not a guarantee of
future results or a claim that either track "wins."
