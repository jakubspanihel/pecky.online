# PečkyBot

Robot (AI), který sestavuje projekt pecky.online. Maskot PečkyBot (`img/peckybot/`:
`welcome.png`, `thinking.png`, `error.png`) se objevuje v patičce a od 5. 10. 2026
je i chatbotem na stránce `/peckybot/`. V této složce jsou uloženy jeho jednotlivé skilly.

## Chatbot (`/peckybot/`)

Návštěvník píše dotaz, stránka ho pošle Cloudflare Workeru, ten v indexu webu najde
nejlepší úryvky a se zdroji se zeptá Claude API. Odpověď přijde s odkazy na zdroj
(`[1]` → odkaz na jednání, osobu nebo sekci).

```
prohlížeč (content/peckybot.html)
   │  POST /chat {messages}
   ▼
Cloudflare Worker (peckybot/worker/)  ── limity a rozpočet ──▶ KV (BUDGET)
   │  1. hledá v peckybot/index.json + peckybot/chunks/*.json (stahuje z webu)
   │  2. volá Claude API (ANTHROPIC_API_KEY je jen secret ve Workeru)
   ▼
odpověď {answer, sources}
```

| Soubor | Co to je |
|---|---|
| `content/peckybot.html` | stránka s chatem (tělo panelu), `needit` vygenerovaný `peckybot/index.html` |
| `config.json` | `{"api": "<URL Workeru>/chat"}`; prázdné = chatbot vypnutý (stránka ukáže „zatím není spuštěný“) |
| `index.json`, `chunks/*.json` | znalostní index, **generuje build** (`scripts/build_peckybot_index.py`), ručně needitovat |
| `worker/` | kód Cloudflare Workeru + testy, postup nasazení v `worker/README.md` |

### Co je v indexu
- jednání zastupitelstva a rady (`jednani/pecky-jednani.json`): bod programu, důvodová zpráva, usnesení s hlasováním; odkaz `/jednani/#<id>`
- lidé s vyplněným životopisem (`lide/people.json`)
- statické texty sekcí Plán, Tělocvična, Pozemky, Pokladna, Smlouvy, Zakázky, Volby, O webu

Mimo index zatím jsou Pečecké noviny, kalendář, komise, výbory a školská rada.
Index se přegeneruje při každém `python3 scripts/build.py`; kolik úryvků se zapsalo,
vypíše build. Soubory se přepisují jen při změně obsahu a nová jednání přibývají na
konec, takže v gitu se mění hlavně rejstřík a poslední dávky.

### Rozpočet (10 USD měsíčně)
- Worker na Cloudflare Free (100 000 požadavků denně) stojí 0 Kč. Rejstřík je malý (≈ 1 MB) a texty se stahují po dávkách právě kvůli limitu CPU na volání.
- Claude API: výchozí model `claude-sonnet-5-5` (2 / 10 USD za milion vstupních / výstupních tokenů). Typický dotaz (≈ 5 000 vstupních a ≈ 400 výstupních tokenů) vychází na ≈ 0,014 USD, měsíční strop 8 USD tak vystačí na zhruba 550 dotazů.
- Worker si počítá odhad útraty z `usage` v KV a po dosažení `MONTHLY_BUDGET_USD` (8) přestane odpovídat. Zbylé 2 USD jsou rezerva na odchylku odhadu. Navíc nastavit **měsíční limit útraty v Anthropic Console** (tvrdý strop).
- Další pojistky: `DAILY_PER_IP` (15 dotazů na IP za den), `DAILY_GLOBAL` (250 dotazů za den), délka dotazu 600 znaků, `max_tokens` 1500, jen povolený `Origin`.

### Model a změna rozpočtu
Model se mění v `worker/wrangler.toml` (`MODEL`). Levnější `claude-haiku-4-5` (1 / 5 USD) zhruba zdvojnásobí počet dotazů, dražší `claude-opus-5-5` (4 / 20 USD) ho zhruba zmenší na polovinu. Ceny jsou v `PRICES` v `worker/src/index.ts`; neznámý model se počítá nejdražší sazbou.

### Texty a pravidla odpovědí
Pravidla pro model jsou v `worker/src/prompt.ts` (odpovídat jen ze zdrojů, uvádět `[n]`, česky, bez „my“, nehodnotit politiky, bez právních rad). Při změně pravidel nebo copywritingu upravit tam.

### Zapnutí a vypnutí
1. Nasadit Worker podle `worker/README.md`.
2. Vepsat jeho URL do `config.json` (`"api": "https://…/chat"`), build, commit, push.
3. Teprve potom přidat odkaz na `/peckybot/` do `assets/nav.html` nebo `assets/footer.html`.
4. Vypnout: `"api": ""`.

### Ověření
- `cd peckybot/worker && npm test` — vyhledávání, shoda tokenizace s Pythonem, limity, rozpočet (volání Claude API je v testu napodobené).
- `npm run typecheck`.
