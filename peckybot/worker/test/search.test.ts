import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { search, tokenize, detectIntent, type Index } from "../src/search.ts";

const index: Index = JSON.parse(readFileSync(new URL("../../index.json", import.meta.url), "utf8"));

test("tokenize: bez diakritiky, zkrácení na 6 znaků, bez stopslov", () => {
  assert.deepEqual(tokenize("Dostavba učeben a tělocvičny v ZŠ Pečky"), ["dostav", "uceben", "telocv", "zs".length >= 3 ? "zs" : ""].filter(Boolean).slice(0, 3));
});

test("tokenize je shodná s Pythonem (scripts/build_peckybot_index.py)", () => {
  const samples = ["Rekonstrukce místních komunikací a vodovodní řad v části Bačov", "Piloty tělocvična — statické zajištění", "Zastupitelé: Paluska, Hubená"];
  const py = execFileSync(
    "python3",
    ["-c", "import sys,json;sys.path.insert(0,'../../scripts');from build_peckybot_index import tokenize;print(json.dumps([tokenize(s) for s in json.loads(sys.argv[1])]))", JSON.stringify(samples)],
    { cwd: new URL("..", import.meta.url).pathname },
  ).toString();
  assert.deepEqual(samples.map(tokenize), JSON.parse(py));
});

test("vyhledávání: tělocvična vrátí úryvky o tělocvičně", () => {
  const hits = search(index, "Co je nového s tělocvičnou a piloty?", 8);
  assert.ok(hits.length > 0);
  const text = hits.map((h) => index.chunks[h.id].t).join(" | ").toLowerCase();
  assert.match(text, /tělocvi|telocvi|dostavba/);
});

test("vyhledávání: neznámý dotaz nevrátí nic", () => {
  assert.equal(search(index, "xqzvwk", 8).length, 0);
});

test("vyhledávání: telefon na starostu vrátí kontakt osoby mezi prvními zdroji", () => {
  const hits = search(index, "telefonní číslo na starostu", 8);
  assert.equal(index.chunks[hits[0].id].t, "Lidé — Milan Paluska");
});

const mini: Index = {
  v: 1,
  shard: 100,
  chunks: [
    { u: "/jednani/#rada-2026-04-13", t: "RM 14/2026 — Schválení programu" },
    { u: "/jednani/#rada-2026-05-04", t: "RM 17/2026 — Schválení programu" },
    { u: "/kalendar/", t: "Kalendář — Koncert v KD" },
    { u: "/jednani/#zastupitelstvo-2026-08-26", t: "ZM 5/2026 — Pozemek u školy" },
  ],
  post: {
    progra: [0, 1, 1, 1, 2, 1],
    koncer: [2, 1],
    pozeme: [3, 1],
    parcel: [3, 1],
    schval: [0, 1, 1, 1],
  },
};

test("synonyma: dotaz „parcela“ najde úryvek s „pozemek“ (nižší váha než přesná shoda)", () => {
  const hits = search(mini, "parcela", 4);
  assert.equal(hits[0].id, 3);
  const exact = search(mini, "pozemek parcela", 4);
  assert.ok(exact[0].score > hits[0].score);
});

test("prefix: tvar bez přesné shody najde delší klíč", () => {
  const hits = search(mini, "koncertní", 4); // koncer je i přesná; zkus prefix přes „progr“
  assert.equal(hits[0].id, 2);
  assert.equal(search(mini, "progr", 4).length, 3);
});

test("detectIntent: odkazy na jednání, data a záměry", () => {
  assert.deepEqual(detectIntent("co bylo na RM 43/2022?").refs, ["RM 43/2022"]);
  assert.deepEqual(detectIntent("ZM 5/2026").refs, ["ZM 5/2026"]);
  assert.deepEqual(detectIntent("usnesení UR-288-32/26").refs, ["RM 32/2026"]);
  assert.deepEqual(detectIntent("jednání 26. 8. 2026").dates, ["2026-08-26"]);
  assert.ok(detectIntent("kdy je koncert").calendar);
  assert.ok(detectIntent("telefon na úřad").contact);
  assert.ok(detectIntent("kdo je starosta").who);
});

