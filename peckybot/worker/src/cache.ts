// Cache odpovědí na jednozónové dotazy; úložiště je D1 (ne KV, ať se neplýtvá zápisy).
export { cacheGet, cacheKey, cachePut, CACHE_TTL_MS } from "./log.ts";
export type { CachedAnswer } from "./log.ts";
