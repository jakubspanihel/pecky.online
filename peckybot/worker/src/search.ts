// Vyhledávání v indexu peckybot/index.json (generuje scripts/build_peckybot_index.py).
// tokenize() MUSÍ dávat stejné tokeny jako tokenize() v tom skriptu (proto se nemění);
// zlepšení probíhají v době dotazu: synonyma, prefixová shoda, boosty záměru, diverzita.

import { SYNONYM_GROUPS } from "./synonyms.ts";

export interface Index {
  v: number;
  shard: number;
  chunks: { u: string; t: string }[];
  post: Record<string, number[]>; // token -> [idx, tf, idx, tf, ...]
}

export interface Hit {
  id: number;
  score: number;
}

const STEM_LEN = 6;
const STOPWORDS = new Set([
  "aby", "ale", "ani", "jak", "jako", "jsou", "jeho", "jejich", "kde", "kdy",
  "kteri", "ktery", "ktera", "ktere", "nebo", "pri", "pro", "proc", "tak",
  "ten", "the", "toho", "tom", "tato", "tyto", "byl", "byla", "bylo", "byt",
  "bude", "jsem", "jste", "jsme", "mesto", "mesta", "mestem", "pecky", "pecek",
  "peckach", "cislo", "cisl", "dle", "ode", "napr", "tzn", "atd",
]);

export function tokenize(text: string): string[] {
  const s = text.toLowerCase().normalize("NFD").replace(/\p{M}/gu, "");
  const out: string[] = [];
  for (const w of s.match(/[a-z0-9]+/g) ?? []) {
    if (w.length < 3 || STOPWORDS.has(w)) continue;
    out.push(w.slice(0, STEM_LEN));
  }
  return out;
}

function fold(text: string): string {
  return text.toLowerCase().normalize("NFD").replace(/\p{M}/gu, "");
}

// ---- synonyma ----
const SYN_WEIGHT = 0.5;
const SYN_BUDGET = 0.8; // max. součet vah synonym jednoho tokenu
const PREFIX_WEIGHT = 0.4;
const CONTEXT_WEIGHT = 0.5; // váha tokenů z předchozí otázky

let synMap: Map<string, string[]> | null = null;
function synonymsOf(tok: string): string[] {
  if (!synMap) {
    synMap = new Map();
    for (const group of SYNONYM_GROUPS) {
      const stems = [...new Set(group.flatMap(tokenize))];
      for (const s of stems) {
        const cur = synMap.get(s) ?? [];
        for (const o of stems) if (o !== s && !cur.includes(o)) cur.push(o);
        synMap.set(s, cur);
      }
    }
  }
  return synMap.get(tok) ?? [];
}

// ---- prefixová shoda (jen pro tokeny bez přesné shody) ----
const prefixCache = new WeakMap<Index, Map<string, string[]>>();
function prefixMap(index: Index): Map<string, string[]> {
  let m = prefixCache.get(index);
  if (!m) {
    m = new Map();
    for (const key of Object.keys(index.post)) {
      for (const len of [4, 5]) {
        if (key.length > len) {
          const p = key.slice(0, len);
          const arr = m.get(p);
          if (arr) arr.push(key);
          else m.set(p, [key]);
        }
      }
    }
    prefixCache.set(index, m);
  }
  return m;
}

function fuzzyKeys(index: Index, tok: string): string[] {
  const m = prefixMap(index);
  const tries = tok.length >= STEM_LEN ? [tok.slice(0, 5), tok.slice(0, 4)] : tok.length <= 5 && tok.length >= 4 ? [tok] : [];
  for (const p of tries) {
    const keys = m.get(p);
    if (keys && keys.length) {
      // nejčastější klíče (největší posting) jako nejpravděpodobnější tvar, max 4
      return keys.slice().sort((a, b) => index.post[b].length - index.post[a].length).slice(0, 4);
    }
  }
  return [];
}

