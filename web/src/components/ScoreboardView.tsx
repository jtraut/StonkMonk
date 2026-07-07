import { useEffect, useState } from "react";
import type { Track, TrackPerformance } from "../lib/types";
import { fetchTrackPerformance } from "../lib/api";

const TRACK_LABELS: Record<Track, string> = {
  algorithmic: "Algorithmic",
  ai: "AI Conviction",
};

const TRACK_ACCENT: Record<Track, string> = {
  algorithmic: "text-blue-700 dark:text-blue-400",
  ai: "text-violet-700 dark:text-violet-400",
};

function fmtPct(value: number | null): string {
  return value === null ? "n/a" : `${value > 0 ? "+" : ""}${value.toFixed(2)}%`;
}

function fmtDate(value: string | null): string {
  if (!value) return "n/a";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(undefined, { dateStyle: "medium" });
}

function TrackCard({ perf }: { perf: TrackPerformance }) {
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-4 flex flex-col gap-3">
      <h3 className={`font-semibold ${TRACK_ACCENT[perf.track]}`}>{TRACK_LABELS[perf.track]}</h3>
      {perf.picks_count === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">No picks tracked yet.</p>
      ) : (
        <dl className="text-sm grid grid-cols-2 gap-x-3 gap-y-2">
          <dt className="text-gray-500 dark:text-gray-400">Picks tracked</dt>
          <dd className="text-gray-900 dark:text-gray-100">{perf.picks_count}</dd>

          <dt className="text-gray-500 dark:text-gray-400">Avg return (5d)</dt>
          <dd className="text-gray-900 dark:text-gray-100">{fmtPct(perf.avg_return_5d)}</dd>

          <dt className="text-gray-500 dark:text-gray-400">Avg return (30d)</dt>
          <dd className="text-gray-900 dark:text-gray-100">{fmtPct(perf.avg_return_30d)}</dd>

          <dt className="text-gray-500 dark:text-gray-400">Win rate</dt>
          <dd className="text-gray-900 dark:text-gray-100">
            {perf.win_rate === null ? "n/a" : `${(perf.win_rate * 100).toFixed(0)}%`}
          </dd>

          <dt className="text-gray-500 dark:text-gray-400">Tracking since</dt>
          <dd className="text-gray-900 dark:text-gray-100">{fmtDate(perf.since)}</dd>
        </dl>
      )}
    </div>
  );
}

export function ScoreboardView() {
  const [performance, setPerformance] = useState<TrackPerformance[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrackPerformance()
      .then(setPerformance)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Failed to load track performance.");
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="text-sm text-gray-500 dark:text-gray-400">Loading scoreboard...</p>;
  }
  if (error) {
    return <p className="text-sm text-red-600 dark:text-red-400">{error}</p>;
  }
  if (!performance) {
    return null;
  }

  return (
    <div className="space-y-4">
      <p className="text-xs text-gray-500 dark:text-gray-400">
        Unrealized/paper performance only — not investment advice. This is an ongoing, honest
        comparison between the two tracks, not a claim that either approach "wins."
      </p>
      <div className="grid gap-4 sm:grid-cols-2">
        {performance.map((perf) => (
          <TrackCard key={perf.track} perf={perf} />
        ))}
      </div>
    </div>
  );
}
