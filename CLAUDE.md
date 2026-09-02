# pecky.online

Neoficiální občanský transparentní web o městě Pečky (okres Kolín).
Vícestránkový statický web (viz `ARCHITEKTURA-MIGRACE.md`) — žádný
runtime framework, žádné závislosti kromě Google Fonts CDN. Jediný
"build krok" je lokální generovací skript `scripts/build.py`, jeho
výstup jsou čisté statické soubory pro GitHub Pages.

## Struktura (od migrace 30. 8. 2026 — viz ARCHITEKTURA-MIGRACE.md)
14 sekcí, každá vlastní adresář/URL: Domů (`/`), Lidé (`/lide/`), Plán
(`/plan/`), Tělocvična (`/telocvicna/`), Volby 2018/2022/2026
(`/volby/2018/` atd.), Jednání (`/jednani/`), Smlouvy (`/smlouvy/`),
Zakázky (`/zakazky/`), Pozemky (`/pozemky/`), Pokladna (`/pokladna/`),
Pečecké noviny (`/noviny/`), O webu (`/o-webu/`). Styl: pergamenově-
úřední (Fraunces + IBM Plex Sans/Mono), `assets/styles.css`.

**Needit přímo vygenerované `<sekce>/index.html` soubory** (přepíše je
příští build) **ani kořenový `index.html`** (to je teď vygenerovaný
výstup pro Domů). Místo toho:
- obsah sekce → `content/<sekce>.html` (jen tělo panelu)
- sdílená navigace/patička → `assets/nav.html` / `assets/footer.html`
- sdílené CSS → `assets/styles.css`
- sdílený JS (nav, subtaby, tabulky) → `assets/common.js`; pomocné
  funkce sdílené mezi Jednáním/Novinami/Lidmi → `assets/helpers.js`;
  JS specifický pro jednu sekci žije přímo v `content/<sekce>.html`
- pak spustit `python3 scripts/build.py` (validuje HTML/JS a přegeneruje
  všech 13 stránek + `sitemap.xml`/`robots.txt`)

Mapování starý slug → nová cesta (kvůli redirectu starých `#panel`
odkazů v `content/domu.html`) je v `ARCHITEKTURA-MIGRACE.md`, sekce 2.3.

## Konvence
- Web celý v češtině, srozumitelným jazykem pro širokou veřejnost
- Žádná vymyšlená data — každý fakt buď označit jako ověřený (.stamp),
  nebo přiznat jako mezeru (.callout)
- Needit vygenerované stránky přímo (viz sekce Struktura výše) — vždy
  přes `content/<sekce>.html` + `scripts/build.py`
- Zdroje: pecky.cz, facebook.com/mestopecky, Hlídač státu (IČO 00239607)
- Každý nový zdroj přidaný do sources.json, který nemá vlastní kontextovou
  citaci jinde na webu (např. konkrétní tabulku nebo callout), doplnit i
  jako odkaz do quicklinks v sekci O webu → Odkazy — i když je jeho status
  zatím "nevytěženo" (obsah nepoužit, ale odkaz má být dohledatelný).
- Po každé kontrole nebo změně obsahu sekce (automatické i ručně vyvolané)
  přepsat její řádek v tabulce `README.md` → „Stav sekcí": datum kontroly
  vždy, datum změny a sloupec „Co naposledy" jen při reálné změně obsahu;
  pak řádek přesunout na správné místo v řazení (nejnovější změna nahoře).
  Datumy se drží absolutní — relativní stáří se dopočítává až při čtení,
  nikdy se do souboru nezapisuje. Restrukturalizace a refactory se do
  tabulky nezapisují.

## Dokumentace jednotlivých sekcí
Každá sekce webu má vlastní složku `<sekce>/` se souborem `README.md` —
hlavní referenční dokument pro práci na dané sekci, načíst ho vždy jako
první. Stejná složka nese i vygenerovaný veřejný `index.html`
(nedit — viz sekce Struktura výše) a u některých sekcí i doplňková
data/skripty. Obsah sekce, který dřív žil v kořenovém `index.html`
(jednosouborová struktura, do 30. 8. 2026), teď žije v
`content/<sekce>.html`.

