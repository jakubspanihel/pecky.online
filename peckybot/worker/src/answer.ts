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
import { isWeak, searchAll, type Hit, type Index, type Src } from "./search.ts";
import { MAX_TOOL_ROUNDS, TOOL_DEFS, executeTool, isArchivTyp, typFilter, type ToolContext } from "./tools.ts";

// ---------- index ----------

// Dva rejstříky: hlavní (vždy) a archiv starších jednání z úřední desky (líně, viz searchAll).
// Každý má vlastní cache rejstříku (modul-level), vlastní dávky textů a vlastní otisk `h`.
const BASE: Record<Src, string> = { main: "/peckybot", archiv: "/peckybot/archiv" };
const indexCache: Partial<Record<Src, { index: Index; at: number }>> = {};
const indexLoading: Partial<Record<Src, Promise<Index>>> = {};
const shardCache = new Map<string, { texts: string[]; at: number }>(); // klíč „main:3“ / „archiv:3“
// rejstřík se obnovuje často (nové jednání, přegenerování); dávky textů jsou vázané na otisk obsahu
const INDEX_TTL_MS = 5 * 60 * 1000;

async function fetchJson<T>(url: string, cacheTtl = 300): Promise<T> {
  const r = await fetch(url, { cf: { cacheTtl, cacheEverything: true } });
  if (!r.ok) throw new HttpError(502, "index", `Index ${url} vrátil ${r.status}`);
  return (await r.json()) as T;
}

async function getIndex(env: Env, src: Src = "main"): Promise<Index> {
  const c = indexCache[src];
  if (c && Date.now() - c.at < INDEX_TTL_MS) return c.index;
  return (indexLoading[src] ??= (async () => {
    try {
      const index = await fetchJson<Index>(
        // časový klíč po 5 minutách = nová položka v cache Cloudflare; GitHub Pages query ignoruje
        `${env.SITE_URL}${BASE[src]}/index.json?t=${Math.floor(Date.now() / INDEX_TTL_MS)}`,
      );
      indexCache[src] = { index, at: Date.now() };
      for (const key of [...shardCache.keys()]) if (key.startsWith(src + ":")) shardCache.delete(key); // nový rejstřík = nové číslování dávek
      return index;
    } finally {
      delete indexLoading[src];
    }
  })());
}

/** Texty úryvků podle `h.src` (každý rejstřík má své dávky a své lokální id). */
export async function getTexts(env: Env, indexes: Record<Src, Index | undefined>, hits: Hit[]): Promise<Map<Hit, string>> {
  const need = new Map<string, { src: Src; k: number; index: Index }>();
  for (const h of hits) {
    const src = h.src ?? "main";
    const index = indexes[src]!;
    const k = Math.floor(h.id / index.shard);
    need.set(`${src}:${k}`, { src, k, index });
  }
  await Promise.all(
    [...need].map(async ([key, { src, k, index }]) => {
      const hit = shardCache.get(key);
      if (hit && Date.now() - hit.at < INDEX_TTL_MS) return;
      const texts = await fetchJson<string[]>(
        `${env.SITE_URL}${BASE[src]}/chunks/${k}.json${index.h ? `?h=${index.h}` : ""}`,
        index.h ? 86400 : 300,
      );
      shardCache.set(key, { texts, at: Date.now() });
    }),
  );
  const out = new Map<Hit, string>();
  for (const h of hits) {
    const src = h.src ?? "main";
    const index = indexes[src]!;
    out.set(h, shardCache.get(`${src}:${Math.floor(h.id / index.shard)}`)?.texts[h.id % index.shard] ?? "");
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

// malé dokumenty (jedno jednání, jeden rok úřední desky): paměť Workeru, nejvýš 24 položek
const docCache = new Map<string, { data: unknown; at: number }>();
const DOC_CACHE_MAX = 24;

async function loadDoc(env: Env, index: Index, path: string): Promise<any> {
  if (!/^(jednani|uredni-deska)\/[a-z0-9-]{3,80}$/.test(path)) throw new Error("neplatná cesta dokumentu");
  const hit = docCache.get(path);
  if (hit && Date.now() - hit.at < INDEX_TTL_MS) return hit.data;
  const q = index.h ? `h=${index.h}` : `t=${Math.floor(Date.now() / INDEX_TTL_MS)}`;
  const data = await fetchJson<unknown>(`${env.SITE_URL}/peckybot/data/${path}.json?${q}`, index.h ? 86400 : 300);
  if (docCache.size >= DOC_CACHE_MAX) docCache.delete(docCache.keys().next().value!);
  docCache.set(path, { data, at: Date.now() });
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
  // archiv se načte jen na požádání (searchAll ho volá jen při dotazu do minulosti nebo slabé shodě)
  const indexes: Record<Src, Index | undefined> = { main: index, archiv: undefined };
  const getArchiv = async () => (indexes.archiv = await getIndex(env, "archiv"));
  const found0 = await searchAll(index, getArchiv, query, TOP_K, { context, today });
  // slabá shoda (nesmyslný nebo mimotematický dotaz): model nedostane náhodné úryvky
  const hits = isWeak(found0) ? [] : found0;
  const texts = await getTexts(env, indexes, hits);
  const chunkOf = (h: Hit) => indexes[h.src ?? "main"]!.chunks[h.id];
  const sources = hits.map((h, i) => ({
    n: i + 1,
    title: chunkOf(h).t,
    url: chunkOf(h).u,
    text: texts.get(h) ?? "",
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
    loadDoc: (path) => loadDoc(env, index, path),
    async searchText(dotaz, typ) {
      const re = typFilter(typ);
      const only = isArchivTyp(typ);
      const found = await searchAll(index, getArchiv, dotaz, re ? 60 : 6, { today, ...(only ? { archiv: "only" as const } : {}) });
      const sel = re ? found.filter((h) => re.test(chunkOf(h).t)).slice(0, 6) : found;
      const tx = await getTexts(env, indexes, sel);
      return sel.map((h) => ({ title: chunkOf(h).t, url: chunkOf(h).u, text: tx.get(h) ?? "" }));
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
