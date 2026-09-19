# Instrukce k sekci: Kalendář (panel `kalendar`)

Referenční dokument pro práci na panelu `panel-kalendar` v
`content/kalendar.html` (generuje se do veřejné stránky `/kalendar/`,
viz `scripts/build.py`). Doplňuje obecné instrukce projektu (Project instructions
/ CLAUDE.md) — tohle je detail jen pro tuhle jednu sekci.

## Účel sekce
Klasický tabulkový kalendář s termíny týkajícími se města Pečky.
Zatím jediný zapojený zdroj je Jednání rady a zastupitelstva; volby
a kalendář akcí z webu města jsou plánované, ale ještě nezapojené
(viz „Co rozhodnout před dalším zdrojem" níže).

## Jak to funguje

- **`kalendar/scripts/update-kalendar.py`** — generátor. Sesbírá
  události ze zdrojů (zatím jen `build_jednani_events()` z
  `jednani/pecky-jednani.json`) do jednoho společného schématu a zapíše
  dva výstupy:
  - **`kalendar/udalosti.json`** — data pro klientské vykreslení,
    `content/kalendar.html` si je natahuje přes `fetch()` (stejný vzor
    jako Jednání/Lidé/Noviny).
  - **`kalendar/kalendar.ics`** — stejné události ve formátu iCalendar
    (RFC 5545), stažitelné/přihlašovatelné tlačítkem na stránce.
- **`content/kalendar.html`** — měsíční mřížka vykreslená v prohlížeči
  (žádný build-time HTML pro jednotlivé dny): navigace měsícem
  (◀ / Dnes / ▶), filtr Vše/Zastupitelstvo/Rada, barevné odznaky
  v buňkách dne (zelená = Rada přes `--field`, bordó = Zastupitelstvo
  přes `--burgundy`) prolinkované na `/jednani/#{typ}-{datum}`.

### Aktualizace
Spustit po každé aktualizaci `jednani/pecky-jednani.json`:
```
python3 kalendar/scripts/update-kalendar.py
python3 scripts/build.py
```
První příkaz přegeneruje `kalendar/udalosti.json` a `kalendar/kalendar.ics`.
Druhý je potřeba, jen pokud se změnil `content/kalendar.html` samotný
(data soubory build.py nekopíruje ani neupravuje — GitHub Pages/
`scripts/serve.py` je servíruje přímo ze složky `kalendar/`).

## Schéma jedné události
Společné pro všechny budoucí zdroje (ne jen Jednání) — nový zdroj
zplošťuje svá specifika na tahle pole, detaily zůstávají dostupné přes
`link`/`source_ref` zpátky do mateřské sekce.

```json
{
  "id": "jednani-zastupitelstvo-2026-09-16",
  "title": "Zastupitelstvo 6/2026",
  "date": "2026-09-16",
  "date_end": null,
  "time": "16:30",
  "all_day": false,
  "category": "zastupitelstvo",
  "link": "/jednani/#zastupitelstvo-2026-09-16",
  "description": "23 bodů programu",
  "image": null,
  "note": null,
  "source_ref": "1e69bf60-aa81-11f1-b174-0242c0a80002"
}
```

- **`category`** — řízený výčet, u Jednání `rada`/`zastupitelstvo`
  (shoduje se se slugem v `link`). Řídí barvu odznaku v mřížce
  (`.kal-ev-rada`/`.kal-ev-zastupitelstvo` v `assets/styles.css`) a filtr
  Vše/Zastupitelstvo/Rada na stránce.
- **`time`/`all_day`** — `time` je vyplněný, jen dokud jednani data mají
  pole `time` (viz `jednani/pecky-jednani.json`: objevuje se u jednání,
  které má zatím jen Pozvánku, mizí po doplnění zápisu) — jinak `all_day:
  true`. Web jinak přesný čas zahájení jednání nedrží.
- **`image`** — jen cesta k souboru, nikdy base64/inline data (stejná
  konvence jako `volby/2022/zastupitele/*.jpg`). U Jednání zatím `null`.
- **`description`** — krátký teaser (u Jednání počet bodů programu), ne
  duplikát obsahu. Plný obsah zůstává na stránce, kam vede `link`.
- **`source_ref`** — ID v zdrojových datech (u Jednání `uuid` z
  `pecky-jednani.json`) — používá se i jako `UID` v `.ics`, musí zůstat
  stabilní napříč přegenerováními.

## Co rozhodnout před dalším zdrojem
- **Volby** — termín zatím nikde strukturovaně neexistuje (jen věta
  v perexu `content/volby2026.html`). Až se rozhodne přidat, jako malý
  ručně psaný soubor (`kalendar/udalosti-rucni.json` nebo podobně),
  který `update-kalendar.py` při běhu přimíchá ke zbytku.
- **Kalendář akcí z webu města** — vyžaduje vlastní scraper (obdoba
  `pecky-online-noviny-check`), zatím neexistuje.
- Jestli zapojit `update-kalendar.py` do týdenní kontroly (spouštět
  automaticky po `pecky-online-jednani-check`, obdoba toho, jak
  `jednani/scripts/update-pozemky.py` navazuje na aktualizaci jednani
  dat) — zatím se spouští jen ručně.
