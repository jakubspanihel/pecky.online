# Data pro nástroje PečkyBota

Soubory generuje `scripts/build_peckybot_tools.py` (spouští ho `scripts/build.py`),
ručně se needitují. Worker je stahuje z webu; každý má `"v": 1`, je pod ~350 kB a řazený
deterministicky. Příklad čtení: `https://pecky.online/peckybot/data/osoby.json`.

- **osoby.json** — `osoby[]`: `id`, `jmeno` (s tituly), `prijmeni`, `funkce[]` (současné funkce, jinak
  působení z tagů), `uskupeni` (politická uskupení oddělená „; “), `tagy[]`, `email`, `telefon`
  (bez ústředny úřadu), `bio` (≤ 400 znaků). Všechny osoby z `lide/people.json`, řazeno podle `id`.
- **slozeni.json** — `organy[]`: `id`, `nazev`, `obdobi`, `aktualni`, `pocet`, `clenove[]`
  (`jmeno`, `funkce`, `uskupeni`). Rada (současná a dřívější), současné zastupitelstvo, výbory,
  komise, školská rada a `starostove` (členové mají navíc `od`, `do`; `do: null` = dosud;
  starší záznamy mají jen rok).
- **kalendar.json** — `udalosti[]` od 2025-01-01 (akce, svoz, volby a plánovaná jednání bez záznamu
  v `jednani.json`): `datum`, `datum_do` (nebo `null`), `cas`, `nazev`, `misto`, `poradatel`, `typ`, `url`.
  `serie[]`: pravidelné kurzy (`nazev`, `popis`, `od`, `do`), bez jednotlivých termínů.
- **jednani.json** — `jednani[]`: všechna jednání (zastupitelstvo, rada, komise, výbory, školská rada,
  vč. starších z úřední desky): `id` (kotva `/jednani/#id`), `typ` (`zastupitelstvo|rada|komise|vybor|skolska-rada`),
  `organ`, `oznaceni` (např. „ZM 5/2026“), `datum`, `body[]` (názvy bodů ≤ 160 znaků; u starších
  jednání z úřední desky prázdné).
- **statistiky.json** — `absence[]` (`organ`, `obdobi`, `clenove[]` s `jmeno`, `mandatu`, `absence_podil`
  v %; jen členové s ≥ 3 mandáty) a `pocty.jednani_podle_typu_a_roku` (`typ` → rok → počet).
