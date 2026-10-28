# pecky.online

Neoficiální občanský transparentní web o městě Pečky (okres Kolín).
Vícestránkový statický web (viz `ARCHITEKTURA-MIGRACE.md`) — žádný
runtime framework, žádné externí závislosti (ani webová písma — jen systémová,
viz proměnné `--font-*` v `assets/styles.css`). Jediný
"build krok" je lokální generovací skript `scripts/build.py`, jeho
výstup jsou čisté statické soubory pro GitHub Pages.

## Struktura (od migrace 30. 8. 2026 — viz ARCHITEKTURA-MIGRACE.md)
Vícestránkový statický web, žádný runtime framework. Styl: pergamenově-
úřední, jen systémová písma (`system-ui` pro text, `ui-serif`/Georgia pro
nadpisy, systémové neproporcionální). Každá sekce má vlastní adresář/URL,
generovaný `index.html` (needit — přepíše ho příští build, viz níže) a
`README.md` (hlavní referenční dokument pro práci na sekci, načíst vždy
jako první):

| Sekce | URL | Dokumentace |
|---|---|---|
| Domů | `/` | `domu/README.md` |
| Lidé | `/lide/` | `lide/README.md` (+ `SPEC.md`; `people.json`/`organizations.json`/`affiliations.json`, kontrola `node lide/validate.mjs`) |
| Plán | `/plan/` | `plan/README.md` |
| Obchvat | `/obchvat/` | `obchvat/README.md` |
| Tělocvična | `/telocvicna/` | `telocvicna/README.md` |
| Volby | `/volby/` | `volby/README.md` (rozcestník) |
| Volby 2018/2022/2026 | `/volby/2018/` atd. | `volby/<rok>/README.md` |
| Jednání | `/jednani/` | `jednani/README.md` (+ `SPEC.md`, `automation-kontrola-usneseni-cz.md`, `automation-katastr-parcely.md`) |
| Smlouvy | `/smlouvy/` | `smlouvy/README.md` |
| Zakázky | `/zakazky/` | `zakazky/README.md` |
| Pozemky | `/pozemky/` | `pozemky/README.md` |
| Prostory | `/prostory/` | `prostory/README.md` (+ `prostory.json`, generátor `prostory/update-prostory.py`) |
| Pokladna | `/pokladna/` | `pokladna/README.md` |
| Dotace od města | `/dotace/` | `dotace/README.md` (+ `dotace.json`, generátor `dotace/update-dotace.py`) |
| Voda | `/voda/` | `voda/README.md` (+ `rozbory.json`, generátor `voda/update-rozbory.py`) |
| Kalendář | `/kalendar/` | `kalendar/README.md` (+ `automation-plakat-akce.md`) |
| Pečecké noviny | `/noviny/` | `noviny/README.md` |
| O webu | `/o-webu/` | `o-webu/README.md` (+ `automation-socialni-site.md`; Monitoring úřední desky `o-webu/uredni-deska-monitoring/README.md`, skill `DoPecek-uredni-deska-check`) |
| Historie změn na webu | `/o-webu/changelog.html` | podstránka O webu, tabulka „Stav sekcí“ z `README.md`; odkaz na konci stránky O webu |

**Needit přímo vygenerované `<sekce>/index.html` soubory ani kořenový
`index.html`** (výstup pro Domů). Místo toho:
- obsah sekce → `content/<sekce>.html` (jen tělo panelu)
- sdílená navigace/patička → `assets/nav.html` / `assets/footer.html`
- sdílené CSS → `assets/styles.css`
- barvy organizací (uskupení, pořadatelé) → `lide/organizations.json`
  (`color`/`color_bg`); build z nich generuje `assets/org-colors.css`
  (`--org-<id>`, aliasy `--party-*`) — ten needitovat, hex jinde nepsat
- sdílený JS (nav, subtaby, tabulky) → `assets/common.js`; pomocné
  funkce sdílené mezi Jednáním/Novinami/Lidmi → `assets/helpers.js`;
  JS specifický pro jednu sekci žije přímo v `content/<sekce>.html`
- pak spustit `python3 scripts/build.py` (validuje HTML/JS a přegeneruje
  všechny stránky + `sitemap.xml`/`robots.txt`)