Data i obrázky patří vždy do složky sekce, ke které se vážou, ne do
kořene repa. Kořenová `img/` je jen pro celowebové obrázky bez vazby na
sekci (`img/favicons/`, `img/peckybot/`); kořenová `data/` neexistuje a
nezakládat ji. Odkazuje se plnou cestou od kořene repa, např.
`volby/2022/zastupitele/paluska.jpg`. Po přesunu souboru vždy
projít příslušný `content/<sekce>.html` a přepsat všechny odkazy, pak
spustit `python3 scripts/build.py`.

- Domů → `domu/README.md`
- Lidé → `lide/README.md` (+ `SPEC.md`; datová sada
  `people.json` / `organizations.json` / `affiliations.json`,
  kontrola `node lide/validate.mjs`)
- Plán → `plan/README.md`
- Tělocvična → `telocvicna/README.md`
- Volby 2018 → `volby/2018/README.md`
- Volby 2022 → `volby/2022/README.md`
- Volby 2026 → `volby/2026/README.md`
  (společný rozcestník pro všechny ročníky: `volby/README.md`)
- Jednání → `jednani/README.md` (+ `SPEC.md`,
  `automation-kontrola-usneseni-cz.md`, `automation-katastr-parcely.md`)
- Smlouvy → `smlouvy/README.md`
- Zakázky → `zakazky/README.md`
- Pozemky → `pozemky/README.md`
- Pokladna → `pokladna/README.md`
- Pečecké noviny / Zpravodaj → `noviny/README.md`
- O webu → `o-webu/README.md` (+ `automation-socialni-site.md`)

## Známé mezery (celoprojektové)
- ~~Kompletní seznam 21 zastupitelů~~ — uzavřeno. pecky.cz sice blokuje
  bot přístup, ale jmenný seznam jde ověřit z prezence jednání v archivu
  (`jednani/pecky-jednani.json`, pole `attendance.present_names`).
  Stav při ustavení 2022 = prezence ZM 7/2022 (21/21), aktuální stav =
  poslední jednání ZM. Uskupení u jmen ale archiv neuvádí — to zůstává
  mezerou a dopočítává se z počtu mandátů (viz `volby/2022/README.md`).

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
- Velké soubory v `jednani/` (`archive-*.json`) čtené přímo z cesty
  přes připojenou složku občas skončí `OSError: [Errno 35] Resource
  deadlock avoided` (Python `open()`, `cat`, `head`...). Obejití: nejdřív
  `cp soubor /tmp/kopie.json`, pak pracovat s kopií — `cp` samo selhání
  nemělo.
- Git přes připojenou složku je nespolehlivý na čtení objektů: `git log`
  s cestou (`git log -- cesta/k/souboru`) **tiše vrací prázdno** místo
  commitů, `git show <commit>:<soubor>`, `git rev-list` i `git diff HEAD --`
  padají na `Bus error`. Bez pathspec (`git log`, `git status`,
  `git log --name-only`) to funguje, ale `--name-only` vypíše soubory jen
  u několika nejnovějších commitů. Prázdný výstup proto neznamená „soubor
  se nikdy neměnil" — na dohledání, kdy co vzniklo, použij mtime souborů
  (`ls -la`, `stat`) a datumy uvnitř dat (`meta.generated_at`) a ověř je
  proti changelogu v `README.md`. Historie repa navíc sahá jen ke
  23. 8. 2026, starší změny v ní nejsou vůbec. (Zjištěno 30. 8. 2026 při
  dohledávání, kdy se doplnil offline archiv Pečeckých novin.)

## Git / GitHub
Remote: https://github.com/jakubspanihel/pecky.online.git
Před pushem vždy commit s popisnou zprávou, zachovej historii verzí webu.
GitHub Integration konektor v chatu je zablokovaný OAuth konfliktem —
publikuj přes přímý git CLI/GitHub API s vlastním GitHub přihlášením (token).
Token (bez expirace) je uložený lokálně v `.github-pat` (v .gitignore,
nikdy nejde do gitu) — před publikací ho odtud načíst, needit znovu žádat.
