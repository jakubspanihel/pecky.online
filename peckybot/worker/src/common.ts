export interface Env {
  ANTHROPIC_API_KEY: string;
  BUDGET: KVNamespace;
  LOG?: D1Database; // anonymní záznamy a cache odpovědí (schema.sql); bez něj Worker jen odpovídá
  EVAL_TOKEN?: string; // secret: hlavička X-Eval-Token obejde limit na IP a cache (měření kvality)
  MODEL?: string;
  SITE_URL: string;
  ALLOWED_ORIGINS: string;
  MONTHLY_BUDGET_USD: string;
  DAILY_PER_IP: string;
  DAILY_GLOBAL: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export const MAX_MESSAGES = 6; // poslední výměny konverzace, které se posílají modelu
export const MAX_USER_CHARS = 600;
export const MAX_ASSISTANT_CHARS = 3000;
export const TOP_K = 8;
export const MAX_OUTPUT_TOKENS = 1500;

// USD za milion tokenů (vstup, výstup) — jen pro odhad útraty proti měsíčnímu stropu.
// Neznámý model se počítá nejdražší sazbou, ať strop spíš zabere dřív než později.
export const PRICES: Record<string, [number, number]> = {
  "claude-haiku-4-5": [1, 5],
  "claude-sonnet-5-5": [2, 10],
  "claude-sonnet-5": [2, 10],
  "claude-opus-5-5": [4, 20],
};
export const FALLBACK_PRICE: [number, number] = [10, 50];

// Modely, které přijímají server-side `fallbacks` (při odmítnutí odpovědi
// přepočítá dotaz jiným modelem) a parametr `output_config.effort`.
export const MODERN_MODEL = /^claude-(fable-5|opus-5|sonnet-5-5)/;

export class HttpError extends Error {
  status: number;
  code: string;
  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

export function pragueDate(): string {
  // sv-SE dává ISO tvar RRRR-MM-DD
  return new Date().toLocaleDateString("sv-SE", { timeZone: "Europe/Prague" });
}

export function czDate(iso: string): string {
  const [y, m, d] = iso.split("-");
  return `${Number(d)}. ${Number(m)}. ${y}`;
}

export async function bump(kv: KVNamespace, key: string, ttlSeconds: number): Promise<number> {
  const n = Number((await kv.get(key)) ?? 0) + 1;
  await kv.put(key, String(n), { expirationTtl: ttlSeconds });
  return n;
}


/** Výsledek answer(); `meta` slouží záznamům a hodnocení (log.ts), neodesílá se do prohlížeče. */
export interface AnswerResult {
  answer: string;
  sources: { n: number; title: string; url: string }[];
  meta: {
    model: string;
    inputTokens: number;
    outputTokens: number;
    costMicro: number; // mikro-USD, součet všech volání modelu v jednom dotazu
    tools: string[]; // názvy nástrojů v pořadí volání (prázdné = jen úryvky)
    retrieved: string[]; // titulky úryvků dodaných modelu
  };
}
