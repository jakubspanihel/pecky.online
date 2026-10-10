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
Zdroje, které generuje `scripts/build_peckybot_index.py` (jednání, lidé, sekce) a `scripts/peckybot_sources.py` (ostatní):
- **jednání** zastupitelstva a rady (`jednani/pecky-jednani.json`): bod programu, důvodová zpráva, usnesení s hlasováním, přehled každého jednání s programem; odkaz `/jednani/#<id>`
- **starší jednání z úřední desky** (`jednani/starsi-jednani.json`, od 8. 10. 2026): zápisy rady 2015–2016 a usnesení zastupitelstva 2015–2021 (72 ze 74, u dvou chybí soubor) po úryvcích (≈ 900), tituly „… — zápis/usnesení z úřední desky (i/n)“; přibývají na konec indexu
- **lidé** (`lide/people.json`): všech 444 osob; jméno s tituly, funkce, uskupení, dřívější příjmení, bio, e-mail, telefon (ústředna se nezapisuje)
- **statické texty sekcí** Plán, Tělocvična, Pozemky, Prostory, Pokladna, Smlouvy, Zakázky, Volby 2018/2022/2026, O webu a podstránky Kdo vede Pečecké noviny, Zhlédnutí záznamů zastupitelstva, Odpracované hodiny, Nejdelší body jednání; dělené podle nadpisů
- **komise, výbory, školská rada** (`jednani/komise.json`, `vybory.json`, `skolska-rada.json`): hlavička jednání, docházka, shrnutí a usnesení s hlasováním
- **kalendář** (`kalendar/udalosti.json` a pravidla): akce, opakované kurzy po sériích, svoz odpadu, hodiny úřadu a sběrného dvora; tituly „Kalendář — …“
- **organizace** (`lide/organizations.json`): adresa, IČO, web, hodiny, propojení lidé; tituly „Organizace — …“
- **Pečecké noviny** (`noviny/`): jeden úryvek na číslo s odkazem na PDF
- **Na oběd**: restaurace a další podniky s adresou, telefonem a hodinami (bez menu)
- **absence zastupitelů** (`jednani/absence.json`)

Mimo index zůstává úřední deska, plné texty novin a denní menu. Odpověď vzniká ze 8 úryvků, takže PečkyBot **nespočítá a nesečte** (na „kolik…“ nedá spolehlivý počet).
Index se přegeneruje při každém `python3 scripts/build.py`; kolik úryvků se zapsalo,
vypíše build. Soubory se přepisují jen při změně obsahu a nová jednání přibývají na
konec, takže v gitu se mění hlavně rejstřík a poslední dávky.

### Rozpočet (10 USD měsíčně)
- Worker na Cloudflare Free (100 000 požadavků denně) stojí 0 Kč. Rejstřík je malý (≈ 1 MB) a texty se stahují po dávkách právě kvůli limitu CPU na volání.
- Claude API: výchozí model `claude-sonnet-5-5` (2 / 10 USD za milion vstupních / výstupních tokenů). Typický dotaz (≈ 5 000 vstupních a ≈ 400 výstupních tokenů) vychází na ≈ 0,014 USD, měsíční strop 8 USD tak vystačí na zhruba 550 dotazů.
- Worker si počítá odhad útraty z `usage` v KV a po dosažení `MONTHLY_BUDGET_USD` (8) přestane odpovídat. Zbylé 2 USD jsou rezerva na odchylku odhadu. Navíc nastavit **měsíční limit útraty v Anthropic Console** (tvrdý strop).
- Další pojistky: `DAILY_PER_IP` (15 dotazů na IP za den), `DAILY_GLOBAL` (250 dotazů za den), délka dotazu 600 znaků, `max_tokens` 1500, jen povolený `Origin`.

### Nástroje
Odpověď má dvě fáze (`worker/src/answer.ts`): nejdřív se jako dosud vyhledá 8 úryvků a jdou s dotazem do **prvního** volání modelu; model k tomu dostane i nástroje. Většina dotazů skončí hned (jedno volání, ≈ 0,014 USD). Jen když úryvky nestačí (výčty, počty, termíny, kontakty), model zavolá nástroj; **nejvýš 3 kola**, potom se zavolá ještě jednou bez nástrojů (`tool_choice: none`).

| Nástroj | Data | K čemu |
|---|---|---|
| `hledej_text(dotaz, typ?)` | rejstřík | druhé hledání jiným dotazem, volitelně jen Lidé/Kalendář/Organizace/Web/jednání/komise/noviny |
| `osoba(jmeno)` | `data/osoby.json` | fuzzy (bez diakritiky, skloňování) podle jména/funkce; kontakty |
| `slozeni(organ)` | `data/slozeni.json` | rada, zastupitelstvo, výbory, komise, školská rada, starostové |
| `kalendar(od, do, hledej?)` | `data/kalendar.json` | akce v rozmezí ISO dat (i vícedenní), max 25, série zvlášť |
| `jednani(typ?, od?, do?, hledej?)` | `data/jednani.json` | seznam jednání, max 15, od nejnovějšího |
| `pocet_bodu(klicova_slova, od?, do?, typ?)` | `data/jednani.json` | počet BODŮ PROGRAMU s danými slovy, po letech + příklady |

