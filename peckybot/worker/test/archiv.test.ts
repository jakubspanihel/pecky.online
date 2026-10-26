import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { mergeHits, searchAll, wantsArchive, isWeak, ARCHIV_FACTOR, type Index } from "../src/search.ts";
import { getTexts } from "../src/answer.ts";

const root = new URL("../../", import.meta.url);
const load = (p: string): Index => JSON.parse(readFileSync(new URL(p, root), "utf8"));

test("wantsArchive: rok 2013–2021, „dříve“, „historie“, „archiv“…", () => {
  for (const q of ["Co řešila rada v roce 2017?", "usnesení zastupitelstva 12. 3. 2019", "Jak to bylo dříve s tělocvičnou?", "historie školy", "starší zápisy", "co tehdy schválili", "v minulosti", "před lety", "archiv jednání"]) {
    assert.equal(wantsArchive(q), true, q);
  }
  for (const q of ["Kdo je starosta?", "rozpočet 2026", "RM 5/2025", "Kdy je příští zastupitelstvo?", "stará radnice"]) {
    assert.equal(wantsArchive(q), false, q);
  }
});

test("mergeHits: archiv ×0.85, při shodě vyhraje hlavní, nejvýš k, src u každého zásahu", () => {
  const m = [{ id: 1, score: 10 }, { id: 2, score: 5 }];
  const a = [{ id: 7, score: 11 }, { id: 8, score: 5.9 }, { id: 9, score: 1 }];
  const r = mergeHits(m, a, 4);
  assert.equal(r.length, 4);
  assert.deepEqual(r.map((h) => `${h.src}:${h.id}`), ["main:1", "archiv:7", "archiv:8", "main:2"]); // 10, 9.35, 5.015, 5
  const tie = mergeHits([{ id: 1, score: 8.5 }], [{ id: 2, score: 10 }], 2); // 10×0.85 = 8.5
  assert.equal(tie[0].src, "main");
  assert.equal(ARCHIV_FACTOR, 0.85);
});

const filler = (n: number) => Array.from({ length: n }, (_, i) => ({ u: `/f/${i}`, t: `Web — Jiné téma ${i}` }));
// výplň zvyšuje idf, ať jediný zásah nemá skóre pod prahem „slabé shody“
const MAIN: Index = {
  v: 1,
  shard: 100,
  chunks: [{ u: "/telocvicna/", t: "Web — Tělocvična a rybník" }, ...filler(400)],
  post: { telocv: [0, 1], rybnik: [0, 1] },
};
const ARCH: Index = {
  v: 1,
  shard: 100,
  chunks: [{ u: "/jednani/#rada-2016-01-01", t: "Rada (1. 1. 2016) — rybník a tělocvična a hřbitov" }, ...filler(400)],
  post: { rybnik: [0, 1], telocv: [0, 1], hrbito: [0, 1] },
};

test("searchAll: archiv se nenačte, když hlavní rejstřík stačí", async () => {
  let loads = 0;
  const hits = await searchAll(MAIN, async () => (loads++, ARCH), "tělocvična", 8);
  assert.equal(loads, 0);
  assert.equal(hits[0].src, "main");
});

test("searchAll: rok ≤ 2021 nebo „dříve“ načte archiv a sloučí výsledky", async () => {
  let loads = 0;
  const get = async () => (loads++, ARCH);
  const h1 = await searchAll(MAIN, get, "tělocvična rybník 2016", 8);
  assert.equal(loads, 1);
  assert.deepEqual(h1.map((h) => h.src).sort(), ["archiv", "main"]);
  await searchAll(MAIN, get, "tělocvična rybník dříve", 8);
  assert.equal(loads, 2);
});

test("searchAll: slabé hlavní výsledky → archiv; šum z hlavního se zahodí", async () => {
  const hits = await searchAll(MAIN, async () => ARCH, "hřbitov", 8);
  assert.deepEqual(hits.map((h) => h.src), ["archiv"]);
  assert.equal(isWeak(hits), false);
});

test("searchAll: nesmysl v obou rejstřících zůstane slabý/prázdný", async () => {
  const hits = await searchAll(MAIN, async () => ARCH, "xqzvwk", 8);
  assert.equal(isWeak(hits), true);
});

test("searchAll: archiv „only“ hledá jen v archivu", async () => {
  const hits = await searchAll(MAIN, async () => ARCH, "tělocvična", 8, { archiv: "only" });
  assert.deepEqual(hits.map((h) => h.src), ["archiv"]);
});

test("getTexts: text se bere z dávek správného rejstříku (adresy a lokální id)", async () => {
  const urls: string[] = [];
  const realFetch = globalThis.fetch;
  globalThis.fetch = (async (u: string) => {
    urls.push(String(u));
    return new Response(JSON.stringify([String(u).includes("/archiv/") ? "TEXT-ARCHIV" : "TEXT-MAIN"]), { status: 200 });
  }) as any;
  try {
    const m: Index = { ...MAIN, h: "aaa" };
    const a: Index = { ...ARCH, h: "bbb" };
    const hits = [{ id: 0, score: 1, src: "main" as const }, { id: 0, score: 1, src: "archiv" as const }];
    const out = await getTexts({ SITE_URL: "https://x.test" } as any, { main: m, archiv: a }, hits);
    assert.equal(out.get(hits[0]), "TEXT-MAIN");
    assert.equal(out.get(hits[1]), "TEXT-ARCHIV");
    assert.ok(urls.includes("https://x.test/peckybot/chunks/0.json?h=aaa"));
    assert.ok(urls.includes("https://x.test/peckybot/archiv/chunks/0.json?h=bbb"));
  } finally {
    globalThis.fetch = realFetch;
  }
});

test("sestavený archiv: titulek odpovídá textu dávky, hlavní rejstřík neobsahuje staré zápisy", () => {
  const main = load("index.json");
  const arch = load("archiv/index.json");
  assert.ok(arch.h && main.h && arch.h !== main.h);
  assert.ok(main.chunks.every((c) => !/^(Rada|Zastupitelstvo) \(/.test(c.t)));
  assert.ok(arch.chunks.every((c) => /^(Rada|Zastupitelstvo) \(/.test(c.t)));
  for (const id of [0, 150, arch.chunks.length - 1]) {
    const texts: string[] = JSON.parse(readFileSync(new URL(`archiv/chunks/${Math.floor(id / arch.shard)}.json`, root), "utf8"));
    assert.ok(texts[id % arch.shard].startsWith(arch.chunks[id].t.slice(0, 30)), arch.chunks[id].t);
  }
});
