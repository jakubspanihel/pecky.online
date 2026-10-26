// Nástroje pro Claude nad strukturovanými daty (peckybot/data/*.json).
// Vykonavatelé jsou čisté funkce nad načtenými daty; načítání a cache řeší answer.ts (ToolContext.load).
// Pozor na CPU (Cloudflare Free = 10 ms): žádné velké smyčky s regulárními výrazy, složené texty se
// skládají jen z toho, co nástroj potřebuje, a výsledky jsou malé.

import { tokenize } from "./search.ts";

export interface ToolContext {
  today: string; // RRRR-MM-DD (Praha)
  load(file: "osoby" | "slozeni" | "kalendar" | "jednani" | "statistiky" | "svoz"): Promise<any>;
  /** malý soubor s dokumentem: „jednani/<id>“ nebo „uredni-deska/<rok>“ (data/…json, cache v answer.ts) */
  loadDoc(path: string): Promise<any>;
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
/** typ „archiv“ = starší jednání z úřední desky (2013 – duben 2021); hledá se jen v archivním rejstříku */
export function isArchivTyp(typ?: string): boolean {
  return !!typ && fold(typ) === "archiv";
}
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
    ...(r.events.length || r.serie.length ? {} : { poznamka: `Žádné události v rozsahu ${czd(r.od)} – ${czd(r.do)}.` }),
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

// ---------- svoz ----------

const SVOZ_POCET = 3;

export function svozQuery(data: any, today: string, lokalita?: string, druh?: string) {
  const l = fold(lokalita ?? "");
  const wanted = (data.lokality as any[]).filter((x) => {
    if (!l) return true;
    if (/sidli|sidlist/.test(l)) return x.id === "sidliste";
    if (/jih|jizn/.test(l)) return x.id === "jih";
    if (/sever|chvalov/.test(l)) return x.id === "sever";
    return true;
  });
  const d = fold(druh ?? "");
  const kinds = (x: any) =>
    (x.druhy as any[]).filter((k) => {
      if (!d) return true;
      if (/bio|biood|bioodpad|zahrad|trav/.test(d)) return k.id === "bio";
      if (/plast|plastic/.test(d)) return k.id === "plast";
      if (/papir|karton/.test(d)) return k.id === "papir";
      if (/komun|smes|popelnic|zbytk|cerna/.test(d)) return k.id === "komunal";
      return true;
    });
  return wanted.map((x) => ({
    lokalita: x.nazev,
    druhy: kinds(x).map((k) => {
      const dalsi = (k.terminy as string[]).filter((t) => t >= today);
      return { druh: k.nazev, pravidlo: k.pravidlo, nejblizsi: dalsi.slice(0, SVOZ_POCET), zbyva_v_roce: dalsi.length };
    }),
  }));
}

async function svozTool(input: any, ctx: ToolContext) {
  const data = await ctx.load("svoz");
  const lokalita = str(input.lokalita, "lokalita");
  const druh = str(input.druh, "druh");
  const r = svozQuery(data, ctx.today, lokalita, druh);
  const n = ctx.cite(`Kalendář — svoz odpadu ${data.rok}`, data.url || "/kalendar/svoz.html");
  return {
    n,
    dnes: ctx.today,
    lokality: r.map((x) => ({
      lokalita: x.lokalita,
      druhy: x.druhy.map((k) =>
        clean({
          druh: k.druh,
          pravidlo: k.pravidlo,
          nejblizsi: k.nejblizsi.map(czd),
          poznamka: k.zbyva_v_roce ? undefined : `V roce ${data.rok} už další termín není.`,
        }),
      ),
    })),
    poznamka: "Harmonogram města neuvádí, které ulice patří do které lokality.",
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
  dostupne?: string[];
  je_posledni?: boolean;
}

// jednoslovné druhy jednání se porovnávají přesně (jinak by „rada“ chytla i „školskou radu“)
const TYP_EXACT: Record<string, string> = {
  rada: "rada", rady: "rada", radu: "rada", "rada mesta": "rada", rm: "rada",
  zastupitelstvo: "zastupitelstvo", zastupitelstva: "zastupitelstvo", zm: "zastupitelstvo", "zastupitelstvo mesta": "zastupitelstvo",
  komise: "komise", vybor: "vybor", vybory: "vybor",
};

function typMatch(j: Jednani, typ?: string): boolean {
  if (!typ) return true;
  const exact = TYP_EXACT[fold(typ).trim()];
  if (exact) return j.typ === exact;
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
  const nejnovejsi = input.nejnovejsi === true;
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
  if (nejnovejsi) {
    // s typem dvě nejnovější (nejnovější může mít jen pozvánku), bez typu nejnovější od každého druhu
    list = typ ? list.slice(0, 2) : list.filter((j) => j.je_posledni);
  }
  const shown = list.slice(0, nejnovejsi ? 6 : 15);
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
        stav: j.datum > ctx.today ? "plánováno (ještě se nekonalo)" : undefined,
        bodu: j.body?.length ?? 0,
        dostupne: j.dostupne,
        shodnych_bodu: matches.get(j.id),
      }),
    ),
    ...(nejnovejsi || list.length ? { dalsi_krok: "Obsah jednání (body, usnesení, hlasování) přečteš nástrojem cti_dokument(id)." } : {}),
  };
}

