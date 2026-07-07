import { useEffect, useState } from "react";
import type { DailyRun, PickAction } from "../lib/types";
import {
  clearQuoteApiKey,
  getQuoteApiKey,
  getWatchlist,
  removeFromWatchlist,
  setQuoteApiKey,
  subscribeToWatchlist,
} from "../lib/storage";
import { fetchQuotes, InvalidApiKeyError, type LiveQuote } from "../lib/quotes";

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
  const [apiKey, setApiKeyState] = useState<string | null>(() => getQuoteApiKey());
  const [keyInputOpen, setKeyInputOpen] = useState(false);
  const [keyInputValue, setKeyInputValue] = useState("");
  const [keyError, setKeyError] = useState<string | null>(null);
  const [quotes, setQuotes] = useState<Map<string, LiveQuote | Error>>(new Map());
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => subscribeToWatchlist(() => setItems(getWatchlist())), []);

  // Auto-refresh once when the sidebar opens, if a key is already saved.
  // Reads storage directly rather than closing over state, so this only
  // depends on `open` and never needs to refire on every watchlist edit.
  useEffect(() => {
    if (!open) return;
    const key = getQuoteApiKey();
    if (!key) return;
    const tickers = getWatchlist().map((item) => item.ticker);
    if (tickers.length === 0) return;
    void refresh(tickers, key);
  }, [open]);

  const entries: ResolvedEntry[] = items
    .map((item) => ({ ticker: item.ticker, addedAt: item.added_at, ...resolveTicker(item.ticker, latest) }))
    .sort((a, b) => a.ticker.localeCompare(b.ticker));

  async function refresh(tickers: string[], key: string) {
    setRefreshing(true);
    try {
      const result = await fetchQuotes(tickers, key);
      const invalidKey = [...result.values()].some((v) => v instanceof InvalidApiKeyError);
      setKeyError(invalidKey ? "Invalid API key — check it and try again." : null);
      setQuotes(result);
    } finally {
      setRefreshing(false);
    }
  }

  function handleSaveKey() {
    const trimmed = keyInputValue.trim();
    if (!trimmed) return;
    setQuoteApiKey(trimmed);
    setApiKeyState(trimmed);
    setKeyInputValue("");
    setKeyInputOpen(false);
    setKeyError(null);
    void refresh(entries.map((e) => e.ticker), trimmed);
  }

  function handleClearKey() {
    clearQuoteApiKey();
    setApiKeyState(null);
    setQuotes(new Map());
    setKeyError(null);
  }

  function handleRefreshClick() {
    if (!apiKey) return;
    void refresh(entries.map((e) => e.ticker), apiKey);
  }

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
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setKeyInputOpen((v) => !v)}
              className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 underline"
            >
              API key
            </button>
            <button
              type="button"
              onClick={onClose}
              aria-label="Close watchlist"
              className="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
            >
              ✕
            </button>
          </div>
        </div>

        {keyInputOpen && (
          <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex flex-col gap-2">
            <label className="text-xs text-gray-500 dark:text-gray-400">
              Finnhub API key (free at finnhub.io) — stored only in this browser, used only to
              call Finnhub directly.
            </label>
            <div className="flex gap-2">
              <input
                type="password"
                value={keyInputValue}
                onChange={(e) => setKeyInputValue(e.target.value)}
                placeholder="Paste your Finnhub key"
                className="flex-1 min-w-0 text-sm px-2 py-1 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              />
              <button
                type="button"
                onClick={handleSaveKey}
                className="text-xs font-medium px-2 py-1 rounded-md border border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400"
              >
                Save
              </button>
            </div>
            {apiKey && (
              <button
                type="button"
                onClick={handleClearKey}
                className="text-xs text-left text-gray-400 hover:text-red-600 dark:hover:text-red-400"
              >
                Clear saved key
              </button>
            )}
          </div>
        )}

        {keyError && <p className="px-4 pt-3 text-xs text-red-600 dark:text-red-400">{keyError}</p>}

        {apiKey ? (
          <div className="px-4 pt-3 flex items-center justify-between gap-2">
            <button
              type="button"
              onClick={handleRefreshClick}
              disabled={refreshing}
              className="text-xs font-medium px-2 py-1 rounded-md border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50"
            >
              {refreshing ? "Refreshing…" : "Refresh prices"}
            </button>
            <span className="text-[11px] text-gray-400 dark:text-gray-500 text-right">
              Live via Finnhub (free tier) — for reference only
            </span>
          </div>
        ) : (
          entries.length > 0 && (
            <p className="px-4 pt-3 text-xs text-gray-500 dark:text-gray-400">
              Add a free Finnhub API key above for live prices.
            </p>
          )
        )}

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {entries.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No stocks watched yet. Add some from today's picks.
            </p>
          ) : (
            entries.map((entry) => {
              const quote = quotes.get(entry.ticker);
              const liveQuote = quote instanceof Error ? null : (quote ?? null);
              const quoteFailed = quote instanceof Error;
              return (
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
                  {liveQuote && (
                    <div
                      className={`text-xs font-medium ${
                        liveQuote.change >= 0
                          ? "text-emerald-600 dark:text-emerald-400"
                          : "text-red-600 dark:text-red-400"
                      }`}
                    >
                      Live: ${liveQuote.price.toFixed(2)} ({liveQuote.change >= 0 ? "+" : ""}
                      {liveQuote.changePercent.toFixed(2)}%)
                    </div>
                  )}
                  {quoteFailed && (
                    <div className="text-[11px] text-gray-400 dark:text-gray-500">Live price unavailable</div>
                  )}
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
              );
            })
          )}
        </div>
      </aside>
    </>
  );
}
