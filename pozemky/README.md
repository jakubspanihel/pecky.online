# Instrukce k sekci: Pozemky (panel `pozemky`)

Referenční dokument pro práci na panelu `panel-pozemky`
(`content/pozemky.html`) webu pecky.online. Doplňuje obecné instrukce
projektu (Project instructions / CLAUDE.md) — tohle je detail jen pro
tuhle jednu sekci.

## Účel sekce
Tabulky Nákup/Prodej v panelu Pozemky jsou statický výřez z usnesení rady
a zastupitelstva o prodeji/nákupu konkrétního pozemku (analogie sekce
Smlouvy) — ne ručně psaný obsah, ale vygenerovaný ze zdrojových dat.

## Umístění dat — proč nejsou v `pozemky/`
Data i generující skript fyzicky žijí v `jednani/`, ne tady:
- `jednani/scripts/update-pozemky.py` — generátor
- `jednani/parcely-pozemky.json` — katastr-přesná cache
  „katastr|číslo parcely" → RUIAN ID
- `jednani/parcely-odkazy.json` — plochá mapa pro obecné prolinkování
  zmínek „parc. NNNN" v sekci Jednání

Důvod: tabulky Pozemky se počítají přímo z `jednani/pecky-jednani.json`
(usnesení rady/zastupitelstva) — data i skript mají těsnější vazbu na
sekci Jednání než na cokoli vlastního, takže zůstávají u zdroje místo
duplikace/kopírování mezi složkami.

## Vyhledávání
Pole „Hledat“ nad tabulkami (`#pozemky-search`, inline `<script>` na konci `content/pozemky.html`) filtruje řádky Nákupu i Prodeje
najednou — všechna slova musí být v řádku (parcela, katastr, název bodu, cena, datum), bez ohledu na diakritiku. Pod polem je
počet shod v obou tabulkách. Hledaný výraz se zapisuje do URL jako `?q=…` (`/pozemky/?q=chvalovice`, funguje i s `#prodej`); tlačítko „Kopírovat odkaz“ ho zkopíruje a odkaz po otevření výraz rovnou vyhledá. Skript `update-pozemky.py` přepisuje jen tabulky, vyhledávání zůstává.

## Starší jednání (od 18. 10. 2026)
Do tabulek vstupují i body ze zápisů a usnesení před usneseni.cz (`jednani/starsi-jednani.json`: úřední deska + archiv města,
2013 – 3/2021; `extract_rows_starsi()` v `update-pozemky.py`). Bod = úsek textu „a) …“ až „b) …“ s klíčovými slovy nákupu/prodeje
a parcelou v úvodu; štítek „zápis RM“ / „usnesení ZM“, odkaz vede na PDF, u RM bez čísla „řešilo se na: Jednání rady <datum>“.
Katastr: z bodu, jinak z kontextu (`parcely-starsi.json` → `inferred_katastr`). Noviny se nezpracovávají. Po přidání starších
jednání spustit `update-pozemky.py` (přegeneruje i `parcely-starsi.json`) a upravit čísla v callout „Poznámky k datům“.

## Aktualizace — spustit po každé změně `pecky-jednani.json`
```
python3 jednani/scripts/update-pozemky.py
python3 scripts/build.py
```
První skript v jednom běhu přegeneruje obě HTML tabulky (Nákup/Prodej)
přímo v `content/pozemky.html` a zároveň `jednani/parcely-odkazy.json`;
ověří i balanci HTML tagů po zásahu (selže s chybou, pokud něco rozbije).
Druhý příkaz je od migrace na vícestránkový web (`ARCHITEKTURA-MIGRACE.md`)
nutný vždy — promítne `content/pozemky.html` do veřejné stránky
`pozemky/index.html`.

Skript přepisuje jen obsah obou subpanelů (jen tabulky; součty cen se neuvádějí). Callouty pod
nimi jsou psané ručně a zůstávají: „Poznámky k datům“ a od 29. 9. 2026
i „Kontrolní výbor k pozemkům“ — zjištění výborů zastupitelstva
(`jednani/vybory.json`, viz `jednani/README.md` → „Jednání výborů ZM“)
k parcelám z tabulek. Zatím jediné: KV 19. 3. 2025 k parc. 1449/118. Při
novém zápisu výboru, který se týká konkrétní parcely, doplnit sem.

Plný technický popis (dohledávání RUIAN ID, katastr-přesná kolize čísel
parcel, proč byl starý globální `katastr-odkazy.json` smazaný, formát
odkazu „řešilo se na: Jednání rady č. N" — od 5. 9. 2026 skutečný
meziseránkový odkaz `/jednani/#rada-YYYY-MM-DD` na trvalý hash jednání,
ne JS-only handler jako dřív) je v
[`jednani/automation-katastr-parcely.md`](../jednani/automation-katastr-parcely.md).

## Kontrola po každém běhu `update-pozemky.py`
Po přegenerování tabulek namátkou ověřit, že odkaz „řešilo se na"
u pár řádků skutečně vede na existující jednání (otevřít
`/jednani/#rada-YYYY-MM-DD` resp. `#zastupitelstvo-YYYY-MM-DD` a ověřit,
že se stránka Jednání načte s rozbaleným správným řádkem) — hlavně po
větším zásahu do `pecky-jednani.json` (přečíslování jednání, oprava
data). Needit se vracet k dřívějšímu vzoru `data-jednani-uuid` +
JS handler — na samostatné stránce Pozemky nikdy nefungoval, viz
`jednani/automation-katastr-parcely.md`.
