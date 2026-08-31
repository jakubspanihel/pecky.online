# Plán: přechod z jednosouborového webu na vícestránkovou statickou strukturu

Stav: **implementováno 30. 8. 2026.** Vzniklo na žádost 28. 8. 2026 — web
přerostl jednosouborový `index.html` (367 KB, 4 154 řádků) a chybí mu
trvalé odkazy na jednotlivé sekce a záložky v rámci sekcí. Tento dokument
popisoval cílovou architekturu a postup migrace; ponechán jako referenční
záznam (důvody rozhodnutí, mapa starý hash → nová cesta v sekci 2.3).
Aktuální stav struktury a konvence pro práci s ní jsou v kořenovém
`CLAUDE.md`.

Dodatek (30. 8. 2026, stejný den): tehdy nově vzniklé bezprefixové
složky sekcí (`jednani/`, `lide/` atd., viz 2.1) zpočátku existovaly
vedle starších `pecky-<sekce>/` složek s dokumentací a daty. Ty byly
následně (v rámci téhož dne) sloučené do bezprefixových složek — dnes
tedy existuje jen jedna složka na sekci, ne dvě. Zbytek tohoto
dokumentu popisuje stav bezprostředně po prvním kroku migrace a
zmínky `pecky-<sekce>/` níže jsou proto historické, ne aktuální cesty.

Dodatek 2 (31. 8. 2026): migrace počítala s doménou `pecky.online` na
kořeni, proto jsou všechny interní odkazy (nav, `content/*.html`,
`sitemap.xml`, canonical/og:url) kořenově-absolutní (`/jednani/` apod.).
Doména `pecky.online` ale patří někomu jinému (zjištěno 31. 8. 2026 při
kontrole nasazení) — web běží na GitHub Pages subcestě
`https://jakubspanihel.github.io/pecky.online/`, kde by tyhle odkazy bez
úpravy mířily mimo web (`/jednani/` by se resolvlo na kořen
`jakubspanihel.github.io`, ne na `.../pecky.online/`). Řešení: build.py
teď má `SITE_BASE_PATH`/`SITE_DOMAIN` (přepínatelné na jeden řádek, až
bude vlastní doména) a při generování přepisuje `href=`/`src=`/`fetch('`
i pár runtime míst, která staví cesty z JSON dat nebo JS řetězců
(`window.SITE_BASE_PATH`, viz `templates/page.html`,
`content/domu.html`, `content/lide.html`, `content/zpravodaj.html`).
Lokální test proto běží přes `python3 scripts/serve.py` (napodobí tu
samou subcestu), ne přímo `python3 -m http.server` — viz `README.md`.

## 1. Současný stav (fakta)

- Jeden soubor `index.html`, 13 panelů (`data-panel`), přepínaných JS.
  Trvalý odkaz existuje jen na panel (`#jednani`) přes `PANEL_NAMES` /
  `applyPanel()` / `hashchange` (řádky ~2765–2861).
- Záložky uvnitř sekcí (`.subtabs`/`.subtablink`/`.subpanel` — Volby
  2018, Volby 2022, Pozemky) **nemají žádnou vazbu na URL** — přepínání
  řádek 2866+ jen mění CSS třídy, hash se netýká.
- Dvě sekce (Jednání, Pečecké noviny) mají navíc samostatnou
  „standalone" kopii (`pecky-jednani/index.html`,
  `pecky-noviny/index.html`) s duplicitní hlavičkou/JS logikou — dnešní
  oprava (RUIAN odkazy) musela jít do obou souborů zvlášť. To je přesně
  ta údržbová bolest, která při růstu webu poroste.
- Celý web má **jeden `<title>`** a žádný `<meta name="description">`,
  žádné OG tagy, žádný `sitemap.xml`/`robots.txt` — sdílené napříč všemi
  sekcemi, i těmi tematicky velmi odlišnými (Pokladna vs. Volby 2026).
- Hledání (`.search-bar`) je vždy jen v rámci jedné sekce (Lidé, Jednání,
  Noviny) — není to web-wide fulltext, takže rozdělení na víc stránek
  hledání nijak nekomplikuje.

## 2. Cílová architektura

**Skládaný statický web** — žádný runtime framework, žádný JS build,
GitHub Pages pořád servíruje čistou statiku. Přibude jeden lokální krok
před publikací: spustit generovací skript, který smontuje finální HTML
soubory ze sdílených částí a obsahu sekce. Výstup (hotové `.html`
soubory) se normálně commitne do repa — stejný duch jako dnešní
`update-pozemky.py`, jen o úroveň výš.

### 2.1 Adresářová struktura

