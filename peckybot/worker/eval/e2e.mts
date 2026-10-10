// Živý end-to-end test PečkyBota — VOLÁ SKUTEČNÝ Worker i Claude API (stojí peníze, ≈ 0,02–0,05 USD za dotaz).
// Spuštění: PECKYBOT_URL=https://peckybot.<účet>.workers.dev EVAL_TOKEN=... node eval/e2e.mts [filtr]
// Každý případ z e2e-cases.json: { q, tools: [očekávané nástroje, aspoň jeden], mustInclude: [regexy] }.
// Worker s platným X-Eval-Token do odpovědi přidává `nastroje` (názvy) a `naklad_micro`; bez nich skript píše „n/a“.
import { readFileSync } from "node:fs";

const url = (process.env.PECKYBOT_URL ?? "").replace(/\/$/, "");
const token = process.env.EVAL_TOKEN ?? "";
if (!url || !token) {
  console.error("Nastavte PECKYBOT_URL a EVAL_TOKEN.");
  process.exit(2);
}
const filter = process.argv[2];
const cases: { q: string; tools: string[]; mustInclude: string[] }[] = JSON.parse(
  readFileSync(new URL("./e2e-cases.json", import.meta.url), "utf8"),
).filter((c: any) => !filter || c.q.toLowerCase().includes(filter.toLowerCase()));

let pass = 0, totalMicro = 0, costKnown = true;
for (const [i, c] of cases.entries()) {
  let line = "", detail = "";
  try {
    const r = await fetch(`${url}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Origin: "https://dopecek.cz", "X-Eval-Token": token },
      body: JSON.stringify({ messages: [{ role: "user", content: c.q }] }),
    });
    const j: any = await r.json();
    if (!r.ok) throw new Error(`HTTP ${r.status}: ${j.error ?? ""}`);
    const answer: string = j.answer ?? "";
    const misses = c.mustInclude.filter((re) => !new RegExp(re, "i").test(answer));
    const used: string[] | undefined = Array.isArray(j.nastroje) ? j.nastroje : undefined;
    const toolOk = !c.tools.length || !used || c.tools.some((t) => used.includes(t));
    if (typeof j.naklad_micro === "number") totalMicro += j.naklad_micro; else costKnown = false;
    const ok = misses.length === 0 && toolOk;
    if (ok) pass++;
    line = `${ok ? "PASS" : "FAIL"} #${String(i + 1).padStart(2)} ${c.q}`;
    detail =
      `      nástroje: ${used ? used.join(", ") || "(žádné)" : "n/a"}` +
      (c.tools.length ? ` (čekáno: ${c.tools.join("|")})` : "") +
      (typeof j.naklad_micro === "number" ? `, ${(j.naklad_micro / 1e6).toFixed(4)} USD` : "") +
      `\n      ${answer.replace(/\s+/g, " ").slice(0, 220)}` +
      (misses.length ? `\n      chybí: ${misses.join(", ")}` : "") +
      (!toolOk ? "\n      nezavolán očekávaný nástroj" : "");
  } catch (e) {
    line = `FAIL #${String(i + 1).padStart(2)} ${c.q}`;
    detail = `      ${e instanceof Error ? e.message : e}`;
  }
  console.log(line + "\n" + detail);
  await new Promise((r) => setTimeout(r, 1000));
}
console.log(`\n${pass}/${cases.length} v pořádku; náklad celkem ${costKnown ? (totalMicro / 1e6).toFixed(3) + " USD" : "n/a (Worker nevrací naklad_micro)"}`);
process.exit(pass === cases.length ? 0 : 1);
