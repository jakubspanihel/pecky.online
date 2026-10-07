import Anthropic from "@anthropic-ai/sdk";
import { formatSources, systemPrompt } from "./prompt.ts";
import { search, type Index } from "./search.ts";

export interface Env {
  ANTHROPIC_API_KEY: string;
  BUDGET: KVNamespace;
  MODEL?: string;
  SITE_URL: string;
  ALLOWED_ORIGINS: string;
  MONTHLY_BUDGET_USD: string;
  DAILY_PER_IP: string;
  DAILY_GLOBAL: string;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

const MAX_MESSAGES = 6; // poslední výměny konverzace, které se posílají modelu
const MAX_USER_CHARS = 600;
const MAX_ASSISTANT_CHARS = 3000;
const TOP_K = 8;
const MAX_OUTPUT_TOKENS = 1500;

// USD za milion tokenů (vstup, výstup) — jen pro odhad útraty proti měsíčnímu stropu.
// Neznámý model se počítá nejdražší sazbou, ať strop spíš zabere dřív než později.
const PRICES: Record<string, [number, number]> = {
  "claude-haiku-4-5": [1, 5],
  "claude-sonnet-5-5": [2, 10],
  "claude-sonnet-5": [2, 10],
  "claude-opus-5-5": [4, 20],
};
const FALLBACK_PRICE: [number, number] = [10, 50];

// Modely, které přijímají server-side `fallbacks` (při odmítnutí odpovědi
// přepočítá dotaz jiným modelem) a parametr `output_config.effort`.
const MODERN_MODEL = /^claude-(fable-5|opus-5|sonnet-5-5)/;

class HttpError extends Error {
  status: number;
  code: string;
  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

// ---------- pomocné ----------

function corsHeaders(origin: string): HeadersInit {
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin",
  };
}

function json(body: unknown, status: number, origin: string): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders(origin) },
  });
}

function pragueDate(): string {
  // sv-SE dává ISO tvar RRRR-MM-DD
  return new Date().toLocaleDateString("sv-SE", { timeZone: "Europe/Prague" });
}

function czDate(iso: string): string {
  const [y, m, d] = iso.split("-");
  return `${Number(d)}. ${Number(m)}. ${y}`;
}

async function bump(kv: KVNamespace, key: string, ttlSeconds: number): Promise<number> {
  const n = Number((await kv.get(key)) ?? 0) + 1;
  await kv.put(key, String(n), { expirationTtl: ttlSeconds });
  return n;
}

// ---------- index ----------

let indexCache: { index: Index; at: number } | null = null;
const shardCache = new Map<number, { texts: string[]; at: number }>();
// rejstřík se obnovuje často (nové jednání, přegenerování); dávky textů jsou vázané na otisk obsahu
const INDEX_TTL_MS = 5 * 60 * 1000;

async function fetchJson<T>(url: string, cacheTtl = 300): Promise<T> {
  const r = await fetch(url, { cf: { cacheTtl, cacheEverything: true } });
  if (!r.ok) throw new HttpError(502, "index", `Index ${url} vrátil ${r.status}`);
  return (await r.json()) as T;
}

async function getIndex(env: Env): Promise<Index> {
  if (indexCache && Date.now() - indexCache.at < INDEX_TTL_MS) return indexCache.index;
  const index = await fetchJson<Index>(
    // časový klíč po 5 minutách = nová položka v cache Cloudflare; GitHub Pages query ignoruje
    `${env.SITE_URL}/peckybot/index.json?t=${Math.floor(Date.now() / INDEX_TTL_MS)}`,
  );
  indexCache = { index, at: Date.now() };
  shardCache.clear(); // nový rejstřík = nové číslování dávek
  return index;
}

