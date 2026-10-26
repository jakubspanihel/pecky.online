// Offline vyhodnocení vyhledávání PečkyBota (bez volání Workeru ani Claude API).
// Spuštění: cd peckybot/worker && node eval/run.mts   (Node 22+)
import { readFileSync } from "node:fs";
import { searchAll, type Hit, type Index, type Src } from "../src/search.ts";

const TODAY = "2026-10-07"; // pevné datum, aby byly dotazy na víkend/dnes deterministické
const K = 8; // stejné jako TOP_K v src/index.ts
const root = new URL("../../", import.meta.url);
const load = (base: string): Index => JSON.parse(readFileSync(new URL(`${base}index.json`, root), "utf8"));
const index = load("");
const archivIndex = load("archiv/");
const indexes: Record<Src, Index> = { main: index, archiv: archivIndex };
const queries: any[] = JSON.parse(readFileSync(new URL("./queries.json", import.meta.url), "utf8"));

// stejně jako Worker: archiv se načte líně, jen když ho searchAll potřebuje
let archivLoads = 0;
const getArchiv = async () => { archivLoads++; return archivIndex; };

const shards = new Map<string, string[]>();
function text(h: Hit): string {
  const src = h.src ?? "main";
  const ix = indexes[src];
  const s = Math.floor(h.id / ix.shard);
  const key = `${src}:${s}`;
  if (!shards.has(key)) shards.set(key, JSON.parse(readFileSync(new URL(`${src === "archiv" ? "archiv/" : ""}chunks/${s}.json`, root), "utf8")));
  return shards.get(key)![h.id % ix.shard];
}
const norm = (s: string) => s.replace(/[  ]/g, " ");

function matches(e: any, h: Hit): boolean {
  if (!new RegExp(e.titleRegex, "i").test(norm(indexes[h.src ?? "main"].chunks[h.id].t))) return false;
  if (e.textRegex && !new RegExp(e.textRegex, "i").test(norm(text(h)))) return false;
  return true;
}

interface Row { cat: string; pending: boolean; pass: boolean; rr: number }
const rows: Row[] = [];
for (const [n, item] of queries.entries()) {
  const before = archivLoads;
  const hits = await searchAll(index, getArchiv, item.q, K, { today: TODAY, ...(item.context ? { context: item.context } : {}) });
  const rank = hits.findIndex((h) => matches(item.expect, h)) + 1; // 0 = nenalezeno
  const pass = rank > 0 && rank <= item.expect.inTop;
  // kontrola očekávání: existuje vůbec v indexu nějaký odpovídající úryvek?
  let anywhere = 0;
  for (const src of ["main", "archiv"] as Src[])
    for (let id = 0; id < indexes[src].chunks.length && anywhere < 3; id++) if (matches(item.expect, { id, score: 0, src })) anywhere++;
  const flag = item.pending ? " [pending]" : anywhere === 0 ? " [!! očekávání nenalezeno nikde v indexu]" : "";
  console.log(`${pass ? "PASS" : "FAIL"} #${String(n + 1).padStart(2)} rank=${rank || "-"} (chci ≤${item.expect.inTop}) ${item.q}${flag}${archivLoads > before ? " [archiv]" : ""}`);
  if (!pass) for (const h of hits.slice(0, 3)) console.log(`        ${h.score.toFixed(1)}  ${indexes[h.src ?? "main"].chunks[h.id].t.slice(0, 90)}`);
  rows.push({ cat: item.category, pending: !!item.pending, pass, rr: rank ? 1 / rank : 0 });
}

const pct = (a: number, b: number) => (b ? `${a}/${b} (${Math.round((100 * a) / b)} %)` : "-");
console.log("\nPo kategoriích:");
for (const cat of [...new Set(rows.map((r) => r.cat))]) {
  const r = rows.filter((x) => x.cat === cat);
  console.log(`  ${cat}: ${pct(r.filter((x) => x.pass).length, r.length)}`);
}
const np = rows.filter((r) => !r.pending), pe = rows.filter((r) => r.pending);
const mrr = (r: Row[]) => (r.reduce((s, x) => s + x.rr, 0) / (r.length || 1)).toFixed(3);
console.log(`\nCelkem (bez pending): ${pct(np.filter((r) => r.pass).length, np.length)}  MRR@${K}=${mrr(np)}`);
console.log(`Pending (zdroj chybí): ${pct(pe.filter((r) => r.pass).length, pe.length)}  MRR@${K}=${mrr(pe)}`);

console.log(`Archiv načten při ${archivLoads} z ${queries.length} dotazů`);
