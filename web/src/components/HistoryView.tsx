import { useEffect, useState } from "react";
import type { DailyRun } from "../lib/types";
import { fetchIndex, fetchPicksForDate } from "../lib/api";
import { PicksList } from "./PicksList";

export function HistoryView() {
  const [dates, setDates] = useState<string[]>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [run, setRun] = useState<DailyRun | null>(null);
  const [indexError, setIndexError] = useState<string | null>(null);
  const [runError, setRunError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchIndex()
      .then((loaded) => {
        setDates(loaded);
        if (loaded.length > 0) setSelectedDate(loaded[0]);
      })
      .catch((err: unknown) => {
        setIndexError(err instanceof Error ? err.message : "Failed to load picks history.");
      });
  }, []);

  useEffect(() => {
    if (!selectedDate) return;
    let cancelled = false;
    setLoading(true);
    setRunError(null);
    fetchPicksForDate(selectedDate)
      .then((data) => {
        if (!cancelled) setRun(data);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setRunError(err instanceof Error ? err.message : `Failed to load picks for ${selectedDate}.`);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedDate]);

  if (indexError) {
    return <p className="text-sm text-red-600 dark:text-red-400">{indexError}</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {dates.map((date) => (
          <button
            key={date}
            type="button"
            onClick={() => setSelectedDate(date)}
            className={`px-3 py-1.5 rounded-md text-sm font-medium border ${
              date === selectedDate
                ? "bg-gray-900 text-white border-gray-900 dark:bg-gray-100 dark:text-gray-900 dark:border-gray-100"
                : "text-gray-600 dark:text-gray-300 border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800"
            }`}
          >
            {date}
          </button>
        ))}
      </div>
      {loading && <p className="text-sm text-gray-500 dark:text-gray-400">Loading...</p>}
      {runError && <p className="text-sm text-red-600 dark:text-red-400">{runError}</p>}
      {!loading && !runError && run && <PicksList run={run} />}
    </div>
  );
}
