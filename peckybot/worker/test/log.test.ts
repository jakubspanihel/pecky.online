import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import worker, { type Env } from "../src/index.ts";
import { isHedge, normalizeQuery, purgeOld, safeEqual, saveVote, scrubQuery } from "../src/log.ts";

const root = new URL("../../../", import.meta.url);

class FakeKV {
  m = new Map<string, string>();
  async get(k: string) { return this.m.get(k) ?? null; }
  async put(k: string, v: string) { this.m.set(k, v); }
}

/** Malé D1 jen pro SQL, které používá log.ts. */
class FakeD1 {
  dotazy = new Map<string, any>();
  hodnoceni = new Map<string, any>();
  cache = new Map<string, { ts: string; odpoved: string }>();
  fail = false;
  prepare(sql: string) {
    const self = this;
    return {
      bind(...a: any[]) {
        const run = async () => {
          if (self.fail) throw new Error("D1 down");
          if (sql.startsWith("INSERT INTO dotazy")) {
            const [id, ts, den, dotaz, predchozi, zdroje, nalezeno, nastroje, model, vi, vy, nak, zc, nevim, ms, chyba, ev] = a;
            self.dotazy.set(id, { id, ts, den, dotaz, predchozi, zdroje, nalezeno, nastroje, model, vi, vy, nak, z_cache: zc, nevim, ms, chyba, eval: ev });
          } else if (sql.startsWith("INSERT INTO hodnoceni")) {
            self.hodnoceni.set(a[0], { id: a[0], ts: a[1], hlas: a[2] });
          } else if (sql.startsWith("INSERT OR REPLACE INTO odpovedi_cache")) {
            self.cache.set(a[0], { ts: a[1], odpoved: a[2] });
          } else if (sql.startsWith("DELETE FROM hodnoceni")) {
            for (const [id, v] of self.dotazy) if (v.ts < a[0]) self.hodnoceni.delete(id);
          } else if (sql.startsWith("DELETE FROM dotazy")) {
            for (const [id, v] of self.dotazy) if (v.ts < a[0]) self.dotazy.delete(id);
          } else if (sql.startsWith("DELETE FROM odpovedi_cache")) {
            for (const [k, v] of self.cache) if (v.ts < a[0]) self.cache.delete(k);
          } else throw new Error("neznámé SQL " + sql);
          return {};
        };
        const first = async () => {
          if (self.fail) throw new Error("D1 down");
          if (sql.startsWith("SELECT ts FROM dotazy")) return self.dotazy.get(a[0]) ? { ts: self.dotazy.get(a[0]).ts } : null;
          if (sql.startsWith("SELECT odpoved FROM odpovedi_cache")) {
            const v = self.cache.get(a[0]);
            return v && v.ts > a[1] ? { odpoved: v.odpoved } : null;
          }
          throw new Error("neznámé SQL " + sql);
        };
        return { run, first };
      },
    };
  }
}

function env(over: Partial<Env> = {}): Env & { LOG: any } {
  return {
    ANTHROPIC_API_KEY: "test",
    BUDGET: new FakeKV() as unknown as KVNamespace,
    LOG: new FakeD1() as unknown as D1Database,
    SITE_URL: "https://site.test",
    ALLOWED_ORIGINS: "https://dopecek.cz",
    MONTHLY_BUDGET_USD: "8",
    DAILY_PER_IP: "2",
    DAILY_GLOBAL: "100",
    ...over,
  } as any;
}

let apiCalls = 0;
let answerText = "Stavba je zastavená kvůli pilotům [1].";
globalThis.fetch = (async (input: any) => {
  const url = typeof input === "string" ? input : input.url;
  if (url.startsWith("https://site.test/")) {
    return new Response(readFileSync(new URL(url.replace("https://site.test/", ""), root)), { headers: { "Content-Type": "application/json" } });
  }
  if (url.includes("/v1/messages")) {
    apiCalls++;
    return new Response(
      JSON.stringify({
        id: "msg_1", type: "message", role: "assistant", model: "claude-sonnet-5-5",
        content: [{ type: "text", text: answerText }],
        stop_reason: "end_turn", stop_sequence: null,
        usage: { input_tokens: 5000, output_tokens: 400 },
      }),
      { headers: { "Content-Type": "application/json" } },
    );
  }
  throw new Error("neočekávané volání " + url);
}) as typeof fetch;

