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
