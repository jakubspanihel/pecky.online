# Instrukce k sekci: Pečecké noviny (panel „Zpravodaj")

Referenční dokument pro práci na panelu `panel-zpravodaj` v `index.html`
webu pecky.online. Doplňuje obecné instrukce projektu (Project instructions
/ CLAUDE.md) — tohle je detail jen pro tuhle jednu sekci.

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

## Stav archivu (aktuální, k 19. 8. 2026)
**156 vydání, 2008–2026** — dva různé zdroje:
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

  Historie dávek: 2008–2011 (43 vydání, `TEMP/{rok}/PN {rok}/{mm}{rr}.pdf`,
  18. 8. 2026) → 2016–2019 (36 vydání, `TEMP/{rok}/Pečecké noviny
  {měsíc}-{rok}[ - web/náhled].pdf`, 19. 8. 2026) → doplnění 2019 (9 vydání,
  `TEMP/Pececke noviny {měsíc}-2019 - web/nahled.pdf`, bez diakritiky a bez
  podsložky roku, 19. 8. 2026 — leden a únor byly v dávce znovu, ale už
  existovaly v archivu, takže byly přeskočeny jako duplicity).

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

### Kde co je
| Co | Kde | Formát |
|---|---|---|
| Obálky vydání (náhledy v gridu) | `pecky-noviny/img/{slug}.jpg` | JPG, 1. strana, `pdftoppm -r 46 -jpegopt quality=75` (~380 px šířka, odpovídá `aspect-ratio:380/538` v CSS) |
| Fulltext obsahu pro vyhledávání | `pecky-noviny/pecky-noviny.json` | JSON: `{meta, editions:[{label, year, url, file, slug, pages:[string], page_count}]}`, extrakce `pdftotext -layout` |
| Přímé PDF odkazy na pecky.cz | `url` pole v `pecky-noviny/pecky-noviny.json` — `null` u vydání 2008–2011 a 2016–2019 (nejsou na pecky.cz, viz mezery výše) | — |
| **Lokální kopie všech PDF** | `pecky-noviny/Data/PN {rok}/{slug}.pdf` (**pozor:** v HTML/JS hrefech se mezera v `PN {rok}` píše jako `PN%20{rok}`, na disku je to reálná mezera ve jménu složky) | PDF, ~232 MB / 156 souborů (68 staženo `pecky-noviny/download.py`, 88 z lokálního archivu 2008–2011 a 2016–2019) |
| **Náhledy jednotlivých stránek** (pro preview ve výsledcích hledání) | `pecky-noviny/pages/{slug}/{page}.jpg` | JPG, **všechny** strany, 40 DPI/kvalita 60 (~32 KB/strana, ~39 MB/2346 stran), vygenerováno `pecky-noviny/render_pages.py` |
| **Samostatná stránka sekce** | `pecky-noviny/index.html` | viz „Samostatná stránka" níže |

`slug` = `{RRRR}-{MM}` (`{RRRR}-{MM}-{MM}` pro červenec–srpen dvojčíslo,
např. `2026-07-08`) — je to pole přímo v `pecky-noviny.json` u každého
vydání, používají ho shodně `img/`, `Data/`, `pages/` i
`pecky-noviny/index.html`, aby nevznikaly nezávislé implementace stejné
konvence pojmenování. `{page}` v `pages/{slug}/{page}.jpg` je 1-based
číslo strany bez zarovnávání nulami (`1.jpg`…`16.jpg`, ne `01.jpg`).

`pecky-noviny/` je kanonické místo pro **všechno** související s touto
sekcí — tenhle dokument, extrahovaný fulltext, obálky, zdrojová PDF,
samostatná stránka i nástroje kolem nich. Jediná výjimka je zobrazení
v hlavním panelu, které zůstává v kořenovém `index.html` (needituje se
do samostatných souborů, jednosouborová struktura webu). Jakékoli nové
soubory týkající se Pečeckých novin (data, poznámky, skripty, obrázky)
patří do `pecky-noviny/`, ne do kořene repa ani do `data/`/`img/`.

