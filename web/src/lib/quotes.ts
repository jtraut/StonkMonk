// Live watchlist quotes via Finnhub's free-tier /quote endpoint, called
// directly from the browser with a user-supplied key (see storage.ts). This
// is a separate data path from the daily yfinance scan - optional, opt-in,
// for reference only.

export interface LiveQuote {
  price: number;
  change: number;
  changePercent: number;
}

export class InvalidApiKeyError extends Error {
  constructor() {
    super("Invalid Finnhub API key");
    this.name = "InvalidApiKeyError";
  }
}

interface FinnhubQuote {
  c: number; // current price
  d: number; // change
  dp: number; // percent change
  pc: number; // previous close
}

export async function fetchQuote(ticker: string, apiKey: string): Promise<LiveQuote> {
  const url = `https://finnhub.io/api/v1/quote?symbol=${encodeURIComponent(ticker)}&token=${encodeURIComponent(apiKey)}`;
  const res = await fetch(url);
  if (res.status === 401) {
    throw new InvalidApiKeyError();
  }
  if (!res.ok) {
    throw new Error(`Finnhub request failed (${res.status})`);
  }
  const data = (await res.json()) as FinnhubQuote;
  if (data.c === 0 && data.pc === 0) {
    throw new Error(`No quote data for ${ticker}`);
  }
  return { price: data.c, change: data.d, changePercent: data.dp };
}

export async function fetchQuotes(tickers: string[], apiKey: string): Promise<Map<string, LiveQuote | Error>> {
  const results = await Promise.allSettled(tickers.map((ticker) => fetchQuote(ticker, apiKey)));
  const out = new Map<string, LiveQuote | Error>();
  tickers.forEach((ticker, i) => {
    const result = results[i];
    out.set(ticker, result.status === "fulfilled" ? result.value : toError(result.reason));
  });
  return out;
}

function toError(reason: unknown): Error {
  return reason instanceof Error ? reason : new Error(String(reason));
}
