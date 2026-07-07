// Mirrors the JSON shape written by scanner/main.py (_pick, _shortlist_entry, run()).
// Keep in sync with scanner/signals.py's Signals fields and scanner/score.py's ScoredTicker.

export interface Signals {
  trend: number | null;
  momentum: number | null;
  volume_surge: number | null;
  range_position: number | null;
  earnings_surprise: number | null;
}

export type PickAction = "buy" | "caution";

export interface Pick {
  ticker: string;
  name: string;
  sector: string | null;
  action: PickAction;
  price_at_pick: number | null;
  signals: Signals;
  // Omitted (null) for AI conviction picks, since they weren't score-selected.
  composite_score: number | null;
  reasoning: string;
  ai_pick?: boolean;
  news_context?: string[];
}

export interface ShortlistEntry {
  ticker: string;
  name: string;
  sector: string | null;
  price_at_pick: number | null;
  signals: Signals;
  composite_score: number;
}

export interface DailyRun {
  date: string;
  generated_at: string;
  universe_size: number;
  universe_coverage: number;
  buys: Pick[];
  cautions: Pick[];
  // Absent on days generated before Phase 2, or when no AI key was configured.
  ai_picks?: Pick[];
  shortlist: ShortlistEntry[];
}

export interface WatchlistItem {
  ticker: string;
  added_at: string;
}

export type Track = "algorithmic" | "ai";

export interface TrackPerformance {
  track: Track;
  picks_count: number;
  avg_return_5d: number | null;
  avg_return_30d: number | null;
  win_rate: number | null;
  since: string | null;
}
