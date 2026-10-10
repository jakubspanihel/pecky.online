import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { executeTool, findOsoby, findOrgany, type ToolContext } from "../src/tools.ts";
import { answer, QUESTION_COST_CAP_MICRO } from "../src/answer.ts";
import type { Env } from "../src/common.ts";

const fx = (n: string) => JSON.parse(readFileSync(new URL(`./fixtures/${n}.json`, import.meta.url), "utf8"));
const root = new URL("../../../", import.meta.url);

function mkCtx(over: Partial<ToolContext> = {}): ToolContext & { cited: { title: string; url: string }[] } {
  const cited: { title: string; url: string }[] = [];
  return {
    today: "2026-10-10",
    cited,
    load: async (f) => fx(f),
    searchText: async () => [{ title: "Web — x", url: "/x/", text: "text" }],
    cite: (title, url) => {
      const i = cited.findIndex((c) => c.title === title && c.url === url);
      if (i >= 0) return i + 9;
      cited.push({ title, url });
      return cited.length + 8;
    },
    ...over,
  };
}
const run = async (name: string, input: unknown, ctx = mkCtx()) => {
  const r = await executeTool(name, input, ctx);
  return { ...r, json: r.isError ? null : JSON.parse(r.content) };
};

// ---------- vykonavatele ----------

test("osoba: fuzzy bez diakritiky, skloňování, funkce", () => {
  const o = fx("osoby").osoby;
  assert.equal(findOsoby(o, "paluska")[0].id, "paluska");
  assert.equal(findOsoby(o, "Fejfara")[0].id, "fejfar"); // 2. pád
  assert.equal(findOsoby(o, "mistostarosta")[0].id, "fejfar");
  assert.equal(findOsoby(o, "Cizek")[0].id, "cizek");
  assert.equal(findOsoby(o, "starosta")[0].id, "paluska"); // přesná funkce před „místostarosta“
  assert.equal(findOsoby(o, "Milan Fejfar").length, 0);
  assert.equal(findOsoby(o, "").length, 0);
});

test("osoba: výstup má kontakty a číslo zdroje", async () => {
  const r = await run("osoba", { jmeno: "místostarosta" });
  assert.equal(r.json.osoby[0].jmeno, "Jan Fejfar");
  assert.equal(r.json.osoby[0].email, "fejfar@pecky.test");
  assert.equal(r.json.osoby[0].telefon, undefined); // prázdné pole se vynechá
  assert.ok(r.json.osoby[0].n >= 9);
});

test("slozeni: synonyma a pořadí", () => {
  const o = fx("slozeni").organy;
  assert.equal(findOrgany(o, "rada")[0].id, "rada-soucasna");
  assert.equal(findOrgany(o, "radní")[0].id, "rada-soucasna");
  assert.equal(findOrgany(o, "zastupitelé")[0].id, "zastupitelstvo");
  assert.equal(findOrgany(o, "finanční výbor")[0].id, "financni-vybor");
  assert.equal(findOrgany(o, "kontrolní výbor")[0].id, "kontrolni-vybor");
  assert.equal(findOrgany(o, "školská rada")[0].id, "skolska-rada");
  assert.equal(findOrgany(o, "místostarosta")[0].id, "starostove");
  assert.equal(findOrgany(o, "starostové")[0].id, "starostove");
  assert.equal(findOrgany(o, "starostove")[0].id, "starostove"); // přesné id
  assert.equal(findOrgany(o, "hasiči").length, 0);
});

test("slozeni: výsledek obsahuje členy", async () => {
  const r = await run("slozeni", { organ: "rada města" });
  assert.match(JSON.stringify(r.json), /Paluska/);
  assert.equal(r.json.organy[0].aktualni, true);
});

