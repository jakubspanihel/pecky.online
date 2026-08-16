# pecky.online

Neoficiální, nezávislý občanský projekt zpřehledňující veřejně dostupné informace
o samosprávě města Pečky (okres Kolín, Středočeský kraj).

## Obsah složky

- `index.html` — celá webová stránka (jeden soubor, HTML/CSS/JS, bez závislostí
  kromě Google Fonts přes CDN). Otevřete přímo v prohlížeči nebo nahrajte na
  GitHub Pages / jakýkoli statický hosting.
- `data/pecky-jednani.json` — datový soubor pro sekci „Jednání" (archiv jednání
  rady a zastupitelstva s fulltextovým hledáním). Stránka si ho načítá přes
  `fetch()`, proto je pro místní test potřeba spustit lokální server (např.
  `python3 -m http.server`), otevření `index.html` přímo ze souboru (`file://`)
  fetch v některých prohlížečích zablokuje.
- `sources/` — zdrojový, kompletní export archivu jednání (surová data,
  specifikace, viz níže).

## Zdroje dat

- Základní fakta o městě: Wikipedie, oficiální web města (pecky.cz)
- Výsledky komunálních voleb 2022: Seznam Zprávy, Novinky.cz
- Jmenný seznam zastupitelstva (21/21 členů): pecky.cz — Složení ZM
- Složení rady města: pecky.cz, web ODS Pečky
- Smlouvy: Hlídač státu (konektor), IČO 00239607 — statický výřez, ne živá data
- Zakázky: Hlídač veřejných zakázek (veřejné vyhledávání, ne konektor), IČO 00239607 — statický výřez, ne živá data
- Pokladna (rozpočet a hospodaření): Monitor Státní pokladny (MF ČR), IČO 00239607 —
  vývoj příjmů/výdajů/salda 2023–2026, struktura výdajů, dluhová služba; dotace
  přes Registr dotací (Hlídač státu, 148 nalezených záznamů)
- Pokladna → Bankovní účty: Návrh závěrečného účtu 2025 (pecky.cz), konkrétně příloha
  Zpráva o přezkoumání hospodaření (auditorská zpráva cituje bankovní výpisy — 9 účtů
  u 5 bank) a přílohy Rekapitulace/Fondy (souhrnné zůstatky)
- Plán: Strategický plán rozvoje města Pečky 2016–2026 — souhrn (pecky.cz, PDF) —
  718 dílčích aktivit ve 4 prioritních oblastech, 360,8 mil. Kč celkem
- Pečecké noviny: pecky.cz — kompletní archiv PDF zpravodaje (68 vydání, 2020–2026)
- Jednání a usnesení: jednorázový strojově čitelný export webu
  mesto-pecky.usneseni.cz z 4. 8. 2026 — 281 jednání (243 Rada, 38
  Zastupitelstvo, 2021–2026), 2 731 usnesení. Kompletní snímek se všemi detaily
  (vč. jmenovitých hlasování a plných zápisů) je v `sources/archive-2026-08-04.json`;
  `data/pecky-jednani.json` je z něj odvozený odlehčený index pro hledání na
  webu. Viz `sources/SPEC.md` a `sources/AUTOMATION.md` pro popis exportu a
  plán budoucí aktualizace.

## Barevná paleta uskupení

Každé politické uskupení má na celém webu jednu pevně přiřazenou barvu — používá se
konzistentně u kartiček lidí, kartiček volebních programů, sloupcového grafu mandátů
i barevných teček (swatch) v tabulkách. CSS třídy `.person-card.party-*` (definice
v `<style>` v `index.html`):

| Uskupení | Třída | Zvýrazňovací barva | Pozadí kartičky |
|---|---|---|---|
| NAŠE PEČKY (STAN + nezávislí) | `party-nasepecky` | `#E20514` | `#F9CDD2` |
| Sdružení ODS a nezávislých kandidátů | `party-ods` | `#1F2363` | `#CCD2E5` |
| SNK Pečky Pečákům | `party-snk` | `#A6528F` | `#EBD9E6` |
| Lidé pro Pečky s podporou SPD | `party-spd` | `#8B5A2B` | `#E5DBD0` |
| ČSSD a sjednocená levice | `party-cssd` | `#FF5F60` | `#FFDFDF` |
| Lidovci a nezávislí | `party-lidovci` | `#EBB91E` | `#F7E6B8` |

Při přidávání nového místa na webu, kde se zobrazuje uskupení nebo jeho člen
(nová kartička, graf, tabulka…), použij stejnou barvu z této tabulky místo
vymýšlení nové.

## Metodika ověřování (POVINNÉ)

Než o čemkoli prohlásíš, že to „v datech není“ nebo že se to „nestalo“, prověř to
**vždy ve všech zdrojích a v jejich plné podobě**. Zkratky vedly už k prokazatelně
chybným závěrům.

1. **Vždy `sources/archive-2026-08-04.json`, ne `data/pecky-jednani.json`.**
   Soubor v `data/` je odlehčený index (jen názvy a texty usnesení). Plný archiv
   obsahuje kompletní zápisy včetně diskuzí, důvodových zpráv a bodů programu —
   řádově víc textu. Pozn.: plný archiv nelze číst přes `mcp__workspace__bash`
   (mount hlásí „Resource deadlock avoided“) — použij nástroje Grep/Read, které
   běží na hostu.
2. **U dotací a smluv nikdy nespoléhej na prvních N záznamů.** Hlídač státu
   defaultně vrací malý vzorek; při řazení `DateAddedDesc` vypadnou starší roky.
   Projdi všechny stránky, nebo cíleně hledej klíčovým slovem k danému projektu.
