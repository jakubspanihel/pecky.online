# Instrukce k sekci: Pečecké noviny (panel „Zpravodaj")

Referenční dokument pro práci na panelu `panel-zpravodaj` v
`content/zpravodaj.html` (generuje se do veřejné stránky `/noviny/`,
viz `scripts/build.py`). Doplňuje obecné instrukce projektu (Project instructions
/ CLAUDE.md) — tohle je detail jen pro tuhle jednu sekci.

## Umístění souborů
Všechny soubory týkající se Pečeckých novin (tento dokument, extrahovaný
fulltext JSON, obálky, stažená PDF, skripty) patří do `noviny/`, ne
do kořene repa ani do `data/`/`img/` — i nově vznikající. Jediná výjimka:
zobrazení sekce žije v `content/zpravodaj.html` (od migrace na
vícestránkový web 30. 8. 2026 — viz `ARCHITEKTURA-MIGRACE.md` v kořeni
repa) — needit vygenerovanou veřejnou stránku (`noviny/index.html`)
přímo, jen `content/zpravodaj.html` a pak spustit `scripts/build.py`.
Dřívější samostatná stránka `noviny/index.html` (kopie bez
hlavičky hlavního webu) migrací zanikla — nahradila ji plnohodnotná
veřejná stránka `/noviny/`.

## Účel sekce
Přehled informačního měsíčníku, který vydává město Pečky: archiv obálek
vydání 2020–2026 s odkazy na PDF a fulltextové vyhledávání napříč jejich
obsahem.

## Ověřená fakta o zpravodaji
- Název: **Pečecké noviny**
- Periodicita: měsíčně, mimo prázdninové dvojčíslo (červenec–srpen)
- Náklad: cca 1 000 kusů
- Vydavatel: Město Pečky
- Redakce: Alena Brantová, kontakt `noviny@pecky.cz`

## Stav archivu (aktuální, k 2. 9. 2026)
**161 vydání, 2001, 2005–2026** (2002–2004 chybí) — tři různé zdroje:
- **2020–2026: 68/68 vydání**, nejnovější je Červenec–srpen 2026. Zrcadlené
  z pecky.cz — dřívější blokáda botů na archivní rozcestníkové stránce (viz
  níže) byla obejita jednorázově, výsledek je uložený lokálně a dál se z něj
  jen doplňuje. `url`/`file` v JSON u těchto vydání odkazují na pecky.cz.
- **2008–2011 a 2016–2019: 88 vydání** (43 + 45) z lokálního archivu, který
  poskytl uživatel postupně ve třech dávkách — adresář `TEMP/*.pdf` (buď
  přímo, nebo v podsložkách `TEMP/{rok}/`), po zpracování vždy smazán,
  obsah beze zbytku v `Data/`. Každá dávka měla jinou strukturu/pojmenování
  (viz historie níže) — název měsíce/roku se vždy parsuje z názvu souboru,
  ne z cesty ani z předpokladu o formátu. **Tato vydání nejsou dostupná
  v aktuálním online archivu pecky.cz** (rozcestník i staré `filemanager`
  odkazy vrací 404) — mají proto `"url": null, "file": null` v JSON a karty
  na webu odkazují jen na lokální `Data/PN {rok}/{slug}.pdf`.
- **2001, 2005–2006: 5 vydání** (2. 9. 2026) — čtvrtá dávka lokálního
  archivu, tentokrát nahraná uživatelem přímo do `Data/PN {rok}/{slug}.pdf`
  (bez mezikroku přes `TEMP/`), soubory už pojmenované přímo cílovým slugem.
  Viz „Dávka 2001/2005/2006" níže pro detaily a známé mezery.

  Historie dávek: 2008–2011 (43 vydání, `TEMP/{rok}/PN {rok}/{mm}{rr}.pdf`,
  18. 8. 2026) → 2016–2019 (36 vydání, `TEMP/{rok}/Pečecké noviny
  {měsíc}-{rok}[ - web/náhled].pdf`, 19. 8. 2026) → doplnění 2019 (9 vydání,
  `TEMP/Pececke noviny {měsíc}-2019 - web/nahled.pdf`, bez diakritiky a bez
  podsložky roku, 19. 8. 2026 — leden a únor byly v dávce znovu, ale už
  existovaly v archivu, takže byly přeskočeny jako duplicity) → 2001/2005/2006
  (5 vydání, přímo do `Data/`, 2. 9. 2026).

