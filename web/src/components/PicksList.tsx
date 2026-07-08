import type { DailyRun } from "../lib/types";
import { PickCard } from "./PickCard";

export function PicksList({ run }: { run: DailyRun }) {
  const aiPicks = run.ai_picks ?? [];
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
      {aiPicks.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-lg font-semibold text-violet-700 dark:text-violet-400">
              AI Conviction Picks
            </h2>
            <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-violet-100 text-violet-800 dark:bg-violet-900/40 dark:text-violet-300">
              AI
            </span>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
            Experimental — a model judgment call, not a formula. Higher variance than the
            algorithmic picks above.
          </p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {aiPicks.map((pick) => (
              <PickCard key={pick.ticker} pick={pick} />
            ))}
          </div>
        </section>
      )}
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
