// Živý end-to-end test PečkyBota — VOLÁ SKUTEČNÝ Worker i Claude API (stojí peníze, ≈ 0,01–0,03 USD za dotaz).
// Spuštění: PECKYBOT_URL=https://peckybot.<účet>.workers.dev EVAL_TOKEN=... node eval/e2e.mts [filtr]
// Případ v e2e-cases.json: { q, tools?, mustInclude: [regexy], mustNotInclude?: [regexy], kalendarAny?, onlyIf?, note? }.
// PASS = všechny mustInclude sedí a žádný mustNotInclude nesedí. `tools` je jen informativní (vypisuje se, nikdy neshazuje test).
// Datumová zástupná slova v regexech (dopočítá se z dnešního data v Praze, týden = po–ne):
//   {{DNES}} {{SOBOTA}} {{NEDELE}} {{PRISTI_TYDEN_PO}} {{PRISTI_TYDEN_NE}} {{PRISTI_TYDEN_ANY}}
//   → alternativy „17\. ?10\.|17\. října“ (bez vnějších závorek, vkládat do `a|b` seznamů).
// kalendarAny: "dnes"|"vikend"|"pristi-tyden"|"7dni" — odpověď musí navíc zmínit aspoň jednu událost typu akce z
//   peckybot/data/kalendar.json v daném rozsahu (porovnání prvních ~14 znaků názvu, bez diakritiky a velikosti písmen).
// onlyIf: "bezKoncertuTentoTyden" — případ se přeskočí, pokud je tento týden v kalendáři koncert.
import { readFileSync } from "node:fs";

const url = (process.env.PECKYBOT_URL ?? "").replace(/\/$/, "");
const token = process.env.EVAL_TOKEN ?? "";
if (!url || !token) {
  console.error("Nastavte PECKYBOT_URL a EVAL_TOKEN.");
  process.exit(2);
}
const filter = process.argv[2];

// ---- datum v Praze ----
const pragueISO = (d = new Date()) => new Intl.DateTimeFormat("sv-SE", { timeZone: "Europe/Prague" }).format(d); // YYYY-MM-DD
const addDays = (iso: string, n: number) => { const d = new Date(iso + "T12:00:00Z"); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
const today = pragueISO();
const dow = (new Date(today + "T12:00:00Z").getUTCDay() + 6) % 7; // 0 = pondělí
const monday = addDays(today, -dow);
const MESICE = ["ledna","února","března","dubna","května","června","července","srpna","září","října","listopadu","prosince"];
const alt = (iso: string) => { const [, m, d] = iso.split("-").map(Number); return `${d}\\. ?${m}\\.|${d}\\. ${MESICE[m - 1]}`; };
const nextWeek = Array.from({ length: 7 }, (_, i) => addDays(monday, 7 + i));
const subst: Record<string, string> = {
  DNES: alt(today), SOBOTA: alt(addDays(monday, 5)), NEDELE: alt(addDays(monday, 6)),
  PRISTI_TYDEN_PO: alt(nextWeek[0]), PRISTI_TYDEN_NE: alt(nextWeek[6]), PRISTI_TYDEN_ANY: nextWeek.map(alt).join("|"),
};
const expand = (s: string) => s.replace(/\{\{(\w+)\}\}/g, (_, k) => subst[k] ?? (() => { throw new Error("neznámé {{" + k + "}}"); })());

// ---- kalendář z repa ----
type Ev = { datum: string; datum_do: string | null; nazev: string; typ: string };
let kal: Ev[] = [];
try { kal = JSON.parse(readFileSync(new URL("../../data/kalendar.json", import.meta.url), "utf8")).udalosti; } catch { /* bez kalendáře se kalendarAny neověřuje */ }
const norm = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/\s+/g, " ").trim();
const inRange = (e: Ev, a: string, b: string) => (e.datum_do ?? e.datum) >= a && e.datum <= b;
const ranges: Record<string, [string, string]> = {
  dnes: [today, today], vikend: [addDays(monday, 5), addDays(monday, 6)],
  "pristi-tyden": [nextWeek[0], nextWeek[6]], "7dni": [today, addDays(today, 7)], "tento-tyden": [monday, addDays(monday, 6)],
};
const eventsIn = (r: string) => kal.filter((e) => e.typ === "akce" && inRange(e, ...ranges[r]));

