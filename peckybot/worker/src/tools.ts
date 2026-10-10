// Nástroje pro Claude nad strukturovanými daty (peckybot/data/*.json).
// Vykonavatelé jsou čisté funkce nad načtenými daty; načítání a cache řeší answer.ts (ToolContext.load).
// Pozor na CPU (Cloudflare Free = 10 ms): žádné velké smyčky s regulárními výrazy, složené texty se
// skládají jen z toho, co nástroj potřebuje, a výsledky jsou malé.

import { tokenize } from "./search.ts";

export interface ToolContext {
  today: string; // RRRR-MM-DD (Praha)
  load(file: "osoby" | "slozeni" | "kalendar" | "jednani" | "statistiky"): Promise<any>;
  searchText(dotaz: string, typ?: string): Promise<{ title: string; url: string; text: string }[]>;
  /** zaregistruje zdroj a vrátí jeho číslo [n] (stejný titulek+odkaz = stejné číslo) */
  cite(title: string, url: string): number;
}

export const MAX_TOOL_ROUNDS = 3;

// ---------- pomocné ----------

export function fold(s: string): string {
  return String(s ?? "").toLowerCase().normalize("NFD").replace(/\p{M}/gu, "");
}

/** hrubý kmen pro české skloňování: krátká slova 3 znaky, ostatní 4 */
function stem(w: string): string {
  return w.length <= 4 ? w.slice(0, 3) : w.slice(0, 4);
}

const WORD_STOP = new Set([
  "slozeni", "mesta", "mestske", "mestsky", "clenove", "clenu", "kdo", "jsou", "aktualni", "soucasne",
  "pecky", "pecek", "jaky", "jaka", "jake", "kteri", "organ", "mestsk",
]);

function words(s: string): string[] {
  return (fold(s).match(/[a-z0-9]+/g) ?? []).filter((w) => w.length >= 3 && !WORD_STOP.has(w));
}

const ISO_RE = /^\d{4}-\d{2}-\d{2}$/;
function isoOrUndef(v: unknown, name: string): string | undefined {
  if (v === undefined || v === null || v === "") return undefined;
  if (typeof v !== "string" || !ISO_RE.test(v)) throw new Error(`Parametr ${name} musí být datum ve tvaru RRRR-MM-DD.`);
  return v;
}
function str(v: unknown, name: string, required = false): string | undefined {
  if (v === undefined || v === null || v === "") {
    if (required) throw new Error(`Chybí parametr ${name}.`);
    return undefined;
  }
  if (typeof v !== "string") throw new Error(`Parametr ${name} musí být text.`);
  return v.slice(0, 200);
}
const short = (s: unknown, n: number) => {
  const t = String(s ?? "").replace(/\s+/g, " ").trim();
  return t.length > n ? t.slice(0, n - 1) + "…" : t;
};
const clean = <T extends Record<string, unknown>>(o: T): T => {
  for (const k of Object.keys(o)) if (o[k] === undefined || o[k] === null || o[k] === "") delete o[k];
  return o;
};

// ---------- hledej_text ----------

const TYP_PREFIX: Record<string, RegExp> = {
  "lidé": /^Lidé/,
  "kalendář": /^Kalendář/,
  "organizace": /^Organizace/,
  "web": /^Web/,
  "jednání": /^(RM|ZM|Rada|Zastupitelstvo) /,
  "komise": /^(Sportovní|Kulturní|Stavebně|Finanční|Kontrolní|Školská|Sbor|Komise|Povodňová|Pracovní)/,
  "noviny": /^Pečecké noviny/,
};
export function typFilter(typ?: string): RegExp | undefined {
  if (!typ) return undefined;
  const t = typ.toLowerCase();
  if (TYP_PREFIX[t]) return TYP_PREFIX[t];
  const f = fold(t);
  for (const [k, re] of Object.entries(TYP_PREFIX)) if (fold(k) === f) return re;
  return undefined;
}

async function hledejText(input: any, ctx: ToolContext) {
  const dotaz = str(input.dotaz, "dotaz", true)!;
  const typ = str(input.typ, "typ");
  const hits = (await ctx.searchText(dotaz, typ)).slice(0, 6);
  return {
    vysledky: hits.map((h) => ({ n: ctx.cite(h.title, h.url), titulek: h.title, url: h.url, text: short(h.text, 700) })),
    ...(hits.length ? {} : { poznamka: "Nic nenalezeno." }),
  };
}

// ---------- osoba ----------

interface Osoba {
  id?: string;
  jmeno?: string;
  prijmeni?: string;
  funkce?: string[];
  uskupeni?: string;
  tagy?: string[];
  email?: string;
  telefon?: string;
  bio?: string;
}