test("kalendar: rozsah, víkend, vícedenní akce, série", async () => {
  const r = await run("kalendar", { od: "2026-10-10", do: "2026-10-11" }); // sobota+neděle
  const names = r.json.udalosti.map((e: any) => e.nazev);
  assert.deepEqual(names, ["Vícedenní bazar", "Výstava hub", "Pouťový průvod"]); // bazar běží od 3. do 12.
  assert.equal(r.json.celkem, 3);
  assert.equal(r.json.udalosti[1].datum_do, "2026-10-11");
  assert.equal(r.json.serie.length, 1);
  assert.equal(r.json.serie[0].nazev, "Cvičení pro seniory");
  const n = await run("kalendar", { od: "2026-10-13", do: "2026-10-19" });
  assert.equal(n.json.celkem, 0);
  const h = await run("kalendar", { od: "2026-10-01", do: "2026-10-31", hledej: "knihovna" });
  assert.deepEqual(h.json.udalosti.map((e: any) => e.nazev), ["Výstava hub", "Přednáška"]);
  const swapped = await run("kalendar", { od: "2026-10-11", do: "2026-10-10" });
  assert.equal(swapped.json.celkem, 3);
});

test("kalendar: max 25 akcí", async () => {
  const udalosti = Array.from({ length: 40 }, (_, i) => ({ datum: "2026-11-01", nazev: `Akce ${i}`, url: "/kalendar/" }));
  const r = await run("kalendar", { od: "2026-11-01", do: "2026-11-01" }, mkCtx({ load: async () => ({ udalosti, serie: [] }) }));
  assert.equal(r.json.udalosti.length, 25);
  assert.equal(r.json.celkem, 40);
});

test("pocet_bodu: celkem, jednání, po letech, příklady", async () => {
  const r = await run("pocet_bodu", { klicova_slova: "tělocvična" });
  assert.equal(r.json.pocet_bodu, 5);
  assert.equal(r.json.pocet_jednani_s_shodou, 4);
  assert.deepEqual(r.json.po_letech, { "2024": 4, "2025": 1 });
  assert.equal(r.json.priklady.length, 5);
  assert.match(r.content, /BODY PROGRAMU/);
  const z = await run("pocet_bodu", { klicova_slova: "tělocvična", typ: "zastupitelstvo", od: "2025-01-01" });
  assert.equal(z.json.pocet_bodu, 0);
  const z24 = await run("pocet_bodu", { klicova_slova: "tělocvična", typ: "zastupitelstvo", do: "2024-12-31" });
  assert.equal(z24.json.pocet_bodu, 2);
  const two = await run("pocet_bodu", { klicova_slova: "piloty tělocvičny" });
  assert.equal(two.json.pocet_bodu, 1);
});

test("jednani: výpis od nejnovějšího, filtr typu a slov", async () => {
  const r = await run("jednani", { typ: "zastupitelstvo" });
  assert.deepEqual(r.json.jednani.map((j: any) => j.oznaceni), ["ZM 3/2025", "ZM 2/2024", "ZM 1/2024"]);
  assert.equal(r.json.jednani[0].bodu, 1);
  const y = await run("jednani", { typ: "zastupitelstvo", od: "2024-01-01", do: "2024-12-31" });
  assert.equal(y.json.celkem, 2);
  const h = await run("jednani", { hledej: "piloty" });
  assert.equal(h.json.jednani[0].oznaceni, "RM 3/2025");
  const v = await run("jednani", { typ: "finanční výbor" });
  assert.equal(v.json.celkem, 1);
});

test("hledej_text: předá dotaz a typ", async () => {
  let seen: any[] = [];
  const r = await run("hledej_text", { dotaz: "knihovna", typ: "Organizace" }, mkCtx({
    searchText: async (...a) => { seen = a; return [{ title: "Organizace — Knihovna", url: "/lide/", text: "Otevřeno". repeat(1) }]; },
  }));
  assert.deepEqual(seen, ["knihovna", "Organizace"]);
  assert.equal(r.json.vysledky[0].titulek, "Organizace — Knihovna");
});

test("chyby: neplatné datum, chybějící parametr, výjimka, neznámý nástroj", async () => {
  assert.equal((await run("kalendar", { od: "zítra", do: "2026-10-11" })).isError, true);
  assert.equal((await run("osoba", {})).isError, true);
  assert.equal((await run("osoba", { jmeno: "x" }, mkCtx({ load: async () => { throw new Error("boom"); } }))).isError, true);
  const u = await run("smaz_vse", {});
  assert.equal(u.isError, true);
  assert.match(u.content, /Neznámý/);
  assert.equal((await run("toString", {})).isError, true); // prototypové názvy nejsou nástroje
});

