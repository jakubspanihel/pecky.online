// Živý adversarial test PečkyBota — VOLÁ SKUTEČNÝ Worker (≈ 0,01 USD za dotaz).
// Spuštění: PECKYBOT_URL=https://peckybot.<účet>.workers.dev EVAL_TOKEN=... node eval/adversarial.mts [filtr]
// adversarial.json → cases[]: { q, kind, mustInclude?: [regexy odmítnutí/přesměrování], mustNotInclude: [regexy úniku/vykonání] }.
// PASS = žádný mustNotInclude nesedí a (pokud je) mustInclude sedí. Plné odpovědi se vypisují k ruční kontrole.
import { readFileSync } from "node:fs";

const url = (process.env.PECKYBOT_URL ?? "").replace(/\/$/, "");
const token = process.env.EVAL_TOKEN ?? "";
if (!url || !token) { console.error("Nastavte PECKYBOT_URL a EVAL_TOKEN."); process.exit(2); }
const filter = process.argv[2];
const cases: any[] = JSON.parse(readFileSync(new URL("./adversarial.json", import.meta.url), "utf8")).cases
  .filter((c: any) => !filter || c.q.toLowerCase().includes(filter.toLowerCase()));

let pass = 0, totalMicro = 0, costKnown = true;
for (const [i, c] of cases.entries()) {
  const id = String(i + 1).padStart(2);
  let line = "", detail = "";
  try {
    const r = await fetch(`${url}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Origin: "https://dopecek.cz", "X-Eval-Token": token },
      body: JSON.stringify({ messages: [{ role: "user", content: c.q }] }),
    });
    const j: any = await r.json();
    const answer: string = j.answer ?? j.error ?? "";
    const blocked = !r.ok; // HTTP chyba (např. rate limit / filtr) není únik; hlásí se zvlášť
    const misses = (c.mustInclude ?? []).filter((re: string) => !new RegExp(re, "i").test(answer));
    const leaks = (c.mustNotInclude ?? []).filter((re: string) => new RegExp(re, "im").test(answer));
    if (typeof j.naklad_micro === "number") totalMicro += j.naklad_micro; else costKnown = false;
    const ok = leaks.length === 0 && (blocked || misses.length === 0);
    if (ok) pass++;
    line = `${ok ? "PASS" : "FAIL"} #${id} [${c.kind}] ${c.q}`;
    detail = `      HTTP ${r.status}${typeof j.naklad_micro === "number" ? `, ${(j.naklad_micro / 1e6).toFixed(4)} USD` : ""}, nástroje: ${Array.isArray(j.nastroje) ? j.nastroje.join(", ") || "(žádné)" : "n/a"}` +
      `\n      ODPOVĚĎ: ${answer.replace(/\s+/g, " ")}` +
      (leaks.length ? `\n      ZAKÁZANÉ nalezeno: ${leaks.join(", ")}` : "") +
      (!blocked && misses.length ? `\n      chybí odmítnutí/přesměrování: ${misses.join(", ")}` : "");
  } catch (e) {
    line = `FAIL #${id} [${c.kind}] ${c.q}`; detail = `      ${e instanceof Error ? e.message : e}`;
  }
  console.log(line + "\n" + detail);
  await new Promise((r) => setTimeout(r, 1000));
}
console.log(`\n${pass}/${cases.length} v pořádku; náklad celkem ${costKnown ? (totalMicro / 1e6).toFixed(3) + " USD" : "n/a"}`);
process.exit(pass === cases.length ? 0 : 1);
