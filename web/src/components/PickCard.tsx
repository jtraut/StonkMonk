import { useEffect, useState } from "react";
import type { Pick, Signals } from "../lib/types";
import { addToWatchlist, isWatchlisted, removeFromWatchlist, subscribeToWatchlist } from "../lib/storage";

const SIGNAL_LABELS: Record<keyof Signals, string> = {
  trend: "Trend",
  momentum: "Momentum",
  volume_surge: "Volume surge",
  range_position: "52-week range position",
  earnings_surprise: "Earnings surprise",
};

function fmt(value: number | null): string {
  return value === null ? "n/a" : value.toFixed(2);
}

export function PickCard({ pick }: { pick: Pick }) {
  const [expanded, setExpanded] = useState(false);
  const [watching, setWatching] = useState(() => isWatchlisted(pick.ticker));

  useEffect(
    () => subscribeToWatchlist(() => setWatching(isWatchlisted(pick.ticker))),
    [pick.ticker],
  );

  const isBuy = pick.action === "buy";
  const badgeClass = isBuy
    ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300"
    : "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300";
  const badgeLabel = isBuy ? "Buy" : "Caution / Consider Trimming";

  function toggleWatchlist() {
    if (watching) {
      removeFromWatchlist(pick.ticker);
      setWatching(false);
    } else {
      addToWatchlist(pick.ticker);
      setWatching(true);
    }
  }

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-4 flex flex-col gap-2">
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="font-semibold text-gray-900 dark:text-gray-100">{pick.ticker}</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">{pick.name}</div>
        </div>
        <span className={`text-xs font-medium px-2 py-1 rounded-full whitespace-nowrap ${badgeClass}`}>
          {badgeLabel}
        </span>
      </div>

      <div className="text-sm text-gray-600 dark:text-gray-300 flex flex-wrap gap-x-3 gap-y-1">
        {pick.sector && <span>{pick.sector}</span>}
        {pick.price_at_pick !== null && <span>${pick.price_at_pick.toFixed(2)}</span>}
        <span>Score: {pick.composite_score.toFixed(1)}/100</span>
      </div>

      <p className="text-sm text-gray-700 dark:text-gray-300">{pick.reasoning}</p>

      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="text-xs text-left text-blue-600 dark:text-blue-400 hover:underline"
      >
        {expanded ? "Hide signal detail" : "Show signal detail"}
      </button>

      {expanded && (
        <dl className="text-xs text-gray-600 dark:text-gray-400 grid grid-cols-2 gap-x-2 gap-y-1">
          {(Object.keys(SIGNAL_LABELS) as (keyof Signals)[]).map((key) => (
            <div key={key} className="contents">
              <dt className="text-gray-500 dark:text-gray-500">{SIGNAL_LABELS[key]}</dt>
              <dd>{fmt(pick.signals[key])}</dd>
            </div>
          ))}
        </dl>
      )}

      <button
        type="button"
        onClick={toggleWatchlist}
        className={`mt-1 text-xs font-medium px-3 py-1.5 rounded-md border ${
          watching
            ? "border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400"
            : "border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400"
        }`}
      >
        {watching ? "✓ Watching" : "+ Add to Watchlist"}
      </button>
    </div>
  );
}
