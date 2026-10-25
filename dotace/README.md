# Dotace od města (`/dotace/`)

Sekce o dotacích, které město Pečky poskytlo spolkům a dalším příjemcům podle
smluv a dodatků vyvěšených na úřední desce. Odkaz je v sekundárním menu
(`assets/footer.html`) hned za Pokladnou. Stránka `content/dotace.html` se
**generuje** — needitovat ručně.

## Soubory
| Soubor | Popis |
|---|---|
| `dotace.json` | Data: `prijemci` (název, `org` = id v `lide/organizations.json`, `barva` = proměnná z `assets/styles.css`), `smlouvy[]` (rok, příjemce, číslo, částka, datum vyvěšení, odkaz na dokument, `investicni`), `dodatky[]` (rok, příjemce, číslo smlouvy a dodatku, typ `navyseni`/`ucel`/`termin`, částka, popis, schvalující jednání, odkaz) |
| `update-dotace.py` | Generátor: z `dotace.json` vytvoří `content/dotace.html` (stat karty, SVG graf, tabulka součtů, blok Investiční akce Sokola 2019, tabulka dodatků). Spouštět z kořene repa, potom `python3 scripts/build.py` |

## Postup aktualizace
1. Nové smlouvy a dodatky o dotaci se objeví v Monitoringu úřední desky
   (`o-webu/uredni-deska-monitoring/<rok>.txt`, název „Smlouva/Dodatek o poskytnutí dotace…“).
   Částku, příjemce a účel vzít z textu přílohy (`Text/<rok>/<složka>/`, lokální index).
2. Doplnit řádek do `smlouvy[]` nebo `dodatky[]` v `dotace.json` (rok = rok, na který
   smlouva platí, podle čísla smlouvy; odkaz = detail dokumentu na pecky.cz).
3. `python3 dotace/update-dotace.py && python3 scripts/build.py`.
4. Přepsat řádek „Dotace od města“ ve „Stavu sekcí“ v kořenovém `README.md`.

## Pravidla výpočtu
- Rok sloupce je rok z čísla smlouvy (u smluv bez čísla v názvu rok vyvěšení).
- Do součtů se počítají smlouvy a dodatky s typem `navyseni`. Dodatky `ucel`
  (změna účelu) a `termin` (přesun nevyčerpané částky) výši dotace nemění.
- Investiční dotace (`investicni: true`, dnes jen Sokol 2019, smlouva č. 30/2019,
  3 600 000 Kč) je v grafu normálně, jen šrafovaná. Bezúročná půjčka 1,5 mil. Kč
  (ZM 22. 5. 2019) se nepočítá, je návratná.
- Barvy: příjemce s organizací, která má `color` v `organizations.json`, bere
  `--org-<id>` (Sokol, AFK, SŽM). Ostatní mají `barva` z tokenů v `assets/styles.css`
  (Spartak, Oddíl vodní turistiky, Zimní turisti, DC GLOW); malí příjemci jsou
  sloučeni do série „Ostatní“. Doplní-li se barva organizace (např. TJ Spartak) do
  `organizations.json`, přepsat v `dotace.json` `barva` na `null`.

## Známé mezery
- Na úřední desce nejsou smlouvy z roku 2017 (jen dodatek z roku 2018 odkazuje na
  smlouvu č. 12/2017 Basketbalu) ani smlouvy č. 17/2020 a č. 18/2020 (jen dodatky);
  tyto dotace v přehledu chybí.
- Smlouvy o dotaci mimo úřední desku (např. na Hlídači státu) se nezpracovávají.
