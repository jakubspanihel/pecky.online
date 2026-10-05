// Vyhledávání v indexu peckybot/index.json (generuje scripts/build_peckybot_index.py).
// tokenize() MUSÍ dávat stejné tokeny jako tokenize() v tom skriptu.

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

export function search(index: Index, query: string, k: number): Hit[] {
  const n = index.chunks.length;
  const scores = new Map<number, number>();
  for (const tok of new Set(tokenize(query))) {
    const list = index.post[tok];
    if (!list) continue;
    const idf = Math.log(1 + n / (list.length / 2));
    for (let i = 0; i < list.length; i += 2) {
      const id = list[i];
      const tf = list[i + 1];
      scores.set(id, (scores.get(id) ?? 0) + (1 + Math.log(tf)) * idf);
    }
  }
  return [...scores.entries()]
    .map(([id, score]) => ({ id, score }))
    .sort((a, b) => b.score - a.score || b.id - a.id) // při shodě novější úryvek
    .slice(0, k);
}
