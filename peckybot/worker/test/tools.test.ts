import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { DOC_MAX_CHARS, executeTool, findOsoby, findOrgany, udUrl, type ToolContext } from "../src/tools.ts";
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
    loadDoc: async (p) => fx(p),
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

test("jednani: nejnovejsi s typem vrátí dvě nejnovější (i s jen pozvánkou), bez typu každý druh; „rada“ nechytí školskou radu", async () => {
  const r = await run("jednani", { typ: "rada", nejnovejsi: true }, mkCtx({ today: "2026-10-15" }));
  assert.deepEqual(r.json.jednani.map((j: any) => j.id), ["rada-2026-10-19", "rada-2026-10-12"]);
  assert.deepEqual(r.json.jednani[0].dostupne, ["pozvanka"]);
  assert.match(r.json.jednani[0].stav, /plánováno/);
  assert.equal(r.json.jednani[1].stav, undefined);
  assert.match(r.content, /cti_dokument/);
  const all = await run("jednani", { nejnovejsi: true });
  assert.deepEqual(all.json.jednani.map((j: any) => j.id), ["skolska-rada-2026-11-01", "rada-2026-10-19", "zastupitelstvo-2025-06-11"]);
  const sr = await run("jednani", { typ: "školská rada" });
  assert.equal(sr.json.celkem, 1);
});

test("cti_dokument: celé jednání s usneseními a hlasováním, zdroj /jednani/#id", async () => {
  const r = await run("cti_dokument", { id: "rada-2026-10-12" });
  assert.equal(r.isError, false);
  assert.equal(r.json.oznaceni, "RM 36/2026");
  assert.equal(r.json.body.length, 3);
  assert.equal(r.json.body[1].usneseni[0].hlasovani, "pro 5, proti 1, zdržel se 0");
  assert.equal(r.json.body[1].usneseni[0].cislo, "UR-323-36/26");
  assert.equal(typeof r.json.n, "number");
  const ctx = mkCtx();
  await run("cti_dokument", { id: "rada-2026-10-12" }, ctx);
  assert.deepEqual(ctx.cited[0], { title: "RM 36/2026 (12. 10. 2026) — program a usnesení", url: "/jednani/#rada-2026-10-12" });
});

test("cti_dokument: bod podrobně, neexistující bod a id, neplatné id", async () => {
  const b = await run("cti_dokument", { id: "rada-2026-10-12", bod: 3 });
  assert.equal(b.json.bod.n, 3);
  assert.equal(b.json.bod.zprava.length <= 900, true);
  assert.equal(b.json.bod.zprava.length > 500, true); // podrobně (celé jednání zkrátí na 350)
  assert.equal(b.json.body, undefined);
  const x = await run("cti_dokument", { id: "rada-2026-10-12", bod: 99 });
  assert.equal(x.isError, true);
  assert.match(x.content, /1, 2, 3/);
  const missing = await run("cti_dokument", { id: "rada-1999-01-01" }, mkCtx({ loadDoc: async () => { throw new Error("404"); } }));
  assert.equal(missing.isError, true);
  assert.match(missing.content, /nástrojem jednani/);
  for (const bad of ["../osoby", "Rada 1", "a/b", ""]) assert.equal((await run("cti_dokument", { id: bad })).isError, true);
});

test("cti_dokument: jen pozvánka nese poznámku a dostupne", async () => {
  const r = await run("cti_dokument", { id: "rada-2026-10-19" });
  assert.deepEqual(r.json.dostupne, ["pozvanka"]);
  assert.match(r.json.poznamka, /zápis a usnesení zatím nevyšly/);
  assert.match(r.json.stav, /plánováno/);
});

test("cti_dokument: velké jednání se zkrátí pod limit (≈ 5 000 tokenů) a ponese pokyn k detailu", async () => {
  const r = await run("cti_dokument", { id: "zastupitelstvo-2025-06-11" });
  assert.equal(r.isError, false);
  assert.ok(r.content.length <= DOC_MAX_CHARS + 500, String(r.content.length));
  assert.ok(r.json.body.length >= 1);
  assert.match(r.content, /cti_dokument\(id, bod\)|zkraceno/);
});

