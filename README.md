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
- Pečecké noviny: pecky.cz — kompletní archiv PDF zpravodaje (68 vydání, 2020–2026)
- Jednání a usnesení: jednorázový strojově čitelný export webu
  mesto-pecky.usneseni.cz z 4. 8. 2026 — 281 jednání (243 Rada, 38
  Zastupitelstvo, 2021–2026), 2 731 usnesení. Kompletní snímek se všemi detaily
  (vč. jmenovitých hlasování a plných zápisů) je v `sources/archive-2026-08-04.json`;
  `data/pecky-jednani.json` je z něj odvozený odlehčený index pro hledání na
  webu. Viz `sources/SPEC.md` a `sources/AUTOMATION.md` pro popis exportu a
  plán budoucí aktualizace.

## Známé mezery

- Tabulka smluv je statický výřez z Hlídače státu, ne živě se obnovující data
  (chybí veřejné API volatelné přímo z prohlížeče).
- Žádosti dle zákona 106/1999 Sb. nedohledány.

## Poslední aktualizace

5. srpna 2026 (doplněn jmenný seznam zastupitelstva a kompletní archiv
Pečeckých novin z pecky.cz — obě dřívější mezery vyřešeny procházením webu
přes prohlížeč, který bot ochranu neblokuje)

## Publikování na GitHub Pages

1. Vytvořte nový repozitář (např. `pecky-online`)
2. Nahrajte `index.html` a složku `data/` do kořene repozitáře
3. Settings → Pages → source: `main` branch, root
4. Web poběží na `https://<vaše-uživatelské-jméno>.github.io/pecky-online/`
