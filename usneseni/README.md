# Instrukce k sekci: Usnesení (`/usneseni/`)

Referenční dokument pro práci na stránce `/usneseni/` (`content/usneseni.html`,
generuje `scripts/build.py`). Doplňuje kořenový `CLAUDE.md`.

## Účel
Seznam všech přijatých usnesení rady a zastupitelstva — na rozdíl od sekce
[Jednání](../jednani/README.md), která ukazuje jednání včetně bodů programu
bez usnesení. Každé usnesení má číslo (odkaz na detail na usneseni.cz), datum,
odkaz na jednání (`/jednani/#rada-RRRR-MM-DD`), název bodu, plný text,
štítek výsledku a hlasování. Fulltext, skrývání nedůležitých a nepřijatých, řazení od nejnovějšího.
Výpis je seskupený podle jednání: každé má nadpis „datum | Rada města / Zastupitelstvo města N/RRRR“
(odkaz na jednání, počet rozhodnutí); uvnitř skupiny jsou karty podle čísla bodu programu.

## Stav
Stránka je od 8. 11. 2026 zveřejněná: v hlavním menu (za Jednáním, `assets/nav.html`), v sitemapě
(`MANIFEST` a `README_TO_SLUG` v `scripts/build.py`, řádek ve „Stav sekcí“ v kořenovém `README.md`).
Podstránka `/usneseni/insta.html` zůstává nástrojová (noindex, mimo sitemapu).

