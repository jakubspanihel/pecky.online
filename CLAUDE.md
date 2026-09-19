# pecky.online

Neoficiální občanský transparentní web o městě Pečky (okres Kolín).
Vícestránkový statický web (viz `ARCHITEKTURA-MIGRACE.md`) — žádný
runtime framework, žádné závislosti kromě Google Fonts CDN. Jediný
"build krok" je lokální generovací skript `scripts/build.py`, jeho
výstup jsou čisté statické soubory pro GitHub Pages.

## Struktura (od migrace 30. 8. 2026 — viz ARCHITEKTURA-MIGRACE.md)
16 sekcí, každá vlastní adresář/URL: Domů (`/`), Lidé (`/lide/`), Plán
(`/plan/`), Tělocvična (`/telocvicna/`), Volby (`/volby/`) a Volby 2018/2022/2026
(`/volby/2018/` atd.), Jednání (`/jednani/`), Smlouvy (`/smlouvy/`),
Zakázky (`/zakazky/`), Pozemky (`/pozemky/`), Pokladna (`/pokladna/`),
Kalendář (`/kalendar/`), Pečecké noviny (`/noviny/`), O webu (`/o-webu/`).
Styl: pergamenově-úřední (Fraunces + IBM Plex Sans/Mono), `assets/styles.css`.

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
- **Perex sekce (`p.lede` pod nadpisem) psát jako profesionální copywriter.**
  Krátké a jednoduché věty. Popisuje, co na stránce *je* — ne obecný výklad
  tématu. Přesnost má přednost před svižností: nic, co se nedá doložit daty
  na té stránce. Nepřehánět počty ani rozsah („u většiny" jen když to sedí).
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
  + build), bod k prodeji/nákupu pozemku sekci Pozemky. Postupy:
  `telocvicna/README.md` → „Pracovní postup: týdenní kontrola“ a
  `jednani/automation-katastr-parcely.md`.
- Každý běh kontroly končí výpisem provedených změn — u každého dotčeného
  souboru jednou větou, co a proč se změnilo. Sekce, kde kontrola nic
  nenašla, se hlásí výslovně jako „zkontrolováno, beze změny“, ne mlčením.
- Po každé kontrole nebo změně obsahu sekce (automatické i ručně vyvolané)
  přepsat její řádek v tabulce `README.md` → „Stav sekcí": datum kontroly
  vždy, datum změny a sloupec „Co naposledy" jen při reálné změně obsahu;
  pak řádek přesunout na správné místo v řazení (nejnovější změna nahoře).
  Datumy se drží absolutní — relativní stáří se dopočítává až při čtení,
  nikdy se do souboru nezapisuje. Restrukturalizace a refactory se do
  tabulky nezapisují.
- Datum „Aktualizováno" pod nadpisem sekce (na stránce samotné, vedle
  perexu) se **negeneruje ručně** — `scripts/build.py` ho vloží
  automaticky z téhož data „Změna" v tabulce `README.md` → „Stav sekcí",
  co používá i `<lastmod>` v sitemapě (funkce `lastmod_map`/`apply_lastmod`).
  Nepsat `<p class="lastmod">` do `content/<sekce>.html` ručně — stačí
  přepsat řádek sekce ve „Stav sekcí" (viz bod výše) a build ho promítne
  na stránku sám. Sekce bez vlastního `<h2 class="title">` (Domů) nebo
  bez řádku ve „Stav sekcí" (podstránky z `EXTRA_PAGES`, např.
  `/jednani/absence.html`) datum nemají.

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
- Volby → `volby/README.md`
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
- Kalendář → `kalendar/README.md`
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
  nemělo. Pozn. 9. 9. 2026: při kontrolním testu se chyba nezopakovala
  (3/3 přímá načtení `archive-2026-08-04.json` prošla), ale protože šlo
  vždy o občasnou chybu, postup přes kopii zůstává doporučený.
