import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import worker, { type Env } from "../src/index.ts";

const root = new URL("../../../", import.meta.url);

class FakeKV {
  m = new Map<string, string>();
  async get(k: string) { return this.m.get(k) ?? null; }
  async put(k: string, v: string) { this.m.set(k, v); }
}

function env(over: Partial<Env> = {}): Env {
  return {
    ANTHROPIC_API_KEY: "test",
    BUDGET: new FakeKV() as unknown as KVNamespace,
    SITE_URL: "https://site.test",
    ALLOWED_ORIGINS: "https://dopecek.cz",
    MONTHLY_BUDGET_USD: "8",
    DAILY_PER_IP: "2",
    DAILY_GLOBAL: "100",
    ...over,
  };
}

let anthropicBodies: any[] = [];
globalThis.fetch = (async (input: any, init?: any) => {
  const url = typeof input === "string" ? input : input.url;
  if (url.startsWith("https://site.test/")) {
    const path = url.replace("https://site.test/", "");
    return new Response(readFileSync(new URL(path, root)), { headers: { "Content-Type": "application/json" } });
  }
  if (url.includes("/v1/messages")) {
    anthropicBodies.push(JSON.parse(init.body));
    return new Response(
      JSON.stringify({
        id: "msg_1", type: "message", role: "assistant", model: "claude-sonnet-5-5",
        content: [{ type: "text", text: "Stavba je zastavená kvůli pilotům [1]." }],
        stop_reason: "end_turn", stop_sequence: null,
        usage: { input_tokens: 5000, output_tokens: 400 },
      }),
      { headers: { "Content-Type": "application/json" } },
    );
  }
  throw new Error("neočekávané volání " + url);
}) as typeof fetch;

const post = (body: unknown, origin = "https://dopecek.cz") =>
  new Request("https://w.test/chat", { method: "POST", headers: { Origin: origin, "Content-Type": "application/json" }, body: JSON.stringify(body) });

test("odpověď se zdroji, útrata se zapíše", async () => {
  const e = env();
  const r = await worker.fetch(post({ messages: [{ role: "user", content: "Co je s tělocvičnou?" }] }), e);
  assert.equal(r.status, 200);
  const j: any = await r.json();
  assert.match(j.answer, /pilot/);
  assert.equal(j.sources.length, 1);
  assert.equal(j.sources[0].n, 1);
  assert.match(j.sources[0].url, /^\//);
  const body = anthropicBodies.at(-1);
  assert.equal(body.model, "claude-sonnet-5-5");
  assert.equal(body.output_config.effort, "low");
  assert.equal(body.fallbacks, "default");
  assert.match(body.messages.at(-1).content, /<zdroje>/);
  const spend = [...(e.BUDGET as unknown as FakeKV).m.entries()].find(([k]) => k.startsWith("spend:"));
  assert.equal(spend?.[1], String(5000 * 2 + 400 * 10));
});

test("cizí Origin je odmítnut", async () => {
  const r = await worker.fetch(post({ messages: [{ role: "user", content: "x" }] }, "https://evil.example"), env());
  assert.equal(r.status, 403);
});

test("limit na IP", async () => {
  const e = env();
  const q = { messages: [{ role: "user", content: "tělocvična" }] };
  assert.equal((await worker.fetch(post(q), e)).status, 200);
  assert.equal((await worker.fetch(post(q), e)).status, 200);
  const r = await worker.fetch(post(q), e);
  assert.equal(r.status, 429);
  assert.equal(((await r.json()) as any).code, "daily_ip");
});

test("vyčerpaný měsíční rozpočet", async () => {
  const e = env();
  const day = new Date().toLocaleDateString("sv-SE", { timeZone: "Europe/Prague" });
  await e.BUDGET.put(`spend:${day.slice(0, 7)}`, String(8_000_000));
  const r = await worker.fetch(post({ messages: [{ role: "user", content: "ahoj" }] }), e);
  assert.equal(r.status, 429);
  assert.equal(((await r.json()) as any).code, "budget");
});

test("neplatný vstup", async () => {
  const r = await worker.fetch(post({ messages: [{ role: "assistant", content: "ahoj" }] }), env());
  assert.equal(r.status, 400);
  const long = await worker.fetch(post({ messages: [{ role: "user", content: "a".repeat(601) }] }), env());
  assert.equal(long.status, 400);
});