async function getTexts(env: Env, index: Index, ids: number[]): Promise<Map<number, string>> {
  const shards = [...new Set(ids.map((id) => Math.floor(id / index.shard)))];
  await Promise.all(
    shards.map(async (k) => {
      const hit = shardCache.get(k);
      if (hit && Date.now() - hit.at < INDEX_TTL_MS) return;
      const texts = await fetchJson<string[]>(
        `${env.SITE_URL}/peckybot/chunks/${k}.json${index.h ? `?h=${index.h}` : ""}`,
        index.h ? 86400 : 300,
      );
      shardCache.set(k, { texts, at: Date.now() });
    }),
  );
  const out = new Map<number, string>();
  for (const id of ids) {
    out.set(id, shardCache.get(Math.floor(id / index.shard))?.texts[id % index.shard] ?? "");
  }
  return out;
}

// ---------- limity a rozpočet ----------

async function enforceLimits(env: Env, ip: string): Promise<{ month: string }> {
  const day = pragueDate();
  const month = day.slice(0, 7);

  const spentMicro = Number((await env.BUDGET.get(`spend:${month}`)) ?? 0);
  if (spentMicro >= Number(env.MONTHLY_BUDGET_USD) * 1_000_000) {
    throw new HttpError(
      429,
      "budget",
      "PečkyBot má na tento měsíc vyčerpaný rozpočet. Zkuste to prosím od prvního dne příštího měsíce.",
    );
  }
  const global = await bump(env.BUDGET, `day:${day}`, 2 * 86400);
  if (global > Number(env.DAILY_GLOBAL)) {
    throw new HttpError(429, "daily_global", "PečkyBot dnes dosáhl denního limitu dotazů. Zkuste to prosím zítra.");
  }
  const perIp = await bump(env.BUDGET, `ip:${day}:${ip}`, 2 * 86400);
  if (perIp > Number(env.DAILY_PER_IP)) {
    throw new HttpError(
      429,
      "daily_ip",
      `Dnes jste využili ${env.DAILY_PER_IP} dotazů, což je denní limit na jednoho návštěvníka. Zkuste to prosím zítra.`,
    );
  }
  return { month };
}

async function recordSpend(env: Env, month: string, model: string, inTok: number, outTok: number) {
  const [pin, pout] = PRICES[model] ?? FALLBACK_PRICE;
  const micro = Math.round(inTok * pin + outTok * pout); // USD/1M tokenů × tokeny = mikro-USD
  const key = `spend:${month}`;
  const total = Number((await env.BUDGET.get(key)) ?? 0) + micro;
  await env.BUDGET.put(key, String(total), { expirationTtl: 40 * 86400 });
}

// ---------- požadavek ----------

function parseMessages(body: unknown): ChatMessage[] {
  const raw = (body as { messages?: unknown })?.messages;
  if (!Array.isArray(raw) || raw.length === 0) throw new HttpError(400, "bad_request", "Chybí zpráva.");
  const msgs: ChatMessage[] = [];
  for (const m of raw.slice(-MAX_MESSAGES)) {
    const role = (m as ChatMessage)?.role;
    const content = (m as ChatMessage)?.content;
    if ((role !== "user" && role !== "assistant") || typeof content !== "string" || !content.trim()) {
      throw new HttpError(400, "bad_request", "Neplatná zpráva.");
    }
    const max = role === "user" ? MAX_USER_CHARS : MAX_ASSISTANT_CHARS;
    if (role === "user" && content.length > max) {
      throw new HttpError(400, "too_long", `Dotaz je příliš dlouhý (nejvýš ${max} znaků).`);
    }
    msgs.push({ role, content: content.slice(0, max) });
  }
  while (msgs.length && msgs[0].role !== "user") msgs.shift(); // první zpráva musí být od uživatele
  if (msgs.length === 0 || msgs[msgs.length - 1].role !== "user") {
    throw new HttpError(400, "bad_request", "Poslední zpráva musí být dotaz.");
  }
  return msgs;
}

