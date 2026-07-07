# Graph Report - .  (2026-07-06)

## Corpus Check
- Corpus is ~10,032 words - fits in a single context window. You may not need a graph.

## Summary
- 127 nodes · 172 edges · 12 communities (9 shown, 3 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Signal Computation (signals.py)|Signal Computation (signals.py)]]
- [[_COMMUNITY_Data Fetch & Caching (data.py)|Data Fetch & Caching (data.py)]]
- [[_COMMUNITY_Pipeline Steps & AIData Providers|Pipeline Steps & AI/Data Providers]]
- [[_COMMUNITY_Project Identity & Design Constraints|Project Identity & Design Constraints]]
- [[_COMMUNITY_Composite Scoring (score.py)|Composite Scoring (score.py)]]
- [[_COMMUNITY_Universe Build (universe.py)|Universe Build (universe.py)]]
- [[_COMMUNITY_Roadmap & Data API Alternatives|Roadmap & Data API Alternatives]]
- [[_COMMUNITY_Frontend Views & Data Shapes|Frontend Views & Data Shapes]]
- [[_COMMUNITY_Brand Logo Assets|Brand Logo Assets]]
- [[_COMMUNITY_StonkMonk Doc Cross-Reference|StonkMonk Doc Cross-Reference]]
- [[_COMMUNITY_Scanner Configuration (config.py)|Scanner Configuration (config.py)]]
- [[_COMMUNITY_Watchlist Feature|Watchlist Feature]]

