// Deterministická kontrola vykonavatelů nástrojů nad skutečnými daty peckybot/data/*.json (bez LLM).
// Spuštění: cd peckybot/worker && node eval/tools.mts   (Node 22+)
import { existsSync, readFileSync } from "node:fs";
import { executeTool, type ToolContext } from "../src/tools.ts";

const dataDir = new URL("../../data/", import.meta.url);
const need = ["osoby", "slozeni", "kalendar", "jednani"];
const missing = need.filter((f) => !existsSync(new URL(`${f}.json`, dataDir)));
if (missing.length) {
  console.log(`SKIP: chybí peckybot/data/${missing.join(".json, ")}.json (spustit python3 scripts/build.py).`);
  process.exit(0);
}

const cache = new Map<string, any>();
const ctx: ToolContext = {
  today: "2026-10-10",
  load: async (f) => {
    if (!cache.has(f)) cache.set(f, JSON.parse(readFileSync(new URL(`${f}.json`, dataDir), "utf8")));
    return cache.get(f);
  },
  searchText: async () => [],
  cite: (() => { const seen: string[] = []; return (t: string, u: string) => { const k = t + u; let i = seen.indexOf(k); if (i < 0) i = seen.push(k) - 1; return i + 1; }; })(),
};

const cases: any[] = JSON.parse(readFileSync(new URL("./tools-cases.json", import.meta.url), "utf8"));
let fail = 0;
for (const c of cases) {
  const t0 = performance.now();
  const r = await executeTool(c.tool, c.input, ctx);
  const ms = performance.now() - t0;
  const problems: string[] = [];
  if (r.isError) problems.push(`chyba: ${r.content}`);
  else {
    for (const s of c.mustInclude ?? []) if (!r.content.includes(s)) problems.push(`chybí „${s}“`);
    if (c.minLength && r.content.length < c.minLength) problems.push(`krátký výsledek (${r.content.length})`);
    if (c.minCount && !(JSON.parse(r.content).pocet_bodu >= c.minCount)) problems.push("pocet_bodu < " + c.minCount);
    if (r.content.length > 6100) problems.push(`výsledek příliš velký (${r.content.length})`);
  }
  if (problems.length) fail++;
  console.log(`${problems.length ? "FAIL" : "PASS"} ${c.tool}(${JSON.stringify(c.input)}) ${r.content.length} zn., ${ms.toFixed(1)} ms${problems.length ? "\n      " + problems.join("; ") : ""}`);
}
console.log(`\n${cases.length - fail}/${cases.length} v pořádku`);
process.exit(fail ? 1 : 0);
