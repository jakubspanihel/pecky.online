# Instrukce k sekci: Usnesení (`/usneseni/`)

Referenční dokument pro práci na stránce `/usneseni/` (`content/usneseni.html`,
generuje `scripts/build.py`). Doplňuje kořenový `CLAUDE.md`.

## Účel
Seznam všech přijatých usnesení rady a zastupitelstva — na rozdíl od sekce
[Jednání](../jednani/README.md), která ukazuje jednání včetně bodů programu
bez usnesení. Každé usnesení má číslo (odkaz na detail na usneseni.cz), datum,
odkaz na jednání (`/jednani/#rada-RRRR-MM-DD`), název bodu, plný text,
štítek výsledku a hlasování. Fulltext, filtr orgánu a roku, řazení od nejnovějšího.

## Stav
Stránka je **zatím bez odkazu** (od 1. 11. 2026): není v navigaci ani nikde
odkázaná, má `noindex` a není v sitemapě. V `scripts/build.py` je v `EXTRA_PAGES`
s `lastmod = None`.

Až se odkáže:
1. přesunout záznam z `EXTRA_PAGES` do `MANIFEST`,
2. přidat `'usneseni': 'usneseni'` do `README_TO_SLUG`,
3. přidat řádek do kořenového `README.md` → „Stav sekcí“,
4. přidat odkaz do `assets/nav.html` (a případně ze stránky Jednání, „Související“).

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

## Filtr a hash
Volba orgánu se pamatuje v hashi: `#rada`, `#zastupitelstvo` (bez hashe = vše). Hash
`#UR-…` / `#UZ-…` je odkaz na konkrétní usnesení a filtry zruší.

## Jmenovité hlasování (zastupitelstvo)
Karty usnesení zastupitelstva mají sbalený blok „Hlasování jmenovitě“ (pro, proti,
zdržel se, případně nehlasoval). Data jsou v `usneseni/hlasovani.json`, generuje je
`python3 usneseni/update-hlasovani.py` z archivu `jednani/archive/` (zápisy zastupitelstva,
jména verbatim). Rada jména neuvádí, tam blok není. Jednání novější než snímek archivu (ZM 5/2026 – 7/2026, 18 usnesení) mají jména
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

## Graf hlasování
Nad výpisem je graf: jeden sloupec = jedno usnesení (rada i zastupitelstvo), od nejstaršího vlevo.
Hlasy pro jdou nahoru od základní čáry, proti dolů, zdržení jsou uprostřed základny. Výška sloupce
odpovídá počtu hlasů. Graf se řídí filtrem orgánu a hledáním; při více než ~160 usneseních se
posouvá vodorovně (6 px na sloupec, začíná u nejnovějších). Popisky osy: roky a začátky čtvrtletí.
Hover (nebo dotyk) ukáže usnesení s hlasy, klik na kartu usnesení. Kreslí `uChart()` v
`content/usneseni.html` jako SVG, barvy z tokenů (`--cyan-deep`, `--burgundy`, `--ink-soft`).
