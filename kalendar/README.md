# Instrukce k sekci: Kalendář (panel `kalendar`)

Referenční dokument pro práci na panelu `panel-kalendar` v
`content/kalendar.html` (generuje se do veřejné stránky `/kalendar/`,
viz `scripts/build.py`). Doplňuje obecné instrukce projektu (Project instructions
/ CLAUDE.md) — tohle je detail jen pro tuhle jednu sekci.

## Účel sekce
Klasický tabulkový kalendář s termíny týkajícími se města Pečky.
Zapojené zdroje jsou dva: Jednání rady a zastupitelstva a kulturní akce
z plakátů Kulturního střediska města Pečky. Termín voleb a kalendář akcí
z webu města jsou plánované, ale ještě nezapojené (viz „Zdroje" níže).

Akce mají navíc vlastní podstránku **`/kalendar/akce/`**
(`content/kalendar-akce.html`, registrovaná v `EXTRA_PAGES` ve
`scripts/build.py`): měsíční výpis s místem, časem, pořadatelem a odkazem
na zdrojový plakát. Odznak akce v mřížce na ni vede kotvou `#<id akce>` —
mřížka sama zdroj ani místo neunese.

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

Po jakékoli aktualizaci dat kteréhokoli zdroje (viz „Zdroje" níže)
spustit:
```
python3 kalendar/scripts/update-kalendar.py
python3 scripts/build.py
```
První příkaz přegeneruje `kalendar/udalosti.json` a `kalendar/kalendar.ics`
ze všech zapojených zdrojů najednou. Druhý je potřeba, jen pokud se
změnil `content/kalendar.html` samotný (data soubory build.py
nekopíruje ani neupravuje — GitHub Pages/`scripts/serve.py` je
servíruje přímo ze složky `kalendar/`).

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
  "place": null,
  "organizer": "mesto-pecky",
  "organizer_name": "Město Pečky",
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
- **`description`** — krátký teaser (u Jednání počet bodů programu,
  u akcí místo konání), ne duplikát obsahu. Plný obsah zůstává na stránce,
  kam vede `link`.
- **`place`** — místo konání, vypisuje se jako `LOCATION` v `.ics`
  a v tooltipu odznaku v mřížce. U Jednání `null` (web místo konání
  strukturovaně nedrží).
- **`organizer`** — id pořadatele v `lide/organizations.json` (rejstřík
  organizací celého webu, kalendář si vlastní seznam nedrží). U Jednání
  `mesto-pecky`. Řídí čipy „Pořadatel" nad mřížkou i na `/kalendar/akce/`.
- **`organizer_name`** — jméno k tomu id (`short_name`, jinak `name`),
  dopsané generátorem, aby ho klient nemusel dohledávat druhým fetchem.
  U pořadatele mimo rejstřík (cizí soubor, soukromý pořadatel) je vyplněné
  samo a `organizer` je `null`.
- **`source_ref`** — ID v zdrojových datech (u Jednání `uuid` z
  `pecky-jednani.json`) — používá se i jako `UID` v `.ics`, musí zůstat
  stabilní napříč přegenerováními.

## Zdroje

Kalendář sbírá události z více zdrojů do jednoho společného schématu
(viz „Schéma jedné události" výše). Každý zdroj má v
`kalendar/scripts/update-kalendar.py` vlastní funkci `build_*_events()`
a tady vlastní záznam s popisem a aktualizačními instrukcemi — nový
zdroj se přidává přesně takhle (nová funkce ve skriptu, přidat její
volání do `main()`, doplnit záznam sem), aby zůstal jeden přehledný
seznam místo rozházených poznámek po repu.

### Jednání rady a zastupitelstva — aktivní

- **Data:** `jednani/pecky-jednani.json`, funkce `build_jednani_events()`.
- **Kategorie:** `rada`, `zastupitelstvo`.
- **Aktualizace:** automaticky jako krok 8b týdenní kontroly Jednání —
  viz `jednani/automation-kontrola-usneseni-cz.md` → „8b. Kalendář".
  Ručně po jakékoli úpravě `pecky-jednani.json`:
  ```
  python3 kalendar/scripts/update-kalendar.py
  ```

### Kulturní a společenské akce — aktivní

- **Data:** `kalendar/akce.json`, funkce `build_akce_events()`.
- **Pořadatel ≠ zdroj.** `organizer` je ten, kdo akci pořádá (id
  v `lide/organizations.json`); `evidence[].source` je ten, od koho o ní
  víme (id v kořenovém `sources.json`). Akci může pořádat spolek a ohlásit
  ji facebook města — slévat obojí do jednoho pole by tabulku rozbilo,
  jakmile přibude druhý zdroj.
- **Kategorie:** `akce` (jednorázové akce — přednášky, divadlo, koncerty,
  slavnosti) a `kurz` (opakující se taneční kurzy, prodloužené, věneček).
  Oddělené proto, že kurzů je na plakátu skoro třetina a v mřížce by
  ostatní akce přebily — filtr „Kurzy" je umí schovat.
- **Zdroje:** zatím plakáty Kulturního střediska města Pečky na
  [facebook.com/kspecky](https://www.facebook.com/kspecky). Program vychází
  vždy na několik měsíců dopředu (např. „Program 9–12/2026" ve dvou
  plakátech), k jednotlivým akcím pak samostatné plakáty. Program je
  obrázek bez textové vrstvy — čte se okem přes claude-in-chrome, ne
  scraperem. Počítá se s dalšími zdroji (knihovna, TJ Sokol, facebook
  města, zpravodaj) — proto `evidence` a ne jedno pole se zdrojem.
- **Doklad (`evidence[]`)** je pole, ne jedna hodnota: tutéž akci ohlásí
  pořadatel na svém profilu, město ji přesdílí a zpravodaj o ní napíše —
  to není trojí akce, ale jeden záznam se třemi doklady. **První doklad je
  ten, podle kterého jsou zapsané údaje**, ostatní ho potvrzují. Každý
  doklad má `source` (id v `sources.json`), `kind` (`plakat` ·
  `prispevek` · `web` · `zpravodaj` · `tisk` · `ustni` — řídí, jak se
  odkaz pojmenuje ve sloupci Zdroj), `url`, `label` (název konkrétního
  plakátu, ne profilu), `published` a `retrieved`.
- **Aktualizace:** skillem `pecky-online-kalendar-plakat` (předhodí se mu
  obrázek plakátu nebo odkaz na příspěvek, akce rozpozná a zapíše).
  Ručně po jakékoli úpravě `akce.json`:
  ```
  python3 kalendar/scripts/update-kalendar.py
  ```
- **Co do `akce.json` nepatří:** jednání rady a zastupitelstva, i když je
  program kulturního domu uvádí (16. 9. 2026 „Zastupitelstvo města, Malý sál
  KD od 16:30") — ta má kalendář z `jednani/pecky-jednani.json` a zápisem
  sem by v mřížce vznikly dva odznaky na tentýž termín.
- **Rozpory mezi zdroji** rozhoduje pořadí: vlastní kanál pořadatele →
  oficiální web města → zpravodaj nebo tisk → přepis třetí strany. Mezi
  doklady téže úrovně vyhrává novější (u Slavností sv. Václava 2026 se
  samostatný plakát lišil od souhrnného programu časem i názvem).
  Poražený údaj patří do pole `note` u akce — na podstránce se vypíše
  kurzivou pod názvem.
- **Nový pořadatel** se nejdřív založí v `lide/organizations.json`
  (`type: "spolek"` u spolků, viz `lide/SPEC.md`), teprve pak se na jeho id
  odkazuje. Spolky tam od 20. 9. 2026 jsou dva — `tj-sokol-pecky`
  a `pececky-okraslovaci-spolek`. Pro jednorázového pořadatele mimo
  rejstřík (cizí divadelní soubor) slouží `organizer: null` +
  `organizer_name: "…"` textem; zakládat kvůli jedné akci organizaci
  nemá smysl, ale ztratit pořadatele taky ne.

### Volby — plánováno, zatím nezapojeno

- **Data:** termín voleb zatím nikde strukturovaně neexistuje, jen věta
  v perexu `content/volby2026.html`.
- **Zdroj termínu:** [csu.gov.cz/informace-k-aktualne-vyhlasenym-volbam](https://csu.gov.cz/informace-k-aktualne-vyhlasenym-volbam)
  → sekce „Aktuálně vyhlášené volby" (proklik na konkrétní ročník, např.
  `csu.gov.cz/volby-2026`) — viz `sources.json` →
  `csu-informace-vyhlasene-volby`. K 20. 9. 2026 odtud potvrzeno: volby
  do zastupitelstev obcí (a souběžně do Senátu) 9.–10. října 2026,
  vyhlášeny rozhodnutím prezidenta republiky č. 117/2026 Sb. — shoduje
  se s dřívějším zdrojem mv.gov.cz citovaným v `content/volby2026.html`.
- **Až se zapojí:** malý ručně psaný soubor (např.
  `kalendar/udalosti-rucni.json`), který `update-kalendar.py` při běhu
  přimíchá ke zbytku přes novou funkci `build_volby_events()`.
- **Aktualizace:** ruční — termín voleb se nemění často, netřeba
  zapojovat do týdenní kontroly. Před zápisem/změnou data vždy ověřit
  proti zdroji ČSÚ výše, ne jen převzít z `content/volby2026.html`.

### Kalendář akcí z webu města — plánováno, zatím nezapojeno

- **Data:** vyžaduje vlastní scraper webu města (obdoba
  `pecky-online-noviny-check`), zatím neexistuje.
- **Až se zapojí:** vlastní `build_akce_events()` + zdrojový JSON
  doplňovaný scraperem.
- **Aktualizace:** kandidát na vlastní projektový skill
  (`pecky-online-*-check`) zapojený do týdenní kontroly, obdoba
  Jednání výše — až bude scraper hotový.
