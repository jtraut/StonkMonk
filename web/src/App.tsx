import { useEffect, useState } from "react";
import type { DailyRun } from "./lib/types";
import { fetchLatest } from "./lib/api";
import { Header } from "./components/Header";
import { ComplianceFooter } from "./components/ComplianceFooter";
import { TodayView } from "./components/TodayView";
import { HistoryView } from "./components/HistoryView";
import { WatchlistSidebar } from "./components/WatchlistSidebar";

type Tab = "today" | "history";

function App() {
  const [activeTab, setActiveTab] = useState<Tab>("today");
  const [latest, setLatest] = useState<DailyRun | null>(null);
  const [latestError, setLatestError] = useState<string | null>(null);
  const [latestLoading, setLatestLoading] = useState(true);
  const [watchlistOpen, setWatchlistOpen] = useState(false);

  useEffect(() => {
    fetchLatest()
      .then(setLatest)
      .catch((err: unknown) => {
        setLatestError(err instanceof Error ? err.message : "Failed to load today's picks.");
      })
      .finally(() => setLatestLoading(false));
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100">
      <Header
        activeTab={activeTab}
        onTabChange={setActiveTab}
        generatedAt={latest?.generated_at ?? null}
        onToggleWatchlist={() => setWatchlistOpen((v) => !v)}
      />
      <main className="max-w-5xl mx-auto w-full px-4 py-6 flex-1">
        {activeTab === "today" ? (
          <TodayView run={latest} loading={latestLoading} error={latestError} />
        ) : (
          <HistoryView />
        )}
      </main>
      <ComplianceFooter />
      <WatchlistSidebar open={watchlistOpen} onClose={() => setWatchlistOpen(false)} latest={latest} />
    </div>
  );
}

export default App;
