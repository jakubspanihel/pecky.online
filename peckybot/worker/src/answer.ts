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
import { MAX_TOOL_ROUNDS, TOOL_DEFS, executeTool, typFilter, type ToolContext } from "./tools.ts";

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

type DataFile = Parameters<ToolContext["load"]>[0];
const dataCache = new Map<string, { data: unknown; at: number }>();

async function loadData(env: Env, index: Index, file: DataFile): Promise<any> {
  const hit = dataCache.get(file);
  if (hit && Date.now() - hit.at < INDEX_TTL_MS) return hit.data;
  const q = index.h ? `h=${index.h}` : `t=${Math.floor(Date.now() / INDEX_TTL_MS)}`;
  const data = await fetchJson<unknown>(`${env.SITE_URL}/peckybot/data/${file}.json?${q}`, index.h ? 86400 : 300);
  dataCache.set(file, { data, at: Date.now() });
  return data;
}

export async function recordSpend(env: Env, month: string, model: string, inTok: number, outTok: number) {
  const [pin, pout] = PRICES[model] ?? FALLBACK_PRICE;
  const micro = Math.round(inTok * pin + outTok * pout); // USD/1M tokenů × tokeny = mikro-USD
  const key = `spend:${month}`;
  const total = Number((await env.BUDGET.get(key)) ?? 0) + micro;
  await env.BUDGET.put(key, String(total), { expirationTtl: 40 * 86400 });
}

/** odhad ceny jednoho volání v mikro-USD; cache: zápis 1,25×, čtení 0,1× sazby vstupu */
function usageCost(model: string, u: any) {
  const [pin, pout] = PRICES[model] ?? FALLBACK_PRICE;
  const inp = u?.input_tokens ?? 0;
  const cc = u?.cache_creation_input_tokens ?? 0;
  const cr = u?.cache_read_input_tokens ?? 0;
  const out = u?.output_tokens ?? 0;
  const effIn = inp + 1.25 * cc + 0.1 * cr;
  return { effIn, out, rawIn: inp + cc + cr, micro: Math.round(effIn * pin + out * pout) };
}

export const QUESTION_COST_CAP_MICRO = 60_000; // 0,06 USD na jeden dotaz
const REFUSAL_TEXT = "Na tuhle otázku PečkyBot odpovědět nemůže. Zkuste ji prosím formulovat jinak.";
const GIVE_UP_TEXT = "PečkyBot na tuhle otázku nedokázal v rozumném rozsahu odpovědět. Zkuste ji prosím zúžit nebo rozdělit.";

