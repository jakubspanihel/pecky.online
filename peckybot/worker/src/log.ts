// Anonymní záznamy dotazů, hodnocení a cache odpovědí v D1 (schema.sql).
// Neukládá se IP adresa ani nic, co návštěvníka identifikuje. Chyba D1 nikdy nesmí rozbít odpověď.
import type { AnswerResult } from "./common.ts";

export const MAX_LOGGED_QUERY = 300;
export const RETENTION_DAYS = 90;
export const CACHE_TTL_MS = 6 * 3600 * 1000;
export const FEEDBACK_WINDOW_MS = 24 * 3600 * 1000;
export const PURGE_PROBABILITY = 1 / 50;

/** Nahradí e-maily, telefonní čísla a dlouhé číselné řady a zkrátí dotaz. */
export function scrubQuery(q: string): string {
  return q
    .replace(/[^\s@<>()]+@[^\s@<>()]+\.[^\s@<>()]+/g, "[e-mail]")
    .replace(/\+?\d(?:[ .\- ]?\d){5,}/g, (m) => {
      const digits = m.replace(/\D/g, "").length;
      return m.startsWith("+") || (digits >= 9 && digits <= 12) ? "[telefon]" : "[číslo]";
    })
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, MAX_LOGGED_QUERY);
}

/** Malá písmena, bez diakritiky, interpunkce a vícenásobných mezer. */
export function normalizeQuery(q: string): string {
  return q
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

const HEDGE =
  /\b(nemam|neni v urycich|neni v dodanych|zdroje (?:to |tuto informaci |tyto informace )?neuvadeji|nenasel|nenalezl|nelze zjistit|nevyplyva|nevim)/;

/** Odpověď říká, že informaci nemá (nepodložená otázka). */
export function isHedge(answer: string): boolean {
  return HEDGE.test(normalizeQuery(answer));
}

export async function sha256Hex(s: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export function newId(): string {
  const alphabet = "abcdefghijklmnopqrstuvwxyz0123456789";
  const bytes = crypto.getRandomValues(new Uint8Array(12));
  return [...bytes].map((b) => alphabet[b % alphabet.length]).join("");
}

export const isValidId = (id: unknown): id is string => typeof id === "string" && /^[a-z0-9]{12}$/.test(id);

/** Porovnání bez závislosti doby na shodné délce předpony. */
export function safeEqual(a: string, b: string): boolean {
  const ea = new TextEncoder().encode(a);
  const eb = new TextEncoder().encode(b);
  let diff = ea.length ^ eb.length;
  const n = Math.max(ea.length, eb.length);
  for (let i = 0; i < n; i++) diff |= (ea[i] ?? 0) ^ (eb[i] ?? 0);
  return diff === 0;
}

export interface LogEntry {
  id: string;
  query: string;
  previous: number;
  result?: Partial<AnswerResult>;
  fromCache?: boolean;
  hedge?: boolean;
  ms: number;
  error?: string;
  eval?: boolean;
  day: string;
}

/** Zapíše řádek do dotazy; nikdy nevyhazuje výjimku. */
export async function writeLog(db: D1Database | undefined, e: LogEntry): Promise<void> {
  if (!db) return;
  try {
    const r = e.result ?? {};
    const m = r.meta;
    await db
      .prepare(
        `INSERT INTO dotazy (id, ts, den, dotaz, predchozi, zdroje, nalezeno, nastroje, model, vstup_tok, vystup_tok, naklad_mikro, z_cache, nevim, ms, chyba, eval)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      )
      .bind(
        e.id,
        new Date().toISOString(),
        e.day,
        scrubQuery(e.query),
        e.previous,
        JSON.stringify((r.sources ?? []).map((s) => s.title)),
        JSON.stringify((m?.retrieved ?? []).slice(0, 8)),
        JSON.stringify(m?.tools ?? []),
        m?.model ?? null,
        e.fromCache ? 0 : (m?.inputTokens ?? null),
        e.fromCache ? 0 : (m?.outputTokens ?? null),
        e.fromCache ? 0 : (m?.costMicro ?? null),
        e.fromCache ? 1 : 0,
        e.hedge ? 1 : 0,
        Math.round(e.ms),
        e.error ?? null,
        e.eval ? 1 : 0,
      )
      .run();
  } catch (err) {
    console.error("peckybot záznam selhal:", err instanceof Error ? err.name : "chyba");
  }
}

// ---------- cache ----------

export interface CachedAnswer {
  answer: string;
  sources: { n: number; title: string; url: string }[];
}

export async function cacheKey(day: string, query: string): Promise<string> {
  return sha256Hex(`${day}|${normalizeQuery(query)}`);
}

export async function cacheGet(db: D1Database | undefined, key: string, now = Date.now()): Promise<CachedAnswer | null> {
  if (!db) return null;
  try {
    const row = await db
      .prepare("SELECT odpoved FROM odpovedi_cache WHERE klic = ? AND ts > ?")
      .bind(key, new Date(now - CACHE_TTL_MS).toISOString())
      .first<{ odpoved: string }>();
    return row ? (JSON.parse(row.odpoved) as CachedAnswer) : null;
  } catch {
    return null;
  }
}

export async function cachePut(db: D1Database | undefined, key: string, value: CachedAnswer): Promise<void> {
  if (!db) return;
  try {
    await db
      .prepare("INSERT OR REPLACE INTO odpovedi_cache (klic, ts, odpoved) VALUES (?, ?, ?)")
      .bind(key, new Date().toISOString(), JSON.stringify(value))
      .run();
  } catch (err) {
    console.error("peckybot cache selhala:", err instanceof Error ? err.name : "chyba");
  }
}

// ---------- hodnocení ----------

export type VoteResult = "ok" | "bad_request" | "not_found" | "expired" | "unavailable";

export async function saveVote(db: D1Database | undefined, body: unknown, now = Date.now()): Promise<VoteResult> {
  const id = (body as { id?: unknown })?.id;
  const hlas = (body as { hlas?: unknown })?.hlas;
  if (!isValidId(id) || (hlas !== 1 && hlas !== -1)) return "bad_request";
  if (!db) return "unavailable";
  try {
    const row = await db.prepare("SELECT ts FROM dotazy WHERE id = ?").bind(id).first<{ ts: string }>();
    if (!row) return "not_found";
    if (now - Date.parse(row.ts) > FEEDBACK_WINDOW_MS) return "expired";
    await db
      .prepare(
        "INSERT INTO hodnoceni (id, ts, hlas) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET ts = excluded.ts, hlas = excluded.hlas",
      )
      .bind(id, new Date(now).toISOString(), hlas)
      .run();
    return "ok";
  } catch (err) {
    console.error("peckybot hodnocení selhalo:", err instanceof Error ? err.name : "chyba");
    return "unavailable";
  }
}

// ---------- uklízení ----------

export async function purgeOld(db: D1Database | undefined, now = Date.now()): Promise<void> {
  if (!db) return;
  try {
    const cutoff = new Date(now - RETENTION_DAYS * 86400_000).toISOString();
    await db.prepare("DELETE FROM hodnoceni WHERE id IN (SELECT id FROM dotazy WHERE ts < ?)").bind(cutoff).run();
    await db.prepare("DELETE FROM dotazy WHERE ts < ?").bind(cutoff).run();
    await db
      .prepare("DELETE FROM odpovedi_cache WHERE ts < ?")
      .bind(new Date(now - 24 * 3600 * 1000).toISOString())
      .run();
  } catch (err) {
    console.error("peckybot úklid selhal:", err instanceof Error ? err.name : "chyba");
  }
}