## God Nodes (most connected - your core abstractions)
1. `compute_signals()` - 11 edges
2. `fetch_prices()` - 9 edges
3. `Signals` - 8 edges
4. `QuoteSnapshot` - 7 edges
5. `_clip()` - 6 edges
6. `_momentum_signal()` - 6 edges
7. `_trend_signal()` - 5 edges
8. `_volume_surge_signal()` - 5 edges
9. `_range_position_signal()` - 5 edges
10. `_earnings_signal()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `Signals` --uses--> `QuoteSnapshot`  [INFERRED]
  scanner/signals.py → scanner/data.py
- `CLAUDE.md — StonkMonk Project Context` --references--> `stonkmonk-spec.md — StonkMonk Full Spec`  [EXTRACTED]
  CLAUDE.md → stonkmonk-spec.md
- `scanner/requirements.txt — Python dependency manifest` --references--> `Anthropic (LLM provider)`  [EXTRACTED]
  scanner/requirements.txt → stonkmonk-spec.md
- `scanner/requirements.txt — Python dependency manifest` --references--> `yfinance (market data source)`  [EXTRACTED]
  scanner/requirements.txt → stonkmonk-spec.md
- `StonkMonk Icon (logo.svg)` --semantically_similar_to--> `StonkMonk App Logo (128px)`  [INFERRED] [semantically similar]
  assets/logo.svg → assets/logo-128.png

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Steps forming the daily pick generation pipeline** — universe_build_step, data_fetch_step, signal_computation_step, selection_step, llm_reasoning_pass_step, persist_step, outcome_tracking_step [EXTRACTED 1.00]
- **Frontend views composing the static site** — today_view, history_view, watchlist_view, preferences_panel [EXTRACTED 1.00]
- **Planned scanner/ modules implementing the pick pipeline** — stonkmonk_spec_universe_py, stonkmonk_spec_data_py, stonkmonk_spec_signals_py, stonkmonk_spec_score_py, stonkmonk_spec_llm_py, stonkmonk_spec_main_py [EXTRACTED 1.00]

## Communities (12 total, 3 thin omitted)

### Community 0 - "Signal Computation (signals.py)"
Cohesion: 0.16
Nodes (23): QuoteSnapshot, Lightweight per-ticker fundamentals we opportunistically capture.      All field, avg_dollar_volume(), _clip(), compute_signals(), _earnings_signal(), latest_price(), _momentum_signal() (+15 more)

### Community 1 - "Data Fetch & Caching (data.py)"
Cohesion: 0.13
Nodes (20): _cache_is_fresh(), _cache_path(), _download_batch(), fetch_prices(), fetch_quotes(), FetchResult, DataFrame, Market-data fetch layer — isolated so it can be swapped wholesale.  Everything Y (+12 more)

### Community 2 - "Pipeline Steps & AI/Data Providers"
Cohesion: 0.16
Nodes (17): Anthropic (LLM provider), Data fetch step, Isolate yfinance fetch layer for future swappability, Fail the run rather than publish a thin/partial day, LLM reasoning pass step, OpenAI (LLM provider), scanner/requirements.txt — Python dependency manifest, Selection step (top-N buy / up-to-N caution) (+9 more)

### Community 3 - "Project Identity & Design Constraints"
Cohesion: 0.15
Nodes (13): Compliance / disclaimer footer, Couchworthy (sibling project), Deterministic-logic-first, LLM-blurb-additive pattern, React + Vite + TypeScript + Tailwind static frontend, GitHub Actions 60-day auto-disable risk & self-sustaining mitigation, GitHub Actions daily cron workflow, Nasdaq Trader symbol directory (nasdaqlisted.txt), No trade execution / no brokerage connection (permanent constraint) (+5 more)

### Community 4 - "Composite Scoring (score.py)"
Cohesion: 0.24
Nodes (10): composite(), Composite scoring and selection.  Combines the normalized signals into a single, Weighted blend of signals -> 0-100 (50 neutral).      Signals absent for a ticke, Compute composites for a list of (ticker, name, sector, price, signals)., Return (buys, cautions) per the config thresholds and counts., score_all(), ScoredTicker, select() (+2 more)

### Community 5 - "Universe Build (universe.py)"
Cohesion: 0.29
Nodes (9): _clean_symbol(), fetch_universe(), parse_nasdaq_listed(), Universe build: fetch and filter the Nasdaq Global Select Market list.  Pulls Na, Normalize a Nasdaq symbol to the form yfinance expects.      Nasdaq uses ``.`` f, Return the filtered Global Select universe.      Raises on network/parse failure, Parse the pipe-delimited nasdaqlisted.txt content.      Columns: Symbol | Securi, UniverseTicker (+1 more)

### Community 6 - "Roadmap & Data API Alternatives"
Cohesion: 0.22
Nodes (9): Alpha Vantage (paid data API candidate), Finnhub (browser-callable quote API candidate), Open decisions to revisit, Phase 1 — MVP, Phase 2 — Watchlist + track record, Phase 3 — Personalization, Phased roadmap (Phase 1–4), Polygon (paid data API candidate) (+1 more)

### Community 7 - "Frontend Views & Data Shapes"
Cohesion: 0.25
Nodes (9): Full scored shortlist enables client-side re-ranking without a backend, DailyRun data shape, History view, Outcome tracking step (Phase 2+), Persist step (write data/picks JSON), Pick data shape, Preferences panel (Phase 3), Today view (buy/caution cards) (+1 more)

### Community 8 - "Brand Logo Assets"
Cohesion: 0.40
Nodes (5): StonkMonk App Logo (128px), StonkMonk Logo Icon (32px), StonkMonk Logo (512px App Icon), StonkMonk Icon (logo.svg), StonkMonk Brand Identity / Monk Mascot Concept

## Knowledge Gaps
- **19 isolated node(s):** `CLAUDE.md — StonkMonk Project Context`, `stonkmonk-spec.md — StonkMonk Full Spec`, `Outcome tracking step (Phase 2+)`, `React + Vite + TypeScript + Tailwind static frontend`, `Today view (buy/caution cards)` (+14 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Nasdaq Trader symbol directory (nasdaqlisted.txt)` connect `Project Identity & Design Constraints` to `Pipeline Steps & AI/Data Providers`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `Pick data shape` connect `Frontend Views & Data Shapes` to `Pipeline Steps & AI/Data Providers`, `Project Identity & Design Constraints`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Signals` (e.g. with `ScoredTicker` and `QuoteSnapshot`) actually correct?**
  _`Signals` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Central configuration for the StonkMonk pick engine.  Everything tunable lives h`, `Market-data fetch layer — isolated so it can be swapped wholesale.  Everything Y`, `Lightweight per-ticker fundamentals we opportunistically capture.      All field` to the rest of the system?**
  _50 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Data Fetch & Caching (data.py)` be split into smaller, more focused modules?**
  _Cohesion score 0.12987012987012986 - nodes in this community are weakly interconnected._