function wordMatch(q: string, w: string): number {
  if (q === w) return 3;
  const m = Math.min(q.length, w.length);
  if (m < 4) return 0;
  let i = 0;
  while (i < m && q[i] === w[i]) i++;
  return i >= Math.max(4, m - 2) ? 2 : 0;
}

export function findOsoby(osoby: Osoba[], dotaz: string, limit = 5): Osoba[] {
  const qs = words(dotaz);
  if (!qs.length) return [];
  const scored: { o: Osoba; s: number }[] = [];
  for (const o of osoby) {
    const nameWords = words(`${o.jmeno ?? ""} ${o.prijmeni ?? ""}`);
    const funcStr = fold((o.funkce ?? []).join(" ; "));
    const funcWords = words(funcStr);
    const rest = fold(`${o.uskupeni ?? ""} ${(o.tagy ?? []).join(" ")}`);
    let total = 0;
    let ok = true;
    for (const q of qs) {
      let best = 0;
      for (const w of nameWords) best = Math.max(best, wordMatch(q, w) * 2);
      for (const w of funcWords) best = Math.max(best, wordMatch(q, w) * 1.2);
      if (!best && q.length >= 5 && funcStr.includes(q.slice(0, 5))) best = 1; // „starosta“ ~ „místostarosta“
      if (!best && q.length >= 4 && rest.includes(q.slice(0, 4))) best = 0.8;
      if (!best) { ok = false; break; }
      total += best;
    }
    if (ok) scored.push({ o, s: total });
  }
  scored.sort((a, b) => b.s - a.s);
  return scored.slice(0, limit).map((x) => x.o);
}

async function osobaTool(input: any, ctx: ToolContext) {
  const jmeno = str(input.jmeno, "jmeno", true)!;
  const data = await ctx.load("osoby");
  const hits = findOsoby(data.osoby ?? [], jmeno, 5);
  return {
    osoby: hits.map((o) =>
      clean({
        n: ctx.cite(`Lidé — ${[o.jmeno, o.prijmeni].filter(Boolean).join(" ")}`, "/lide/"),
        jmeno: [o.jmeno, o.prijmeni].filter(Boolean).join(" "),
        funkce: o.funkce?.length ? o.funkce.slice(0, 8) : undefined,
        uskupeni: o.uskupeni,
        email: o.email,
        telefon: o.telefon,
        bio: o.bio ? short(o.bio, 300) : undefined,
      }),
    ),
    ...(hits.length ? {} : { poznamka: "Nikdo takový nenalezen." }),
  };
}

// ---------- slozeni ----------

const ORGAN_ALIAS: Record<string, string> = {
  radni: "rada", radnich: "rada", radnimi: "rada", radnice: "rada",
  zastupitele: "zastupitelstvo", zastupitelu: "zastupitelstvo", zastupitel: "zastupitelstvo",
  starosta: "starostove", starosty: "starostove", starostu: "starostove", starostka: "starostove",
  mistostarosta: "starostove", mistostarosty: "starostove", mistostarostu: "starostove",
  primator: "starostove",
};

interface Organ {
  id: string;
  nazev: string;
  obdobi?: string;
  aktualni?: boolean;
  pocet?: number;
  clenove?: { jmeno: string; funkce?: string; uskupeni?: string; od?: string; do?: string }[];
}

export function findOrgany(organy: Organ[], dotaz: string): Organ[] {
  const f = fold(dotaz).trim();
  const exact = organy.filter((o) => fold(o.id) === f);
  if (exact.length) return exact;
  const qs = [...new Set(words(dotaz).map((w) => stem(ORGAN_ALIAS[w] ?? w)))];
  if (!qs.length) return [];
  const scored: { o: Organ; s: number }[] = [];
  for (const o of organy) {
    const ws = new Set(words(`${o.id.replaceAll("-", " ")} ${o.nazev}`).map(stem));
    let hit = 0;
    for (const q of qs) if (ws.has(q)) hit++;
    if (!hit) continue;
    const s = hit / qs.length + (hit === qs.length ? 1 : 0) - 0.08 * (ws.size - hit) + (o.aktualni ? 0.05 : 0);
    scored.push({ o, s });
  }
  scored.sort((a, b) => b.s - a.s);
  if (!scored.length) return [];
  const top = scored[0].s;
  return scored.filter((x) => x.s >= top - 0.35).slice(0, 3).map((x) => x.o);
}

