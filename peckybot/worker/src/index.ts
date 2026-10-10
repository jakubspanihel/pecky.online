import Anthropic from "@anthropic-ai/sdk";
import { answer } from "./answer.ts";
import {
  HttpError,
  MAX_ASSISTANT_CHARS,
  MAX_MESSAGES,
  MAX_USER_CHARS,
  bump,
  pragueDate,
  type ChatMessage,
  type Env,
} from "./common.ts";
import {
  cacheGet,
  cacheKey,
  cachePut,
  isHedge,
  newId,
  purgeOld,
  PURGE_PROBABILITY,
  safeEqual,
  saveVote,
  writeLog,
} from "./log.ts";

export type { Env } from "./common.ts";

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

async function limitPerIp(env: Env, day: string, ip: string): Promise<void> {
  const perIp = await bump(env.BUDGET, `ip:${day}:${ip}`, 2 * 86400);
  if (perIp > Number(env.DAILY_PER_IP)) {
    throw new HttpError(
      429,
      "daily_ip",
      `Dnes jste využili ${env.DAILY_PER_IP} dotazů, což je denní limit na jednoho návštěvníka. Zkuste to prosím zítra.`,
    );
  }
}

/** Měsíční rozpočet a celodenní limit; dotaz z cache se tu nepočítá. */
async function limitGlobalAndBudget(env: Env, day: string): Promise<{ month: string }> {
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
  return { month };
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

/** V produkci běží na pozadí (ctx.waitUntil); bez ctx (testy) se počká. */
async function defer(ctx: ExecutionContext | undefined, p: Promise<unknown>): Promise<void> {
  if (ctx) ctx.waitUntil(p);
  else await p;
}

export default {
  async fetch(request: Request, env: Env, ctx?: ExecutionContext): Promise<Response> {
    const origin = request.headers.get("Origin") ?? "";
    const allowed = env.ALLOWED_ORIGINS.split(",").map((s) => s.trim());
    if (!allowed.includes(origin)) {
      return new Response("Forbidden", { status: 403 });
    }
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }
    const path = new URL(request.url).pathname;
    if (request.method !== "POST" || (path !== "/chat" && path !== "/feedback")) {
      return json({ error: "Nenalezeno.", code: "not_found" }, 404, origin);
    }

    if (path === "/feedback") {
      let body: unknown;
      try {
        body = await request.json();
      } catch {
        return json({ error: "Neplatný požadavek.", code: "bad_request" }, 400, origin);
      }
      const r = await saveVote(env.LOG, body);
      if (r === "ok") return json({ ok: true }, 200, origin);
      const map = {
        bad_request: [400, "Neplatné hodnocení."],
        not_found: [404, "Odpověď nebyla nalezena."],
        expired: [410, "Odpověď už nelze hodnotit."],
        unavailable: [503, "Hodnocení teď nelze uložit."],
      } as const;
      const [status, error] = map[r];
      return json({ error, code: r }, status, origin);
    }

    const started = Date.now();
    let query = "";
    let previous = 0;
    const day = pragueDate();
    const isEval = !!env.EVAL_TOKEN && safeEqual(request.headers.get("X-Eval-Token") ?? "", env.EVAL_TOKEN);
    try {
      let body: unknown;
      try {
        body = await request.json();
      } catch {
        throw new HttpError(400, "bad_request", "Neplatný požadavek.");
      }
      const messages = parseMessages(body);
      query = messages[messages.length - 1].content;
      previous = messages.length - 1;
      const ip = request.headers.get("CF-Connecting-IP") ?? "unknown";
      if (!isEval) await limitPerIp(env, day, ip);

      if (Math.random() < PURGE_PROBABILITY) await defer(ctx, purgeOld(env.LOG));

      // cache: jen první otázka konverzace, ne měřicí dotazy
      const cacheable = messages.length === 1 && !isEval && !!env.LOG;
      const key = cacheable ? await cacheKey(day, query) : "";
      if (cacheable) {
        const hit = await cacheGet(env.LOG, key);
        if (hit) {
          const id = newId();
          await defer(
            ctx,
            writeLog(env.LOG, {
              id, query, previous, day, ms: Date.now() - started, fromCache: true,
              result: { answer: hit.answer, sources: hit.sources },
            }),
          );
          return json({ answer: hit.answer, sources: hit.sources, id }, 200, origin);
        }
      }

      const { month } = await limitGlobalAndBudget(env, day);
      const { meta, ...result } = await answer(env, messages, month);
      const id = newId();
      const hedge = isHedge(result.answer);
      await defer(
        ctx,
        writeLog(env.LOG, {
          id, query, previous, day, ms: Date.now() - started, hedge, eval: isEval,
          result: { ...result, meta },
        }),
      );
      if (cacheable && !hedge) {
        await defer(ctx, cachePut(env.LOG, key, { answer: result.answer, sources: result.sources }));
      }
      // měřicí dotazy (platný X-Eval-Token) dostanou navíc použité nástroje a náklad
      const extra = isEval ? { nastroje: meta.tools, naklad_micro: meta.costMicro } : {};
      return json({ ...result, id, ...extra }, 200, origin);
    } catch (err) {
      if (err instanceof HttpError) {
        if (err.status >= 500 && query) {
          await defer(ctx, writeLog(env.LOG, { id: newId(), query, previous, day, ms: Date.now() - started, error: err.code, eval: isEval }));
        }
        return json({ error: err.message, code: err.code }, err.status, origin);
      }
      const upstream = err instanceof Anthropic.RateLimitError || err instanceof Anthropic.APIConnectionError;
      if (query) {
        await defer(
          ctx,
          writeLog(env.LOG, { id: newId(), query, previous, day, ms: Date.now() - started, error: upstream ? "upstream" : "internal", eval: isEval }),
        );
      }
      if (upstream) {
        return json({ error: "PečkyBot je momentálně přetížený. Zkuste to prosím za chvíli.", code: "upstream" }, 503, origin);
      }
      console.error("peckybot chyba:", err);
      return json({ error: "PečkyBot teď neodpovídá. Zkuste to prosím později.", code: "internal" }, 500, origin);
    }
  },
} satisfies ExportedHandler<Env>;
