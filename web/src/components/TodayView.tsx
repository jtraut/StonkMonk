import type { DailyRun } from "../lib/types";
import { PicksList } from "./PicksList";

interface TodayViewProps {
  run: DailyRun | null;
  loading: boolean;
  error: string | null;
}

export function TodayView({ run, loading, error }: TodayViewProps) {
  if (loading) {
    return <p className="text-sm text-gray-500 dark:text-gray-400">Loading today's picks...</p>;
  }
  if (error) {
    return <p className="text-sm text-red-600 dark:text-red-400">{error}</p>;
  }
  if (!run) {
    return null;
  }
  return <PicksList run={run} />;
}