async function slozeniTool(input: any, ctx: ToolContext) {
  const organ = str(input.organ, "organ", true)!;
  const data = await ctx.load("slozeni");
  const found = findOrgany(data.organy ?? [], organ);
  let budget = 90;
  const organy = found.map((o) => {
    const clenove = (o.clenove ?? []).slice(0, Math.max(0, Math.min(45, budget)));
    budget -= clenove.length;
    return clean({
      n: ctx.cite(`Složení — ${o.nazev}`, "/lide/"),
      organ: o.nazev,
      obdobi: o.obdobi,
      aktualni: o.aktualni,
      pocet: o.pocet ?? o.clenove?.length,
      clenove: clenove.map((c) => clean({ ...c })),
      zkraceno: (o.clenove?.length ?? 0) > clenove.length ? true : undefined,
    });
  });
  return { organy, ...(organy.length ? {} : { poznamka: "Žádný takový orgán nenalezen." }) };
}

// ---------- kalendar ----------

const MAX_EVENTS = 25;

export function kalendarQuery(data: any, od: string, doo: string, hledej?: string) {
  if (doo < od) [od, doo] = [doo, od];
  const kw = hledej ? words(hledej).map((w) => w.slice(0, 5)) : [];
  const match = (hay: string) => kw.every((k) => hay.includes(k));
  const events = ((data.udalosti ?? []) as any[])
    .filter((e) => e.datum && e.datum <= doo && (e.datum_do || e.datum) >= od)
    .filter((e) => !kw.length || match(fold(`${e.nazev} ${e.misto ?? ""} ${e.poradatel ?? ""} ${e.typ ?? ""}`)))
    .sort((a, b) => (a.datum + (a.cas ?? "")).localeCompare(b.datum + (b.cas ?? "")));
  const serie = ((data.serie ?? []) as any[])
    .filter((s) => (!s.od || s.od <= doo) && (!s.do || s.do >= od))
    .filter((s) => !kw.length || match(fold(`${s.nazev} ${s.popis ?? ""}`)))
    .slice(0, 5);
  return { od, do: doo, events, serie };
}

async function kalendarTool(input: any, ctx: ToolContext) {
  const od = isoOrUndef(input.od, "od");
  const doo = isoOrUndef(input.do, "do");
  if (!od || !doo) throw new Error("Chybí parametr od nebo do (RRRR-MM-DD).");
  const hledej = str(input.hledej, "hledej");
  const data = await ctx.load("kalendar");
  const r = kalendarQuery(data, od, doo, hledej);
  const shown = r.events.slice(0, MAX_EVENTS);
  return {
    od: r.od,
    do: r.do,
    celkem: r.events.length,
    ...(r.events.length > shown.length ? { zobrazeno: shown.length } : {}),
    udalosti: shown.map((e) =>
      clean({
        n: ctx.cite(`Kalendář — ${short(e.nazev, 80)} (${czd(e.datum)})`, e.url || "/kalendar/"),
        datum: e.datum,
        datum_do: e.datum_do && e.datum_do !== e.datum ? e.datum_do : undefined,
        cas: e.cas,
        nazev: short(e.nazev, 120),
        misto: e.misto ? short(e.misto, 80) : undefined,
        poradatel: e.poradatel,
        typ: e.typ,
      }),
    ),
    serie: r.serie.map((s) =>
      clean({
        n: ctx.cite(`Kalendář — ${short(s.nazev, 80)}`, "/kalendar/"),
        nazev: short(s.nazev, 100),
        popis: s.popis ? short(s.popis, 160) : undefined,
        od: s.od,
        do: s.do,
      }),
    ),
  };
}

function czd(iso: string): string {
  const [y, m, d] = String(iso).split("-");
  return `${Number(d)}. ${Number(m)}. ${y}`;
}

// ---------- jednani / pocet_bodu ----------

interface Jednani {
  id: string;
  typ?: string;
  organ?: string;
  oznaceni?: string;
  datum: string;
  body?: string[];
}

function typMatch(j: Jednani, typ?: string): boolean {
  if (!typ) return true;
  const hay = fold(`${j.typ ?? ""} ${j.organ ?? ""}`);
  return words(typ).every((w) => hay.includes(stem(ORGAN_ALIAS[w] ?? w)));
}

function inRange(j: Jednani, od?: string, doo?: string): boolean {
  return (!od || j.datum >= od) && (!doo || j.datum <= doo);
}

const foldedBodies = new WeakMap<Jednani, string[]>();
function bodiesFolded(j: Jednani): string[] {
  let f = foldedBodies.get(j);
  if (!f) {
    f = (j.body ?? []).map(fold);
    foldedBodies.set(j, f);
  }
  return f;
}

