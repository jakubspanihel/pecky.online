-- Anonymní záznamy dotazů, hodnocení a cache odpovědí PečkyBota (Cloudflare D1, databáze peckybot-log).
-- Žádná IP adresa, cookie ani identifikátor návštěvníka. Záznamy starší než 90 dní Worker maže sám.
-- Použití: npx wrangler d1 execute peckybot-log --remote --file=schema.sql   (bezpečné spustit opakovaně)

CREATE TABLE IF NOT EXISTS dotazy (
  id           TEXT PRIMARY KEY,      -- náhodných 12 znaků
  ts           TEXT NOT NULL,         -- ISO čas (UTC)
  den          TEXT NOT NULL,         -- RRRR-MM-DD podle pražského času
  dotaz        TEXT NOT NULL,         -- nejvýš 300 znaků, bez e-mailů a telefonních čísel
  predchozi    INTEGER NOT NULL DEFAULT 0, -- počet předchozích zpráv v konverzaci
  zdroje       TEXT,                  -- JSON: titulky zdrojů citovaných v odpovědi
  nalezeno     TEXT,                  -- JSON: titulky nalezených úryvků (nejvýš 8)
  nastroje     TEXT,                  -- JSON: názvy použitých nástrojů
  model        TEXT,
  vstup_tok    INTEGER,
  vystup_tok   INTEGER,
  naklad_mikro INTEGER,               -- odhad nákladu v mikro-USD
  z_cache      INTEGER NOT NULL DEFAULT 0,
  nevim        INTEGER NOT NULL DEFAULT 0, -- odpověď říká, že informace nemá
  ms           INTEGER,
  chyba        TEXT,                  -- kód chyby, pokud odpověď selhala
  eval         INTEGER NOT NULL DEFAULT 0  -- 1 = měřicí dotaz (X-Eval-Token), statistiky ho přeskakují
);
CREATE INDEX IF NOT EXISTS dotazy_den ON dotazy (den);
CREATE INDEX IF NOT EXISTS dotazy_ts ON dotazy (ts);

CREATE TABLE IF NOT EXISTS hodnoceni (
  id   TEXT PRIMARY KEY REFERENCES dotazy (id),
  ts   TEXT NOT NULL,
  hlas INTEGER NOT NULL CHECK (hlas IN (1, -1))
);

CREATE TABLE IF NOT EXISTS odpovedi_cache (
  klic    TEXT PRIMARY KEY,           -- sha-256(den + normalizovaný dotaz)
  ts      TEXT NOT NULL,
  odpoved TEXT NOT NULL               -- JSON {answer, sources}
);
CREATE INDEX IF NOT EXISTS odpovedi_cache_ts ON odpovedi_cache (ts);
