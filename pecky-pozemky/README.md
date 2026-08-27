# Instrukce k sekci: Pozemky (panel `pozemky`)

Referenční dokument pro práci na panelu `panel-pozemky` v `index.html`
webu pecky.online. Doplňuje obecné instrukce projektu (Project instructions
/ CLAUDE.md) — tohle je detail jen pro tuhle jednu sekci.

## Účel sekce
Tabulky Nákup/Prodej v panelu Pozemky jsou statický výřez z usnesení rady
a zastupitelstva o prodeji/nákupu konkrétního pozemku (analogie sekce
Smlouvy) — ne ručně psaný obsah, ale vygenerovaný ze zdrojových dat.

## Umístění dat — proč nejsou v `pecky-pozemky/`
Data i generující skript fyzicky žijí v `pecky-jednani/`, ne tady:
- `pecky-jednani/scripts/update-pozemky.py` — generátor
- `pecky-jednani/parcely-pozemky.json` — katastr-přesná cache
  „katastr|číslo parcely" → RUIAN ID
- `pecky-jednani/parcely-odkazy.json` — plochá mapa pro obecné prolinkování
  zmínek „parc. NNNN" v sekci Jednání

Důvod: tabulky Pozemky se počítají přímo z `pecky-jednani/pecky-jednani.json`
(usnesení rady/zastupitelstva) — data i skript mají těsnější vazbu na
sekci Jednání než na cokoli vlastního, takže zůstávají u zdroje místo
duplikace/kopírování mezi složkami.

## Aktualizace — spustit po každé změně `pecky-jednani.json`
```
python3 pecky-jednani/scripts/update-pozemky.py
```
Skript v jednom běhu přegeneruje obě HTML tabulky (Nákup/Prodej) přímo
v kořenovém `index.html` a zároveň `pecky-jednani/parcely-odkazy.json`.
Ověří i balanci HTML tagů po zásahu (selže s chybou, pokud něco rozbije).

Plný technický popis (dohledávání RUIAN ID, katastr-přesná kolize čísel
parcel, proč byl starý globální `katastr-odkazy.json` smazaný, formát
odkazu „řešilo se na: Jednání rady č. N" s deep-linkem do panelu Jednání)
je v [`pecky-jednani/automation-katastr-parcely.md`](../pecky-jednani/automation-katastr-parcely.md).
