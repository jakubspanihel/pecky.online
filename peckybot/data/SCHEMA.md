# Data pro nástroje PečkyBota

Soubory generuje `scripts/build_peckybot_tools.py` (spouští ho `scripts/build.py`),
ručně se needitují. Worker je stahuje z webu (ze složek vždy jen potřebný soubor); každý má `"v": 1`, je pod ~350 kB a řazený
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
  jednání z úřední desky prázdné), `dostupne[]` (co je zveřejněno: `pozvanka`, `zapis`, `usneseni`;
  jen `["pozvanka"]` = zápis ještě nevyšel) a `je_posledni: true` u nejnovějšího jednání každého `typu`
  (může být i plánované, tedy jen s pozvánkou).
- **jednani/<id>.json** — obsah jednoho jednání pro nástroj `cti_dokument` (`id` = kotva `/jednani/#id`
  = `jednani[].id`; 499 souborů, jeden na jednání, každý ≤ 25 kB, dohromady ≈ 2,7 MB; zastaralé se při
  generování mažou): `id`, `oznaceni`, `datum`, `typ`, `cas`, `misto`, `odkazy` (`zapis`, `usneseni`,
  `pozvanka`, `pdf`), `dostupne[]` (jako výše), `poznamka` (u jednání jen s pozvánkou: zápis a usnesení
  zatím nevyšly; u jednání bez programu: nic není zveřejněno), `je_posledni`, `body[]`
  (`n`, `nazev`, `predkladatel`, `zprava` ≤ 900 znaků, `usneseni[]` s `cislo`, `text` ≤ 500,
  `hlasovani` „pro X, proti Y, zdržel se Z“, případně `neprijato`, `poznamka`) a `usneseni_ostatni[]`
  (usnesení bez vazby na bod, typicky komise a výbory). Starší jednání z úřední desky nemají `body`,
  jen `text_dokumentu` (≤ 3 000 znaků z textu dokumentu). Při překročení 25 kB se nejdřív zkracují
  nejdelší zprávy, potom usnesení.
- **uredni-deska/<rok>.json** — úřední deska z `o-webu/uredni-deska-monitoring/<rok>.txt` pro nástroj
  `uredni_deska` (12 souborů 2015–2026, ≈ 275 kB): `rok`, `d[]` = `[vyvěšeno, sejmuto, typ, název, id]`
  (data ISO, nejnovější první; `id` je buď celé `id_slug` z pecky.cz, nebo jen číslo — slug se pak odvodí
  z názvu, odkaz je `https://pecky.cz/default/report/<číslo>_<slug>`; `as4u:<id>` = starý web).
  Jen názvy a data, ne obsah dokumentů.
- **statistiky.json** — `absence[]` (`organ`, `obdobi`, `clenove[]` s `jmeno`, `mandatu`, `absence_podil`
  v %; jen členové s ≥ 3 mandáty) a `pocty.jednani_podle_typu_a_roku` (`typ` → rok → počet).
- **svoz.json** — svoz odpadu z domácností pro nástroj `svoz` (z `kalendar/svoz-odpadu.json`, ≈ 6 kB): `rok`, `url`
  (`/kalendar/svoz.html`), `lokality[]` (`id` `sever|jih|sidliste`, `nazev`, `druhy[]` s `id`
  `komunal|bio|plast|papir`, `nazev`, `pravidlo`, `terminy[]` ISO data). Nejbližší termíny od dneška počítá
  nástroj za běhu; harmonogram města neuvádí, které ulice patří do které lokality.
