// Client-side watchlist storage. No backend — the picks pipeline never knows
// what a user is watching, only the browser does.
import type { WatchlistItem } from "./types";

const WATCHLIST_KEY = "stonkmonk:watchlist";
const WATCHLIST_EVENT = "stonkmonk:watchlist-changed";

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
  window.dispatchEvent(new Event(WATCHLIST_EVENT));
}

export function getWatchlist(): WatchlistItem[] {
  return readWatchlist();
}

// Lets any mounted component (sidebar, per-pick toggle buttons) stay in sync
// since watchlist state lives outside React in localStorage.
export function subscribeToWatchlist(callback: () => void): () => void {
  window.addEventListener(WATCHLIST_EVENT, callback);
  return () => window.removeEventListener(WATCHLIST_EVENT, callback);
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

// BYO-key for live watchlist quotes (Finnhub) - client-side only, same
// plaintext-localStorage pattern as the watchlist itself. Never sent
// anywhere but directly to Finnhub from the browser.
const QUOTE_API_KEY = "stonkmonk:finnhub-key";

export function getQuoteApiKey(): string | null {
  return localStorage.getItem(QUOTE_API_KEY);
}

export function setQuoteApiKey(key: string): void {
  localStorage.setItem(QUOTE_API_KEY, key);
}

export function clearQuoteApiKey(): void {
  localStorage.removeItem(QUOTE_API_KEY);
}
