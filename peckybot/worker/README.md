# PečkyBot Worker

Cloudflare Worker, který odpovídá na dotazy z `/peckybot/`. Přehled architektury,
rozpočtu a zapínání je v `../README.md`; tady je jen postup nasazení.

## Jednorázové nasazení

Potřebný je účet Cloudflare (stačí Free) a klíč k Claude API s nastaveným **měsíčním
limitem útraty** v Anthropic Console.

```bash
cd peckybot/worker
npm install
npx wrangler login

# 1. KV pro počítadla; vypsané id vložit do wrangler.toml (kv_namespaces → id)
npx wrangler kv namespace create BUDGET

# 2. API klíč jako secret (nikdy do gitu ani do wrangler.toml)
npx wrangler secret put ANTHROPIC_API_KEY

# 3. D1 pro záznamy, hodnocení a cache (databázi vytvořit jen poprvé: npx wrangler d1 create peckybot-log);
#    schéma lze spustit opakovaně
npx wrangler d1 execute peckybot-log --remote --file=schema.sql

# 3b. volitelně: tajný token pro měřicí dotazy (obejde limit na IP a cache, ne rozpočet)
npx wrangler secret put EVAL_TOKEN

# 4. nasazení; vypíše adresu https://peckybot.<účet>.workers.dev
npx wrangler deploy
```

Pak do `../config.json` vepsat `{"api": "https://peckybot.<účet>.workers.dev/chat"}`,
spustit `python3 scripts/build.py` a publikovat.

Před zapnutím zkontrolovat v `wrangler.toml`:
- `ALLOWED_ORIGINS` — domény, ze kterých smí prohlížeč volat Worker (výchozí `https://dopecek.cz`). Pro místní test přidat `http://localhost:8000`.
- `SITE_URL` — odkud se stahuje index (musí už být publikovaný `peckybot/index.json`).
- `MONTHLY_BUDGET_USD`, `DAILY_PER_IP`, `DAILY_GLOBAL` — viz `../README.md`.

## Místní vývoj

```bash
echo 'ANTHROPIC_API_KEY=sk-ant-…' > .dev.vars   # v .gitignore
npx wrangler dev
```
Worker poběží na `http://localhost:8787`; pro test z `localhost:8000` přidat obě adresy
do `ALLOWED_ORIGINS` a do `config.json` dát `http://localhost:8787/chat`.

## Bezpečnost a provoz
- API klíč je jen secret Workeru. Worker odmítá požadavky bez povoleného `Origin`.
- Do logů Workeru se neukládá obsah dotazů, jen chyby. Anonymní záznamy dotazů jsou v D1 (viz `../README.md` → „Záznamy a hodnocení“).
- V Cloudflare doporučeno přidat pravidlo Rate Limiting na `/chat` (např. 10 požadavků za minutu na IP); počítadla v KV chrání rozpočet, ne před zahlcením.
- KV počítadla nejsou atomická, odhad útraty se může při souběhu lehce rozejít; proto rezerva ve stropu a tvrdý limit u Anthropic.
- Zhroutí-li se kvůli limitu CPU na Free plánu načtení indexu (v logu chyba „exceeded CPU“), přejít na Workers Paid (5 USD/měsíc) nebo zmenšit index (`MAX_CHUNK`, `MIN_CHUNK` v `scripts/build_peckybot_index.py`).

## Testy
`npm test` (Node 22+) — vyhledávání nad skutečným indexem, shoda tokenizace s Pythonem, odpověď se zdroji, limity na IP, měsíční rozpočet, neplatný vstup. `npm run typecheck` — TypeScript.