`pecky-noviny/download.py` čte `pecky-noviny/pecky-noviny.json` a
stahuje/doplňuje chybějící PDF do `Data/` (idempotentní — existující
soubory přeskakuje).

`pecky-noviny/render_pages.py` čte `pecky-noviny/pecky-noviny.json`,
pro každé vydání spustí `pdftoppm` (poppler — stejná rodina nástrojů
jako `pdftotext`) na `Data/PN {rok}/{slug}.pdf` a uloží každou stranu jako
`pages/{slug}/{page}.jpg`. Idempotentní (přeskočí vydání, které má
všechny strany už vyrenderované) — vygenerování celého archivu (1022
stran) trvá ~15 s.

### Zobrazení v panelu
V `index.html` je to grid karet (`.noviny-card`) seskupený po letech
(nejnovější rok nahoře, v roce nejnovější měsíc jako první), každá karta
= obálka + odkaz na PDF (`target="_blank"`). Nad gridem je fulltextové
vyhledávací pole (`#noviny-search`), které při vstupu do panelu asynchronně
načte `pecky-noviny/pecky-noviny.json` (`loadNoviny()`, index.html ~ř. 2096) a hledá
bez ohledu na diakritiku/velikost písmen napříč stránkami všech vydání.

### Náhledy stránek ve výsledcích hledání
Každý výsledek hledání (`.hit-card.hit-card--noviny`) zobrazuje vlevo
malý náhled konkrétní nalezené strany (`pages/{slug}/{page}.jpg`, karta
odkazuje na PDF na dané straně) vedle úryvku textu s zvýrazněním. Náhled
je při 40 DPI čitelný jen jako vizuální orientace (rozložení, fotky,
nadpisy) — pro text slouží zvýrazněný úryvek, ne obrázek. Implementace
(CSS `.hit-preview`/`.hit-body`, JS šablona v `nRunSearch`) je stejná
v kořenovém `index.html` i v `pecky-noviny/index.html`. `.hit-card`
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
2. Stáhnout PDF do `pecky-noviny/Data/PN {rok}/{slug}.pdf` (přímý `curl`, bez bot
   ochrany — viz výše), případně přes `pecky-noviny/download.py` po
   doplnění záznamu do `pecky-noviny/pecky-noviny.json`.
3. Extrahovat text (`pdftotext -layout`) a přidat `edition` objekt do
   `pecky-noviny/pecky-noviny.json` (`label`, `year`, `url`, `file`, `slug`,
   `pages`, `page_count`) a zvýšit `meta.editions_count`/`meta.pages_total`.
4. Vygenerovat/uložit náhled obálky do `pecky-noviny/img/{slug}.jpg`.
5. Spustit `pecky-noviny/render_pages.py` — vygeneruje náhledy všech stran
   nového vydání do `pages/{slug}/` (idempotentní, existující vydání
   přeskočí, takže stačí spustit bez parametrů).
6. Přidat kartu do příslušné roční sekce v kořenovém `index.html`
   (`.noviny-card`, nejnovější nahoře) a upravit počet vydání v
   `<p class="lede">` textu panelu.
7. `pecky-noviny/index.html` (samostatná stránka, viz níže) se aktualizuje
   **automaticky** — grid i vyhledávání (včetně náhledů stránek z kroku 5)
   se generují za běhu z `pecky-noviny.json`, stačí krok 3.
8. Ověřit datum poslední aktualizace v odkazu na zdroj archivu v
   kořenovém `index.html` (ř. ~1657).

### Doplnění dávky z lokálního archivu (TEMP/)
Když uživatel dodá další skupinu PDF mimo pecky.cz (např. do budoucna
2012–2015), postup:

