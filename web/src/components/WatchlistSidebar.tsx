import { useEffect, useState } from "react";
import type { DailyRun, PickAction } from "../lib/types";
import { getWatchlist, removeFromWatchlist, subscribeToWatchlist } from "../lib/storage";

interface WatchlistSidebarProps {
  open: boolean;
  onClose: () => void;
  latest: DailyRun | null;
}

interface ResolvedEntry {
  ticker: string;
  addedAt: string;
  name: string | null;
  price: number | null;
  compositeScore: number | null;
  action: PickAction | null;
}

function resolveTicker(ticker: string, latest: DailyRun | null): Omit<ResolvedEntry, "ticker" | "addedAt"> {
  const fromBuy = latest?.buys.find((p) => p.ticker === ticker);
  if (fromBuy) {
    return { name: fromBuy.name, price: fromBuy.price_at_pick, compositeScore: fromBuy.composite_score, action: "buy" };
  }
  const fromCaution = latest?.cautions.find((p) => p.ticker === ticker);
  if (fromCaution) {
    return {
      name: fromCaution.name,
      price: fromCaution.price_at_pick,
      compositeScore: fromCaution.composite_score,
      action: "caution",
    };
  }
  const fromShortlist = latest?.shortlist.find((s) => s.ticker === ticker);
  if (fromShortlist) {
    return {
      name: fromShortlist.name,
      price: fromShortlist.price_at_pick,
      compositeScore: fromShortlist.composite_score,
      action: null,
    };
  }
  return { name: null, price: null, compositeScore: null, action: null };
}

export function WatchlistSidebar({ open, onClose, latest }: WatchlistSidebarProps) {
  const [items, setItems] = useState(() => getWatchlist());

  useEffect(() => subscribeToWatchlist(() => setItems(getWatchlist())), []);

  const entries: ResolvedEntry[] = items
    .map((item) => ({ ticker: item.ticker, addedAt: item.added_at, ...resolveTicker(item.ticker, latest) }))
    .sort((a, b) => a.ticker.localeCompare(b.ticker));

  return (
    <>
      {open && <div className="fixed inset-0 bg-black/30 z-40" onClick={onClose} aria-hidden="true" />}
      <aside
        className={`fixed top-0 right-0 z-50 h-full w-80 max-w-full bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700 shadow-xl flex flex-col transform transition-transform duration-200 ease-in-out ${
          open ? "translate-x-0" : "translate-x-full"
        }`}
        aria-hidden={!open}
      >
        <div className="flex items-center justify-between px-4 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="font-semibold text-gray-900 dark:text-gray-100">Watchlist</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close watchlist"
            className="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
          >
            ✕
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {entries.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No stocks watched yet. Add some from today's picks.
            </p>
          ) : (
            entries.map((entry) => (
              <div
                key={entry.ticker}
                className="rounded-lg border border-gray-200 dark:border-gray-700 p-3 flex flex-col gap-1"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="font-semibold text-gray-900 dark:text-gray-100">{entry.ticker}</div>
                    {entry.name && <div className="text-xs text-gray-500 dark:text-gray-400">{entry.name}</div>}
                  </div>
                  <button
                    type="button"
                    onClick={() => removeFromWatchlist(entry.ticker)}
                    aria-label={`Remove ${entry.ticker} from watchlist`}
                    className="text-xs text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                  >
                    Remove
                  </button>
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-300 flex flex-wrap gap-x-2 gap-y-1">
                  {entry.price !== null && <span>${entry.price.toFixed(2)}</span>}
                  {entry.compositeScore !== null && <span>Score: {entry.compositeScore.toFixed(1)}/100</span>}
                  {entry.action && (
                    <span
                      className={
                        entry.action === "buy"
                          ? "text-emerald-700 dark:text-emerald-400"
                          : "text-amber-700 dark:text-amber-400"
                      }
                    >
                      {entry.action === "buy" ? "Buy" : "Caution"}
                    </span>
                  )}
                </div>
                <div className="text-[11px] text-gray-400 dark:text-gray-500">
                  Added {new Date(entry.addedAt).toLocaleDateString()}
                </div>
              </div>
            ))
          )}
        </div>
      </aside>
    </>
  );
}