export async function answer(env: Env, messages: ChatMessage[], month: string): Promise<AnswerResult> {
  const model = env.MODEL || "claude-sonnet-5-5";
  const modern = MODERN_MODEL.test(model);
  const today = pragueDate();

  // dotaz pro vyhledávání = poslední otázka + předchozí (kvůli navazujícím dotazům „a kdo to navrhl?“)
  const users = messages.filter((m) => m.role === "user");
  // nejnovější otázka má plnou váhu, předchozí jen poloviční (viz search.ts)
  const query = users[users.length - 1].content;
  const context = users.length > 1 ? users[users.length - 2].content : undefined;
  const index = await getIndex(env);
  const hits = search(index, query, TOP_K, { context, today });
  const texts = await getTexts(env, index, hits.map((h) => h.id));
  const sources = hits.map((h, i) => ({
    n: i + 1,
    title: index.chunks[h.id].t,
    url: index.chunks[h.id].u,
    text: texts.get(h.id) ?? "",
  }));

  // registr zdrojů: úvodní úryvky + zdroje z výsledků nástrojů (číslování navazuje)
  const registry: { n: number; title: string; url: string }[] = sources.map(({ n, title, url }) => ({ n, title, url }));
  const cite = (title: string, url: string): number => {
    const hit = registry.find((s) => s.title === title && s.url === url);
    if (hit) return hit.n;
    registry.push({ n: registry.length + 1, title, url });
    return registry.length;
  };
  const toolCtx: ToolContext = {
    today,
    cite,
    load: (file) => loadData(env, index, file),
    async searchText(dotaz, typ) {
      const re = typFilter(typ);
      const found = search(index, dotaz, re ? 60 : 6, { today });
      const sel = re ? found.filter((h) => re.test(index.chunks[h.id].t)).slice(0, 6) : found;
      const tx = await getTexts(env, index, sel.map((h) => h.id));
      return sel.map((h) => ({ title: index.chunks[h.id].t, url: index.chunks[h.id].u, text: tx.get(h.id) ?? "" }));
    },
  };

  const last = messages[messages.length - 1];
  const apiMessages: any[] = [
    ...messages.slice(0, -1),
    {
      role: "user",
      content: `${sources.length ? formatSources(sources) : "<zdroje></zdroje>"}\n\nOtázka: ${last.content}`,
    },
  ];

  const client = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY, maxRetries: 1, timeout: 45_000 });
  // prompt caching: systémový prompt a definice nástrojů jsou stejné pro všechny dotazy
  const system = [{ type: "text" as const, text: systemPrompt(czDate(today)), cache_control: { type: "ephemeral" as const } }];
  const tools = TOOL_DEFS.map((t, i) =>
    i === TOOL_DEFS.length - 1 ? { ...t, cache_control: { type: "ephemeral" as const } } : { ...t },
  );

  const meta: AnswerResult["meta"] = { model, inputTokens: 0, outputTokens: 0, costMicro: 0, tools: [], retrieved: sources.map((s) => s.title) };
  const finish = (text: string, forceEmpty = false): AnswerResult => {
    // vrací se jen zdroje, na které odpověď skutečně odkazuje ([n])
    const cited = new Set(forceEmpty ? [] : [...text.matchAll(/\[(\d+)\]/g)].map((m) => Number(m[1])));
    return { answer: text, sources: registry.filter((s) => cited.has(s.n)), meta };
  };

  let toolRounds = 0;
  for (;;) {
    const noMoreTools = toolRounds >= MAX_TOOL_ROUNDS;
    const params: any = {
      model,
      max_tokens: MAX_OUTPUT_TOKENS,
      system,
      tools,
      ...(noMoreTools ? { tool_choice: { type: "none" } } : {}),
      messages: apiMessages,
      // krátké odpovědi z dodaných úryvků nepotřebují hluboké uvažování
      ...(modern ? { output_config: { effort: "low" as const } } : {}),
    };
    const response: any = modern
      ? await client.beta.messages.create({ ...params, betas: ["server-side-fallback-2026-07-01"], fallbacks: "default" })
      : await client.beta.messages.create(params);

    const u = usageCost(model, response.usage);
    await recordSpend(env, month, model, u.effIn, u.out);
    meta.inputTokens += u.rawIn;
    meta.outputTokens += u.out;
    meta.costMicro += u.micro;

    if (response.stop_reason === "refusal") return finish(REFUSAL_TEXT, true);

    const textOf = (): string =>
      (response.content as any[])
        .flatMap((b) => (b.type === "text" ? [b.text] : []))
        .join("")
        .trim();
    const uses = (response.content as any[]).filter((b) => b.type === "tool_use");
    if (!uses.length || noMoreTools) {
      const text = textOf();
      return finish(text || "PečkyBot teď nedokázal odpovědět. Zkuste to prosím znovu.");
    }
    // další kolo jen v rámci rozpočtu na dotaz (potřebuje ještě jedno volání modelu)
    if (meta.costMicro > QUESTION_COST_CAP_MICRO) {
      const text = textOf();
      return finish(text || GIVE_UP_TEXT, !text);
    }

    toolRounds++;
    const results = await Promise.all(
      uses.map(async (b) => {
        meta.tools.push(b.name);
        const r = await executeTool(b.name, b.input, toolCtx);
        return { type: "tool_result", tool_use_id: b.id, content: r.content, ...(r.isError ? { is_error: true } : {}) };
      }),
    );
    apiMessages.push({ role: "assistant", content: response.content }, { role: "user", content: results });
  }
}
