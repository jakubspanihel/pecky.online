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
