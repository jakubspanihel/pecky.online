// Statistiky z anonymních záznamů (D1 peckybot-log). Spuštění:
//   npm run stats [-- --days 7]
//   npm run export-failures      → eval/candidates.json (dotazy bez odpovědi a s palcem dolů)
// Volá `wrangler d1 execute --remote`, takže vyžaduje přihlášený wrangler.
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { normalizeQuery } from "../src/log.ts";

const args = process.argv.slice(2);
const mode = args.includes("--export-failures") ? "export" : "stats";
const di = args.indexOf("--days");
const days = di >= 0 ? Math.max(1, Number(args[di + 1]) || 7) : 7;
const since = new Date(Date.now() - days * 86400_000).toISOString().slice(0, 10);

function sql<T = Record<string, any>>(command: string): T[] {
  const out = execFileSync(
    "npx",
    ["wrangler", "d1", "execute", "peckybot-log", "--remote", "--json", "--command", command],
    { encoding: "utf8", maxBuffer: 64 * 1024 * 1024, cwd: new URL("..", import.meta.url).pathname },
  );
  const json = JSON.parse(out.slice(out.indexOf("[")));
  return json[0]?.results ?? [];
}

const pct = (a: number, b: number) => (b ? `${((100 * a) / b).toFixed(1)} %` : "–");
const usd = (micro: number) => `${(micro / 1_000_000).toFixed(3)} USD`;
const title = (s: string) => console.log(`\n== ${s} ==`);

function stats() {
  const real = "eval = 0";
  console.log(`PečkyBot — statistiky od ${since} (měřicí dotazy se nepočítají)`);

  title("Dotazů za den");
  const perDay = sql(`SELECT den, COUNT(*) n, SUM(z_cache) cache, SUM(nevim) nevim FROM dotazy WHERE ${real} AND den >= '${since}' GROUP BY den ORDER BY den`);
  for (const r of perDay) console.log(`${r.den}  ${String(r.n).padStart(4)}  (z cache ${r.cache}, „nevím“ ${r.nevim})`);

  const t = sql(`SELECT COUNT(*) n, SUM(nevim) nevim, SUM(z_cache) cache, AVG(CASE WHEN z_cache = 0 AND chyba IS NULL THEN naklad_mikro END) prumer FROM dotazy WHERE ${real} AND den >= '${since}'`)[0];
  title("Souhrn");
  console.log(`Dotazů celkem: ${t.n}`);
  console.log(`Podíl „nevím“: ${pct(t.nevim ?? 0, t.n)}`);
  console.log(`Podíl odpovězených z cache: ${pct(t.cache ?? 0, t.n)}`);
  console.log(`Průměrný náklad dotazu (bez cache): ${t.prumer ? usd(t.prumer) : "–"}`);

  title("Náklad po měsících");
  for (const r of sql(`SELECT substr(den,1,7) mesic, COUNT(*) n, SUM(naklad_mikro) naklad FROM dotazy WHERE ${real} GROUP BY mesic ORDER BY mesic`)) {
    console.log(`${r.mesic}  ${String(r.n).padStart(5)} dotazů  ${usd(r.naklad ?? 0)}`);
  }

  title("Použité nástroje");
  const tools = new Map<string, number>();
  for (const r of sql(`SELECT nastroje FROM dotazy WHERE ${real} AND den >= '${since}' AND nastroje IS NOT NULL AND nastroje != '[]'`)) {
    for (const name of JSON.parse(r.nastroje)) tools.set(name, (tools.get(name) ?? 0) + 1);
  }
  if (!tools.size) console.log("(žádné)");
  for (const [k, v] of [...tools].sort((a, b) => b[1] - a[1])) console.log(`${String(v).padStart(5)}  ${k}`);

  title("Nejčastější dotazy (20, po normalizaci)");
  const freq = new Map<string, { n: number; example: string }>();
  for (const r of sql(`SELECT dotaz FROM dotazy WHERE ${real} AND den >= '${since}' ORDER BY ts DESC LIMIT 5000`)) {
    const k = normalizeQuery(r.dotaz);
    const f = freq.get(k) ?? { n: 0, example: r.dotaz };
    f.n++;
    freq.set(k, f);
  }
  for (const f of [...freq.values()].sort((a, b) => b.n - a.n).slice(0, 20)) console.log(`${String(f.n).padStart(5)}  ${f.example}`);

  title("Posledních 20 dotazů bez odpovědi („nevím“)");
  for (const r of sql(`SELECT den, dotaz FROM dotazy WHERE ${real} AND nevim = 1 ORDER BY ts DESC LIMIT 20`)) console.log(`${r.den}  ${r.dotaz}`);

  title("Odpovědi s palcem dolů");
  const down = sql(`SELECT d.den, d.dotaz, d.zdroje FROM hodnoceni h JOIN dotazy d ON d.id = h.id WHERE h.hlas = -1 AND d.${real} ORDER BY h.ts DESC LIMIT 50`);
  if (!down.length) console.log("(žádné)");
  for (const r of down) console.log(`${r.den}  ${r.dotaz}\n            zdroje: ${JSON.parse(r.zdroje || "[]").join(" | ") || "–"}`);
  const up = sql(`SELECT COUNT(*) n FROM hodnoceni h JOIN dotazy d ON d.id = h.id WHERE h.hlas = 1 AND d.${real}`)[0];
  console.log(`\nPalců nahoru celkem: ${up.n}`);
}

function exportFailures() {
  const file = new URL("../eval/candidates.json", import.meta.url);
  const known = new Set<string>();
  const qf = new URL("../eval/queries.json", import.meta.url);
  if (existsSync(qf)) for (const q of JSON.parse(readFileSync(qf, "utf8"))) known.add(normalizeQuery(q.q));
  const out = new Map<string, { q: string; reason: string }>();
  const rows = [
    ...sql(`SELECT dotaz q, 'nevim' reason FROM dotazy WHERE eval = 0 AND nevim = 1 ORDER BY ts DESC LIMIT 500`),
    ...sql(`SELECT d.dotaz q, 'hlas-' reason FROM hodnoceni h JOIN dotazy d ON d.id = h.id WHERE h.hlas = -1 AND d.eval = 0 ORDER BY h.ts DESC LIMIT 500`),
  ];
  for (const r of rows) {
    const k = normalizeQuery(r.q);
    if (!k || known.has(k) || out.has(k)) continue;
    out.set(k, { q: r.q, reason: r.reason });
  }
  writeFileSync(file, JSON.stringify([...out.values()], null, 2) + "\n");
  console.log(`Zapsáno ${out.size} kandidátů do eval/candidates.json`);
}

if (mode === "export") exportFailures();
else stats();