```
/index.html                  → Domů (zůstává na kořeni)
/lide/index.html             → Lidé
/plan/index.html             → Plán
/volby/2018/index.html       → Volby 2018
/volby/2022/index.html       → Volby 2022
/volby/2026/index.html       → Volby 2026
/jednani/index.html          → Jednání (nahradí dnešní standalone kopii)
/smlouvy/index.html          → Smlouvy
/zakazky/index.html          → Zakázky
/pozemky/index.html          → Pozemky
/pokladna/index.html         → Pokladna
/noviny/index.html           → Pečecké noviny (nahradí standalone kopii)
/o-webu/index.html           → O webu

/assets/styles.css           → sdílené CSS (dnešní <style> v hlavičce)
/assets/common.js            → sdílená JS logika (nav, hledání, helpery
                                jako jEscapeHtml, jLinkParcely, apod.)
/assets/nav.html             → šablona hlavičky + navigace (partial)
/assets/footer.html          → šablona patičky (partial), pokud vznikne

/templates/page.html         → kostra stránky ({{TITLE}}, {{DESC}},
                                {{NAV}}, {{CONTENT}}, {{SCRIPTS}}...)
/content/<sekce>.html        → jen tělo panelu (dnešní obsah
                                <section class="panel" id="panel-...">,
                                bez obalu)
/scripts/build.py            → generovací skript
```

GitHub Pages servíruje adresář s `index.html` automaticky na čisté URL
(`pecky.online/pozemky/` funguje bez jakékoli konfigurace) — nic navíc
není potřeba řešit na straně hostingu.

### 2.2 URL schéma

- **Sekce** = vlastní adresář a soubor → `pecky.online/pozemky/`,
  `pecky.online/jednani/`. Nejčistší možná trvalá adresa, funguje i bez
  JS, dobře se sdílí a indexuje.
- **Záložky v rámci sekce** = hash na stránce té sekce →
  `pecky.online/pozemky/#prodej`, `pecky.online/volby/2022/#rozbor`.
  Jedna stránka na sekci, JS při načtení přečte hash a nastaví aktivní
  subtab — rozšíření dnešního `.subtabs` handleru (řádek 2866), který
  dnes hash vůbec nezapisuje ani nečte. Zůstává tak zachovaná dnešní
  interaktivita (hledání, filtrování) v rámci sekce, jen přibude
  zápis/čtení hashe při přepnutí záložky.

### 2.3 Zpětná kompatibilita (důležité — jde o veřejný web se sdílenými odkazy)

Staré odkazy typu `pecky.online/#pozemky` (dnešní jednostránkový hash
routing) se po migraci rozbijou, pokud se o ně nikdo nepostará — a lidé
je mohli nasdílet na Facebooku, v novinách, v diskuzích. Řešení:
`index.html` na kořeni (Domů) si ponechá malý JS snippet, který při
načtení zkontroluje starý hash a přesměruje (`location.replace`) na
novou adresu.

**Pozor — nejde o prostou náhradu `#panel` → `/panel/`.** Dnešní
`data-panel` hodnoty (skutečné hodnoty z `index.html`, ne odhad) se u
části sekcí liší od navržených nových cest v 2.1:

| starý hash (`#...`) | nová cesta |
|---|---|
| `#domu` | `/` |
| `#jednani` | `/jednani/` |
| `#zpravodaj` | `/noviny/` |
| `#lide` | `/lide/` |
| `#plan` | `/plan/` |
| `#volby2018` | `/volby/2018/` |
| `#volby2022` | `/volby/2022/` |
| `#volby2026` | `/volby/2026/` |
| `#smlouvy` | `/smlouvy/` |
| `#zakazky` | `/zakazky/` |
| `#pozemky` | `/pozemky/` |
| `#pokladna` | `/pokladna/` |
| `#owebu` | `/o-webu/` |

U 5 z 13 sekcí (`zpravodaj`, `owebu`, `volby2018/2022/2026`) se starý
slug a nová cesta liší (přejmenování nebo rozklad do vnořené cesty) —
redirect skript proto musí mít tuhle mapu natvrdo v sobě, ne odvozovat
cestu z hashe automaticky. Bez ní by právě těchto 5 sekcí po migraci
mířilo na neexistující URL a starý sdílený odkaz by skončil na chybové
stránce. Alternativa (jednodušší na údržbu, ale méně hezké URL): nová
cesta = starý `data-panel` slug beze změny (`/zpravodaj/`, `/owebu/`,
`/volby2018/`) — pak mapovací tabulka odpadá úplně. Rozhodnutí mezi
hezčími URL (s mapou) a jednoduššími URL (beze změny slugů) je na
zvážení, až se půjde do realizace.

Záložky v rámci sekce (`#zalozka`, viz 2.2) dnes nemají žádnou URL
reprezentaci vůbec (viz sekce 1) — pro ně tedy žádná zpětná
kompatibilita řešit netřeba, jen dopředná (nový zápis/čtení hashe).
Tenhle redirect snippet by měl zůstat natrvalo, ne jen po dobu migrace.

## 3. Generovací skript (`scripts/build.py`)

- Čistě Python (stejně jako zbytek automatizace v projektu), žádná nová
  závislost.
- Jednoduché šablonování — `{{PLACEHOLDER}}` nahrazování v
  `templates/page.html`, žádný šablonovací framework (Jinja apod. by byl
  zbytečná závislost pro tuhle velikost webu).
- Pro každou sekci: načte `content/<sekce>.html` + metadata (title,
  description — nové, per-sekce, na rozdíl od dnešního jednoho
  společného `<title>`) → vloží do `templates/page.html` spolu s
  `assets/nav.html` → zapíše `<sekce>/index.html`.
