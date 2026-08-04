# pecky.online

Neoficiální, nezávislý občanský projekt zpřehledňující veřejně dostupné informace
o samosprávě města Pečky (okres Kolín, Středočeský kraj).

## Obsah složky

- `index.html` — celá webová stránka (jeden soubor, HTML/CSS/JS, bez závislostí
  kromě Google Fonts přes CDN). Otevřete přímo v prohlížeči nebo nahrajte na
  GitHub Pages / jakýkoli statický hosting.

## Zdroje dat

- Základní fakta o městě: Wikipedie, oficiální web města (pecky.cz)
- Výsledky komunálních voleb 2022: Seznam Zprávy, Novinky.cz
- Složení rady města: pecky.cz, web ODS Pečky
- Smlouvy: Hlídač státu (konektor), IČO 00239607 — statický výřez, ne živá data
- Pečecké noviny: pecky.cz (jednotlivá čísla dohledaná webovým vyhledáváním)

## Známé mezery

- Chybí jmenný seznam všech 21 zastupitelů (stránka na pecky.cz blokuje
  automatizovaný přístup) — máme jen rozložení mandátů podle stran.
- Archiv Pečeckých novin není kompletní, jen tři dohledaná vydání.
- Tabulka smluv je statický výřez z Hlídače státu, ne živě se obnovující data
  (chybí veřejné API volatelné přímo z prohlížeče).

## Poslední aktualizace

4. srpna 2026

## Publikování na GitHub Pages

1. Vytvořte nový repozitář (např. `pecky-online`)
2. Nahrajte `index.html` do kořene repozitáře
3. Settings → Pages → source: `main` branch, root
4. Web poběží na `https://<vaše-uživatelské-jméno>.github.io/pecky-online/`
