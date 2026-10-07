# Monitoring úřední desky

Zdroj veřejné stránky **Monitoring úřední desky**
(`/o-webu/uredni-deska-monitoring/`, registrace `EXTRA_PAGES['udmonitoring']`
ve `scripts/build.py`, odkaz z O webu → Odkazy pod „Oficiální web města“).
Vzor: Monitoring Facebooku (`../facebook-monitoring/`) — stejný layout: graf, od 768 px vlevo
sticky strom let a měsíců (`ud-tree`), vpravo jednosloupcový výpis měsíce (`ud-pane`), na mobilu akordeon.
Tento layout platí pro všechny monitoringy.

## Data

`<rok>.txt` — jeden řádek na dokument, pole oddělená svislítkem:
`id_slug | vyvěšeno | sejmuto | typ | název`. Prázdný typ = „Úřední deska“.
Detail dokumentu je `https://pecky.cz/default/report/<id_slug>`. Soubory jsou
v gitu (data jsou veřejná). Aktuálně `2015.txt` až `2026.txt` — dokumenty vyvěšené od června 2015 do 6. 10. 2026,
celkem 1 919 záznamů (2015: 62, 2016: 185, 2017: 154, 2018: 142, 2019: 166, 2020: 194, 2021: 192,
2022: 198, 2023: 163, 2024: 149, 2025: 177, 2026: 137).

**Dva zdroje.** Základ je archiv na pecky.cz (nejstarší záznam 15. 3. 2016), který je za řadu let
neúplný (2016–2018 a 2021–2022 jen zlomek). Doplněn je starým webem `pecky.as4u.cz` (Úřední deska →
Hledat včetně archivu; data od 2015, od března 2026 se neaktualizuje). Řádky ze starého webu mají místo
`id_slug` předponu `as4u:<detail_claim>` (detail
`https://pecky.as4u.cz/redakce/index.php?lanG=cs&clanek=106922&slozka=106925&detail_claim=<id>`).
Záznam, který je na obou webech (shodný nebo téměř shodný název + datum vyvěšení), se drží jen
z pecky.cz. Sejmuto `do odvolání` = bez konečného data; sejmutí před vyvěšením (chyba zdroje)
generátor zobrazí jako „datum sejmutí je ve zdroji chybné“; typ `-----` = výchozí.

Sběr ze starého webu: `curl` na
`/redakce/index.php?lanG=cs&clanek=106922&slozka=106925&scearch=scearch&oddne=1.1.RRRR&dodne=31.12.RRRR&inclarch=1&list_from=N`
(stránkování po 100, řádky `detail_claim=<id>`; filtr zahrnuje i dokumenty vyvěšené dřív, ale ještě
platné — filtrovat podle roku vyvěšení). Starší než 2015 tam nic není.

## Sběr (claude-in-chrome, pecky.cz je bot-chráněná)

1. Otevřít `https://pecky.cz/office/board`, v „Hledání / Archiv“ vyplnit
   „Dokumenty vyvěšené od“ (filtr `…[dateTo]` omezení shora nedodržuje přesně — řádky filtrovat podle roku vyvěšení
   a deduplikovat podle odkazu; stránkování za posledním řádkem opakuje poslední stránku) a nastavit 50 záznamů na stránku → v adrese se objeví
   parametry `boardControl-boardGrid-perPage=50` a `…-filter[dateFrom]=…`.
2. Stránky procházet parametrem `boardControl-boardGrid-page=N`; řádky
   (`#snippet-boardControl-boardGrid-table tbody tr`) vyčíst přes `fetch` +
   `DOMParser` v `javascript_tool` (odkazy `a[href^="/default/report/"]`).
   `javascript_tool` odmítne výstup s URL s query stringem — vypisovat jen cesty
   a text; velký výpis jde přes `get_page_text` po vložení do `<pre>`.
3. Nové řádky doplnit do `<rok>.txt` (nejnovější nahoře), sloupec
   „značka“ se nepřenáší.

## Generování

```bash
python3 o-webu/uredni-deska-monitoring/summary.py   # -> content/udmonitoring.html
python3 scripts/build.py
```

Pak přepsat `lastmod` v `EXTRA_PAGES['udmonitoring']` a řádek O webu ve
„Stav sekcí“ (`README.md`). Témata dokumentů (barvy grafu) určují regulární
výrazy `GROUPS` v `summary.py` podle názvu; zařazení je orientační.
Nový rok = nový soubor `<rok>.txt`, skript načte všechny.

## Lokální archiv příloh (od 6. 10. 2026)

Přílohy dokumentů se stahují do `Data/<rok>/<číslo dokumentu>/<soubor>` — **`Data/` je v `.gitignore`**
(jen lokální archiv, na GitHub Pages nejde; stránka dál odkazuje na detail na původním webu).
V gitu jsou jen seznam příloh `prilohy-<rok>.txt` a `prilohy-manifest.json` (velikost, SHA-256, stav).