- Validace po sestavení: rozšířit dnešní tag-balance/JS-syntax kontrolu
  (používaná už u `update-pozemky.py`) na všechny vygenerované soubory,
  ne jen na `index.html`.
- Vygeneruje navíc `sitemap.xml` (výčet všech `<sekce>/index.html`) a
  `robots.txt` — dnes chybí obojí.
- Spouští se ručně před `git push`/publikací, stejně jako dnešní
  `update-pozemky.py` — žádný CI, žádný automatický build na
  GitHub Pages straně.

## 4. Co migrace ruší / nahrazuje

- `pecky-jednani/index.html` a `pecky-noviny/index.html` (dnešní
  standalone kopie) — jejich smysl (samostatná stránka pro sekci) splní
  nově `/jednani/index.html` a `/noviny/index.html` generované ze
  stejného `content/jednani.html` jako uvidí uživatel na webu. Duplicitní
  ruční údržba dvou kopií té samé logiky odpadá.
- Konvence „needit do samostatných JS/CSS souborů" v `CLAUDE.md` (řádek
  17) — po migraci naopak *needit* přímo do vygenerovaných
  `<sekce>/index.html`, ale do `content/<sekce>.html` +
  `assets/common.js`/`styles.css` a pustit `build.py`. Tohle je potřeba
  v `CLAUDE.md` přepsat, až se migrace provede — jinak bude dokumentace
  mluvit proti nové realitě.

## 5. Co se nemění

- Datové soubory (`pecky-jednani/pecky-jednani.json`, `people.json`,
  `sources.json` atd.) — beze změny, jen HTML kolem nich.
- Dokumentace jednotlivých sekcí (`pecky-<sekce>/README.md`) — zůstává,
  jen přibude zmínka, že zobrazení dané sekce žije v
  `content/<sekce>.html`, ne přímo v kořenovém `index.html`.
- Git/GitHub publikační workflow („Publikuj" jako explicitní spouštěč,
  token z `.github-pat`) — beze změny.
- Vizuální styl (pergamenově-úřední, Fraunces + IBM Plex) — jen se CSS
  přesune z `<style>` v hlavičce do `assets/styles.css`, obsahově beze
  změny.

## 6. Doporučené pořadí, až se půjde do realizace

I když se má migrace odbýt jako jeden souvislý běh (ne postupně po
sekcích s průběžným publikováním), v rámci toho jednoho běhu dává smysl
tenhle vnitřní pořadí kroků — minimalizuje riziko, že se něco rozbije
nepozorovaně:

1. Postavit kostru: `templates/page.html`, `assets/nav.html`,
   `assets/styles.css`, `assets/common.js`, `scripts/build.py` (zatím
   bez obsahu sekcí).
2. Rozřezat dnešní `index.html` na `content/<sekce>.html` (13 souborů) —
   mechanický krok, obsah beze změny.
3. Rozšířit `.subtabs` handler o čtení/zápis hashe (`#zalozka`) — otestovat
   na sekcích, které záložky už mají (Volby 2018, Volby 2022, Pozemky).
4. Přidat redirect snippet pro staré `#panel` odkazy do kořenového
   `index.html`.
5. Spustit `build.py`, projet validaci (tag balance + JS syntax) na
   všech 13 vygenerovaných souborů.
6. Ručně proklikat každou sekci a každou záložku — zkontrolovat, že
   hledání, filtrování a interaktivní prvky (typicky JS funkce vázané na
   `id`, které teď žijí v jedné velké `<script>`) fungují i po rozdělení.
7. Smazat `pecky-jednani/index.html` a `pecky-noviny/index.html`
   (nahrazené), aktualizovat `CLAUDE.md` (bod 4) a `AUTOMATION.md`
   (cesty k souborům, které update-pozemky.py přepisuje, se změní z
   `index.html` na `content/pozemky.html`).
8. Teprve pak `git push` / „Publikuj".

## 7. Rizika

- **2 800+ řádků provázaného JS** — funkce jako `jLinkParcely`,
  `loadJednani`, `loadNoviny` očekávají dnes existenci konkrétních `id`
  na stránce; při rozdělení do `assets/common.js` je třeba ověřit, že
  žádná sekce netiše nespoléhá na to, že běží vedle jiné (zatím nic
  takového nebylo v kódu vidět, ale je to potřeba prověřit při kroku 6
  výše).
- **Staré odkazy** — bez redirect snippetu (bod 2.3) by migrace tiše
  rozbila sdílené odkazy na Facebooku/v novinách. Musí být hotové dřív,
  než se stránka publikuje.
- **SEO přechodný výpadek** — změna URL sekcí (`/#jednani` →
  `/jednani/`) může krátkodobě ovlivnit vyhledávací indexaci; zmírňuje
  to `sitemap.xml` a to, že redirect snippet aspoň funguje pro uživatele
  (ne pro boty, ti starou stránku prostě přeindexují na novou přes
  odkazy v `sitemap.xml`).