// ---------- cti_dokument ----------

export const DOC_MAX_CHARS = 13000; // ≈ 5 000 tokenů češtiny v JSONu; čtení stojí ≲ 0,01 USD za každé další kolo
const DOC_LEVELS: [number, number][] = [[900, 500], [350, 300], [150, 200], [0, 120]]; // [zpráva, usnesení]
const ID_RE = /^[a-z0-9-]{3,80}$/;

function docItem(b: any, z: number, u: number) {
  return clean({
    n: b.n,
    nazev: b.nazev,
    predkladatel: b.predkladatel,
    zprava: z && b.zprava ? short(b.zprava, z) : undefined,
    usneseni: b.usneseni?.length
      ? b.usneseni.map((r: any) => clean({ cislo: r.cislo, text: short(r.text, u), hlasovani: r.hlasovani, neprijato: r.neprijato, poznamka: r.poznamka }))
      : undefined,
  });
}

async function ctiDokumentTool(input: any, ctx: ToolContext) {
  const id = str(input.id, "id", true)!;
  if (!ID_RE.test(id)) throw new Error("Neplatné id jednání (např. „rada-2026-10-12“, id vrací nástroj jednani).");
  const bodRaw = input.bod;
  const bodNum = bodRaw === undefined || bodRaw === null || bodRaw === "" ? undefined : Number(bodRaw);
  if (bodNum !== undefined && !Number.isInteger(bodNum)) throw new Error("Parametr bod musí být číslo bodu programu.");
  let doc: any;
  try {
    doc = await ctx.loadDoc(`jednani/${id}`);
  } catch {
    throw new Error(`Jednání „${id}“ nenalezeno. Správné id zjistíš nástrojem jednani.`);
  }
  const titulek = `${doc.oznaceni ?? id} (${czd(doc.datum)}) — program a usnesení${bodNum !== undefined ? `, bod ${bodNum}` : ""}`;
  const head = clean({
    n: ctx.cite(titulek, `/jednani/#${doc.id ?? id}`),
    id: doc.id ?? id,
    oznaceni: doc.oznaceni,
    datum: doc.datum,
    stav: doc.datum > ctx.today ? "plánováno (ještě se nekonalo)" : undefined,
    misto: doc.misto,
    dostupne: doc.dostupne,
    poznamka: doc.poznamka,
  });
  const body: any[] = doc.body ?? [];
  const extra = {
    ...(doc.text_dokumentu ? { text_dokumentu: short(doc.text_dokumentu, 3000) } : {}),
  };

  if (bodNum !== undefined) {
    const b = body.find((x) => x.n === bodNum);
    if (!b) {
      const cisla = body.map((x) => x.n).join(", ");
      throw new Error(`Bod ${bodNum} v jednání ${doc.oznaceni ?? id} neexistuje. Body: ${cisla || "žádné"}.`);
    }
    return { ...head, bod: docItem(b, 900, 500), ...extra };
  }

  const ostatni: any[] = doc.usneseni_ostatni ?? [];
  const ostatniOut = (u: number) =>
    ostatni.length
      ? ostatni.map((r) => clean({ cislo: r.cislo, text: short(r.text, u), hlasovani: r.hlasovani, neprijato: r.neprijato, poznamka: r.poznamka }))
      : undefined;
  for (const [z, u] of DOC_LEVELS) {
    const out = { ...head, body: body.map((b) => docItem(b, z, u)), usneseni_ostatni: ostatniOut(u), ...extra };
    if (!out.usneseni_ostatni) delete (out as any).usneseni_ostatni;
    if (JSON.stringify(out).length <= DOC_MAX_CHARS) return z < 900 ? { ...out, poznamka_zkraceni: "Dlouhé texty jsou zkrácené; detail bodu: cti_dokument(id, bod)." } : out;
  }
  // i nejstručnější verze je dlouhá: bez zpráv, bodů ubývá od konce
  const [z, u] = DOC_LEVELS[DOC_LEVELS.length - 1];
  const items = body.map((b) => docItem(b, z, u));
  while (items.length > 1) {
    const out = { ...head, body: items, ...extra };
    if (JSON.stringify(out).length <= DOC_MAX_CHARS - 200) break;
    items.pop();
  }
  return {
    ...head,
    body: items,
    ...extra,
    zkraceno: `Zobrazeno ${items.length} z ${body.length} bodů; další jsou dostupné přes cti_dokument(id, bod).`,
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

// ---------- uredni_deska ----------

const UD_MAX = 20;
const UD_MAX_YEARS = 3;

function slugCz(t: string): string {
  return fold(t).replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

/** odkaz na detail dokumentu: číslo → pecky.cz/default/report/<číslo>_<slug názvu>, as4u:<id> → starý web */
export function udUrl(id: string, nazev: string): string {
  if (id.startsWith("as4u:"))
    return `https://pecky.as4u.cz/redakce/index.php?lanG=cs&clanek=106922&slozka=106925&detail_claim=${id.slice(5)}`;
  return `https://pecky.cz/default/report/${id.includes("_") ? id : `${id}_${slugCz(nazev)}`}`;
}

function addDays(iso: string, days: number): string {
  const d = new Date(iso + "T12:00:00Z");
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}

async function uredniDeskaTool(input: any, ctx: ToolContext) {
  const hledej = str(input.hledej, "hledej");
  let doo = isoOrUndef(input.do, "do") ?? ctx.today;
  let od = isoOrUndef(input.od, "od") ?? addDays(doo, -365);
  if (doo < od) [od, doo] = [doo, od];
  const y0 = Number(od.slice(0, 4));
  const y1 = Number(doo.slice(0, 4));
  if (y1 - y0 + 1 > UD_MAX_YEARS) throw new Error(`Rozsah od–do může zasahovat nejvýš do ${UD_MAX_YEARS} roků.`);
  const kws = hledej ? keywordStems(hledej) : [];
  const rows: any[][] = [];
  for (let y = y1; y >= Math.max(y0, 2015); y--) {
    let doc: any;
    try {
      doc = await ctx.loadDoc(`uredni-deska/${y}`);
    } catch {
      continue; // rok bez dat
    }
    for (const r of (doc.d ?? []) as any[][]) {
      if (!r[0] || r[0] < od || r[0] > doo) continue;
      if (kws.length) {
        const hay = fold(`${r[3]} ${r[2]}`);
        if (!kws.every((k) => hay.includes(k))) continue;
      }
      rows.push(r);
    }
  }
  rows.sort((a, b) => b[0].localeCompare(a[0]));
  const shown = rows.slice(0, UD_MAX);
  return {
    od,
    do: doo,
    celkem: rows.length,
    ...(rows.length > shown.length ? { zobrazeno: shown.length } : {}),
    dokumenty: shown.map((r) =>
      clean({
        n: ctx.cite(`Úřední deska — ${short(r[3], 80)} (${czd(r[0])})`, udUrl(String(r[4]), String(r[3]))),
        vyveseno: r[0],
        sejmuto: r[1],
        typ: r[2],
        nazev: short(r[3], 140),
      }),
    ),
    poznamka:
      "Úřední deska od června 2015, jen názvy a data (ne obsah dokumentů); starší roky mohou být neúplné. Obsah zasedání: jednani + cti_dokument.",
  };
}

// ---------- registr ----------

type Exec = (input: any, ctx: ToolContext) => Promise<unknown>;

export const TOOL_DEFS = [
  {
    name: "hledej_text",
    description:
      "Znovu prohledá textový rejstřík webu jiným dotazem; vrátí až 6 úryvků s titulkem a odkazem. Použij, když dodané zdroje na otázku neodpovídají. Volitelně omezí typ zdroje; starší jednání z úřední desky (2013 – duben 2021) se hledají jen s typem „archiv“ nebo když dotaz zmiňuje rok do 2021 či „dříve/historie“.",
    input_schema: {
      type: "object",
      properties: {
        dotaz: { type: "string", description: "Dotaz nebo klíčová slova česky." },
        typ: { type: "string", enum: ["Lidé", "Kalendář", "Organizace", "Web", "jednání", "komise", "noviny", "archiv"], description: "Volitelně jen tento typ zdroje; „archiv“ = starší jednání z úřední desky 2013–2021." },
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
      "Akce z kalendáře webu v rozmezí dat (včetně vícedenních akcí), seřazené po dnech, a pravidelné série. Nejvýš 25 akcí. Pro „tento víkend / týden / příští týden“ zadej celý rozsah (pondělí–neděle). Data v ISO tvaru RRRR-MM-DD, spočítej je z dnešního data.",
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
    name: "svoz",
    description:
      "Nejbližší termíny svozu odpadu z domácností (komunální, BIO, plast, papír) podle lokality: Pečky sever a Velké Chvalovice, Pečky jih, Pečky sídliště. Vrátí po třech nejbližších termínech od dnešního dne a pravidlo svozu. Bez parametrů vrátí všechny lokality a druhy.",
    input_schema: {
      type: "object",
      properties: {
        lokalita: { type: "string", description: "„sever“ (vč. Velkých Chvalovic), „jih“ nebo „sídliště“; bez ní všechny tři." },
        druh: { type: "string", description: "„komunální“, „bio“, „plast“ nebo „papír“; bez něj všechny čtyři." },
      },
      additionalProperties: false,
    },
  },
  {
    name: "jednani",
    description:
      "Seznam jednání (zastupitelstvo, rada, komise, výbory, školská rada) od nejnovějšího, nejvýš 15, s id, označením, datem, počtem bodů a příznakem dostupne (pozvanka/zapis/usneseni). Jen názvy bodů, ne obsah. Pro „poslední rada/zasedání“, „co se probíralo naposledy“ použij nejnovejsi=true (s typem vrátí dvě nejnovější, protože nejnovější může mít zatím jen pozvánku) a potom zavolej cti_dokument(id). Volitelně filtr typu, období a slov v názvech bodů.",
    input_schema: {
      type: "object",
      properties: {
        typ: { type: "string", description: "např. „zastupitelstvo“, „rada“, „finanční výbor“, „komise“." },
        od: { type: "string", description: "RRRR-MM-DD" },
        do: { type: "string", description: "RRRR-MM-DD" },
        hledej: { type: "string", description: "Slova z názvu bodu programu." },
        nejnovejsi: { type: "boolean", description: "true = jen nejnovější jednání (s typem dvě, bez typu nejnovější od každého druhu)." },
      },
      additionalProperties: false,
    },
  },
  {
    name: "cti_dokument",
    description:
      "Přečte obsah jednání podle jeho id (z nástroje jednani): všechny body programu s předkladatelem, důvodovou zprávou, usneseními a výsledky hlasování. S parametrem bod vrátí jeden bod podrobně. Pole dostupne říká, co je zveřejněno; když je jen pozvanka, zápis a usnesení ještě nevyšly. Použij na otázky, co se na jednání probíralo, schválilo nebo jak se hlasovalo, a po nástroji jednani.",
    input_schema: {
      type: "object",
      properties: {
        id: { type: "string", description: "Id jednání, např. „rada-2026-10-12“ nebo „zastupitelstvo-2026-10-07“." },
        bod: { type: "integer", description: "Volitelně číslo bodu programu pro podrobný výpis jen tohoto bodu." },
      },
      required: ["id"],
      additionalProperties: false,
    },
  },
  {
    name: "uredni_deska",
    description:
      "Dokumenty z úřední desky města (od 2015) podle slov v názvu a data vyvěšení: záměry pronájmu a prodeje, veřejné vyhlášky, výběrová řízení, rozpočty, pozvánky a zápisy. Jen názvy, data a odkazy; nejvýš 20 nejnovějších. Bez dat hledá v posledním roce; rozsah nejvýš 3 roky. Data RRRR-MM-DD.",
    input_schema: {
      type: "object",
      properties: {
        hledej: { type: "string", description: "Slova z názvu dokumentu, např. „záměr pronájem“." },
        od: { type: "string", description: "Vyvěšeno od, RRRR-MM-DD." },
        do: { type: "string", description: "Vyvěšeno do, RRRR-MM-DD." },
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
  svoz: svozTool,
  jednani: jednaniTool,
  cti_dokument: ctiDokumentTool,
  uredni_deska: uredniDeskaTool,
  pocet_bodu: pocetBoduTool,
};

export function isKnownTool(name: string): boolean {
  return Object.hasOwn(EXEC, name);
}

export const MAX_RESULT_CHARS = 6000; // ≈ 1500 tokenů
const RESULT_LIMIT: Record<string, number> = { cti_dokument: DOC_MAX_CHARS + 500 }; // čtení celého jednání

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
    const limit = RESULT_LIMIT[name] ?? MAX_RESULT_CHARS;
    if (s.length > limit) s = s.slice(0, limit) + "…[výsledek zkrácen]";
    return { content: s, isError: false };
  } catch (e) {
    return { content: `Nástroj selhal: ${e instanceof Error ? e.message : String(e)}`, isError: true };
  }
}
