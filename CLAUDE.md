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
- **AI:** Anthropic/OpenAI, used for the "why" reasoning blurb (never the
  underlying scoring) and, as of Phase 2, for 1–3 additional **AI conviction
  picks** per day — see below. Public demo uses your API key as a **GitHub
  Actions secret** (server-side only, never shipped to the browser).
  Personal/local runs use BYO-key like Couchworthy.
- **AI conviction picks (Phase 2):** key-gated (skipped entirely with no
  key, day is algo-only). The model picks 1–3 buys from the full shortlist
  (not just the algorithmic top-5), grounded in the same computed signals
  plus fresh news headlines, and tagged `ai_pick: true` — algorithmic picks
  carry no tag. Each day's prompt also includes a rolling summary of the AI
  track's own past picks and what happened to them — in-context learning,
  not fine-tuning/RL (too little data, too much market noise for that to be
  reliable at this scale). Outcomes are tracked separately by track
  (algorithmic vs. AI) and shown on a Scoreboard view — a live, honest
  comparison, not a claim that either approach wins.
- **Pick counts:** 5 buy, up to 5 caution/sell (0–5, config constant), plus
  up to 3 AI conviction picks when a key is available.
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
  AI conviction picks need a stronger, distinct disclaimer/badge than
  algorithmic picks — they're a model judgment call, not a formula.
- Published LLM-stock-picking research (StockBench, LLM-equity surveys,
  2025-era sentiment/RL work) shows models prompted from static knowledge
  alone struggle to beat buy-and-hold; grounding in retrieved data (news,
  filings) + blending with quant signals does better. AI picks are designed
  around that: grounded in computed signals + fresh news, tracked separately,
  not a replacement for the scoring engine.
- News grounding for AI picks: `yfinance .news` first (free, already in the
  stack), Finnhub free tier as fallback if it's too thin. Cap to shortlist
  candidates only to bound token/API cost on the daily Actions run.

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
6. (Phase 2, key-gated) AI conviction pick pass → full shortlist + news
   headlines + rolling summary of the AI track's own past results →
   1–3 picks, tagged `ai_pick: true`. Skipped entirely with no key.
7. Persist → `data/picks/YYYY-MM-DD.json` (incl. `ai_pick` flag + news
   context), update `data/latest.json`, commit.
8. (Phase 2) Outcome tracking, split by track → record current price against
   recent past picks, keyed by algorithmic vs. AI, feeding both the
   history/track-record view and the Scoreboard.

## Current status

- [x] Concept, stack, and phased roadmap finalized (`stonkmonk-spec.md`).
- [ ] Repo not yet created.
- [ ] Phase 1 scaffold not started.

### Layout (proposed, not yet built)

```
scanner/            # Python pick-generation engine
  universe.py, data.py, signals.py, score.py, llm.py
  ai_picks.py, outcomes.py   # Phase 2
  main.py
data/
  latest.json, picks/YYYY-MM-DD.json, index.json
  track_performance.json    # Phase 2: algo vs ai aggregates
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

**Phase 2** (next up after Phase 1) adds: watchlist + live quote refresh, AI
conviction picks (1–3/day, key-gated, news-grounded, in-context feedback
loop, tagged `ai_pick`), and outcome tracking split by algorithmic vs. AI
track with a Scoreboard view comparing the two over time.

Phases 3–4 (personalization, expansion/notifications/backtesting) are
detailed in the spec.

## Open decisions to revisit

- Exact indicator set / scoring weights (start simple, tune later).
- Stay Nasdaq Global Select only, or broaden universe sooner for closer
  Robinhood parity?
- Paid data API upgrade path if yfinance reliability becomes a blocker
  (Finnhub, Polygon, Alpha Vantage are candidates).
- Notification delivery mechanism for Phase 4.
- News grounding source for AI picks: start with `yfinance .news`, revisit
  if too thin (Finnhub free tier as fallback).
- Exact shape of the rolling feedback summary in the AI pick prompt (how
  many past picks, what stats) — tune once there's real AI-track history.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