// ---- záměr dotazu ----
const PEOPLE_BOOST = 1.8;
const WHO_BOOST = 1.4;
const ROLE_BOOST = 1.2; // obecné slovo role bez „kdo je“ (starosta, zastupitel…)
const ORG_BOOST = 1.7;
const NUMBER_BOOST = 1.6;
const SUMMARY_BOOST = 1.3;
const WEB_NUMBER_BOOST = 1.0; // ostatní “Web —” úryvky beze změny (zvýšení na 1.2+ zhoršilo eval)
const ROSTER_BOOST = 2.2;
const JEDNANI_PENALTY = 0.75; // jednání při dotazu na osobu/složení
const PAKT_PENALTY = 0.5;
const CALENDAR_BOOST = 1.5;
const CAL_DATE_BOOST = 2.2;
const CAL_FUTURE_BOOST = 1.25;
const REF_BOOST = 2;
const DATE_BOOST = 1.8;

const CONTACT_RE = /\b(telefon\w*|mobil\w*|e-?mail\w*|kontakt\w*)/;
const WHO_RE = /\bkdo (je|jsou|byl|byla|byli)\b/;
const ROLE_RE = /\b(starost\w*|mistostarost\w*|zastupitel\w*|radni\w*|clen\w*|reditel\w*|predsed\w*)\b/;
const ORG_RE = /\b(knihovn\w*|skol[aeuy]|skolk\w*|restaurac\w*|spolek|spolk\w*|klub\w*|najist|najez\w*|hospod\w*|hospud\w*|kavarn\w*|hasic\w*|sokol\w*|organizac\w*|obed\w*|jidelna|jidelny)\b/;
const NUMBER_RE = /\b(kolik|stoji|stal\w*|plati\w*|poplat\w*|cena|cen[auy]|castk\w*|rozpocet|rozpoct\w*|dluh\w*|uver\w*|dotac\w*|naklad\w*|mil[ie]on\w*)\b/;
const ROSTER_RE = /\b(slozeni|starostov\w*|kolik je (zastupitel\w*|clenu|radnich)|kdo (sedi|zasedal\w*|je|jsou|byl\w*|zastupuje).*\b(rad[eayuě]|rade|zastupitelstv\w*|vybor\w*|komis\w*)|kdo byl\w* .*starost\w*|(clen\w*|sloz\w*).*\b(rad[ay]|vybor\w*|komis\w*|zastupitelstv\w*))/;
const CALENDAR_RE = /\b(kdy|akce|akci|akcich|dnes|zitra|pozitri|vikend\w*|tyden|tydne|koncert\w*|kalendar\w*|plakat\w*|program|sobot\w*|nedel\w*)\b/;

export interface Intent {
  contact: boolean;
  who: boolean;
  role: boolean;
  org: boolean;
  number: boolean;
  roster: boolean;
  history: boolean; // minulost: roky, „byl“, „po revoluci“, „dříve“
  calendar: boolean;
  namesPerson: boolean; // v dotazu je slovo s velkým písmenem mimo začátek (jméno)
  refs: string[]; // např. "RM 5/2026"
  dates: string[]; // ISO RRRR-MM-DD (z dotazu)
  calDates: string[]; // ISO data odvozená z „dnes/zítra/víkend/týden“
}