test("boost: číslo jednání zvedne úryvky téhož jednání, ostatní nezahodí", () => {
  const hits = search(mini, "schválení RM 17/2026", 4);
  assert.equal(hits[0].id, 1);
  assert.ok(hits.length >= 2);
});

test("boost: datum v dotazu zvedne jednání z toho dne", () => {
  const hits = search(mini, "pozemek program 26. 8. 2026", 4);
  assert.equal(hits[0].id, 3);
});

test("boost: kalendářový záměr zvedne úryvky „Kalendář“", () => {
  const hits = search(mini, "kdy je program", 4);
  assert.equal(hits[0].id, 2);
});

test("kontext: předchozí otázka má nižší váhu než aktuální", () => {
  const hits = search(mini, "pozemek", 4, { context: "koncert" });
  assert.equal(hits[0].id, 3);
  assert.ok(hits.some((h) => h.id === 2));
});

test("diverzita: nikdy nevrací méně výsledků kvůli limitu na odkaz", () => {
  const big: Index = {
    v: 1,
    shard: 100,
    chunks: Array.from({ length: 10 }, (_, i) => ({ u: i < 8 ? "/a/" : "/b/", t: `X ${i}` })),
    post: { tema: Array.from({ length: 10 }, (_, i) => [i, 1 + (i < 8 ? 0 : 3)]).flat() },
  };
  const hits = search(big, "tema", 8, { perUrlCap: 2 });
  assert.equal(hits.length, 8);
  assert.ok(hits.slice(0, 2).every((h) => big.chunks[h.id].u === "/b/"));
});

test("CPU: hledání nad celým indexem je řádově do milisekund", () => {
  const qs = ["Kdo je místostarosta?", "kdy je příští akce", "prodej pozemku u hřiště", "ZM 5/2026 usnesení"];
  search(index, qs[0], 8); // zahřátí (prefixová mapa)
  const t = performance.now();
  for (let i = 0; i < 200; i++) search(index, qs[i % qs.length], 8);
  assert.ok((performance.now() - t) / 200 < 5);
});

test("relativeDates: dnes, zítra, víkend, týden vůči zadanému datu (st 2026-10-07)", async () => {
  const { relativeDates } = await import("../src/search.ts");
  assert.deepEqual(relativeDates("co je zitra", "2026-10-07"), ["2026-10-08"]);
  assert.deepEqual(relativeDates("tento vikend", "2026-10-07"), ["2026-10-10", "2026-10-11"]);
  assert.deepEqual(relativeDates("tento tyden", "2026-10-07"), ["2026-10-07", "2026-10-08", "2026-10-09", "2026-10-10", "2026-10-11"]);
  assert.deepEqual(relativeDates("pristi tyden", "2026-10-07").length, 7);
});

test("boost: kalendářová akce z dnešního data se zvedne; dotaz na organizaci boostuje Organizace, ne Lidé", () => {
  const cal: Index = {
    v: 1, shard: 100,
    chunks: [
      { u: "/kalendar/", t: "Kalendář — Koncert A (3. 10. 2026)" },
      { u: "/kalendar/", t: "Kalendář — Koncert B (8. 10. 2026)" },
      { u: "/lide/", t: "Lidé — Jana Knihovníková" },
      { u: "/lide/", t: "Organizace — Městská knihovna (příspěvková organizace)" },
    ],
    post: { koncer: [0, 1, 1, 1], kontak: [2, 1, 3, 1], knihov: [2, 1, 3, 1] },
  };
  assert.equal(search(cal, "koncert zítra", 4, { today: "2026-10-07" })[0].id, 1);
  assert.equal(search(cal, "kontakt knihovna", 4)[0].id, 3);
});

test("roster/number záměry: Složení a shrnutí web", () => {
  const it = detectIntent("Kdo sedí v radě města?");
  assert.ok(it.roster);
  assert.ok(detectIntent("Kolik stojí tělocvična?").number);
  assert.ok(!detectIntent("kontakt knihovna").who);
});