## Data
Žádný vlastní datový soubor. Stránka za běhu načítá `jednani/pecky-jednani.json`
(zdroj [mesto-pecky.usneseni.cz/verejne](https://mesto-pecky.usneseni.cz/verejne/),
`meetings[].resolutions`, jen Rada a Zastupitelstvo, od 12. 4. 2021). Aktualizuje
se tedy sama s kontrolou Jednání (`jednani/automation-kontrola-usneseni-cz.md`).
Usnesení výborů a komisí tu nejsou (nejsou na usneseni.cz). Starší usnesení
(před 4/2021, z úřední desky a novin) jsou jen jako text dokumentů v Jednání.

## Sdílený kód
Klasifikace výsledku (`jClassifyOutcome`, `jRevokeTargets`, `jOutcomeBadgeHtml`)
je v `assets/helpers.js` a používá ji i Jednání. Odkazy „ZM 6/2026“ v textech
řeší `jLinkRefs()`.

## Odkazy v textu
- Číslo usnesení v textu jiného usnesení (revokace, změna termínu…, tvar `UR-328-37/26`
  i `…/2026`) míří na kotvu karty na této stránce (`#UR-328-37/26`); odkaz zruší filtry
  a kartu zvýrazní. Zmínky ZM/RM míří do Jednání, čísla parcel do KN (`jLinkParcely()`).

## Postranní strom let a měsíců
Vlevo je sbalovací strom (rok → měsíce, počty rozhodnutí po aktuálních filtrech), vpravo výpis jednoho
vybraného měsíce seskupený podle jednání. Výchozí je nejnovější měsíc s výsledky, jeho rok je rozbalený.
Stejné rozložení jako Monitoring (sticky strom vlevo od 768 px; na telefonu strom nad výpisem).
Při hledání jsou ve výpisu všechny shody ze všech měsíců a strom (s počty shod) jen odskočí na měsíc.
Kreslí `uTree()` v `content/usneseni.html`.

## Filtr a hash
Filtr orgánu (Vše / Rada / Zastupitelstvo) není. Dvě zaškrtávátka, obě ve výchozím stavu zapnutá:
- „Skrýt nedůležité“ — jen body „Schválení programu jednání“ a „Schválení ověřovatelů zápisu“
  (seznam je i v tooltipu), regex `U_NEDULEZITA_RE` v `content/usneseni.html`.
- „Skrýt nepřijaté“ — návrhy, které při hlasování neprošly (viz „Nepřijaté návrhy“).

Vypnutá volba se pamatuje v hashi: `#nedulezite` (nedůležité zobrazeny), `#neprijata` (nepřijaté
zobrazeny), vybraný měsíc jako `#RRRR-MM`; lze spojit (`#nedulezite,2025-03`); bez hashe jsou obojí skrytá
a vybraný je nejnovější měsíc. Hash `#UR-…` / `#UZ-…`
je odkaz na konkrétní usnesení a filtry podle potřeby zruší.
Rozbalená karta má stejný vzhled jako text usnesení v Jednání (`.agenda-res > .info-toggle-text`,
`.res-block-head`, tučné rozhodnutí a částky přes `jResTextHtml()` z `assets/helpers.js`).

## Jmenovité hlasování (zastupitelstvo)
Rozbalená karta začíná nadpisem = úvodem věty usnesení („Rada města schvaluje“, `jResSplit()` v
`assets/helpers.js`), pod ním je zbytek textu. Končí blokem hlasování (`jVotesBlockHtml()` v `assets/helpers.js`,
stejný jako v Jednání): plnobarevný štítek výsledku, pod ním Pro / Proti / Zdrželi se (případně
Nehlasovali) a na konci řádek „Zdroj: Usnesení 48-7/26“ (odkaz na detail na usneseni.cz s ikonou odkazu ven)
s ikonou sdílení vpravo, která otevírá `/usneseni/insta.html#<číslo usnesení>`.

## Obrázek pro sociální sítě (`/usneseni/insta.html`)
Nástrojová stránka jako ostatní „insta“ (`content/usneseni-insta.html`, v `EXTRA_PAGES` jako `usneseni-insta`;
bez hlavičky a patičky, noindex, mimo sitemapu). Karta s jedním usnesením (rada = bordó, zastupitelstvo =
modrá): datum, nadpis = úvod věty („Rada města schvaluje“), pod ním zbytek textu, štítek výsledku s hlasy. Listování tlačítky ‹ ›
a swipem; přepínač Rada / Zastupitelstvo, velikost písma, formát 1:1 / 4:5 / 3:4, Uložit / Sdílet.
Data bere za běhu z `jednani/pecky-jednani.json`; přeskakuje „Schválení programu“ a „Schválení ověřovatelů“
(mimo odkaz přímo na ně). Text na kartě jde upravit kliknutím. U zastupitelstva s jmény, u rady jen s počty. Data jsou v `usneseni/hlasovani.json`, generuje je
`python3 usneseni/update-hlasovani.py` z archivu `jednani/archive/` (zápisy zastupitelstva,
jména verbatim). Rada jména neuvádí, tam jsou jen počty. Jednání novější než snímek archivu (ZM 5/2026 – 7/2026, 18 usnesení) mají jména
ručně přepsaná ze zápisů na usneseni.cz v `usneseni/hlasovani-rucne.json`; generátor je
doplní, pokud je archiv nemá (archiv má přednost). Počty jmen u každého usnesení se shodují
s počty hlasů v `pecky-jednani.json`. Nové zasedání zastupitelstva: jména přibudou po novém snímku
archivu, do té doby u něj karty ukazují větu „Jména hlasujících zatím nejsou k dispozici“
(nebo jména doplnit do `hlasovani-rucne.json`).

## Projednávání bodu u rozpočtových opatření
U usnesení k bodu „Rozpočtové/á opatření“ je sbalovací blok s předkladatelem a důvodovou zprávou
z programu jednání (`agenda[].duvodova_zprava` v `jednani/pecky-jednani.json`, párování podle názvu bodu).
Titulek bloku je shrnutí změny rozpočtu z `usneseni/rozpocet-shrnuti.json` (klíč = číslo usnesení,
„Celkem: zvýšení výdajů o 380 000 Kč“…). Shrnutí je sestavené ručně z důvodové zprávy a jen tam,
kde text uvádí úplné částky (součty položek se počítají; přesuny mezi výdaji se uvádějí jako přesun).
U ostatních usnesení (jen dotace bez částek, neúplné položky) je titulek „Projednávání bodu“.
Při přidání nového rozpočtového opatření doplnit shrnutí do JSON, pokud zpráva částky uvádí.

## Nepřijaté návrhy

Vedle přijatých usnesení výpis ukazuje i návrhy, které při hlasování neprošly (štítek „Nepřijato“).
- Zdroj: archiv usneseni.cz, hlasování s výsledkem „Návrh nebyl přijat“ a bez čísla usnesení.
  `update-hlasovani.py` je ukládá do `neprijata.json` (rada i zastupitelstvo, u většiny se jmény).
  Hlasování z jednání novějších než archiv načítá stránka z pole `rejected_vote` u bodu v `jednani/pecky-jednani.json`.
- Zdroj neuvádí znění návrhu: karta ukazuje název bodu programu, předkladatele a hlasování
  (u dvou návrhů z `rejected_vote` i text). Návrhy stažené před hlasováním v datech nejsou.
- Ve výchozím stavu jsou skryté (zaškrtávátko „Skrýt nepřijaté“); skupiny mluví o „rozhodnutích“.
- Číslo karty je `NP-<datum>-<RM|ZM>-<bod>-<pořadí hlasování>`; karty jsou ve výchozím stavu sbalené (datum | nadpis, „+“).
