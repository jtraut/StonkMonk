import { useEffect, useState } from "react";
import logo from "../assets/logo.svg";
import { getWatchlist, subscribeToWatchlist } from "../lib/storage";

type Tab = "today" | "history";

interface HeaderProps {
  activeTab: Tab;
  onTabChange: (tab: Tab) => void;
  generatedAt: string | null;
  onToggleWatchlist: () => void;
}

function formatGeneratedAt(iso: string | null): string {
  if (!iso) return "unknown";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "unknown";
  return date.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

const TABS: Tab[] = ["today", "history"];

export function Header({ activeTab, onTabChange, generatedAt, onToggleWatchlist }: HeaderProps) {
  const [watchlistCount, setWatchlistCount] = useState(() => getWatchlist().length);

  useEffect(() => subscribeToWatchlist(() => setWatchlistCount(getWatchlist().length)), []);

  return (
    <header className="border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-5xl mx-auto px-4 py-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <img src={logo} alt="StonkMonk" className="w-9 h-9" />
          <div>
            <div className="font-bold text-lg text-gray-900 dark:text-gray-100">StonkMonk</div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              Last successful run: {formatGeneratedAt(generatedAt)}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <nav className="flex gap-2">
            {TABS.map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => onTabChange(tab)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium capitalize ${
                  activeTab === tab
                    ? "bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900"
                    : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                }`}
              >
                {tab}
              </button>
            ))}
          </nav>
          <button
            type="button"
            onClick={onToggleWatchlist}
            className="px-3 py-1.5 rounded-md text-sm font-medium border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center gap-1.5"
          >
            Watchlist
            {watchlistCount > 0 && (
              <span className="inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1 rounded-full bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900 text-[11px] font-semibold">
                {watchlistCount}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