- Data generuje `scripts/build_peckybot_tools.py` (viz `data/SCHEMA.md`); Worker je stahuje s `?h=<otisk rejstříku>` a drží v paměti 5 minut, vždy jen soubor, který nástroj potřebuje (CPU limit 10 ms na požadavek).
- Výsledky jsou JSON do ≈ 1 500 tokenů (tvrdý řez 6 000 znaků). Každá položka nese číslo zdroje `n`, které navazuje na úvodní úryvky; stránce se vrací jen zdroje, na které odpověď odkazuje.
- Pojistky: cena jednoho dotazu se sčítá přes všechna volání a po překročení 0,06 USD se další kola nespouštějí; útrata se zapisuje (`recordSpend`) po každém volání. Chybný nebo neznámý nástroj se vrátí modelu jako `is_error`. `meta` (tokeny, cena, `tools[]`, `retrieved[]`) sčítá všechna volání.
- Systémový prompt a definice nástrojů mají `cache_control`; do ceny se zápis do cache počítá 1,25×, čtení 0,1×.
- Odhad ceny: bez nástrojů ≈ 0,014 USD; s jedním nástrojem ≈ 0,02–0,03 USD (druhé volání má úvodní úryvky + výsledek); se 3 koly nejvýš ≈ 0,06 USD.
- Kontroly: `npm test` (vykonavatelé nad fixturami v `worker/test/fixtures/`, smyčka s falešným klientem), `node eval/tools.mts` (vykonavatelé nad skutečnými `data/*.json`, bez LLM), `PECKYBOT_URL=… EVAL_TOKEN=… node eval/e2e.mts` (25 živých dotazů, stojí peníze, vyžaduje, aby Worker při platném `X-Eval-Token` vracel `nastroje` a `naklad_micro`).

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
- `npm run eval` — offline měření kvality hledání: 59 dotazů v `worker/eval/queries.json` s očekávaným zdrojem mezi prvními osmi (výsledek podle kategorií a MRR; stav 6. 10. 2026: 41/46 běžných a 12/13 dotazů na nové zdroje). Po každé změně indexu nebo `src/search.ts` pustit a hlídat, že čísla neklesla; nový typ dotazu, který selhal, přidat do `queries.json`.

### Hledání
`worker/src/search.ts`: slova bez diakritiky zkrácená na 6 znaků, váha TF-IDF, titulek má dvojnásobnou váhu. Navíc synonyma (`src/synonyms.ts`, 18 skupin, váha 0,5), předpony pro tvary slov, zvýhodnění podle záměru dotazu (kontakt, „kdo je“, kalendář, číslo jednání, datum) a nejvýš 4 výsledky ze stejného jednání. `tokenize()` musí zůstat shodná s Pythonem (hlídá test).

### Záznamy a hodnocení
Měření skutečného provozu (databáze Cloudflare D1 `peckybot-log`, vazba `LOG`, schéma `worker/schema.sql`). Nic se neukládá do KV.
- **Co se ukládá** (tabulka `dotazy`): čas a den, dotaz (nejvýš 300 znaků; e-maily, telefony a dlouhá čísla nahrazena značkami), počet předchozích zpráv, titulky citovaných zdrojů a nalezených úryvků, použité nástroje, model, tokeny a odhad nákladu, zda odpověď přišla z cache, zda odpověď říká „nevím“, doba odpovědi, kód chyby. **Neukládá se IP adresa, cookie ani identifikátor návštěvníka.** Záznamy starší než 90 dní se mažou samy (při zhruba každém padesátém požadavku).
- **Hodnocení**: pod odpovědí jsou tlačítka 👍/👎. `POST /feedback {id, hlas: 1|-1}`; platí jen pro existující odpověď mladší 24 hodin, poslední hlas přepíše předchozí (tabulka `hodnoceni`). Odpověď z `/chat` nese pole `id`.
- **Cache odpovědí** (tabulka `odpovedi_cache`): jen první dotaz konverzace; klíč je sha-256 z data a normalizovaného dotazu (malá písmena, bez diakritiky a interpunkce); platnost 6 hodin; odpovědi typu „nevím“ se neukládají. Zásah z cache nestojí nic, nepočítá se do měsíční útraty ani do `DAILY_GLOBAL`, ale počítá se do `DAILY_PER_IP`. Pořadí: kontrola vstupu → limit na IP → cache → globální limit a rozpočet → odpověď.
- **Měřicí dotazy**: hlavička `X-Eval-Token` shodná se secretem `EVAL_TOKEN` obejde limit na IP a cache; měsíční rozpočet a `DAILY_GLOBAL` platí dál. Řádek je označený `eval = 1` a statistiky ho přeskakují. Skript musí posílat `Origin` z `ALLOWED_ORIGINS`.
- **Vyhodnocení**: `cd worker && npm run stats [-- --days 7]` vypíše dotazy po dnech, podíl „nevím“ a cache, náklady, nástroje, nejčastější dotazy, poslední „nevím“ a odpovědi s 👎. `npm run export-failures` zapíše do `worker/eval/candidates.json` dotazy (`{q, reason: "nevim"|"hlas-"}`), které ještě nejsou v `eval/queries.json`. Oba příkazy volají `wrangler d1 execute --remote`.
- Na stránce `/peckybot/` je u pole pro dotaz upozornění, že se dotazy anonymně ukládají 90 dní.

