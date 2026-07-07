export function ComplianceFooter() {
  return (
    <footer className="mt-auto border-t border-gray-200 dark:border-gray-700 text-xs text-gray-500 dark:text-gray-400">
      <div className="max-w-5xl mx-auto px-4 py-4 space-y-1">
        <p>
          Educational use only. Not financial advice. Data via Yahoo Finance (yfinance) and Nasdaq
          Trader. Not affiliated with or endorsed by Robinhood, Nasdaq, or Yahoo.
        </p>
        <p>
          Buy/caution picks are generated algorithmically from computed technical signals and are
          not reviewed by a human before publishing. AI conviction picks (badged "AI Pick," when
          present) are an experimental, model-judgment layer — closer to a judgment call than a
          formula, not score-selected, and carry higher variance.
        </p>
      </div>
    </footer>
  );
}