function keywordStems(s: string): string[] {
  return [...new Set(tokenize(s))];
}

export function countItems(
  jednani: Jednani[],
  kws: string[],
  opt: { od?: string; do?: string; typ?: string },
) {
  const perYear: Record<string, number> = {};
  const examples: { j: Jednani; bod: string }[] = [];
  let count = 0;
  let meetings = 0;
  let inScope = 0;
  const sorted = jednani.filter((j) => typMatch(j, opt.typ) && inRange(j, opt.od, opt.do)).sort((a, b) => b.datum.localeCompare(a.datum));
  for (const j of sorted) {
    inScope++;
    const f = bodiesFolded(j);
    let m = 0;
    for (let i = 0; i < f.length; i++) {
      const t = f[i];
      let all = true;
      for (const k of kws) if (!t.includes(k)) { all = false; break; }
      if (!all) continue;
      m++;
      if (examples.length < 10) examples.push({ j, bod: j.body![i] });
    }
    if (m) {
      count += m;
      meetings++;
      const y = j.datum.slice(0, 4);
      perYear[y] = (perYear[y] ?? 0) + m;
    }
  }
  return { count, meetings, inScope, perYear, examples };
}

async function jednaniTool(input: any, ctx: ToolContext) {
  const typ = str(input.typ, "typ");
  const od = isoOrUndef(input.od, "od");
  const doo = isoOrUndef(input.do, "do");
  const hledej = str(input.hledej, "hledej");
  const data = await ctx.load("jednani");
  const kws = hledej ? keywordStems(hledej) : [];
  let list = ((data.jednani ?? []) as Jednani[])
    .filter((j) => typMatch(j, typ) && inRange(j, od, doo))
    .sort((a, b) => b.datum.localeCompare(a.datum));
  const matches = new Map<string, number>();
  if (kws.length) {
    list = list.filter((j) => {
      const n = bodiesFolded(j).filter((t) => kws.every((k) => t.includes(k))).length;
      if (n) matches.set(j.id, n);
      return n > 0;
    });
  }
  const shown = list.slice(0, 15);
  return {
    celkem: list.length,
    ...(list.length > shown.length ? { zobrazeno: shown.length } : {}),
    jednani: shown.map((j) =>
      clean({
        n: ctx.cite(`${j.oznaceni ?? j.id} — přehled jednání`, `/jednani/#${j.id}`),
        id: j.id,
        oznaceni: j.oznaceni,
        organ: j.organ,
        datum: j.datum,
        bodu: j.body?.length ?? 0,
        shodnych_bodu: matches.get(j.id),
      }),
    ),
  };
}

async function pocetBoduTool(input: any, ctx: ToolContext) {
  const kw = str(input.klicova_slova, "klicova_slova", true)!;
  const kws = keywordStems(kw);
  if (!kws.length) throw new Error("Klíčová slova jsou příliš krátká.");
  const typ = str(input.typ, "typ");
  const od = isoOrUndef(input.od, "od");
  const doo = isoOrUndef(input.do, "do");
  const data = await ctx.load("jednani");
  const r = countItems((data.jednani ?? []) as Jednani[], kws, { od, do: doo, typ });
  return {
    pocet_bodu: r.count,
    pocet_jednani_s_shodou: r.meetings,
    jednani_v_rozsahu: r.inScope,
    po_letech: Object.fromEntries(Object.entries(r.perYear).sort(([a], [b]) => a.localeCompare(b))),
    priklady: r.examples.map(({ j, bod }) => ({
      n: ctx.cite(`${j.oznaceni ?? j.id} — přehled jednání`, `/jednani/#${j.id}`),
      datum: j.datum,
      jednani: j.oznaceni ?? j.id,
      bod: short(bod, 160),
    })),
    poznamka:
      "Počítají se BODY PROGRAMU jednání, jejichž název obsahuje všechna slova (bez ohledu na diakritiku a skloňování). Není to počet povolení, smluv ani jiných věcí; jeden bod může být opakovaný na více jednáních.",
  };
}

// ---------- registr ----------

type Exec = (input: any, ctx: ToolContext) => Promise<unknown>;

