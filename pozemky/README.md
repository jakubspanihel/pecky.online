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
