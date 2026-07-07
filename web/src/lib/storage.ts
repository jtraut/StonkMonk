// Client-side watchlist storage. No backend — the picks pipeline never knows
// what a user is watching, only the browser does.
import type { WatchlistItem } from "./types";

const WATCHLIST_KEY = "stonkmonk:watchlist";

function readWatchlist(): WatchlistItem[] {
  try {
    const raw = localStorage.getItem(WATCHLIST_KEY);
    return raw ? (JSON.parse(raw) as WatchlistItem[]) : [];
  } catch {
    return [];
  }
}

function writeWatchlist(items: WatchlistItem[]): void {
  localStorage.setItem(WATCHLIST_KEY, JSON.stringify(items));
}

export function getWatchlist(): WatchlistItem[] {
  return readWatchlist();
}

export function isWatchlisted(ticker: string): boolean {
  return readWatchlist().some((item) => item.ticker === ticker);
}

export function addToWatchlist(ticker: string): void {
  const items = readWatchlist();
  if (items.some((item) => item.ticker === ticker)) return;
  items.push({ ticker, added_at: new Date().toISOString() });
  writeWatchlist(items);
}

export function removeFromWatchlist(ticker: string): void {
  writeWatchlist(readWatchlist().filter((item) => item.ticker !== ticker));
}
