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
v gitu (data jsou veřejná). Aktuálně `2016.txt` až `2026.txt` — dokumenty vyvěšené od 15. 3. 2016 (nejstarší
v archivu) do 6. 10. 2026, celkem 841 záznamů (2016: 9, 2017: 5, 2018: 19, 2019: 156,
2020: 90, 2021: 9, 2022: 16, 2023: 135, 2024: 122, 2025: 143, 2026: 137). Archiv není za všechny
roky úplný (viz poznámka na stránce). Starší data se přidávají po jednom kalendářním roce.

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