- ~~Git přes připojenou složku je nespolehlivý na čtení objektů~~ —
  **VYŘEŠENO 9. 9. 2026.** Příčinou nebyl git, ale to, že připojená
  složka odmítala `unlink` („Operation not permitted"): git po sobě
  nemohl uklidit `.git/index.lock` ani rozepsané `.git/objects/tmp_obj_*`,
  takže každý další příkaz spadl na „Another git process seems to be
  running" nebo na `Bus error`. Mazání se zapíná nástrojem
  `allow_cowork_file_delete` (stačí jednou, platí pro celou složku) —
  **narazíš-li na „Operation not permitted" při `rm`, zavolej ho místo
  hlášení, že to nejde.** Po zapnutí ověřeno, že funguje `git log --
  cesta/k/souboru`, `git show <commit>:<soubor>` i `git diff HEAD~1 --stat`.
  Zbytek staré poznámky ale platí dál: **historie repa sahá jen ke
  23. 8. 2026**, starší změny v ní nejsou vůbec — na dohledání, kdy co
  vzniklo před tímto datem, použij mtime souborů (`ls -la`, `stat`),
  datumy uvnitř dat (`meta.generated_at`) a changelog v `README.md`.
  Nouzové obejití, kdyby se blokované mazání někdy vrátilo: zámky
  nemazat, ale přejmenovat (`mv .git/index.lock .git/index.lock.bak.$(date +%s%N)`)
  — rename mount povoluje i tehdy, když unlink ne.
- **`preview_start` s `name` (spuštění dev serveru podle `.claude/launch.json`)
  na tomhle stroji spolehlivě padá na `[Errno 1] Operation not permitted`
  při otevírání `scripts/serve.py`.** Diagnostikováno 14. 9. 2026: jde
  o macOS sandbox/TCC omezení konkrétního launcher procesu, který
  `preview_start` interně používá — ne chybu v `serve.py` ani v repu
  (stejný soubor se bez problému spustí ručně přes Bash tool). Neřeší se
  úpravou skriptu/configu. **Obejití:** spustit server ručně přes Bash
  (`python3 scripts/serve.py`, typicky na pozadí), pak zavolat
  `preview_start` s `url` (`http://localhost:8000`) místo `name` — Browser
  pane se tak napojí na už běžící server, aniž by ho sám spouštěl. `serve.py`
  vždy defaultuje na port 8000 a od 14. 9. 2026 je idempotentní — když je
  port už obsazený (typicky server z předchozí relace), vypíše hlášku
  a skončí čistě (exit 0) místo pádu na traceback, takže "jen to spusť" je
  vždy bezpečné zavolat znovu bez kontroly předem. Tenhle postup je
  zabalený jako projektový skill `.claude/skills/pecky-online-dev-server/`
  (needit se přímo, `.claude/` je celé v `.gitignore`) — viz i konvence
  pojmenování skillů níže.

## Projektové skilly
Všechny projektové skilly v `.claude/skills/` pojmenovávat s prefixem
`pecky-online-` (např. `pecky-online-dev-server`) — odlišuje je to od
globálních/pluginových skillů se stejným obecným názvem.

## Git / GitHub
Remote: https://github.com/jakubspanihel/pecky.online.git
Před pushem vždy commit s popisnou zprávou, zachovej historii verzí webu.
GitHub Integration konektor v chatu je zablokovaný OAuth konfliktem —
publikuj přes přímý git CLI/GitHub API s vlastním GitHub přihlášením (token).
Token (bez expirace) je uložený lokálně v `.github-pat` (v .gitignore,
nikdy nejde do gitu) — před publikací ho odtud načíst, needit znovu žádat.

Postup publikace ověřený 9. 9. 2026:

```bash
PAT=$(tr -d '\r\n' < .github-pat)
git push "https://x-access-token:${PAT}@github.com/jakubspanihel/pecky.online.git" main
# tracking ref se pushem na explicitní URL neaktualizuje — dorovnat:
git fetch "https://x-access-token:${PAT}@github.com/jakubspanihel/pecky.online.git" \
  main:refs/remotes/origin/main --force
```

- Push přes pojmenovaný `origin` selže na chybějící přihlášení; posílat
  na explicitní URL s tokenem. Token nikdy nevypisovat do výstupu —
  filtrovat přes `sed -e "s|${PAT}|***|g"`.
- Hláška `git: 'credential-osxkeychain' is not a git command` je
  **neškodná** — repo má v konfiguraci macOS credential helper, který
  v linuxovém sandboxu neexistuje. Push i tak projde.
- Bez toho `fetch` výše bude `git status -sb` tvrdit „ahead N", i když
  je vše nahrané. Není to chyba pushe, jen zastaralý `origin/main`.
- Commit vždy s popisnou zprávou přes `-F soubor` (víceřádkové české
  zprávy v `-m` se v shellu lámou), autor
  `Jakub Španihel <jakubspanihel@gmail.com>`.