export const TOOL_DEFS = [
  {
    name: "hledej_text",
    description:
      "Znovu prohledá textový rejstřík webu jiným dotazem; vrátí až 6 úryvků s titulkem a odkazem. Použij, když dodané zdroje na otázku neodpovídají. Volitelně omezí typ zdroje.",
    input_schema: {
      type: "object",
      properties: {
        dotaz: { type: "string", description: "Dotaz nebo klíčová slova česky." },
        typ: { type: "string", enum: ["Lidé", "Kalendář", "Organizace", "Web", "jednání", "komise", "noviny"], description: "Volitelně jen tento typ zdroje." },
      },
      required: ["dotaz"],
      additionalProperties: false,
    },
  },
  {
    name: "osoba",
    description:
      "Najde osobu podle jména, příjmení nebo funkce (např. „místostarosta“); bez ohledu na diakritiku a skloňování. Vrátí až 5 shod s funkcemi, uskupením a kontakty (e-mail, telefon).",
    input_schema: {
      type: "object",
      properties: { jmeno: { type: "string", description: "Jméno, příjmení nebo funkce." } },
      required: ["jmeno"],
      additionalProperties: false,
    },
  },
  {
    name: "slozeni",
    description:
      "Vrátí aktuální i historické složení orgánu: rada města, zastupitelstvo, finanční výbor, kontrolní výbor, školská rada, komise (sportovní, kulturní…), starostové a místostarostové.",
    input_schema: {
      type: "object",
      properties: { organ: { type: "string", description: "Název orgánu, např. „rada“, „finanční výbor“, „starostové“." } },
      required: ["organ"],
      additionalProperties: false,
    },
  },
  {
    name: "kalendar",
    description:
      "Akce z kalendáře webu v rozmezí dat (včetně vícedenních akcí) a pravidelné série. Nejvýš 25 akcí. Data v ISO tvaru RRRR-MM-DD, spočítej je z dnešního data.",
    input_schema: {
      type: "object",
      properties: {
        od: { type: "string", description: "První den, RRRR-MM-DD." },
        do: { type: "string", description: "Poslední den včetně, RRRR-MM-DD." },
        hledej: { type: "string", description: "Volitelně slovo v názvu, místě nebo pořadateli." },
      },
      required: ["od", "do"],
      additionalProperties: false,
    },
  },
  {
    name: "jednani",
    description:
      "Seznam jednání (zastupitelstvo, rada, komise, výbory, školská rada) od nejnovějšího, nejvýš 15, s označením, datem a počtem bodů. Volitelně filtr typu, období a slov v názvech bodů.",
    input_schema: {
      type: "object",
      properties: {
        typ: { type: "string", description: "např. „zastupitelstvo“, „rada“, „finanční výbor“, „komise“." },
        od: { type: "string", description: "RRRR-MM-DD" },
        do: { type: "string", description: "RRRR-MM-DD" },
        hledej: { type: "string", description: "Slova z názvu bodu programu." },
      },
      additionalProperties: false,
    },
  },
  {
    name: "pocet_bodu",
    description:
      "Spočítá BODY PROGRAMU jednání, jejichž název obsahuje všechna klíčová slova. Vrátí počet, počet jednání, rozpad po letech a až 10 příkladů s odkazy. Pro otázky „kolik…“; nepočítá povolení, smlouvy apod., jen body programu.",
    input_schema: {
      type: "object",
      properties: {
        klicova_slova: { type: "string", description: "Slova, která musí být v názvu bodu, např. „tělocvična“." },
        od: { type: "string", description: "RRRR-MM-DD" },
        do: { type: "string", description: "RRRR-MM-DD" },
        typ: { type: "string", description: "např. „zastupitelstvo“, „rada“." },
      },
      required: ["klicova_slova"],
      additionalProperties: false,
    },
  },
] as const;

const EXEC: Record<string, Exec> = {
  hledej_text: hledejText,
  osoba: osobaTool,
  slozeni: slozeniTool,
  kalendar: kalendarTool,
  jednani: jednaniTool,
  pocet_bodu: pocetBoduTool,
};

export function isKnownTool(name: string): boolean {
  return Object.hasOwn(EXEC, name);
}

export const MAX_RESULT_CHARS = 6000; // ≈ 1500 tokenů

/** Vykoná nástroj; vždy vrací text pro tool_result (chyby jako is_error). */
export async function executeTool(
  name: string,
  input: unknown,
  ctx: ToolContext,
): Promise<{ content: string; isError: boolean }> {
  if (!isKnownTool(name)) return { content: `Neznámý nástroj „${name}“.`, isError: true };
  try {
    const inp = input && typeof input === "object" ? input : {};
    const out = await EXEC[name](inp, ctx);
    let s = JSON.stringify(out);
    if (s.length > MAX_RESULT_CHARS) s = s.slice(0, MAX_RESULT_CHARS) + "…[výsledek zkrácen]";
    return { content: s, isError: false };
  } catch (e) {
    return { content: `Nástroj selhal: ${e instanceof Error ? e.message : String(e)}`, isError: true };
  }
}