function iso(d: Date): string {
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}-${String(d.getUTCDate()).padStart(2, "0")}`;
}

// today = ISO datum (RRRR-MM-DD); relativní výrazy se počítají vůči němu
export function relativeDates(q: string, today: string): string[] {
  const t0 = new Date(today + "T00:00:00Z");
  if (isNaN(t0.getTime())) return [];
  const day = (n: number) => iso(new Date(t0.getTime() + n * 86400000));
  const dow = (t0.getUTCDay() + 6) % 7; // po=0 … ne=6
  const out: string[] = [];
  const range = (from: number, to: number) => { for (let i = from; i <= to; i++) out.push(day(i)); };
  if (/\bdnes\w*/.test(q)) out.push(day(0));
  if (/\bzitra\b/.test(q)) out.push(day(1));
  if (/\bpozitri\b/.test(q)) out.push(day(2));
  if (/\bvikend\w*/.test(q)) {
    const nextWeek = /\b(pristi|dalsi)\b/.test(q);
    const sat = nextWeek ? 12 - dow : 5 - dow;
    out.push(day(sat), day(sat + 1));
  }
  if (/\b(tento|tenhle|ten|tohoto) tyden\b|\btydne\b/.test(q) && !/\bpristi\b/.test(q)) range(0, 6 - dow);
  if (/\bpristi (tyden|tydne)\b/.test(q)) range(7 - dow, 13 - dow);
  return [...new Set(out)];
}

export function detectIntent(query: string, today?: string): Intent {
  const q = fold(query);
  const refs: string[] = [];
  const dates: string[] = [];
  for (const m of q.matchAll(/\b(rm|zm|rada|rady|zastupitelstv\w*)\s*(?:c\.?\s*)?(\d{1,3})\s*\/\s*(\d{4})\b/g)) {
    const kind = m[1] === "zm" || m[1].startsWith("zastup") ? "ZM" : "RM";
    refs.push(`${kind} ${Number(m[2])}/${m[3]}`);
  }
  for (const m of q.matchAll(/\bu([rz])\s*-\s*\d+\s*-\s*(\d{1,3})\s*\/\s*(\d{2})\b/g)) {
    refs.push(`${m[1] === "z" ? "ZM" : "RM"} ${Number(m[2])}/20${m[3]}`);
  }
  for (const m of q.matchAll(/\b(\d{1,2})\s*\.\s*(\d{1,2})\s*\.\s*(\d{4})\b/g)) {
    const [d, mo] = [Number(m[1]), Number(m[2])];
    if (d >= 1 && d <= 31 && mo >= 1 && mo <= 12) {
      dates.push(`${m[3]}-${String(mo).padStart(2, "0")}-${String(d).padStart(2, "0")}`);
    }
  }
  const words = query.split(/\s+/).slice(1);
  return {
    contact: CONTACT_RE.test(q),
    who: WHO_RE.test(q),
    role: ROLE_RE.test(q),
    org: ORG_RE.test(q),
    number: NUMBER_RE.test(q),
    roster: ROSTER_RE.test(q),
    history: /\b(byl\w*|\d{4}|revoluc\w*|drive|historie|minul\w*|davn\w*|predchozi)\b/.test(q),
    calendar: CALENDAR_RE.test(q),
    namesPerson: words.some((w) => /^\p{Lu}\p{Ll}{2,}/u.test(w)),
    refs,
    dates,
    calDates: today ? relativeDates(q, today) : [],
  };
}

export interface SearchOptions {
  context?: string; // předchozí otázka (nižší váha)
  perUrlCap?: number; // max. úryvků ze stejného odkazu, pokud skóre není dominantní
  today?: string; // RRRR-MM-DD (Praha); pro „dnes/zítra/víkend/tento týden“
}

const DEFAULT_CAP = 4;
const DOMINANT = 0.8; // úryvek se skóre >= 80 % nejlepšího se do limitu nepočítá

function chunkBoost(c: { u: string; t: string }, it: Intent, today?: string): number {
  let f = 1;
  const isPerson = c.t.startsWith("Lidé —");
  const isMeeting = c.t.startsWith("RM ") || c.t.startsWith("ZM ");
  const personIntent = it.who || it.roster || (it.contact && (it.role || it.namesPerson));
  if (isPerson) {
    if (it.contact && !it.org && (it.role || it.who || it.namesPerson)) f *= PEOPLE_BOOST;
    else if (it.who) f *= WHO_BOOST;
    else if (it.role && !it.org) f *= ROLE_BOOST;
  }
  if (it.org && c.t.startsWith("Organizace —")) f *= ORG_BOOST;
  if (it.number && c.t.startsWith("Web —")) f *= /shrnut/i.test(c.t) ? NUMBER_BOOST * SUMMARY_BOOST : WEB_NUMBER_BOOST;
  if (it.roster && /Složení|Starostové/.test(c.t)) f *= ROSTER_BOOST;
  else if (/^Starostové/.test(c.t) && !it.history && (it.who || it.role)) f *= 0.5; // přítomný čas: nejdřív aktuální osoba
  else if (/^Složení/.test(c.t) && !it.roster && it.who && it.role) f *= 0.7;
  if (isPerson && it.who && it.role && !it.history && !it.org) f *= PEOPLE_BOOST / WHO_BOOST;
  if (c.t.startsWith("Kalendář") && it.number && !it.calendar) f *= 0.6;
  if (personIntent && isMeeting) f *= JEDNANI_PENALTY;
  if (personIntent && /Pakt/.test(c.t)) f *= PAKT_PENALTY;
  if (c.t.startsWith("Kalendář")) {
    if (it.calendar) f *= CALENDAR_BOOST;
    const m = c.t.match(/\((\d{1,2})\. (\d{1,2})\. (\d{4})\)\s*$/);
    if (m) {
      const d = `${m[3]}-${m[2].padStart(2, "0")}-${m[1].padStart(2, "0")}`;
      if (it.calDates.includes(d) || it.dates.includes(d)) f *= CAL_DATE_BOOST;
      else if (it.calendar && today && d >= today) f *= CAL_FUTURE_BOOST;
    }
  }
  if (it.refs.some((r) => c.t.startsWith(r + " "))) f *= REF_BOOST;
  if (it.dates.some((d) => c.u.includes(d))) f *= DATE_BOOST;
  return f;
}

function addTerm(w: Map<string, number>, tok: string, weight: number) {
  if ((w.get(tok) ?? 0) < weight) w.set(tok, weight);
}

export function search(index: Index, query: string, k: number, opts: SearchOptions = {}): Hit[] {
  const n = index.chunks.length;
  const weights = new Map<string, number>();
  for (const t of tokenize(query)) addTerm(weights, t, 1);
  if (opts.context) for (const t of tokenize(opts.context)) addTerm(weights, t, CONTEXT_WEIGHT);
  for (const [t, w] of [...weights]) {
    const syns = synonymsOf(t);
    // celkový příspěvek synonym jednoho tokenu je omezen, ať nepřebije původní slovo
    const sw = Math.min(SYN_WEIGHT, SYN_BUDGET / Math.max(1, syns.length));
    for (const s of syns) addTerm(weights, s, w * sw);
  }
  for (const [t, w] of [...weights]) {
    if (index.post[t]) continue;
    for (const key of fuzzyKeys(index, t)) addTerm(weights, key, w * PREFIX_WEIGHT);
  }

  const scores = new Map<number, number>();
  for (const [tok, w] of weights) {
    const list = index.post[tok];
    if (!list) continue;
    const idf = Math.log(1 + n / (list.length / 2));
    for (let i = 0; i < list.length; i += 2) {
      const id = list[i];
      scores.set(id, (scores.get(id) ?? 0) + w * (1 + Math.log(list[i + 1])) * idf);
    }
  }
  if (scores.size === 0) return [];

  const intent = detectIntent(query, opts.today);
  const boosted = [...scores.entries()].map(([id, score]) => ({
    id,
    score: score * chunkBoost(index.chunks[id], intent, opts.today),
  }));
  boosted.sort((a, b) => b.score - a.score || b.id - a.id); // při shodě novější úryvek

  const cap = opts.perUrlCap ?? DEFAULT_CAP;
  const top = boosted[0].score;
  const out: Hit[] = [];
  const overflow: Hit[] = [];
  const perUrl = new Map<string, number>();
  for (const h of boosted) {
    if (out.length >= k) break;
    const c = index.chunks[h.id];
    // omezení platí jen pro jednání a stránky „Web“; osoby, organizace, akce mají jeden společný odkaz
    const u = c.u.startsWith("/jednani/") || c.t.startsWith("Web —") ? c.u : c.t;
    const cnt = perUrl.get(u) ?? 0;
    if (cnt >= cap && h.score < DOMINANT * top) overflow.push(h);
    else {
      out.push(h);
      perUrl.set(u, cnt + 1);
    }
  }
  for (const h of overflow) if (out.length < k) out.push(h); // nikdy nezahazovat výsledky
  return out;
}
