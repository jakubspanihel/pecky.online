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

## Známé mezery

- Tabulky smluv a zakázek jsou statický výřez z Hlídače státu, ne živě se obnovující
  data (chybí veřejné API volatelné přímo z prohlížeče).
- Žádosti dle zákona 106/1999 Sb. nedohledány.

## Poslední aktualizace

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