test("uredni_deska: filtr slov, rozsah a odkazy (číslo → slug z názvu, as4u)", async () => {
  const r = await run("uredni_deska", { od: "2026-01-01", do: "2026-12-31" });
  assert.equal(r.json.celkem, 3);
  assert.equal(r.json.dokumenty[0].vyveseno, "2026-10-09");
  const h = await run("uredni_deska", { hledej: "záměr", od: "2025-06-01", do: "2026-12-31" });
  assert.equal(h.json.celkem, 2);
  const ctx = mkCtx();
  await run("uredni_deska", { od: "2026-01-01", do: "2026-12-31" }, ctx);
  assert.equal(ctx.cited[0].url, "https://pecky.cz/default/report/491473_zapis-ze-zasedani-zastupitelstva-mesta-c-7-2026");
  assert.match(ctx.cited[2].url, /^https:\/\/pecky\.as4u\.cz\/.*detail_claim=123$/);
  assert.equal(udUrl("111_zamer-x", "Záměr"), "https://pecky.cz/default/report/111_zamer-x");
  assert.equal((await run("uredni_deska", { od: "2020-01-01", do: "2026-12-31" })).isError, true); // víc než 3 roky
  const none = await run("uredni_deska", { od: "2010-01-01", do: "2010-12-31" }, mkCtx({ loadDoc: async () => { throw new Error("404"); } }));
  assert.equal(none.json.celkem, 0);
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
    const n = url.split("/peckybot/data/")[1].split(".json")[0];
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
  assert.ok(bodies[0].tools.length === 9);
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

test("smyčka: poslední rada → jednani → cti_dokument, zdroj z dokumentu v odpovědi, cena v limitu", async () => {
  script = [
    toolUse("jednani", { typ: "rada", nejnovejsi: true }, "t1"),
    toolUse("cti_dokument", { id: "rada-2026-10-12" }, "t2"),
    text("Rada schválila pronájem ordinace logopedie [10]."),
  ];
  bodies = [];
  const e = env();
  const r = await answer(e, [{ role: "user", content: "Co se probíralo na poslední radě?" }], "2026-10");
  assert.deepEqual(r.meta.tools, ["jednani", "cti_dokument"]);
  assert.equal(bodies.length, 3);
  const doc = bodies[2].messages.at(-1).content[0];
  assert.equal(doc.tool_use_id, "t2");
  assert.match(doc.content, /UR-323-36\/26/);
  assert.ok(r.meta.costMicro < QUESTION_COST_CAP_MICRO);
  assert.equal(r.sources.length, 1);
  assert.equal(r.sources[0].url, "/jednani/#rada-2026-10-12");
  assert.match(bodies[0].system[0].text, /pozvanka/);
  assert.match(bodies[0].tools.find((t: any) => t.name === "jednani").description, /nejnovejsi/);
  assert.ok(bodies[0].tools.some((t: any) => t.name === "cti_dokument"));
});

test("smyčka: čtení dokumentu přidá nejvýš ≈ 0,02 USD (limit výsledku v tokenech)", async () => {
  const r = await executeTool("cti_dokument", { id: "zastupitelstvo-2025-06-11" }, mkCtx());
  const tokens = r.content.length / 2.3; // pesimistický odhad pro češtinu v JSONu
  assert.ok((tokens * 2) / 1e6 * 2 < 0.02, `${tokens} tokenů`); // 2 další volání × 2 USD/M
});

test("kalendar: prázdný rozsah vrátí výslovnou poznámku s rozsahem", async () => {
  const r = await run("kalendar", { od: "2031-01-01", do: "2031-01-07" }, mkCtx({ load: async () => ({ udalosti: [], serie: [] }) }));
  assert.equal(r.json.celkem, 0);
  assert.match(r.json.poznamka, /Žádné události v rozsahu 1\. 1\. 2031 – 7\. 1\. 2031/);
});

test("prompt: pravidla pro stav, kalendář, soukromí a zastaralé údaje", async () => {
  const { systemPrompt } = await import("../src/prompt.ts");
  const p = systemPrompt("15. 10. 2026");
  for (const re of [/cti_dokument/, /CELÉHO rozsahu/, /„Ano“ jen když/, /Soukromé osoby/, /nejnovější údaj/, /otevírací dobu/]) assert.match(p, re);
});
