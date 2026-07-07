# Graph Report - StonkMonk  (2026-07-07)

## Corpus Check
- 45 files · ~26,901 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 352 nodes · 456 edges · 69 communities (19 shown, 50 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `67ebbaeb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

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
- [[_COMMUNITY_App.tsx|App.tsx]]
- [[_COMMUNITY_devDependencies|devDependencies]]
- [[_COMMUNITY_compilerOptions|compilerOptions]]
- [[_COMMUNITY_compilerOptions|compilerOptions]]
- [[_COMMUNITY_StonkMonk — Full Spec|StonkMonk — Full Spec]]
- [[_COMMUNITY_StonkMonk — Project Context|StonkMonk — Project Context]]
- [[_COMMUNITY_StonkMonk|StonkMonk]]
- [[_COMMUNITY_.oxlintrc.json|.oxlintrc.json]]
- [[_COMMUNITY_React + TypeScript + Vite|React + TypeScript + Vite]]
- [[_COMMUNITY_tsconfig.json|tsconfig.json]]
- [[_COMMUNITY_Couchworthy (sibling project)|Couchworthy (sibling project)]]
- [[_COMMUNITY_DailyRun data shape|DailyRun data shape]]
- [[_COMMUNITY_Data fetch step|Data fetch step]]
- [[_COMMUNITY_Isolate yfinance fetch layer for future swappability|Isolate yfinance fetch layer for future swappability]]
- [[_COMMUNITY_Deterministic-logic-first, LLM-blurb-additive pattern|Deterministic-logic-first, LLM-blurb-additive pattern]]
- [[_COMMUNITY_Fail the run rather than publish a thinpartial day|Fail the run rather than publish a thin/partial day]]
- [[_COMMUNITY_Finnhub (browser-callable quote API candidate)|Finnhub (browser-callable quote API candidate)]]
- [[_COMMUNITY_React + Vite + TypeScript + Tailwind static frontend|React + Vite + TypeScript + Tailwind static frontend]]
- [[_COMMUNITY_GitHub Actions 60-day auto-disable risk & self-sustaining mitigation|GitHub Actions 60-day auto-disable risk & self-sustaining mitigation]]
- [[_COMMUNITY_GitHub Actions daily cron workflow|GitHub Actions daily cron workflow]]
- [[_COMMUNITY_History view|History view]]
- [[_COMMUNITY_LLM reasoning pass step|LLM reasoning pass step]]
- [[_COMMUNITY_Nasdaq Trader symbol directory (nasdaqlisted.txt)|Nasdaq Trader symbol directory (nasdaqlisted.txt)]]
- [[_COMMUNITY_No trade execution  no brokerage connection (permanent constraint)|No trade execution / no brokerage connection (permanent constraint)]]
- [[_COMMUNITY_OpenAI (LLM provider)|OpenAI (LLM provider)]]
- [[_COMMUNITY_Outcome tracking step (Phase 2+)|Outcome tracking step (Phase 2+)]]
- [[_COMMUNITY_Persist step (write datapicks JSON)|Persist step (write data/picks JSON)]]
- [[_COMMUNITY_Phase 1 — MVP|Phase 1 — MVP]]
- [[_COMMUNITY_Phase 2 — Watchlist + track record|Phase 2 — Watchlist + track record]]
- [[_COMMUNITY_Phase 3 — Personalization|Phase 3 — Personalization]]
- [[_COMMUNITY_Phase 4 — Expansion|Phase 4 — Expansion]]
- [[_COMMUNITY_Phased roadmap (Phase 1–4)|Phased roadmap (Phase 1–4)]]
- [[_COMMUNITY_Pick generation pipeline|Pick generation pipeline]]
- [[_COMMUNITY_Pick data shape|Pick data shape]]
- [[_COMMUNITY_Polygon (paid data API candidate)|Polygon (paid data API candidate)]]
- [[_COMMUNITY_Preferences panel (Phase 3)|Preferences panel (Phase 3)]]
- [[_COMMUNITY_Nasdaq Global Select as Robinhood-tradable proxy|Nasdaq Global Select as Robinhood-tradable proxy]]
- [[_COMMUNITY_Selection step (top-N buy  up-to-N caution)|Selection step (top-N buy / up-to-N caution)]]
- [[_COMMUNITY_CautionConsider Trimming sell-framing rationale|Caution/Consider Trimming sell-framing rationale]]
- [[_COMMUNITY_Signal computation step (deterministic, no AI)|Signal computation step (deterministic, no AI)]]
- [[_COMMUNITY_StonkMonk (the project)|StonkMonk (the project)]]
- [[_COMMUNITY_scannerdata.py (planned module)|scanner/data.py (planned module)]]
- [[_COMMUNITY_scannerllm.py (planned module)|scanner/llm.py (planned module)]]
- [[_COMMUNITY_scannermain.py (planned module)|scanner/main.py (planned module)]]
- [[_COMMUNITY_scannerscore.py (planned module)|scanner/score.py (planned module)]]
- [[_COMMUNITY_scannersignals.py (planned module)|scanner/signals.py (planned module)]]
- [[_COMMUNITY_stonkmonk-spec.md — StonkMonk Full Spec|stonkmonk-spec.md — StonkMonk Full Spec]]
- [[_COMMUNITY_scanneruniverse.py (planned module)|scanner/universe.py (planned module)]]
- [[_COMMUNITY_Today view (buycaution cards)|Today view (buy/caution cards)]]
- [[_COMMUNITY_Twelve Data (browser-callable quote API candidate)|Twelve Data (browser-callable quote API candidate)]]
- [[_COMMUNITY_Universe build step|Universe build step]]
- [[_COMMUNITY_UserPreferences data shape|UserPreferences data shape]]
- [[_COMMUNITY_WatchlistItem data shape|WatchlistItem data shape]]
- [[_COMMUNITY_App.tsx|App.tsx]]
- [[_COMMUNITY_outcomes.py|outcomes.py]]
- [[_COMMUNITY_main.py|main.py]]

## God Nodes (most connected - your core abstractions)
1. `ScoredTicker` - 20 edges
2. `compilerOptions` - 18 edges
3. `compilerOptions` - 15 edges
4. `compute_signals()` - 11 edges
5. `StonkMonk — Full Spec` - 11 edges
6. `fetch_prices()` - 9 edges
7. `DailyRun` - 9 edges
8. `StonkMonk — Project Context` - 8 edges
9. `QuoteSnapshot` - 7 edges
10. `Signals` - 7 edges

## Surprising Connections (you probably didn't know these)
- `_aggregate()` --references--> `Track`  [EXTRACTED]
  scanner/outcomes.py → web/src/lib/types.ts
- `ScoredTicker` --uses--> `Signals`  [INFERRED]
  scanner/score.py → scanner/signals.py
- `WatchlistSidebarProps` --references--> `DailyRun`  [EXTRACTED]
  web/src/components/WatchlistSidebar.tsx → web/src/lib/types.ts
- `scanner/requirements.txt — Python dependency manifest` --references--> `Anthropic (LLM provider)`  [EXTRACTED]
  scanner/requirements.txt → stonkmonk-spec.md
- `scanner/requirements.txt — Python dependency manifest` --references--> `yfinance (market data source)`  [EXTRACTED]
  scanner/requirements.txt → stonkmonk-spec.md

## Import Cycles
- None detected.

## Communities (69 total, 50 thin omitted)

### Community 0 - "Signal Computation (signals.py)"
Cohesion: 0.14
Nodes (25): QuoteSnapshot, Lightweight per-ticker fundamentals we opportunistically capture.      All field, avg_dollar_volume(), _clip(), compute_signals(), _earnings_signal(), latest_price(), _momentum_signal() (+17 more)

### Community 1 - "Data Fetch & Caching (data.py)"
Cohesion: 0.10
Nodes (24): _cache_is_fresh(), _cache_path(), _download_batch(), fetch_current_prices(), fetch_news(), fetch_prices(), fetch_quotes(), FetchResult (+16 more)

### Community 2 - "Pipeline Steps & AI/Data Providers"
Cohesion: 0.67
Nodes (3): Anthropic (LLM provider), scanner/requirements.txt — Python dependency manifest, yfinance (market data source)

### Community 4 - "Composite Scoring (score.py)"
Cohesion: 0.13
Nodes (27): _build_prompt(), _call_model(), _candidate_line(), _feedback_block(), generate_ai_picks(), AI conviction picks (Phase 2, key-gated) - a separate idea source from the compo, Return 0-``config.AI_PICK_COUNT_MAX`` AI conviction pick dicts, shaped like ``Pi, _shape_pick() (+19 more)

### Community 5 - "Universe Build (universe.py)"
Cohesion: 0.29
Nodes (9): _clean_symbol(), fetch_universe(), parse_nasdaq_listed(), Universe build: fetch and filter the Nasdaq Global Select Market list.  Pulls Na, Normalize a Nasdaq symbol to the form yfinance expects.      Nasdaq uses ``.`` f, Return the filtered Global Select universe.      Raises on network/parse failure, Parse the pipe-delimited nasdaqlisted.txt content.      Columns: Symbol | Securi, UniverseTicker (+1 more)

### Community 8 - "Brand Logo Assets"
Cohesion: 0.40
Nodes (5): StonkMonk App Logo (128px), StonkMonk Logo Icon (32px), StonkMonk Logo (512px App Icon), StonkMonk Icon (logo.svg), StonkMonk Brand Identity / Monk Mascot Concept

### Community 12 - "App.tsx"
Cohesion: 0.10
Nodes (32): formatGeneratedAt(), Header(), HeaderProps, Tab, TABS, fmt(), PickCard(), SIGNAL_LABELS (+24 more)

### Community 13 - "devDependencies"
Cohesion: 0.09
Nodes (22): dependencies, react, react-dom, tailwindcss, @tailwindcss/vite, devDependencies, oxlint, @types/node (+14 more)

### Community 14 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+11 more)

### Community 15 - "compilerOptions"
Cohesion: 0.12
Nodes (16): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+8 more)

### Community 16 - "StonkMonk — Full Spec"
Cohesion: 0.17
Nodes (11): Compliance (permanent, not a phase), Data model (illustrative shapes, not final types), Decisions already made, Frontend (React + Vite + TS + Tailwind, static), Key technical notes, Open decisions to revisit, Phased roadmap, Pick generation pipeline (runs once per trading day, in Actions) (+3 more)

### Community 17 - "StonkMonk — Project Context"
Cohesion: 0.18
Nodes (10): Current status, Decisions already made, graphify, Key technical notes, Layout (proposed, not yet built), Open decisions to revisit, Pick generation pipeline (per trading day), Status: Not started — Phase 1 is the next milestone (+2 more)

### Community 18 - "StonkMonk"
Cohesion: 0.22
Nodes (8): Compliance, Frontend (Vite + React), Live demo, Repo layout, Running locally, Scanner (Python), StonkMonk, Tech stack

### Community 19 - ".oxlintrc.json"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 20 - "React + TypeScript + Vite"
Cohesion: 0.50
Nodes (3): Expanding the Oxlint configuration, React Compiler, React + TypeScript + Vite

### Community 66 - "App.tsx"
Cohesion: 0.14
Nodes (22): App(), Tab, ComplianceFooter(), HistoryView(), PicksList(), fmtDate(), fmtPct(), ScoreboardView() (+14 more)

### Community 67 - "outcomes.py"
Cohesion: 0.19
Nodes (15): _aggregate(), _collect_entries(), _iter_picks(), _load_ledger(), load_recent_ai_outcomes(), Outcome tracking, split by algorithmic vs. AI track.  Runs best-effort at the en, Last ``limit`` resolved AI-track entries, most recent first.      Used as the ro, Aggregate the ledger into the Scoreboard's per-track summary. (+7 more)

### Community 68 - "main.py"
Cohesion: 0.33
Nodes (9): main(), _persist(), _pick(), Orchestrates the daily pick-generation pipeline end-to-end.  Universe build -> d, Best-effort outcome tracking - never blocks or fails today's publish., run(), _shortlist_entry(), _track_outcomes() (+1 more)

## Knowledge Gaps
- **138 isolated node(s):** `$schema`, `plugins`, `react/rules-of-hooks`, `react/only-export-components`, `name` (+133 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **50 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ScoredTicker` connect `Composite Scoring (score.py)` to `Signal Computation (signals.py)`, `main.py`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `Track` connect `App.tsx` to `outcomes.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Why does `_aggregate()` connect `outcomes.py` to `App.tsx`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **What connects `AI conviction picks (Phase 2, key-gated) - a separate idea source from the compo`, `Return 0-``config.AI_PICK_COUNT_MAX`` AI conviction pick dicts, shaped like ``Pi`, `Central configuration for the StonkMonk pick engine.  Everything tunable lives h` to the rest of the system?**
  _191 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Signal Computation (signals.py)` be split into smaller, more focused modules?**
  _Cohesion score 0.13675213675213677 - nodes in this community are weakly interconnected._
- **Should `Data Fetch & Caching (data.py)` be split into smaller, more focused modules?**
  _Cohesion score 0.10461538461538461 - nodes in this community are weakly interconnected._
- **Should `Composite Scoring (score.py)` be split into smaller, more focused modules?**
  _Cohesion score 0.12643678160919541 - nodes in this community are weakly interconnected._