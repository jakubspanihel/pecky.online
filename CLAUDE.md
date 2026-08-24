# pecky.online

Neoficiální občanský transparentní web o městě Pečky (okres Kolín).
Jednosouborová statická stránka — index.html, žádný build proces,
žádné závislosti kromě Google Fonts CDN.

## Struktura
Jediný soubor index.html, panely přepínané přes JS (data-panel atributy):
Domů, Lidé, Plán, Volby 2018, Volby 2022, Volby 2026, Jednání, Smlouvy,
Zakázky, Pozemky, Pokladna, Pečecké noviny, O webu.
Styl: pergamenově-úřední (Fraunces + IBM Plex Sans/Mono), viz <style> v hlavičce.

## Konvence
- Web celý v češtině, srozumitelným jazykem pro širokou veřejnost
- Žádná vymyšlená data — každý fakt buď označit jako ověřený (.stamp),
  nebo přiznat jako mezeru (.callout)
- Zachovávat jednosouborovou strukturu, needit do samostatných JS/CSS souborů
- Zdroje: pecky.cz, facebook.com/mestopecky, Hlídač státu (IČO 00239607)
- Každý nový zdroj přidaný do sources.json, který nemá vlastní kontextovou
  citaci jinde na webu (např. konkrétní tabulku nebo callout), doplnit i
  jako odkaz do quicklinks v sekci O webu → Odkazy — i když je jeho status
  zatím "nevytěženo" (obsah nepoužit, ale odkaz má být dohledatelný).

## Dokumentace jednotlivých sekcí
Každá sekce webu má vlastní složku `pecky-<sekce>/` se souborem
`README.md` — hlavní referenční dokument pro práci na dané sekci, načíst
ho vždy jako první. Zobrazení všech sekcí zůstává v jednom souboru
kořenovém `index.html` (jednosouborová struktura webu) — tyhle složky
nesou jen dokumentaci a (u některých sekcí) doplňková data/skripty.

- Domů → `pecky-domu/README.md`
- Lidé → `pecky-lide/README.md`
- Plán → `pecky-plan/README.md`
- Volby 2018 → `pecky-volby/2018/README.md`
- Volby 2022 → `pecky-volby/2022/README.md`
- Volby 2026 → `pecky-volby/2026/README.md`
  (společný rozcestník pro všechny ročníky: `pecky-volby/README.md`)
- Jednání → `pecky-jednani/README.md` (+ `SPEC.md`, `AUTOMATION.md`)
- Smlouvy → `pecky-smlouvy/README.md`
- Zakázky → `pecky-zakazky/README.md`
- Pozemky → `pecky-pozemky/README.md`
- Pokladna → `pecky-pokladna/README.md`
- Pečecké noviny / Zpravodaj → `pecky-noviny/README.md`
- O webu → `pecky-o-webu/README.md`

## Známé mezery (celoprojektové)
- Kompletní seznam 21 zastupitelů (pecky.cz blokuje bot přístup)

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
- Velké soubory v `pecky-jednani/` (`archive-*.json`) čtené přímo z cesty
  přes připojenou složku občas skončí `OSError: [Errno 35] Resource
  deadlock avoided` (Python `open()`, `cat`, `head`...). Obejití: nejdřív
  `cp soubor /tmp/kopie.json`, pak pracovat s kopií — `cp` samo selhání
  nemělo.

## Git / GitHub
Remote: https://github.com/jakubspanihel/pecky.online.git
Před pushem vždy commit s popisnou zprávou, zachovej historii verzí webu.
GitHub Integration konektor v chatu je zablokovaný OAuth konfliktem —
publikuj přes přímý git CLI/GitHub API s vlastním GitHub přihlášením (token).
Token (bez expirace) je uložený lokálně v `.github-pat` (v .gitignore,
nikdy nejde do gitu) — před publikací ho odtud načíst, needit znovu žádat.
