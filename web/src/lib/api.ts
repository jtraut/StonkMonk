// Fetches the static JSON the scanner pipeline commits to data/ and the deploy
// workflow copies into public/data/. No backend — this is all static file reads.
import type { DailyRun, TrackPerformance } from "./types";

const base = import.meta.env.BASE_URL;

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${base}data/${path}`);
  if (!res.ok) {
    throw new Error(`Failed to load ${path} (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export function fetchLatest(): Promise<DailyRun> {
  return fetchJson<DailyRun>("latest.json");
}

export function fetchIndex(): Promise<string[]> {
  return fetchJson<string[]>("index.json");
}

export function fetchPicksForDate(date: string): Promise<DailyRun> {
  return fetchJson<DailyRun>(`picks/${date}.json`);
}

export function fetchTrackPerformance(): Promise<TrackPerformance[]> {
  return fetchJson<TrackPerformance[]>("track_performance.json");
}