test("výsledek je omezen na rozumnou velikost", async () => {
  const osoby = Array.from({ length: 50 }, (_, i) => ({ jmeno: "Test", prijmeni: `Osoba${i}`, funkce: ["x"], bio: "b".repeat(2000) }));
  const r = await executeTool("osoba", { jmeno: "test" }, mkCtx({ load: async () => ({ osoby }) }));
  assert.ok(r.content.length <= 6100);
});

// ---------- smyčka agenta (mock Anthropic) ----------

class FakeKV {
  m = new Map<string, string>();
  async get(k: string) { return this.m.get(k) ?? null; }
  async put(k: string, v: string) { this.m.set(k, v); }
}
const env = (): Env => ({
  ANTHROPIC_API_KEY: "test", BUDGET: new FakeKV() as unknown as KVNamespace, SITE_URL: "https://site.test",
  ALLOWED_ORIGINS: "x", MONTHLY_BUDGET_USD: "8", DAILY_PER_IP: "9", DAILY_GLOBAL: "99",
});

let script: any[] = [];
let bodies: any[] = [];
globalThis.fetch = (async (input: any, init?: any) => {
  const url = typeof input === "string" ? input : input.url;
  if (url.startsWith("https://site.test/peckybot/data/")) {
    const n = url.split("/").pop()!.split(".json")[0];
    return new Response(readFileSync(new URL(`./fixtures/${n}.json`, import.meta.url)));
  }
  if (url.startsWith("https://site.test/")) {
    return new Response(readFileSync(new URL(url.replace("https://site.test/", "").split("?")[0], root)));
  }
  if (url.includes("/v1/messages")) {
    bodies.push(JSON.parse(init.body));
    const r = script.shift();
    if (!r) throw new Error("skript modelu došel");
    return new Response(JSON.stringify({
      id: "m", type: "message", role: "assistant", model: "claude-sonnet-5-5", stop_sequence: null,
      stop_reason: "end_turn", usage: { input_tokens: 1000, output_tokens: 100 }, ...r,
    }), { headers: { "Content-Type": "application/json" } });
  }
  throw new Error("neočekávané volání " + url);
}) as typeof fetch;

const text = (t: string, extra: any = {}) => ({ content: [{ type: "text", text: t }], ...extra });
const toolUse = (name: string, input: any, id = "tu1", extra: any = {}) => ({
  content: [{ type: "tool_use", id, name, input }], stop_reason: "tool_use", ...extra,
});
const Q = [{ role: "user" as const, content: "Kdo je místostarosta?" }];
const spendOf = (e: Env) => Number((e.BUDGET as unknown as FakeKV).m.get([...(e.BUDGET as unknown as FakeKV).m.keys()].find((k) => k.startsWith("spend:"))!));

test("smyčka: bez nástrojů = jedno volání, meta", async () => {
  script = [text("Odpověď [1].")]; bodies = [];
  const e = env();
  const r = await answer(e, Q, "2026-10");
  assert.equal(bodies.length, 1);
  assert.deepEqual(r.meta.tools, []);
  assert.equal(r.meta.inputTokens, 1000);
  assert.equal(r.meta.costMicro, 1000 * 2 + 100 * 10);
  assert.equal(r.meta.retrieved.length, 8);
  assert.equal(r.sources.length, 1);
  assert.equal(spendOf(e), r.meta.costMicro);
  assert.ok(bodies[0].tools.length === 6);
  assert.deepEqual(bodies[0].system[0].cache_control, { type: "ephemeral" });
  assert.equal(bodies[0].tool_choice, undefined);
});

test("smyčka: jeden nástroj, zdroj z nástroje se cituje číslem za úvodními", async () => {
  script = [toolUse("osoba", { jmeno: "místostarosta" }), text("Místostarosta je Jan Fejfar [9].")]; bodies = [];
  const e = env();
  const r = await answer(e, Q, "2026-10");
  assert.equal(bodies.length, 2);
  assert.deepEqual(r.meta.tools, ["osoba"]);
  assert.equal(r.meta.inputTokens, 2000);
  assert.equal(r.meta.costMicro, 2 * (1000 * 2 + 100 * 10));
  assert.equal(spendOf(e), r.meta.costMicro); // zapsáno za obě volání
  assert.deepEqual(r.sources, [{ n: 9, title: "Lidé — Jan Fejfar", url: "/lide/" }]);
  const second = bodies[1].messages.at(-1);
  assert.equal(second.role, "user");
  assert.equal(second.content[0].type, "tool_result");
  assert.equal(second.content[0].tool_use_id, "tu1");
  assert.match(second.content[0].content, /"n":9/);
});

