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

## Stav archivu (aktuální, k 16. 8. 2026)
**Kompletní: 68/68 vydání, 2020–2026**, nejnovější je Červenec–srpen 2026.
Archiv byl zrcadlený z pecky.cz — dřívější blokáda botů na archivní
rozcestníkové stránce (viz níže) byla obejita jednorázově, výsledek je
uložený lokálně a dál se z něj jen doplňuje.

### Kde co je
| Co | Kde | Formát |
|---|---|---|
| Obálky vydání (náhledy v gridu) | `pecky-noviny/img/{slug}.jpg` | JPG |
| Fulltext obsahu pro vyhledávání | `pecky-noviny/pecky-noviny.json` | JSON: `{meta, editions:[{label, year, url, file, slug, pages:[string], page_count}]}`, extrakce `pdftotext -layout` |
| Přímé PDF odkazy na pecky.cz | `url` pole v `pecky-noviny/pecky-noviny.json` | — |
| **Lokální kopie všech PDF** | `pecky-noviny/Data/{slug}.pdf` | PDF, ~177 MB / 68 souborů, staženo `pecky-noviny/download.py` |
| **Samostatná stránka sekce** | `pecky-noviny/index.html` | viz „Samostatná stránka" níže |

`slug` = `{RRRR}-{MM}` (`{RRRR}-{MM}-{MM}` pro červenec–srpen dvojčíslo,
např. `2026-07-08`) — je to pole přímo v `pecky-noviny.json` u každého
vydání, používají ho shodně `img/`, `Data/` i `pecky-noviny/index.html`,
aby nevznikaly tři nezávislé implementace stejné konvence pojmenování.

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

### Zobrazení v panelu
V `index.html` je to grid karet (`.noviny-card`) seskupený po letech
(nejnovější rok nahoře, v roce nejnovější měsíc jako první), každá karta
= obálka + odkaz na PDF (`target="_blank"`). Nad gridem je fulltextové
vyhledávací pole (`#noviny-search`), které při vstupu do panelu asynchronně
načte `pecky-noviny/pecky-noviny.json` (`loadNoviny()`, index.html ~ř. 2096) a hledá
bez ohledu na diakritiku/velikost písmen napříč stránkami všech vydání.

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
2. Stáhnout PDF do `pecky-noviny/Data/{slug}.pdf` (přímý `curl`, bez bot
   ochrany — viz výše), případně přes `pecky-noviny/download.py` po
   doplnění záznamu do `pecky-noviny/pecky-noviny.json`.
3. Extrahovat text (`pdftotext -layout`) a přidat `edition` objekt do
   `pecky-noviny/pecky-noviny.json` (`label`, `year`, `url`, `file`, `slug`,
   `pages`, `page_count`) a zvýšit `meta.editions_count`/`meta.pages_total`.
4. Vygenerovat/uložit náhled obálky do `pecky-noviny/img/{slug}.jpg`.
5. Přidat kartu do příslušné roční sekce v kořenovém `index.html`
   (`.noviny-card`, nejnovější nahoře) a upravit počet vydání v
   `<p class="lede">` textu panelu.
6. `pecky-noviny/index.html` (samostatná stránka, viz níže) se aktualizuje
   **automaticky** — grid i vyhledávání se generují za běhu z
   `pecky-noviny.json`, stačí krok 3.
7. Ověřit datum poslední aktualizace v odkazu na zdroj archivu v
   kořenovém `index.html` (ř. ~1657).

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
- Karty i výsledky hledání odkazují na **lokální PDF** (`Data/{slug}.pdf`),
  ne na pecky.cz — stránka tak funguje i offline/mimo hosting hlavního
  webu. Výsledky hledání navíc nabízí i odkaz na originál na pecky.cz.
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