const post = (body: unknown, headers: Record<string, string> = {}, path = "/chat") =>
  new Request("https://w.test" + path, {
    method: "POST",
    headers: { Origin: "https://dopecek.cz", "Content-Type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
const ask = (q: string) => ({ messages: [{ role: "user", content: q }] });

test("scrubQuery maskuje e-mail, telefon a dlouhá čísla", () => {
  assert.equal(scrubQuery("pište na jan.novak@seznam.cz prosím"), "pište na [e-mail] prosím");
  assert.equal(scrubQuery("volejte +420 321 785 050"), "volejte [telefon]");
  assert.equal(scrubQuery("tel 606 609 572"), "tel [telefon]");
  assert.equal(scrubQuery("rodné číslo 1234567890123"), "rodné číslo [číslo]");
  assert.equal(scrubQuery("ZM 6/2026 dne 3. 9. 2026"), "ZM 6/2026 dne 3. 9. 2026");
  assert.equal(scrubQuery("a".repeat(500)).length, 300);
});

test("normalizeQuery a detekce „nevím“", () => {
  assert.equal(normalizeQuery("  Kdo JE starosta?! "), "kdo je starosta");
  assert.ok(isHedge("Bohužel to nemám ve zdrojích."));
  assert.ok(isHedge("Tuto informaci zdroje neuvádějí."));
  assert.ok(isHedge("Odpověď nelze zjistit z úryvků."));
  assert.ok(!isHedge("Starostou je Milan Paluska [1]."));
});

test("safeEqual", () => {
  assert.ok(safeEqual("abc", "abc"));
  assert.ok(!safeEqual("abc", "abd"));
  assert.ok(!safeEqual("abc", "abcd"));
});

test("odpověď se zapíše do D1 a vrátí id", async () => {
  const e = env();
  const j: any = await (await worker.fetch(post(ask("Co je s tělocvičnou? volejte 606 609 572")), e)).json();
  assert.match(j.id, /^[a-z0-9]{12}$/);
  const row = e.LOG.dotazy.get(j.id);
  assert.equal(row.dotaz, "Co je s tělocvičnou? volejte [telefon]");
  assert.equal(row.z_cache, 0);
  assert.equal(row.nevim, 0);
  assert.equal(row.eval, 0);
  assert.equal(row.nak, 5000 * 2 + 400 * 10);
  assert.ok(!JSON.stringify(row).includes("CF-Connecting"));
});

test("selhání D1 neshodí odpověď", async () => {
  const e = env();
  e.LOG.fail = true;
  const r = await worker.fetch(post(ask("tělocvična D1 selhává")), e);
  assert.equal(r.status, 200);
  assert.match(((await r.json()) as any).answer, /pilot/);
});

test("bez vazby LOG Worker odpovídá", async () => {
  const e = env({ LOG: undefined });
  assert.equal((await worker.fetch(post(ask("tělocvična bez logu")), e)).status, 200);
});

test("cache: zásah, druhý dotaz nestojí nic, počítá se do limitu na IP", async () => {
  const e = env({ DAILY_PER_IP: "2" });
  const before = apiCalls;
  const a: any = await (await worker.fetch(post(ask("Kdo je starosta?")), e)).json();
  const b: any = await (await worker.fetch(post(ask("  kdo je STAROSTA ")), e)).json();
  assert.equal(apiCalls, before + 1);
  assert.equal(b.answer, a.answer);
  assert.notEqual(b.id, a.id);
  assert.equal(e.LOG.dotazy.get(b.id).z_cache, 1);
  assert.equal(e.LOG.dotazy.get(b.id).nak, 0);
  const kv = (e.BUDGET as unknown as FakeKV).m;
  const day = [...kv.keys()].find((k) => k.startsWith("day:"))!;
  assert.equal(kv.get(day), "1"); // globální počítadlo jen u skutečného volání
  assert.equal((await worker.fetch(post(ask("Kdo je starosta?")), e)).status, 429); // třetí dotaz na IP
});

test("cache: platnost 6 hodin a vícekolová konverzace se necachuje", async () => {
  const e = env({ DAILY_PER_IP: "50" });
  await worker.fetch(post(ask("kolik stojí tělocvična")), e);
  for (const v of e.LOG.cache.values()) v.ts = new Date(Date.now() - 7 * 3600_000).toISOString();
  const before = apiCalls;
  await worker.fetch(post(ask("kolik stojí tělocvična")), e);
  assert.equal(apiCalls, before + 1);
  const size = e.LOG.cache.size;
  await worker.fetch(
    post({ messages: [{ role: "user", content: "a" }, { role: "assistant", content: "b" }, { role: "user", content: "a co dál" }] }),
    e,
  );
  assert.equal(e.LOG.cache.size, size);
});

test("cache: „nevím“ odpověď se neukládá", async () => {
  const e = env({ DAILY_PER_IP: "50" });
  answerText = "To bohužel nemám ve zdrojích.";
  try {
    const j: any = await (await worker.fetch(post(ask("něco neznámého zcela")), e)).json();
    assert.equal(e.LOG.dotazy.get(j.id).nevim, 1);
    assert.equal(e.LOG.cache.size, 0);
  } finally {
    answerText = "Stavba je zastavená kvůli pilotům [1].";
  }
});

test("EVAL_TOKEN obejde limit na IP i cache a řádek se označí", async () => {
  const e = env({ DAILY_PER_IP: "1", EVAL_TOKEN: "tajne" });
  const h = { "X-Eval-Token": "tajne" };
  const before = apiCalls;
  const ids: string[] = [];
  for (let i = 0; i < 3; i++) {
    const r = await worker.fetch(post(ask("stejný měřicí dotaz"), h), e);
    assert.equal(r.status, 200);
    ids.push(((await r.json()) as any).id);
  }
  assert.equal(apiCalls, before + 3);
  assert.ok(ids.every((id) => e.LOG.dotazy.get(id).eval === 1));
  assert.equal(e.LOG.cache.size, 0);
  // špatný token = běžný návštěvník
  const bad = { "X-Eval-Token": "spatne" };
  assert.equal((await worker.fetch(post(ask("x1"), bad), e)).status, 200);
  assert.equal((await worker.fetch(post(ask("x2"), bad), e)).status, 429);
  // měsíční rozpočet platí i pro eval
  const day = new Date().toLocaleDateString("sv-SE", { timeZone: "Europe/Prague" });
  await e.BUDGET.put(`spend:${day.slice(0, 7)}`, String(8_000_000));
  assert.equal((await worker.fetch(post(ask("x3"), h), e)).status, 429);
});

test("odmítnuté požadavky se nezapisují", async () => {
  const e = env({ DAILY_PER_IP: "0" });
  assert.equal((await worker.fetch(post(ask("zamítnuto limitem")), e)).status, 429);
  assert.equal((await worker.fetch(post({ messages: [] }), e)).status, 400);
  assert.equal(e.LOG.dotazy.size, 0);
});

test("hodnocení: validace, upsert, stáří", async () => {
  const e = env({ DAILY_PER_IP: "50" });
  const j: any = await (await worker.fetch(post(ask("tělocvična hodnocení")), e)).json();
  const fb = (b: unknown) => worker.fetch(post(b, {}, "/feedback"), e);
  assert.equal((await fb({ id: j.id, hlas: 2 })).status, 400);
  assert.equal((await fb({ id: "x", hlas: 1 })).status, 400);
  assert.equal((await fb({ id: "aaaaaaaaaaaa", hlas: 1 })).status, 404);
  assert.equal((await fb({ id: j.id, hlas: 1 })).status, 200);
  assert.equal((await fb({ id: j.id, hlas: -1 })).status, 200);
  assert.equal(e.LOG.hodnoceni.size, 1);
  assert.equal(e.LOG.hodnoceni.get(j.id).hlas, -1);
  assert.equal(await saveVote(e.LOG, { id: j.id, hlas: 1 }, Date.now() + 25 * 3600_000), "expired");
  assert.equal(await saveVote(undefined, { id: j.id, hlas: 1 }), "unavailable");
  const evil = new Request("https://w.test/feedback", { method: "POST", headers: { Origin: "https://evil.example" }, body: "{}" });
  assert.equal((await worker.fetch(evil, e)).status, 403);
});

test("úklid maže záznamy starší než 90 dní", async () => {
  const e = env();
  e.LOG.dotazy.set("old", { id: "old", ts: new Date(Date.now() - 91 * 86400_000).toISOString() });
  e.LOG.dotazy.set("new", { id: "new", ts: new Date().toISOString() });
  e.LOG.hodnoceni.set("old", { id: "old", hlas: 1 });
  await purgeOld(e.LOG);
  assert.deepEqual([...e.LOG.dotazy.keys()], ["new"]);
  assert.equal(e.LOG.hodnoceni.size, 0);
});
