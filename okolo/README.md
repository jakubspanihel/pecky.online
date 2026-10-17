# Okolo (Pro přespolní) — obce ve správním obvodu Peček

Sekce `/okolo/` o obcích v okolí Peček. Stránka `content/okolo.html` zobrazuje
SVG mapu devíti obcí (sekundární menu v `assets/footer.html`, řádek ve
„Stavu sekcí“ v kořenovém `README.md`). Znaky obcí jsou na mapě; popisy symbolů
na stránce zatím nejsou.

## Obsah adresáře
| Soubor | Popis |
|---|---|
| `mapa.json` | Obrysy obcí jako SVG cesty a pozice popisků; generuje `update-mapa.py` (hranice z OpenStreetMap přes Nominatim, ODbL) |
| `update-mapa.py` | Generátor `mapa.json`; spouštět z kořene repa, potom `python3 scripts/build.py` |
| `vesnice-okolo.json` | Obce správního obvodu obce s pověřeným obecním úřadem Pečky (okres Kolín, Středočeský kraj) včetně popisů znaku a vlajky |
| `loga/` | Obrázky znaků a vlajek (`<id>-znak.*`, `<id>-vlajka.*`), velikost do 800×500 px |

## Obce (9)
Pečky, Cerhenice, Vrbčany, Dobřichov, Tatce, Chotutice, Plaňany, Radim, Ratenice.

## Struktura `vesnice-okolo.json`
Kořen: `zdroj` (URL výpisu), `stazeno` (datum stažení, 17. 10. 2026), `obce[]`.
Každá obec:
- `id` — slug názvu (shodný s názvy souborů v `loga/`)
- `nazev`, `kraj`, `okres`, `pou` (pověřený obecní úřad)
- `rekos_id`, `rekos_url` — záznam v registru
- `znak`, `vlajka` — objekt `popis` (heraldický popis), `datum_rozhodnuti`,
  `cislo_rozhodnuti`, `obrazek` (cesta od kořene repa), nebo `null`, pokud
  obec symbol nemá

## Zdroj
Registr komunálních symbolů Poslanecké sněmovny Parlamentu ČR:
[výpis pověřené obce Pečky](https://rekos.psp.cz/vyhledani-symbolu?obec=&poverena_obec=pe%C4%8Dky&popis=&kraj=27&okres=3204&od=&do=&typ=0&order=asc&sort=municipality.name_pou).
Popisy a obrázky jsou převzaty z detailu každé obce
(`/detail-symbolu/id/<rekos_id>`). Zdroj dosud není v `sources.json` ani
v quicklinks sekce O webu → Odkazy — doplnit při zakládání sekce.

## Aktualizace
Stažení je jednorázové. Při obnově znovu projít výpis, u každé obce detail
a přepsat JSON i obrázky. Dosud není pro to skript.

## Poznámky
- Obce v JSON nejsou kompletní popis okolí: jde jen o symboly (znak, vlajka).
  Další údaje (počet obyvatel, starosta, web obce) je třeba doplnit
  z ověřeného zdroje.
- Obrázky symbolů jsou převzaté z registru; před zveřejněním ověřit
  podmínky užití.