3. **Zkoušej víc názvových variant.** Projekty se v dokumentech jmenují jinak než
   v plánu („kabiny AFK“ vs. „fotbalové kabiny“, „revitalizace rybníka“ vs.
   „odbahnění“). Jeden neúspěšný dotaz neznamená, že věc neexistuje.
4. **Kontroluj časový rozsah zdroje.** Archiv usnesení začíná až 04/2021 — cokoli
   staršího v něm být nemůže. Dotace a Registr smluv sahají hlouběji, Pečecké
   noviny až do 2020.
5. **Křížově ověřuj mezi zdroji** (usnesení × dotace × smlouvy × zakázky ×
   noviny). Teprve shoda dvou nezávislých zdrojů je doklad.
6. **Pro obsah oficiálního webu města používej `pecky.as4u.cz`, ne `www.pecky.cz`.**
   Je to tentýž web bez bot-ochrany a bez JS renderování — čte se běžným
   `web_fetch`. Pozor, některé stránky jsou dlouhé a přetečou limit odpovědi;
   pak na uložený výstup použij Grep místo čtení celého souboru.

Konkrétní případ, kvůli kterému toto pravidlo vzniklo: rekonstrukce kabin AFK
(dotace NSA 4 753 860 Kč, 2023) a revitalizace rybníka Benešák (OPŽP 3 146 174 Kč,
2019) byly nejprve chybně označeny za nerealizované — kvůli hledání v odlehčeném
indexu, špatnému názvu projektu a vzorku pouhých 20 nejnovějších dotací.

## Známé mezery

- Tabulky smluv a zakázek jsou statický výřez z Hlídače státu, ne živě se obnovující
  data (chybí veřejné API volatelné přímo z prohlížeče).
- ~~Žádosti dle zákona 106/1999 Sb. nedohledány.~~ **VYŘEŠENO 6. 8. 2026** — zdroj
  nalezen na `pecky.as4u.cz` (výroční zprávy 2011–2024 + jednotlivé žádosti a
  odpovědi v PDF). Obsah zatím nevytěžen, na web nepromítnut.
- Srovnání plánu se skutečností (sekce Plán → Jak se plán plní?) je zatím hotové jen
  pro vybrané projekty. Zbytek ze 183 aktivit plánu nebyl proti plnému archivu
  a všem 148 dotacím systematicky prověřen — dokud se to nestane, netvrdit o nich,
  že se nerealizovaly.

## Poslední aktualizace

16. srpna 2026 (denní kontrola zdrojů: do sekce Smlouvy doplněny 2 nové smlouvy
zachycené konektorem Hlídače státu — „Dar — zdravotnický batoh" 10 381 Kč
(Krajské ředitelství policie Středočeského kraje, 22. 7. 2026) a „Smlouva o
spolupráci — Digitální odysea 26/27" bez ceny (Sdružení knihoven ČR, Městská
knihovna Svatopluka Čecha, 14. 7. 2026); součty aktualizovány na 182 smluv ve
skupině (102 416 276 Kč) a 47 smluv jen za úřad (33 132 977 Kč). Jednání a
usnesení, Pečecké noviny a Zakázky zkontrolovány, beze změny — viz poznámka
u příslušných zdrojů v sources.json.)

6. srpna 2026 (nový zdroj knihovnapecky.cz → odhalil `pecky.as4u.cz`, čitelnou verzi
oficiálního webu města bez bot-ochrany. Uzavřena mezera u zákona 106/1999 Sb.
Oba zdroje zapsány do sources.json, doplněno pravidlo č. 6 do metodiky ověřování.)

6. srpna 2026 (na stránku Plán přidána sekce „Jak se plán plní?“ — spárování
vybraných položek plánu s archivem usnesení, dotacemi a Pečeckými novinami:
8 projektů se stavem, zjištění o dotačně řízených prioritách a explicitní
poznámka o hranicích srovnání. Zároveň do README doplněna povinná metodika
ověřování.)

6. srpna 2026 (přidána nová stránka Plán — souhrn Strategického plánu rozvoje
města Pečky 2016–2026: perex, klíčová čísla, konkrétní projekty a zjištění,
že sledování plnění aktivit se v dokumentu po roce 2017 přestalo aktualizovat.
Zařazena do navigace hned za stránku Lidé.)

6. srpna 2026 (denní kontrola zdrojů: do sekce Zakázky doplněna 1 nová zakázka
nalezená diffem proti `data/pecky-zakazky-ids.json` — P26V00002056, Obnova
dětského hřiště Sídliště, 18. 6. 2026, cena neuvedena. Jednání/usnesení,
Pečecké noviny a Smlouvy/dotace přes Hlídače státu zkontrolovány, beze změn.)

6. srpna 2026 (do sekce Pokladna přidán blok Bankovní účty — 9 konkrétních čísel
účtů u 5 bank dohledaných v auditorské zprávě k Závěrečnému účtu 2025, plus
souhrnné zůstatky a poznámka, že žádný účet není „transparentní")

6. srpna 2026 (přidána sekce Zakázky — výřez veřejných zakázek Města Pečky
z Hlídače veřejných zakázek, 193 nalezených záznamů)

6. srpna 2026 (přidána sekce Pokladna — rozpočet a hospodaření města z Monitoru
Státní pokladny a přehled dotací z Registru dotací)

5. srpna 2026 (doplněn jmenný seznam zastupitelstva a kompletní archiv
Pečeckých novin z pecky.cz — obě dřívější mezery vyřešeny procházením webu
přes prohlížeč, který bot ochranu neblokuje)

## Publikování na GitHub Pages

1. Vytvořte nový repozitář (např. `pecky-online`)
2. Nahrajte `index.html` a složku `data/` do kořene repozitáře
3. Settings → Pages → source: `main` branch, root
4. Web poběží na `https://<vaše-uživatelské-jméno>.github.io/pecky-online/`