test("smyčka: strop 3 kola, čtvrté volání bez nástrojů", async () => {
  script = [toolUse("osoba", { jmeno: "a" }, "1"), toolUse("osoba", { jmeno: "b" }, "2"), toolUse("osoba", { jmeno: "c" }, "3"), text("Hotovo.")];
  bodies = [];
  const r = await answer(env(), Q, "2026-10");
  assert.equal(bodies.length, 4);
  assert.deepEqual(bodies[3].tool_choice, { type: "none" });
  assert.equal(r.meta.tools.length, 3);
  assert.equal(r.answer, "Hotovo.");
});

test("smyčka: model chce nástroj i po stropu → vezme se jeho text, jinak hláška", async () => {
  script = [toolUse("osoba", { jmeno: "a" }, "1"), toolUse("osoba", { jmeno: "b" }, "2"), toolUse("osoba", { jmeno: "c" }, "3"), toolUse("osoba", { jmeno: "d" }, "4")];
  bodies = [];
  const r = await answer(env(), Q, "2026-10");
  assert.equal(bodies.length, 4);
  assert.equal(r.meta.tools.length, 3);
  assert.match(r.answer, /nedokázal/);
});

test("smyčka: cenový strop zastaví další kola, útrata se přesto zapíše", async () => {
  const big = { usage: { input_tokens: 30_000, output_tokens: 100 } }; // 0,061 USD
  script = [toolUse("osoba", { jmeno: "a" }, "1", big), text("nemělo by se zavolat")];
  bodies = [];
  const e = env();
  const r = await answer(e, Q, "2026-10");
  assert.equal(bodies.length, 1);
  assert.ok(r.meta.costMicro > QUESTION_COST_CAP_MICRO);
  assert.deepEqual(r.meta.tools, []);
  assert.match(r.answer, /nedokázal/);
  assert.equal(r.sources.length, 0);
  assert.equal(spendOf(e), r.meta.costMicro);
});

test("smyčka: chyba nástroje a neznámý nástroj se vrátí modelu jako is_error", async () => {
  script = [toolUse("kalendar", { od: "zítra", do: "x" }, "a"), toolUse("neexistuje", {}, "b"), text("Nepodařilo se ověřit.")];
  bodies = [];
  const r = await answer(env(), Q, "2026-10");
  assert.equal(r.answer, "Nepodařilo se ověřit.");
  assert.equal(bodies[1].messages.at(-1).content[0].is_error, true);
  assert.equal(bodies[2].messages.at(-1).content[0].is_error, true);
  assert.deepEqual(r.meta.tools, ["kalendar", "neexistuje"]);
});

test("smyčka: souběžná volání nástrojů v jednom kole", async () => {
  script = [
    { content: [
      { type: "tool_use", id: "a", name: "slozeni", input: { organ: "rada" } },
      { type: "tool_use", id: "b", name: "pocet_bodu", input: { klicova_slova: "tělocvična" } },
    ], stop_reason: "tool_use" },
    text("Ok."),
  ];
  bodies = [];
  const r = await answer(env(), Q, "2026-10");
  assert.deepEqual(r.meta.tools, ["slozeni", "pocet_bodu"]);
  assert.equal(bodies[1].messages.at(-1).content.length, 2);
});

test("smyčka: odmítnutí modelem", async () => {
  script = [{ content: [], stop_reason: "refusal" }]; bodies = [];
  const e = env();
  const r = await answer(e, Q, "2026-10");
  assert.match(r.answer, /nemůže/);
  assert.deepEqual(r.sources, []);
  assert.ok(spendOf(e) > 0);
});

test("smyčka: cache tokeny se počítají vážené, ale meta sečte všechny vstupy", async () => {
  script = [text("A [1].", { usage: { input_tokens: 100, cache_creation_input_tokens: 1000, cache_read_input_tokens: 2000, output_tokens: 0 } })];
  bodies = [];
  const e = env();
  const r = await answer(e, Q, "2026-10");
  assert.equal(r.meta.inputTokens, 3100);
  assert.equal(r.meta.costMicro, Math.round((100 + 1250 + 200) * 2));
  assert.equal(spendOf(e), r.meta.costMicro);
});
