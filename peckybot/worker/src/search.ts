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
const CALENDAR_BOOST = 1.5;
const REF_BOOST = 2;
const DATE_BOOST = 1.8;

const CONTACT_RE = /\b(telefon\w*|mobil\w*|e-?mail\w*|kontakt\w*)/;
const WHO_RE = /\bkdo (je|jsou|byl|byla|byli)\b|\b(starost\w*|mistostarost\w*|zastupitel\w*|radni\w*)\b/;
const CALENDAR_RE = /\b(kdy|akce|akci|akcich|dnes|zitra|pozitri|vikend\w*|tyden|tydne|koncert\w*|kalendar\w*|plakat\w*|program)\b/;

export interface Intent {
  contact: boolean;
  who: boolean;
  calendar: boolean;
  refs: string[]; // např. "RM 5/2026"
  dates: string[]; // ISO RRRR-MM-DD
}

export function detectIntent(query: string): Intent {
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
  return {
    contact: CONTACT_RE.test(q),
    who: WHO_RE.test(q),
    calendar: CALENDAR_RE.test(q),
    refs,
    dates,
  };
}

export interface SearchOptions {
  context?: string; // předchozí otázka (nižší váha)
  perUrlCap?: number; // max. úryvků ze stejného odkazu, pokud skóre není dominantní
}

const DEFAULT_CAP = 4;
const DOMINANT = 0.8; // úryvek se skóre >= 80 % nejlepšího se do limitu nepočítá

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

  const intent = detectIntent(query);
  const boosted = [...scores.entries()].map(([id, score]) => {
    const c = index.chunks[id];
    let f = 1;
    if (c.t.startsWith("Lidé —")) {
      if (intent.contact) f *= PEOPLE_BOOST;
      else if (intent.who) f *= WHO_BOOST;
    }
    if (intent.calendar && c.t.startsWith("Kalendář")) f *= CALENDAR_BOOST;
    if (intent.refs.some((r) => c.t.startsWith(r + " "))) f *= REF_BOOST;
    if (intent.dates.some((d) => c.u.includes(d))) f *= DATE_BOOST;
    return { id, score: score * f };
  });
  boosted.sort((a, b) => b.score - a.score || b.id - a.id); // při shodě novější úryvek

  const cap = opts.perUrlCap ?? DEFAULT_CAP;
  const top = boosted[0].score;
  const out: Hit[] = [];
  const overflow: Hit[] = [];
  const perUrl = new Map<string, number>();
  for (const h of boosted) {
    if (out.length >= k) break;
    const u = index.chunks[h.id].u;
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