### Známé mezery v archivu 2008–2011
- **2/2011 a 3/2011 chybí.** Soubor archivovaný jako „0211" je ve
  skutečnosti duplicitní kopie ledna 2011 (15/16 stran textově identických s
  „0111", 16. strana se liší jen o jednu větu) — ne skutečné únorové číslo.
  Vyřazeno, aby se pod únorem nepublikoval fakticky lednový obsah.
- **10/2009, 11/2010 a 12/2010 chybí** — v poskytnutém archivu nebyly.
- **9/2010 je dochované jen jako neúplný 4stránkový výřez** (chybí titulní
  strana a většina čísla) — ponecháno v archivu i tak, karta na webu je
  označená „neúplné".
- **8/2009 (`0809.pdf`)** měl při extrakci `pdftotext` text na všech
  stránkách zrcadlově obrácený znak po znaku (zjevná vada zdrojového PDF/jeho
  fontu, ne chyba nástroje) — opraveno zpětným obrácením každého řádku po
  extrakci, obsah čísla je jinak kompletní a čitelný.
- **7/2011** má v tiráži překlep zdroje „červnec" místo „červenec" —
  ponecháno verbatim (text se nepřepisuje, i když je zjevný překlep
  originálu).

### Známé mezery v archivu 2016–2019
- **Celé roky 2012–2015 chybí** — zatím nedohledáno, žádný zdroj poskytnutý
  ani nalezený.
- **Leden 2016 chybí** — v poskytnuté dávce nebyl, ostatních 11 čísel roku
  2016 (únor–prosinec) je kompletních.
- **Srpen 2019 chybí** — jediný chybějící měsíc v roce 2019, zbytek roku
  (leden–červenec, září–prosinec) je po třetí dávce kompletní.
- 2016 a 2017 mají červenec a srpen jako **dvě samostatná čísla** (ne
  dvojčíslo); 2018 naopak jako **jedno dvojčíslo** „7-8" — zachováno podle
  skutečné struktury zdrojových souborů, ne sjednoceno uměle.

### Dávka 2001/2005/2006 (2. 9. 2026)
5 vydání nahraných přímo do `Data/`, soubory už pojmenované cílovým slugem
(`{RRRR}-{MM}.pdf`), žádné přejmenovávání podle obsahu nebylo potřeba —
jen sejmutí popisných přípisků v původním názvu souboru (`(1st page)`,
`(1st page missing)`) do samostatné poznámky/badge na kartě, viz níže.

- **2001: dochoval se jen červen, a to jako 1stránkové torzo** (jen titulní
  strana) — karta označená „neúplné". Zbytek roku 2001 ani roky 2002–2004
  nedohledány.
- **2005: dochovalo se jen dvojčíslo červenec–srpen** (28 stran, kompletní).
  Zbytek roku nedohledán.
- **2006: dochovaly se jen leden (bez titulní strany, 7 stran), únor
  (18 stran) a březen (20 stran)**, únor a březen kompletní. Leden karta
  označená „neúplné" (stejný vzor jako 9/2010 výše). Duben–prosinec 2006
  nedohledány.
- **Fyzická velikost stránky A3, ne A4** (842×1191 pt) u `2001-06` a
  `2006-01` — na rozdíl od zbytku archivu (A4, 595×842 pt). Pevné DPI podle
  vzorce v „Kde co je" (46 DPI pro obálky, 40 DPI pro `pages/`) by u těchto
  dvou vydání dalo ~1,4× větší obrázky než zbytek archivu. Obálky proto
  vygenerovány přes `pdftoppm -scale-to-x 380 -scale-to-y -1` (cílová šířka
  přímo, bez ohledu na zdrojovou velikost stránky) — `pages/` náhledy jsou
  o něco větší (468×662 px místo 331×468 px), ale to nevadí: `.hit-preview`
  v CSS je má stejně omezené na pevných 72 px šířky (`aspect-ratio` +
  `object-fit:cover`), takže se to na webu nijak neprojeví.
- **`2001-06` a `2006-01` (dohromady 8 stran) měly text z `pdftotext`
  nepoužitelný** — vlastní/poškozené kódování fontů z dobového DTP softwaru
  (tituly `06str1.pm6`/`06str2.pm6` v metadatech PDF potvrzují PageMaker).
  Na rozdíl od 8/2009 výše (kde šlo o čistě zrcadlené znaky, opravitelné
  jednoduchým obrácením řádku) je tahle vada nevratná — chybí i jednotlivé
  diakritické znaky, ne jen přehozené pořadí. Řešení: nainstalován
  `tesseract` (+ `tesseract-lang` pro češtinu) přes Homebrew, stránky
  vyrenderovány přes `pdftoppm -r 300 -png` a rozpoznány `tesseract … -l ces
  --psm 3`. Výsledek je čitelný, ojedinělé chyby rozpoznání se dají čekat
  hlavně v hustě sázených tabulkách (viz str. 7 vydání `2006-01`). Zbytek
  archivu dál extrahuje `pdftotext -layout` beze změny — OCR je jen záložní
  cesta pro tato dvě konkrétní vydání, ne nová výchozí metoda.
  **Vedlejší efekt instalace:** `brew install tesseract` vyvolal upgrade
  `icu4c`, což rozbilo systémový `node` (starý binář odkazoval na
  neexistující `libicui18n.69.dylib`, potřebné pro JS-syntax validaci
  v `scripts/build.py`) — opraveno `brew reinstall node` (16.2.0 → 26.8.1).

### Kde co je
| Co | Kde | Formát |
|---|---|---|
| Obálky vydání (náhledy v gridu) | `noviny/img/{slug}.jpg` | JPG, 1. strana, `pdftoppm -r 46 -jpegopt quality=75` (~380 px šířka, odpovídá `aspect-ratio:380/538` v CSS); u stránek jiné fyzické velikosti než A4 (viz „Dávka 2001/2005/2006") místo pevného DPI `-scale-to-x 380 -scale-to-y -1` |
| Fulltext obsahu pro vyhledávání | `noviny/pecky-noviny.json` | JSON: `{meta, editions:[{label, year, url, file, slug, pages:[string], page_count}]}`, extrakce `pdftotext -layout`; u 2 vydání (`2001-06`, `2006-01`) OCR přes `tesseract -l ces` místo toho, viz „Dávka 2001/2005/2006" |
| Přímé PDF odkazy na pecky.cz | `url` pole v `noviny/pecky-noviny.json` — `null` u vydání 2001, 2005–2006, 2008–2011 a 2016–2019 (nejsou na pecky.cz, viz mezery výše) | — |
| **Lokální kopie všech PDF** | `noviny/Data/PN {rok}/{slug}.pdf` (**pozor:** v HTML/JS hrefech se mezera v `PN {rok}` píše jako `PN%20{rok}`, na disku je to reálná mezera ve jménu složky) | PDF, ~236 MB / 161 souborů (68 staženo `noviny/download.py`, 93 z lokálního archivu — 2001, 2005–2006, 2008–2011 a 2016–2019) |
| **Náhledy jednotlivých stránek** (pro preview ve výsledcích hledání) | `noviny/pages/{slug}/{page}.jpg` | JPG, **všechny** strany, 40 DPI/kvalita 60 (~32 KB/strana, ~39 MB/2346 stran), vygenerováno `noviny/render_pages.py` |

`slug` = `{RRRR}-{MM}` (`{RRRR}-{MM}-{MM}` pro červenec–srpen dvojčíslo,
např. `2026-07-08`) — je to pole přímo v `pecky-noviny.json` u každého
vydání, používají ho shodně `img/`, `Data/`, `pages/` i
`content/zpravodaj.html`, aby nevznikaly nezávislé implementace stejné
konvence pojmenování. `{page}` v `pages/{slug}/{page}.jpg` je 1-based
číslo strany bez zarovnávání nulami (`1.jpg`…`16.jpg`, ne `01.jpg`).

`noviny/` je kanonické místo pro **všechno** související s touto
sekcí — tenhle dokument, extrahovaný fulltext, obálky, zdrojová PDF
i nástroje kolem nich. Jediná výjimka je zobrazení v hlavním panelu,
které žije v `content/zpravodaj.html` (needituje se vygenerovaná
veřejná stránka přímo, viz sekce Umístění souborů výše). Jakékoli nové
soubory týkající se Pečeckých novin (data, poznámky, skripty, obrázky)
patří do `noviny/`, ne do kořene repa ani do `data/`/`img/`.

`noviny/download.py` čte `noviny/pecky-noviny.json` a
stahuje/doplňuje chybějící PDF do `Data/` (idempotentní — existující
soubory přeskakuje).

`noviny/render_pages.py` čte `noviny/pecky-noviny.json`,
pro každé vydání spustí `pdftoppm` (poppler — stejná rodina nástrojů
jako `pdftotext`) na `Data/PN {rok}/{slug}.pdf` a uloží každou stranu jako
`pages/{slug}/{page}.jpg`. Idempotentní (přeskočí vydání, které má
všechny strany už vyrenderované) — vygenerování celého archivu (1022
stran) trvá ~15 s.

### Zobrazení v panelu
V `content/zpravodaj.html` je to grid karet (`.noviny-card`) seskupený po
letech (nejnovější rok nahoře, v roce nejnovější měsíc jako první), každá
karta = obálka + odkaz na PDF (`target="_blank"`). Nad gridem je fulltextové
vyhledávací pole (`#noviny-search`), které při vstupu do panelu asynchronně
načte `noviny/pecky-noviny.json` (`loadNoviny()` v `content/zpravodaj.html`)
a hledá bez ohledu na diakritiku/velikost písmen napříč stránkami všech vydání.

### Náhledy stránek ve výsledcích hledání
Každý výsledek hledání (`.hit-card.hit-card--noviny`) zobrazuje vlevo
malý náhled konkrétní nalezené strany (`pages/{slug}/{page}.jpg`, karta
odkazuje na PDF na dané straně) vedle úryvku textu s zvýrazněním. Náhled
je při 40 DPI čitelný jen jako vizuální orientace (rozložení, fotky,
nadpisy) — pro text slouží zvýrazněný úryvek, ne obrázek. Implementace
(CSS `.hit-preview`/`.hit-body`, JS šablona v `nRunSearch`) žije v
`content/zpravodaj.html` — od migrace na vícestránkový web (30. 8. 2026)
existuje jen jednou, žádná ruční synchronizace duplicitní kopie (viz
„Samostatná stránka" níže). `.hit-card`
sdílí základní styl s výsledky hledání v sekci Jednání — modifikátor
`.hit-card--noviny` (flex layout s náhledem) je proto samostatná třída,
ne úprava `.hit-card` samotné, aby se nerozbilo rozvržení jednání.

## Známá mezera — archivní rozcestník na pecky.cz
Stránka `pecky.cz/default/default/21389_pdf-zpravodaje` (JS rozcestník na
jednotlivá PDF) je **primární zdroj pro měsíční kontrolu** (oficiální
městský archiv), ale je nespolehlivá — chráněná proti botům, `web_fetch`
na ni často selhává kvůli JS renderování. To už neblokuje nic zásadního
pro existující archiv (ten je kompletní), ale znamená to, že kontrola
nových čísel musí počítat s fallbackem, viz níže.

## Vzor URL jednotlivých PDF
Odkazy na jednotlivá vydání mají tvar:
```
https://pecky.cz/files/pecky/gallery/{gallery_id}/{hash}_{nazev-souboru}.pdf
```
Např. `.../18743/69cced40a0d6d_Pececke-noviny-4-2026.pdf`. `gallery_id` a
`hash` nejsou předvídatelné (nejde je odhadem dopočítat pro další čísla).
Přímé PDF odkazy samotné bot ochranou chráněné **nejsou** (na rozdíl od
rozcestníkové stránky) — `curl`/`web_fetch` na ně funguje běžně.

## Měsíční kontrola nových vydání
Zpravodaj vychází cca k začátku měsíce (mimo červenec–srpen, kdy je jedno
dvojčíslo). Postup pro doplnění nového čísla:

1. **Primární zdroj: archivní rozcestník** —
   `pecky.cz/default/default/21389_pdf-zpravodaje`. Je to oficiální
   městský archiv všech vydání, takže nejspolehlivější zdroj, *když
   funguje*. Zkusit nejdřív `web_fetch`/`WebFetch`. Stránka je ale známá
   tím, že vykresluje seznam přes JS a bot ochranu — pokud fetch vrátí
   prázdnou/obecnou stránku bez skutečného seznamu vydání, brát to jako
   „zdroj teď nedostupný", ne jako „nové číslo neexistuje", a pokračovat
   na fallback.
2. **claude-in-chrome jako druhý pokus na rozcestník** — reálná
   prohlížečová session někdy projde bot ochranu, kterou `web_fetch`
   neobejde. Navigovat přímo na URL výše a přečíst odkaz na nejnovější
   PDF ze stránky.
3. **`web_search`** — dotaz typu `Pečecké noviny [měsíc] [rok] pdf
   pecky.cz`. Funguje nezávisle na blokádě rozcestníku.
4. **Facebook města** (`facebook.com/mestopecky`) často avizuje nové číslo
   se sdíleným odkazem — stojí za prohledání příspěvků, když ostatní
   zdroje nic nenajdou (typicky těsně po vydání, než se to indexuje).
5. Jakmile je URL nalezená, **ověřit vzorem výše**, že jde skutečně o PDF
   z galerie zpravodajů (ne jiný dokument).

Poznámka k automatizované měsíční kontrole (cloud routine, viz níže): ta
má k dispozici jen `WebFetch`/`WebSearch`, ne `claude-in-chrome` (to je
nástroj jen v lokální desktop session) — zkouší tedy krok 1, pak rovnou
kroky 3–4. Krok 2 (claude-in-chrome) je dostupný jen když kontrolu dělá
Claude Code lokálně.

### Po nalezení nového čísla
1. Vytvořit `slug` pro vydání (`{RRRR}-{MM}`, resp. `{RRRR}-{MM}-{MM}` pro
   červenec–srpen dvojčíslo, např. `2026-09`).
2. Stáhnout PDF do `noviny/Data/PN {rok}/{slug}.pdf` (přímý `curl`, bez bot
   ochrany — viz výše), případně přes `noviny/download.py` po
   doplnění záznamu do `noviny/pecky-noviny.json`.
3. Extrahovat text (`pdftotext -layout`) a přidat `edition` objekt do
   `noviny/pecky-noviny.json` (`label`, `year`, `url`, `file`, `slug`,
   `pages`, `page_count`) a zvýšit `meta.editions_count`/`meta.pages_total`.
4. Vygenerovat/uložit náhled obálky do `noviny/img/{slug}.jpg`.
5. Spustit `noviny/render_pages.py` — vygeneruje náhledy všech stran
   nového vydání do `pages/{slug}/` (idempotentní, existující vydání
   přeskočí, takže stačí spustit bez parametrů).
6. Přidat kartu do příslušné roční sekce v `content/zpravodaj.html`
   (`.noviny-card`, nejnovější nahoře), upravit počet vydání v
   `<p class="lede">` textu panelu a spustit `python3 scripts/build.py`,
   ať se promítne do veřejné stránky `/noviny/`.
7. Ověřit datum poslední aktualizace v odkazu na zdroj archivu v
   `content/zpravodaj.html` (hledat text „Zdroj: … archiv PDF
   zpravodaje").

Vyhledávání (včetně náhledů stránek z kroku 5) se generuje za běhu z
`pecky-noviny.json` — žádný další ruční krok navíc, stačí krok 3.

### Doplnění dávky z lokálního archivu (TEMP/)
Když uživatel dodá další skupinu PDF mimo pecky.cz (např. do budoucna
2012–2015), postup:

1. Soubory čekají v `noviny/TEMP/{rok}/*.pdf` — **struktura ani
   pojmenování souborů nejsou garantované** (dvě dosavadní dávky měly
   každá jiný formát názvu, viz „Stav archivu" výše). Nejdřív se podívat,
   jak jsou pojmenované, a podle toho napsat/upravit parsovací regex
   (měsíc/rok z názvu souboru, ne z cesty ani obsahu).
2. Pro každý soubor: `slug` = `{RRRR}-{MM}` (`{RRRR}-{MM}-{MM}` pro
   dvojčíslo — **ověřit z názvu, jestli jde skutečně o dvojčíslo, ne
   předpokládat** — červenec/srpen bývají v různých letech samostatně
   i spojeně, viz mezery výše).
3. Zkopírovat PDF do `Data/PN {rok}/{slug}.pdf`, extrahovat text `pdftotext -layout`
   (normalizace: ořezat okraje řádků, sloučit vícenásobné mezery, zahodit
   prázdné řádky — viz co dělal skript použitý pro dávku 2016–2019).
4. Vygenerovat obálku (`pdftoppm -r 46 -jpegopt quality=75 -f 1 -l 1`) do
   `img/{slug}.jpg`.
5. Přidat `edition` objekt (`label`, `year`, `url: null`, `file: null`,
   `slug`, `pages`, `page_count`) do `pecky-noviny.json`, přepočítat
   `meta.editions_count`/`meta.pages_total`.
6. Spustit `render_pages.py` (doplní náhledy stránek pro nová vydání,
   idempotentní).
7. Doplnit kartu do `content/zpravodaj.html` (`href` rovnou na
   `noviny/Data/PN {rok}/{slug}.pdf`, ne na pecky.cz — url je `null`) a do
   společné „Zdroj: lokální archiv…" poznámky pod gridem aktualizovat
   celkový počet a rozsah let, upravit počet vydání v perexu a v
   `<meta name="description">`, pak spustit `python3 scripts/build.py`.
8. Ověřit, že `.hit-card` fallback na lokální PDF funguje i pro nová
   vydání (`h.ed.url || 'noviny/Data/PN%20' + h.ed.year + '/' + h.ed.slug + '.pdf'`
   v `content/zpravodaj.html`) — u dosavadních dávek už to
   funguje, nová vydání jen musí mít `url: null`. **Mezera v `PN {rok}`
   musí být v URL/href jako `%20`**, ne doslovná mezera (prohlížeč ji
   sice u kliknutí obvykle dokáže domyslet, ale `fetch()` a některé
   nástroje ne — viz „Kde co je" výše).
9. Smazat `TEMP/` (obsah je beze zbytku v `Data/`) a jednorázový
   zpracovávací skript, pokud byl napsaný jako samostatný soubor.

## Samostatná stránka (zaniklo migrací 30. 8. 2026)
Dřív (do 30. 8. 2026) existovala vedle panelu v hlavním webu i samostatná,
nezávisle otevíratelná stránka `noviny/index.html` se stejným
obsahem, ale bez hlavičky/navigace hlavního webu — duplicitní kód, který
šlo snadno rozjet (JS hledání muselo zůstávat ručně synchronizované mezi
oběma soubory). Migrace na vícestránkový web (`ARCHITEKTURA-MIGRACE.md`)
tenhle problém odstranila: `noviny/index.html` byl smazán, veřejná
stránka `/noviny/` se teď generuje ze stejného `content/zpravodaj.html`,
který vidí i tenhle dokument výše — žádná ruční synchronizace dvou kopií
JS logiky (`jStripDiacritics`, `jNorm`, `jHighlight`, `nRunSearch` apod.)
už není potřeba, `jStripDiacritics`/`jNorm`/`jHighlight`/`jEscapeHtml`
navíc teď žijí sdíleně v `assets/helpers.js`.

## Co NEPSAT do této sekce
- Odhadovaná nebo rekonstruovaná témata čísel, která nebyla fyzicky
  nalezena (žádné vyplňování mezer domněnkou)
- Interpretace/komentář k obsahu novin nad rámec věcného shrnutí témat
