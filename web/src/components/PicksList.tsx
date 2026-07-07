import type { DailyRun } from "../lib/types";
import { PickCard } from "./PickCard";

export function PicksList({ run }: { run: DailyRun }) {
  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-lg font-semibold text-emerald-700 dark:text-emerald-400 mb-3">Buy</h2>
        {run.buys.length === 0 ? (
          <p className="text-sm text-gray-500 dark:text-gray-400">No buy signals today.</p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {run.buys.map((pick) => (
              <PickCard key={pick.ticker} pick={pick} />
            ))}
          </div>
        )}
      </section>
      <section>
        <h2 className="text-lg font-semibold text-amber-700 dark:text-amber-400 mb-3">
          Caution / Consider Trimming
        </h2>
        {run.cautions.length === 0 ? (
          <p className="text-sm text-gray-500 dark:text-gray-400">No caution flags today.</p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {run.cautions.map((pick) => (
              <PickCard key={pick.ticker} pick={pick} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