Mapování starý slug → nová cesta (kvůli redirectu starých `#panel`
odkazů v `content/domu.html`) je v `ARCHITEKTURA-MIGRACE.md`, sekce 2.3.

Data i obrázky patří vždy do složky sekce, ke které se vážou, ne do
kořene repa. Kořenová `img/` je jen pro celowebové obrázky bez vazby na
sekci (`img/favicons/`, `img/peckybot/`); kořenová `data/` neexistuje a
nezakládat ji. Odkazuje se plnou cestou od kořene repa, např.
`volby/2022/zastupitele/paluska.jpg`. Po přesunu souboru vždy projít
příslušný `content/<sekce>.html` a přepsat všechny odkazy, pak spustit
`python3 scripts/build.py`.

## Konvence
- Web celý v češtině, srozumitelným jazykem pro širokou veřejnost
- České pevné mezery (jednopísmenné předložky, číslo + jednotka, data, tituly,
  zkratky) doplňuje build automaticky — ve zdrojích psát běžné mezery;
  pravidla a implementace v `TYPOGRAFIE.md`.
- **Zmínky jednání jsou vždy odkazy** přímo v textu věty: „ZM 6/2026“,
  „RM 35/2026“, komise, výbory, školská rada → `/jednani/#<id>` (zastupitelstvo
  `#zastupitelstvo-RRRR-MM-DD`, rada `#rada-RRRR-MM-DD`, ostatní id z
  `jednani/komise.json` / `vybory.json` / `skolska-rada.json`). Platí i pro
  „RM 14. 11. 2022“ (datumový zápis), usnesení „UR-288-32/26“ / „UZ-35-6/26“
  (→ jednání, na kterém bylo přijato) a pro „Pečecké noviny 12/2018[, s. 3]“
  → PDF `/noviny/Data/PN%20RRRR/<slug>.pdf[#page=N]` (slug z `noviny/issues.json`,
  generuje build). Texty z JSON dat (Lidé: poznámky, bio, zdroj fotky) se
  odkazují v JS přes `jLinkRefs()` v `assets/helpers.js`; ve statickém HTML ručně.
- **Akce v Kalendáři: hlavní zdroj je pecky.cz.** Když jakýkoli zdroj zmiňuje
  akci, která v `kalendar/akce.json` už existuje, a stejná akce je v kalendáři
  města (`pecky.cz/default/events`, `/default/report/<id>_<slug>`), přidat tento
  doklad jako `evidence[0]` (z něj se bere `link`); starší doklady zůstanou za ním.
  Postup: `kalendar/automation-plakat-akce.md`, krok „Pořadí zdrojů“.
  **Jedna akce = jeden záznam**, i když ji pořadatel ohlásil na webu,
  Facebooku i Instagramu pod mírně odlišným názvem: shoda se hledá podle
  dne + času + místa/pořadatele, ne jen názvu. Při duplicitě zůstane záznam
  s dokladem z pecky.cz, ostatní doklady se přesunou do jeho `evidence`
  a druhý záznam se smaže.
- **Zmínky konkrétního příspěvku/zdroje v textu** („3. 9. 2026, na Facebooku
  města“, „podle příspěvku na Facebooku“) jsou odkazem na ten příspěvek
  (URL z řádku/štítku vedle); formulace se liší, hledat i varianty.
- **Budoucí datum v tabulkách a výpisech** má vedle sebe vždy chip s relativním
  údajem (dnes / zítra / pozítří / za 3 dny / za 2 týdny): v HTML
  `<span class="tag probiha fut-chip" data-date="YYYY-MM-DD">plánováno</span>`,
  text dopočítá `relBudouci()` v `assets/common.js` (v JS rendererech volat
  přímo). Ne holé „plánováno“.
