# StonkMonk — Project Context

> Handoff notes for Claude Code. Read `stonkmonk-spec.md` in this repo for
> the full spec, architecture, data model, and phased roadmap. This file is
> the quick orientation + current status.

## What it is

A daily stock picker for the Nasdaq Global Select Market. Produces a small,
ranked **buy** list plus an **up-to** sized **caution/sell** list each trading
day, each pick with a plain-English reasoning blurb grounded in computed
signals. Ships as a public, no-login **live demo** (static site, refreshed
daily by GitHub Actions) and as a personal, run-it-yourself version with your
own preferences and AI key. Also has a user-managed **watchlist** and a
**picks history** so nothing gets missed after time away.

Sibling project to Couchworthy — same BYO-key AI philosophy, same
deterministic-logic-first-then-LLM-blurb pattern, same React/Vite/TS/Tailwind
frontend approach.

**Permanent constraint: this app never places trades or connects to a
brokerage account.** Informational only.

## Decisions already made

- **Name:** StonkMonk. Repo: `github.com/jtraut/StonkMonk` (adjust if taken).
- **Frontend:** React (Vite) + Tailwind, TypeScript (strict). Static build,
  deployed to GitHub Pages. No always-on server for the public demo.
- **Pick engine:** Python (pandas, yfinance, pandas-ta or equivalent),
  orchestrated by a GitHub Actions cron workflow that writes committed JSON.
- **Data source:** `yfinance` (free, unofficial, no key). Known to be
  unreliable — see Key technical notes. Fetch layer is isolated
  (`scanner/data.py`) so swapping to a paid API later is contained.
- **Universe:** Nasdaq Global Select Market via Nasdaq Trader's symbol
  directory, `Market Category = Q`. Used as a free proxy for "Robinhood-
  tradable" since Robinhood has no public equities API to check against
  directly.
- **AI:** Anthropic/OpenAI, used only for the "why" reasoning blurb, never
  for the underlying scoring. Public demo uses your API key as a **GitHub
  Actions secret** (server-side only, never shipped to the browser).
  Personal/local runs use BYO-key like Couchworthy.
- **Pick counts:** 5 buy, up to 5 caution/sell (0–5, config constant).
- **Sell framing:** "Caution / Consider Trimming," not "sell" — the app
  doesn't know what you actually own.
- **Storage:** Daily picks as committed JSON (`data/picks/YYYY-MM-DD.json` +
  `data/latest.json`) — this is both the backend and the history feature.
  Watchlist and preferences are client-side (localStorage).
- **No trade execution, ever.**

## Key technical notes

- Nasdaq symbol directory
  (`https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt`) is
  pipe-delimited: `Symbol | Security Name | Market Category | Test Issue |
  Financial Status | Round Lot Size | ETF | NextShares`. Filter `Market
  Category = Q`, drop `Test Issue = Y` and `ETF = Y`.
- `yfinance` is an unofficial scraper, not an official API (Yahoo retired its
  public API in 2017). It rate-limits and changes shape without notice.
  Cache once-per-day, retry with backoff, and **fail the run rather than
  publish a thin/partial day** if too much of the universe comes back empty.
- GitHub Actions scheduled workflows **auto-disable after 60 days of zero
  repo activity**. This workflow commits daily so it should self-sustain,
  but a silent failure streak (fetch breaks, every run aborts pre-commit)
  could still trigger it with no alert — worth a visible "last successful
  run" indicator on the demo site.
- The browser can't call yfinance directly (server-side Python, not a CORS
  API). Daily picks are Python-generated static JSON; any "live" watchlist
  price refresh (Phase 2+) needs a separate browser-callable quote API
  (Finnhub/Twelve Data, BYO-key), not the yfinance pipeline.
- Robinhood has no public API for US equity trading/tradability lookups
  (only a crypto trading API as of 2026) — Global Select Market is a
  documented approximation, not a verified match.
- Compliance footer required everywhere: not financial advice, educational
  only, data source attribution, no affiliation with Robinhood/Nasdaq/Yahoo.

## Pick generation pipeline (per trading day)

1. Universe build → Nasdaq symbol directory, filter to Global Select,
   drop test issues/ETFs, apply liquidity floor.
2. Data fetch → yfinance OHLCV + quote snapshot, retry/backoff, cache.
3. Signal computation (deterministic, no AI) → trend, momentum, volume
   surge, 52-week range position, earnings surprise where available →
   composite bullish/bearish score.
4. Selection → top 5 bullish → buy list. Bearish names clearing a minimum
   threshold, up to 5 → caution list (can be fewer or zero).
5. LLM reasoning pass → finalists only, blurb grounded strictly in computed
   signals.
6. Persist → `data/picks/YYYY-MM-DD.json`, update `data/latest.json`, commit.
7. (Phase 2+) Outcome tracking → record current price against recent past
   picks for the history/track-record view.

## Current status

- [x] Concept, stack, and phased roadmap finalized (`stonkmonk-spec.md`).
- [ ] Repo not yet created.
- [ ] Phase 1 scaffold not started.

### Layout (proposed, not yet built)

```
scanner/            # Python pick-generation engine
  universe.py, data.py, signals.py, score.py, llm.py, main.py
data/
  latest.json, picks/YYYY-MM-DD.json, index.json
web/                 # Vite + React + TS + Tailwind, static frontend
  src/lib/types.ts, src/lib/storage.ts, src/components/
.github/workflows/
  daily-scan.yml, deploy-pages.yml
```

### Status: Not started — Phase 1 is the next milestone

**Phase 1** (universe build, yfinance fetch, deterministic scoring, top-5
buy / up-to-5 caution selection, LLM blurbs via Actions secret, daily JSON
commit, static frontend with Today + History views, GitHub Pages deploy,
compliance footer) is the first build target.

Phases 2–4 (watchlist + track record, personalization, expansion/
notifications/backtesting) are detailed in the spec.

## Open decisions to revisit

- Exact indicator set / scoring weights (start simple, tune later).
- Stay Nasdaq Global Select only, or broaden universe sooner for closer
  Robinhood parity?
- Paid data API upgrade path if yfinance reliability becomes a blocker
  (Finnhub, Polygon, Alpha Vantage are candidates).
- Notification delivery mechanism for Phase 4.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