async function answer(env: Env, messages: ChatMessage[], month: string) {
  const model = env.MODEL || "claude-sonnet-5-5";
  const modern = MODERN_MODEL.test(model);

  // dotaz pro vyhledávání = poslední otázka + předchozí (kvůli navazujícím dotazům „a kdo to navrhl?“)
  const users = messages.filter((m) => m.role === "user");
  // nejnovější otázka má plnou váhu, předchozí jen poloviční (viz search.ts)
  const query = users[users.length - 1].content;
  const context = users.length > 1 ? users[users.length - 2].content : undefined;
  const index = await getIndex(env);
  const hits = search(index, query, TOP_K, { context, today: pragueDate() });
  const texts = await getTexts(env, index, hits.map((h) => h.id));
  const sources = hits.map((h, i) => ({
    n: i + 1,
    title: index.chunks[h.id].t,
    url: index.chunks[h.id].u,
    text: texts.get(h.id) ?? "",
  }));

  const last = messages[messages.length - 1];
  const apiMessages: Anthropic.Beta.BetaMessageParam[] = [
    ...messages.slice(0, -1),
    {
      role: "user",
      content: `${sources.length ? formatSources(sources) : "<zdroje></zdroje>"}\n\nOtázka: ${last.content}`,
    },
  ];

  const client = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY, maxRetries: 1, timeout: 45_000 });
  const params = {
    model,
    max_tokens: MAX_OUTPUT_TOKENS,
    system: systemPrompt(czDate(pragueDate())),
    messages: apiMessages,
    // krátké odpovědi z dodaných úryvků nepotřebují hluboké uvažování
    ...(modern ? { output_config: { effort: "low" as const } } : {}),
  };
  const response = modern
    ? await client.beta.messages.create({
        ...params,
        betas: ["server-side-fallback-2026-07-01"],
        fallbacks: "default",
      } as Anthropic.Beta.MessageCreateParamsNonStreaming)
    : await client.beta.messages.create(params);

  await recordSpend(env, month, model, response.usage.input_tokens, response.usage.output_tokens);

  if (response.stop_reason === "refusal") {
    return { answer: "Na tuhle otázku PečkyBot odpovědět nemůže. Zkuste ji prosím formulovat jinak.", sources: [] };
  }
  const text = response.content
    .flatMap((b) => (b.type === "text" ? [b.text] : []))
    .join("")
    .trim();
  // vrací se jen zdroje, na které odpověď skutečně odkazuje ([n])
  const cited = new Set([...text.matchAll(/\[(\d+)\]/g)].map((m) => Number(m[1])));
  return {
    answer: text || "PečkyBot teď nedokázal odpovědět. Zkuste to prosím znovu.",
    sources: sources.filter((s) => cited.has(s.n)).map(({ n, title, url }) => ({ n, title, url })),
  };
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const origin = request.headers.get("Origin") ?? "";
    const allowed = env.ALLOWED_ORIGINS.split(",").map((s) => s.trim());
    if (!allowed.includes(origin)) {
      return new Response("Forbidden", { status: 403 });
    }
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }
    if (request.method !== "POST" || new URL(request.url).pathname !== "/chat") {
      return json({ error: "Nenalezeno.", code: "not_found" }, 404, origin);
    }

    try {
      let body: unknown;
      try {
        body = await request.json();
      } catch {
        throw new HttpError(400, "bad_request", "Neplatný požadavek.");
      }
      const messages = parseMessages(body);
      const ip = request.headers.get("CF-Connecting-IP") ?? "unknown";
      const { month } = await enforceLimits(env, ip);
      return json(await answer(env, messages, month), 200, origin);
    } catch (err) {
      if (err instanceof HttpError) {
        return json({ error: err.message, code: err.code }, err.status, origin);
      }
      if (err instanceof Anthropic.RateLimitError || err instanceof Anthropic.APIConnectionError) {
        return json({ error: "PečkyBot je momentálně přetížený. Zkuste to prosím za chvíli.", code: "upstream" }, 503, origin);
      }
      console.error("peckybot chyba:", err);
      return json({ error: "PečkyBot teď neodpovídá. Zkuste to prosím později.", code: "internal" }, 500, origin);
    }
  },
} satisfies ExportedHandler<Env>;
