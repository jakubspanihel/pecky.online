import Anthropic from "@anthropic-ai/sdk";
import {
  FALLBACK_PRICE,
  HttpError,
  MAX_OUTPUT_TOKENS,
  MODERN_MODEL,
  PRICES,
  TOP_K,
  czDate,
  pragueDate,
  type AnswerResult,
  type ChatMessage,
  type Env,
} from "./common.ts";
import { formatSources, systemPrompt } from "./prompt.ts";
import { search, type Index } from "./search.ts";

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

export async function recordSpend(env: Env, month: string, model: string, inTok: number, outTok: number) {
  const [pin, pout] = PRICES[model] ?? FALLBACK_PRICE;
  const micro = Math.round(inTok * pin + outTok * pout); // USD/1M tokenů × tokeny = mikro-USD
  const key = `spend:${month}`;
  const total = Number((await env.BUDGET.get(key)) ?? 0) + micro;
  await env.BUDGET.put(key, String(total), { expirationTtl: 40 * 86400 });
}

export async function answer(env: Env, messages: ChatMessage[], month: string): Promise<AnswerResult> {
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

  const [pin, pout] = PRICES[model] ?? FALLBACK_PRICE;
  const meta: AnswerResult["meta"] = {
    model,
    inputTokens: response.usage.input_tokens,
    outputTokens: response.usage.output_tokens,
    costMicro: Math.round(response.usage.input_tokens * pin + response.usage.output_tokens * pout),
    tools: [],
    retrieved: sources.map((s) => s.title),
  };
  if (response.stop_reason === "refusal") {
    return { answer: "Na tuhle otázku PečkyBot odpovědět nemůže. Zkuste ji prosím formulovat jinak.", sources: [], meta };
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
    meta,
  };
}

