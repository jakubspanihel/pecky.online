# pecky.online

Neoficiální občanský transparentní web o městě Pečky (okres Kolín).
Vícestránkový statický web (viz `ARCHITEKTURA-MIGRACE.md`) — žádný
runtime framework, žádné závislosti kromě Google Fonts CDN. Jediný
"build krok" je lokální generovací skript `scripts/build.py`, jeho
výstup jsou čisté statické soubory pro GitHub Pages.

## Struktura (od migrace 30. 8. 2026 — viz ARCHITEKTURA-MIGRACE.md)
Vícestránkový statický web, žádný runtime framework. Každá sekce má vlastní
adresář/URL, generovaný `index.html` (needit — přepíše ho příští build,
viz níže) a `README.md` (hlavní referenční dokument pro práci na sekci,
načíst vždy jako první):

| Sekce | URL | Dokumentace |
|---|---|---|
| Domů | `/` | `domu/README.md` |
| Lidé | `/lide/` | `lide/README.md` (+ `SPEC.md`; `people.json`/`organizations.json`/`affiliations.json`, kontrola `node lide/validate.mjs`) |
| Plán | `/plan/` | `plan/README.md` |
| Tělocvična | `/telocvicna/` | `telocvicna/README.md` |
| Volby | `/volby/` | `volby/README.md` (rozcestník) |
| Volby 2018/2022/2026 | `/volby/2018/` atd. | `volby/<rok>/README.md` |
| Jednání | `/jednani/` | `jednani/README.md` (+ `SPEC.md`, `automation-kontrola-usneseni-cz.md`, `automation-katastr-parcely.md`) |
| Smlouvy | `/smlouvy/` | `smlouvy/README.md` |
| Zakázky | `/zakazky/` | `zakazky/README.md` |
| Pozemky | `/pozemky/` | `pozemky/README.md` |
| Pokladna | `/pokladna/` | `pokladna/README.md` |
| Pečecké noviny | `/noviny/` | `noviny/README.md` |
| O webu | `/o-webu/` | `o-webu/README.md` (+ `automation-socialni-site.md`) |

**Needit přímo vygenerované `<sekce>/index.html` soubory ani kořenový
`index.html`** (výstup pro Domů). Místo toho:
- obsah sekce → `content/<sekce>.html` (jen tělo panelu)
- sdílená navigace/patička → `assets/nav.html` / `assets/footer.html`
- sdílené CSS → `assets/styles.css`
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

- Push přes pojmenovaný `origin` selže na chybějící přihlášení — posílat
  na explicitní URL s tokenem (bez toho i `git status -sb` po pushi
  mylně tvrdí „ahead N", proto ten `fetch` výše). Token nikdy
  nevypisovat do výstupu — filtrovat přes `sed -e "s|${PAT}|***|g"`.
  Hláška `git: 'credential-osxkeychain' is not a git command` je
  neškodná (macOS credential helper v linuxovém sandboxu neexistuje) —
  push i tak projde.
- Commit vždy s popisnou zprávou přes `-F soubor` (víceřádkové české
  zprávy v `-m` se v shellu lámou), autor
  `Jakub Španihel <jakubspanihel@gmail.com>`.