1. Soubory čekají v `pecky-noviny/TEMP/{rok}/*.pdf` — **struktura ani
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
7. Doplnit kartu do kořenového `index.html` (`href` rovnou na
   `pecky-noviny/Data/PN {rok}/{slug}.pdf`, ne na pecky.cz — url je `null`) a do
   společné „Zdroj: lokální archiv…" poznámky pod gridem aktualizovat
   celkový počet a rozsah let. `pecky-noviny/index.html` se aktualizuje
   automaticky (viz „Samostatná stránka" níže), stačí upravit počet
   vydání v perexu a v `<meta name="description">`.
8. Ověřit, že `.hit-card` fallback na lokální PDF funguje i pro nová
   vydání (`h.ed.url || 'pecky-noviny/Data/PN%20' + h.ed.year + '/' + h.ed.slug + '.pdf'`
   v kořenovém `index.html`; `pecky-noviny/index.html` používá lokální PDF
   vždy, viz „Rozdíly oproti panelu" níže) — u dosavadních dávek už to
   funguje, nová vydání jen musí mít `url: null`. **Mezera v `PN {rok}`
   musí být v URL/href jako `%20`**, ne doslovná mezera (prohlížeč ji
   sice u kliknutí obvykle dokáže domyslet, ale `fetch()` a některé
   nástroje ne — viz „Kde co je" výše).
9. Smazat `TEMP/` (obsah je beze zbytku v `Data/`) a jednorázový
   zpracovávací skript, pokud byl napsaný jako samostatný soubor.

## Samostatná stránka (`pecky-noviny/index.html`)
Vedle panelu v hlavním webu existuje i samostatná, nezávisle otevíratelná
stránka `pecky-noviny/index.html` — stejný obsah (úvod, fulltextové
hledání, grid vydání po letech), ale bez hlavičky/navigace na ostatní
sekce webu (`header.site`/`nav.tabs` z kořenového `index.html` tam
záměrně nejsou — je to čistě samostatná obrazovka). V patičce je jen
textový odkaz zpět na `pecky.online`.

Rozdíly oproti panelu v hlavním webu:
- **Grid vydání se generuje za běhu v JS** z `pecky-noviny.json`
  (`renderGrid()`), ne jako ručně psané `.noviny-card` odkazy — nový
  záznam v JSON se tedy v gridu objeví bez úpravy HTML.
- Karty, náhledy stránek ve výsledcích hledání i odkazy v patičce
  výsledku odkazují na **lokální PDF** (`Data/PN {rok}/{slug}.pdf`), ne na
  pecky.cz — stránka tak funguje i offline/mimo hosting hlavního webu.
  Výsledky hledání navíc nabízí i odkaz na originál na pecky.cz (v
  kořenovém `index.html` je to naopak — tam odkazuje na pecky.cz,
  lokální PDF se tam neodkazují). **Výjimka:** u vydání s `url: null`
  (archiv 2008–2011, viz mezery výše) odkazuje na lokální PDF i kořenový
  `index.html` — jinak by karta/odkaz vedly na neexistující URL. Karty
  grid v kořenovém `index.html` to řeší přímo v ručně psaném `href`, JS
  hledání v obou souborech fallbackem
  `h.ed.url || 'Data/PN%20' + h.ed.year + '/' + h.ed.slug + '.pdf'`.
- Sdílí stejné CSS proměnné a fonty (Fraunces/IBM Plex) jako hlavní web
  pro vizuální konzistenci, ale jen podmnožinu stylů, které skutečně
  používá (žádné styly pro ostatní panely).
- JS logika hledání (`jStripDiacritics`, `jNorm`, `jHighlight`,
  `nRunSearch` apod.) je zkopírovaná z kořenového `index.html` — při
  úpravě chování hledání na jednom místě zvážit, jestli neupravit i
  druhé (zatím není sdílené, jednosouborová konvence hlavního webu
  brání společnému JS souboru).

## Co NEPSAT do této sekce
- Odhadovaná nebo rekonstruovaná témata čísel, která nebyla fyzicky
  nalezena (žádné vyplňování mezer domněnkou)
- Interpretace/komentář k obsahu novin nad rámec věcného shrnutí témat