const cases: any[] = JSON.parse(readFileSync(new URL("./e2e-cases.json", import.meta.url), "utf8"))
  .filter((c: any) => !filter || c.q.toLowerCase().includes(filter.toLowerCase()));

let pass = 0, ran = 0, totalMicro = 0, costKnown = true;
for (const [i, c] of cases.entries()) {
  const id = String(i + 1).padStart(2);
  let line = "", detail = "";
  try {
    if (c.onlyIf === "bezKoncertuTentoTyden" && kal.some((e) => /koncert/i.test(e.nazev) && inRange(e, ...ranges["tento-tyden"]))) {
      console.log(`SKIP #${id} ${c.q}\n      tento týden je v kalendáři koncert, předpoklad případu neplatí`); continue;
    }
    ran++;
    const r = await fetch(`${url}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Origin: "https://dopecek.cz", "X-Eval-Token": token },
      body: JSON.stringify({ messages: [{ role: "user", content: c.q }] }),
    });
    const j: any = await r.json();
    if (!r.ok) throw new Error(`HTTP ${r.status}: ${j.error ?? ""}`);
    const answer: string = j.answer ?? "";
    const misses = (c.mustInclude ?? []).filter((re: string) => !new RegExp(expand(re), "i").test(answer));
    const forbidden = (c.mustNotInclude ?? []).filter((re: string) => new RegExp(expand(re), "i").test(answer));
    let calMiss = "";
    if (c.kalendarAny && kal.length) {
      const evs = eventsIn(c.kalendarAny);
      const na = norm(answer);
      if (evs.length && !evs.some((e) => na.includes(norm(e.nazev).slice(0, 14)))) calMiss = `žádná z ${evs.length} událostí kalendáře (${c.kalendarAny}) není v odpovědi, např. „${evs[0].nazev}“`;
    }
    const used: string[] | undefined = Array.isArray(j.nastroje) ? j.nastroje : undefined;
    if (typeof j.naklad_micro === "number") totalMicro += j.naklad_micro; else costKnown = false;
    const ok = misses.length === 0 && forbidden.length === 0 && !calMiss;
    if (ok) pass++;
    line = `${ok ? "PASS" : "FAIL"} #${id} ${c.q}`;
    detail =
      `      nástroje (informativně): ${used ? used.join(", ") || "(žádné)" : "n/a"}` +
      (c.tools?.length ? ` (typicky: ${c.tools.join("|")})` : "") +
      (typeof j.naklad_micro === "number" ? `, ${(j.naklad_micro / 1e6).toFixed(4)} USD` : "") +
      `\n      ODPOVĚĎ: ${answer.replace(/\s+/g, " ")}` +
      (misses.length ? `\n      chybí: ${misses.join(", ")}` : "") +
      (forbidden.length ? `\n      zakázané nalezeno: ${forbidden.join(", ")}` : "") +
      (calMiss ? `\n      kalendář: ${calMiss}` : "");
  } catch (e) {
    line = `FAIL #${id} ${c.q}`;
    detail = `      ${e instanceof Error ? e.message : e}`;
  }
  console.log(line + "\n" + detail);
  await new Promise((r) => setTimeout(r, 1000));
}
console.log(`\n${pass}/${ran} v pořádku (dnes ${today}); náklad celkem ${costKnown ? (totalMicro / 1e6).toFixed(3) + " USD" : "n/a (Worker nevrací naklad_micro)"}`);
process.exit(pass === ran ? 0 : 1);