- `prilohy-<rok>.txt` — řádek `<číslo dokumentu>|<soubor>|<soubor>|…`; soubor leží na
  `https://pecky.cz/files/pecky/attachments/<číslo dokumentu>/<soubor>`. Seznam se vyčítá z úřední
  desky v Chrome (stejné stránkování a `fetch` + `DOMParser` jako při sběru dokumentů, ve sloupci
  příloh jsou odkazy `/files/pecky/attachments/…`); názvy souborů přepisovat přesně — překlep dá 404.
- `python3 o-webu/uredni-deska-monitoring/download.py [rok …]` — stáhne chybějící soubory (běžný
  `curl`, `/files/` není chráněné proti botům), už stažené přeskočí, chyby zapíše do manifestu.
- Hotovo (6. 10. 2026):
  - **pecky.cz, všechny roky 2016–2026** (`download.py`): 542 souborů, 204,8 MB, bez chyb. Přílohy
    jsou v archivu jen u části dokumentů (sloupec příloh je jinak prázdný): 2026: 178 souborů (134 ze 137
    dokumentů), 2025: 83 (z 165), 2024: 67 (z 137), 2023: 78 (z 145), 2022: 12 (z 24), 2021: 1 (z 9),
    2020: 31 (z 90), 2019: 71 (z 156), 2018: 13 (z 19), 2017: 3 (z 5), 2016: 5 (z 9).
  - **starý web `pecky.as4u.cz`, 2015–2025** (`download_as4u.py`): 1 773 dokumentů, 2 513 souborů,
    1 064 MB, bez chyb; 3 dokumenty bez příloh. Soubory leží v `Data/<rok>/as4u-<detail_claim>/<soubor>`
    (název podle hlavičky serveru). Starý web má přílohy téměř u všech dokumentů, pecky.cz jen u části.
  - Celkem v `Data/` ~1,2 GB. Dokument, který je na obou webech, má přílohy v obou podobách
    (`Data/<rok>/<číslo>/…` z pecky.cz a `Data/<rok>/as4u-<id>/…` ze starého webu).
- `as4u-<rok>.txt` — dokumenty starého webu vyvěšené v daném roce (`<detail_claim>|<vyvěšeno>|<název>`),
  vstup pro `download_as4u.py`. Starý web se od března 2026 neaktualizuje, takže seznam je uzavřený.
- Pozor při sběru seznamu z pecky.cz: filtr „vyvěšené do“ (`…[dateTo]`) skrývá dokumenty, které jsou ještě
  vyvěšené po tomto datu (smlouvy na 3 roky apod.). Seznam proto brát **bez `dateTo`** (jen
  `dateFrom=01.01.2000`, stránkovat do konce) a řádky třídit podle roku vyvěšení. Při doplnění příloh
  za 2022–2025 se tak našlo 55 dokumentů, které `<rok>.txt` neměly (na stránce už byly ze starého webu
  a nyní odkazují na pecky.cz).

## Starší data (před 2015) — k pozdějšímu řešení

Monitoring sahá k červnu 2015: starý web `pecky.as4u.cz` nemá nic staršího a archiv pecky.cz začíná
v březnu 2016. Starší dokumenty by šly získat jen z Internet Archive (Wayback Machine, 6. 10. 2026
dočasně offline): `pecky.cz/urad/ured_deska.htm(l)` (snímky 2004–2010, zhruba měsíčně),
`pecky.cz/index.php/mestsky-urad/uredni-deska` a `…/verejne-dokumenty/uredni-deska` (2011–2013, jen
několik snímků), `pecky.cz/cs/mestsky-urad/uredni-deska-2.html` (8/2015). Data by byla neúplná (jen
to, co bylo na desce v den snímku), každá éra webu má jiný formát a příloh bude málo. Doporučený
začátek: 2008–2010 (snímky měsíčně); na stránce označit jako „z archivní kopie webu, neúplné“.
Rozhodnuto 6. 10. 2026: zatím stačí od 2015, k tématu se vrátit (uživatel chce připomenout).

## Fulltext — lokální index (od 6. 10. 2026)

Text příloh se z `Data/` vytahuje skriptem `extract.py` do `Text/<rok>/<složka>/<soubor>.txt`;
přehled (znaky, metoda, stav, poznámka) je v `text-manifest.json`. **`Text/` i `text-manifest.json` jsou
v `.gitignore`** — index je jen lokální (na GitHub Pages ani do repa nejde). Typ souboru se pozná podle
prvních bajtů: PDF (`pdftotext -layout`, bez textové vrstvy OCR `pdftoppm` + `tesseract -l ces`, nejvýš 40
stran), DOCX/XLSX (zipfile), DOC/RTF (`textutil`), ZIP (členy se zpracují), obrázky (OCR). Opakované
spuštění přeskočí nezměněné soubory. Použití: `python3 o-webu/uredni-deska-monitoring/extract.py [rok …]`.

Stav 6. 10. 2026: 3 055 souborů, 48,1 M znaků, 55 MB textu; 3 soubory bez textu, žádná chyba.
Metody: pdftotext 2 250, OCR 423, DOCX 172, DOC/RTF 151, XLSX 42, ZIP 15, XLS 2. OCR je v češtině
čitelné, ale s drobnými chybami v písmenech (u skenů fulltext nenajde všechna slova).
