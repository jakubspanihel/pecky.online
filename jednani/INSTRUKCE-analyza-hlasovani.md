# Instrukce: analýza hlasovacího chování zastupitele

Postup pro rozbor toho, jak konkrétní člen zastupitelstva hlasuje vůči
zbytku sboru. Poprvé použito 4. 9. 2026 na Mgr. Alenu Švejnohovou
(výstup: `analyza-hlasovani-svejnohova.md`).

> **Stav: rozpracováno.** Zatím jde o jednorázový rozbor jedné osoby.
> Počítá se s tím, že se k tomu vrátíme a **doplníme další osoby** —
> nejspíš celý sbor, aby šlo osoby porovnávat mezi sebou a případně
> z toho udělat obsah na web (sekce Jednání nebo Lidé). Tenhle dokument
> je proto psaný jako opakovatelný postup, ne jako záznam jednoho běhu.
> Až se to bude zobecňovat, viz „Otevřené otázky" na konci.

## 1. Zdroj dat

`jednani/archive-2026-08-04.json` — pole
`meetings[].minutes.agenda_items[].votes[]`, kde každý blok
(`pro`, `proti`, `zdrzel_se`, `nehlasoval`) nese `count` i `names`.

Omezení, která se musí přiznat ve výstupu:

- **Jen Zastupitelstvo.** U Rady web jména nehlasujících neuvádí
  (`names: null`), takže se hlasování rady analyzovat nedá.
- **Jen do data snímku.** Archiv je datovaný (2026-08-04); novější jednání
  v něm nejsou. `pecky-jednani.json` sice nová jednání má, ale u hlasování
  drží jen počty (`pro`/`proti`/`zdrzel`), **ne jména** — na tuhle analýzu
  tedy nestačí. Novější jednání se musí buď dohledat ručně ze stránky
  `/verejne/<uuid>/zapis/`, nebo počkat na nový běh scraperu.
- Velký `archive-*.json` se z připojené složky občas nedá číst přímo
  (`OSError: [Errno 35]`). Nejdřív `cp` do `/tmp`, pak pracovat s kopií.

## 2. Identifikace osoby

Jména jsou v zápisech verbatim včetně titulů a nekonzistentní interpunkce.
Hledat podložetězcem příjmení bez diakritických pastí (např. `Švejnoh`),
pak **ověřit, že se trefil právě jeden tvar jména** — jinak hrozí sloučení
dvou různých lidí se stejným příjmením. U Švejnohové vyšel jediný tvar
`Mgr. Alena Švejnohová`, 465 výskytů.

## 3. Co se počítá

Pro každé hlasování, kde osoba hlasovala:

- **její pozice** = blok, ve kterém je její jméno,
- **většinový blok** = nejpočetnější z `pro`/`proti`/`zdrzel_se`/`nehlasoval`,
- **odchylka** = její pozice ≠ většinový blok,
- **izolovanost** = velikost jejího bloku (nejvýš 3) proti velikosti
  většinového bloku (aspoň 12). Tahle hranice je arbitrární volba, ne nic
  daného zdrojem — pokud se změní, musí se změnit i ve výstupu.

Nepřítomnost u hlasování se počítá zvlášť (`absent`), nemíchá se do
odchylek.

## 4. Členění výstupu

Odchylky se neházejí na jednu hromadu — čtou se čtyři různé situace:

- **A) Hlasovala proti, návrh přesto prošel** — seřazeno od
  nejizolovanějších, s uvedením, kdo hlasoval stejně.
- **B) Hlasovala pro, návrh neprošel a proti bylo víc hlasů než pro.**
  Pozor: „pro v menšině" samo o sobě nestačí — většina takových případů
  jsou protinávrhy, které padly na *zdržení se*, ne na odpor. Ty patří do
  poznámky, ne do tabulky střetů.
- **C) Zdržela se proti téměř jednomyslné většině.**
- **D) Souvislé bloky nesouhlasu** (u Švejnohové ustavující zasedání
  20. 10. 2022 — proti starostovi, místostarostům i radě).

Plus **shoda s ostatními zastupiteli** (v kolika procentech hlasování, kde
byli oba přítomni, hlasovali stejně). **Počítat zvlášť po volebních
obdobích** — u Švejnohové se čísla za celé období 2021–2026 slévala do
nicneříkajícího průměru a skutečný příběh (většina do 2022 → opozice po
2022) byl vidět, až když se to rozdělilo. Práh minimálního počtu společných
hlasování (použito 20) uvádět, jinak vyskočí nesmysly u lidí s pár hlasy.

## 5. Co vyřadit ručně

Strojové „izolované hlasování" není totéž co opoziční postoj. Před
publikací projít nejizolovanější případy a vyřadit (s poznámkou, ne
potichu):

- **hlasování o sobě samém** — Švejnohová se zdržela volby sebe do
  kontrolního výboru (20 : 0 : 1), což vypadá jako maximální izolace, ale
  je to běžná slušnost;
- procedurální hlasování bez věcného obsahu, pokud se opakují a nic
  nevypovídají (schválení programu ale často věcné je — dopisuje se jím
  konkrétní bod, viz VPK Suchý 5/2025).

## 6. Ověření před odevzdáním

- Namátkou zpětně dohledat 4–5 uvedených poměrů přímo v archivu.
- Ověřit texty usnesení (`resolutions[].text_verbatim`) u případů, které se
  ve výstupu popisují slovy — číslo usnesení k hlasování je
  `votes[].adopted_resolution_number`.
- Zkontrolovat, že se osoba neúčastnila i jednání novějších než snímek
  archivu (a případně doplnit / přiznat mezeru).

## 7. Zásady výstupu

Platí obecné konvence webu (viz kořenový `CLAUDE.md`): žádná vymyšlená
data, každý údaj dohledatelný ve zdroji, mezery se přiznávají. Analýza
popisuje **jak kdo hlasoval**, nehodnotí, jestli hlasoval správně —
motivace se ze zápisu vyčíst nedá a nedopočítává se.

## Otevřené otázky (k vyřešení při rozšíření na další osoby)

- Kde to má žít: samostatný soubor na osobu, jeden společný dataset, nebo
  strojové JSON + generovaná stránka?
- Vazba na `lide/people.json` — spárovat jména z prezence přes
  `jNameKey()` (assets/helpers.js), jako to dělá výpis jednání.
- Chce se to zveřejnit na webu? Pokud ano, rozhodnout, jestli v sekci
  Jednání (u hlasování) nebo Lidé (u osoby), a jak formulovat, aby to bylo
  popisné, ne hodnotící.
- Skript zatím není — analýza běžela jako jednorázový Python nad kopií
  archivu. Při rozšíření na víc osob se vyplatí ho uložit do
  `jednani/scripts/`.