- **Bannery (výrazný blok s CTA)** stavět na sdíleném `.banner` v `assets/styles.css`
  (vzor: banner Kalendáře `.kal-banner` a banner příštího zasedání na Domů,
  `_dash_zastupitelstvo()` v `scripts/build.py`): bordó přechod, vnitřní padding
  `26px 30px` (mobil `22px 20px`), nadpis `.banner-title`, ikonové řádky
  `.banner-meta-item` (📅 datum, pin místo), odstavce `.banner-text`, hlavní CTA
  bílá pilulka `.banner-cta` (s ikonou) v `.banner-actions`; varianta `.banner--slate`,
  barvy přes `--banner-from/-to/-accent`. Nové CSS pro banner nepsat od nuly.
  Po buildu vždy zkontrolovat screenshotem — hlavně vnitřní odsazení
  (kolize s `.dash-list`, který nuluje padding).
- **Perex sekce (`p.lede` pod nadpisem) psát jako profesionální copywriter.**
  Krátké a jednoduché věty. Popisuje, co na stránce *je* — ne obecný výklad
  tématu. Přesnost má přednost před svižností: nic, co se nedá doložit daty
  na té stránce. Nepřehánět počty ani rozsah („u většiny" jen když to sedí).
- **Copywriting pravidla pro všechny texty na webu** (perexy, popisky, calloutu,
  poznámky, tabulky, generované stránky) — **kromě přímých citací** zdrojů:
  - **Žádné „my".** Web nemá autorský kolektiv, který by mluvil o sobě: nepsat
    „máme", „jsme", „našli jsme", „zkusili jsme", „naše", „nezveřejňujeme",
    „sbíráme". Psát věcně a neosobně: *co na stránce je* („Přehled obsahuje…",
    „Výpočet započítává…", „je dopočítané z…", „k dispozici jsou 3 jednání").
  - **Žádný interní slang**, kterému čtenář nerozumí: „sesbírané", „vytěženo",
    „snímek dat", „rozpracované", „bereme z…". Říct, co čtenář vidí a odkud to je.
  - Neodkazovat na to, jak práce probíhá („sbírá se ručně"); stačí zdroj
    („Data pocházejí z veřejného profilu…").
  - Rozsah a mezery uvádět konkrétně („od ledna 2025 do září 2026"), ne
    obecně („zatím nemáme všechno").
  - Kontrola před publikací: `grep -iE "\b(máme|jsme|naše|našich|nám|nás)\b"`
    v `content/*.html` a generátorech; shody jsou povolené jen v citacích
    a v názvech (např. uskupení NAŠE PEČKY, skupina „Máme rádi Pečky").
- **Stav načítání** (`.search-status`) je vždy `<h3 class="search-status">` s `<span class="spinner" aria-hidden="true"></span>` před textem (vzor: Jednání) a po načtení v něm zůstává jen počet záznamů. Platí pro každou novou sekci s načítáním dat.
- Žádná vymyšlená data — každý fakt buď označit jako ověřený (.stamp),
  nebo přiznat jako mezeru (.callout)
- Needit vygenerované stránky přímo (viz sekce Struktura výše) — vždy
  přes `content/<sekce>.html` + `scripts/build.py`
- Zdroje: pecky.cz, facebook.com/mestopecky, Hlídač státu (IČO 00239607)
- Každý nový zdroj přidaný do sources.json, který nemá vlastní kontextovou
  citaci jinde na webu (např. konkrétní tabulku nebo callout), doplnit i
  jako odkaz do quicklinks v sekci O webu → Odkazy — i když je jeho status
  zatím "nevytěženo" (obsah nepoužit, ale odkaz má být dohledatelný).
- Body jednání se promítají do sekcí, kterých se věcně týkají — ne jen
  do Jednání. Konkrétně: bod nebo usnesení ke stavbě tělocvičny („Dostavba
  učeben a tělocvičny v ZŠ Pečky“, piloty, statické zajištění, dodatky ke
  SoD) vždy aktualizuje i sekci Tělocvična (přes `content/telocvicna.html`
  + build), bod k prodeji/nákupu pozemku sekci Pozemky, usnesení k pronájmu/výpůjčce nebytových prostor sekci
  Prostory. Postupy:
  `telocvicna/README.md` → „Pracovní postup: týdenní kontrola“ a
  `jednani/automation-katastr-parcely.md`, `prostory/README.md`.
- **Každé nově přidané jednání** (rada, zastupitelstvo, komise, výbory,
  školská rada) dostane při přidání do seznamu shrnutí podle
  `jednani/INSTRUKCE-shrnuti-schuzky.md` (Nejdůležitější témata + Shrnutí),
  uložené do **nového souboru** `jednani/shrnuti/{datum}-{typ}.md`
  (název začíná datem, např. `2026-10-12-rada.md`). U Rady města z něj build
  sestaví banner „Z poslední Rady města“ na Domů; v sekci Jednání se
  shrnutí nezobrazuje; build ho předá i PečkyBotovi (fulltext a `cti_dokument`). Zařazeno do kroku 8f
  `jednani/automation-kontrola-usneseni-cz.md` a do postupů komisí a výborů
  v `jednani/README.md`; do výpisu běhu.
- Každý běh kontroly končí výpisem provedených změn — u každého dotčeného
  souboru jednou větou, co a proč se změnilo. Sekce, kde kontrola nic
  nenašla, se hlásí výslovně jako „zkontrolováno, beze změny“, ne mlčením.
- Po každé kontrole nebo změně obsahu sekce (automatické i ručně vyvolané)
  přepsat její řádek v tabulce `README.md` → „Stav sekcí" (build ji vykreslí na
  stránce `/o-webu/changelog.html` — Historie změn na webu; ručně se tam nepíše): datum kontroly
  vždy, datum změny a sloupec „Co naposledy" jen při reálné změně obsahu;
  pak řádek přesunout na správné místo v řazení (nejnovější změna nahoře).
  Datumy se drží absolutní — relativní stáří se dopočítává až při čtení,
  nikdy se do souboru nezapisuje. Restrukturalizace a refactory se do
  tabulky nezapisují.
- Údaj „Poslední kontrola: před N dny“ pod nadpisem sekce (šedě, bez
  podtržení) se **negeneruje ručně** — `scripts/build.py` ho vloží
  automaticky z data „Kontrola" v tabulce `README.md` → „Stav sekcí"
  (`<lastmod>` v sitemapě zůstává z data „Změna"; funkce `lastmod_map`/`apply_lastmod`).
  Nepsat `<p class="lastmod">` do `content/<sekce>.html` ručně — stačí
  přepsat řádek sekce ve „Stav sekcí" (viz bod výše) a build ho promítne
  na stránku sám. Sekce bez vlastního `<h2 class="title">` (Domů) datum
  nemá. Podstránky z `EXTRA_PAGES` nemají řádek ve „Stav sekcí" (žádné
  pravidelné kontroly odtamtud), ale mají-li vyplněné šesté pole
  (`lastmod`, ruční ISO datum — viz `/jednani/absence.html`,
  `/jednani/nejdelsi.html`), dostanou stejný údaj (s tímto datem) jako běžné sekce;
  ruční přepsání toho pole ve `scripts/build.py` funguje stejně jako
  přepsání řádku ve „Stav sekcí" jinde.

## Design systém
Vizuální pravidla webu (barvy, písma, mezery, zaoblení, bannery, štítky,
loga) jsou v design systému **DoPeček.cz** — soukromém artefaktu na claude.ai:
https://claude.ai/artifact/DwEbaA4VMfiDfjauCZ9dc8. Web ho za běhu nečte;
zdrojem pravdy pro hodnoty zůstává `assets/styles.css` a
`lide/organizations.json`.
- Před úpravou stylů, nového banneru nebo nové stránky přečíst přes nástroj
  Artifact (akce `read`) `project/README.md` systému, podle potřeby
  `project/tokens.json` (hodnoty) a `project/api/tokens.md`.
- Slovo „apply“ od uživatele = přenést úpravy z design systému do repa:
  hodnoty tokenů do `assets/styles.css` (barvy, písma, `--space-*`,
  `--radius-*`, `--shadow-*`, `--fs-*`, `--fw-*`, `--ctl-h`) a barvy organizací
  do `lide/organizations.json`, pak `python3 scripts/build.py`, bez commitu
  (náhled na localhostu). Měnit jen hodnotu proměnné v `:root`, ne pravidla.
  Nepřenáší se, co proměnnou nemá: složené textové styly (velikost + tloušťka
  + řádkování najednou), `line-height`, `letter-spacing`, zvláštní hodnoty
  zapsané přímo v pravidlech a inline styly v `content/*.html`; takové změny
  jen vypsat.
- Nové CSS psát přes tyto proměnné (`padding:var(--space-4)`,
  `border-radius:var(--radius-sm)`, `font-size:var(--fs-5)`), pevné číslo jen
  tam, kde pro hodnotu token není.
- Po větší změně vzhledu webu systém znovu sesynchronizovat s repem
  (tokeny, README, cover) a nové tokeny, které zdroj už nedefinuje, jen
  vypsat — neodstraňovat bez souhlasu.
- Systém je soukromý; jiným lidem nebo agentům je třeba ho nasdílet
  (Share na stránce artefaktu).

## Poznámky k datům
- Hlídač státu MCP: použij ICO_of_holding_structure (celá skupina),
  ne jen ICOs_of_contracting_party (jen úřad)
- with_serious_issues_only nespolehlivě vrací 0 — rizikové smlouvy
  identifikovat ručně z běžných výsledků
- Bot-chráněné / JS-vykreslované stránky (pecky.cz, mesto-pecky.usneseni.cz):
  web_fetch často vrací prázdný obsah — zkus claude-in-chrome (navigate +
  get_page_text/find), případně web_search jako fallback
- pecky.cz prošel redesignem (nová platforma, nové URL jako /office/board) —
  je aktuální, ale číst jen přes claude-in-chrome. Starší mirror
  pecky.as4u.cz od cca 3/2026 přestal být průběžně aktualizovaný (např.
  jeho úřední deska je zamrzlá na únoru/březnu 2026) — pro časově citlivý
  obsah (úřední deska, aktuality) použij pecky.cz, ne pecky.as4u.cz;
  as4u.cz zůstává užitečný pro starší/archivní obsah, viz sources.json

Provozní pasti prostředí (git deadlock na velkých souborech, pád
`preview_start`, historie repa) a jejich obejití → `TROUBLESHOOTING.md`.

## Projektové skilly
Všechny projektové skilly v `.claude/skills/` pojmenovávat s prefixem
`DoPecek-` (např. `DoPecek-dev-server`) — odlišuje je to od
globálních/pluginových skillů se stejným obecným názvem.

## Git / GitHub
Remote: https://github.com/jakubspanihel/pecky.online.git
Před pushem vždy commit s popisnou zprávou, zachovej historii verzí webu.
Na repu často souběžně pracuje víc relací — commituj jen změny svého
běhu, ne cizí rozpracovanou práci (ani ve sdíleném `README.md`); postup
a pomocný skript jsou ve skillu `DoPecek-commit`.
GitHub Integration konektor v chatu je zablokovaný OAuth konfliktem —
publikuj přes přímý git CLI/GitHub API s vlastním GitHub přihlášením (token).
Token (bez expirace) je uložený lokálně v `.github-pat` (v .gitignore,
nikdy nejde do gitu) — před publikací ho odtud načíst, needit znovu žádat.

Publikace jde přes skript `scripts/git-sync.sh` (načte token z
`.github-pat`, nic z něj nevypíše, nepushuje s force):

```bash
scripts/git-sync.sh fetch   # stáhne origin/main a vypíše rozdíly obou směrů
scripts/git-sync.sh push    # fetch + push main + dorovnání tracking refu
```

Skript je jeden jednoduchý příkaz bez proměnných, takže ho lze povolit
v allowlistu (`Bash(scripts/git-sync.sh:*)`) a bezobslužné běhy se nezastaví
na dotazu. Ručně psaný `PAT=$(…); git push "…${PAT}…"` nepoužívat.

- Push přes pojmenovaný `origin` selže na chybějící přihlášení — posílat
  na explicitní URL s tokenem (bez toho i `git status -sb` po pushi
  mylně tvrdí „ahead N", proto skript po pushi dělá `fetch`). Token
  nikdy nevypisovat do výstupu (skript ho maskuje).
  Hláška `git: 'credential-osxkeychain' is not a git command` je
  neškodná (macOS credential helper v linuxovém sandboxu neexistuje) —
  push i tak projde.
- Commit vždy s popisnou zprávou přes `-F soubor` (víceřádkové české
  zprávy v `-m` se v shellu lámou), autor
  `Jakub Španihel <jakubspanihel@gmail.com>`.
