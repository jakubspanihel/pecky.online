# Instrukce k sekci: Smlouvy (panel `smlouvy`)

Referenční dokument pro práci na panelu `panel-smlouvy` v
`content/smlouvy.html` (generuje se do veřejné stránky `/smlouvy/`,
viz `scripts/build.py`). Doplňuje obecné instrukce projektu (Project instructions
/ CLAUDE.md) — tohle je detail jen pro tuhle jednu sekci.

## Účel sekce
Registr smluv, které Město Pečky uzavírá za peníze daňových poplatníků.
Zdroj: Hlídač státu (konektor), IČO 00239607 — statický výřez, ne živá
data (chybí veřejné API volatelné přímo z prohlížeče).

Poznámky k datům (viz i kořenový `CLAUDE.md` → „Poznámky k datům"):
- Hlídač státu MCP: použij `ICO_of_holding_structure` (celá skupina), ne
  jen `ICOs_of_contracting_party` (jen úřad).
- `with_serious_issues_only` nespolehlivě vrací 0 — rizikové smlouvy
  identifikovat ručně z běžných výsledků.

Obsah panelu žije v `content/smlouvy.html` (žádná samostatná datová sada).

## Pracovní postup: denní kontrola

Sekce nemá vlastní snímek ID jako Zakázky — porovnává se přímo proti
tomu, co je v tabulkách v `content/smlouvy.html`.

1. Zavolat konektor Hlídače státu `search_contracts` s
   `ICO_of_holding_structure: "00239607"` a `order_result: "DateSignedDesc"`.
   Není-li konektor připojený, krok přeskočit a napsat to do shrnutí.
2. Porovnat nejnovější podpisy s tabulkou „Nejnovější smlouvy". Nová
   smlouva = podpis, který v tabulce ještě není. Přidat řádek (datum
   podpisu, předmět, protistrana, částka; u smlouvy bez ceny „bez ceny",
   nikdy nedopočítávat).
3. Druhým dotazem s `order_result: "PriceDesc"` ověřit, jestli nová
   smlouva nepatří i do tabulky „Největší smlouvy v registru" (řazená
   podle částky sestupně).
4. Souhrnná čísla v `subject-box` a v calloutu nad tabulkou (počet smluv
   a celková hodnota za skupinu i za samotný úřad) přepsat podle
   `total_Number_Of_Found_Contracts` / `total_Value_Of_Found_Contracts`
   z obou dotazů — skupina přes `ICO_of_holding_structure`, úřad přes
   `ICOs_of_contracting_party: ["00239607"]`.
   **Pozor na úbytek:** klesne-li počet záznamů proti minulému běhu,
   čísla nepřepisovat naslepo. Registr smluv sice umí záznam stáhnout,
   ale u transparentního webu je horší tiše zapsat nevysvětlený pokles
   než přiznat datovaný snímek — pokles nahlásit uživateli a čísla nechat
   být, dokud nerozhodne. (Nastalo 30. 8. 2026: skupina 182 → 179 smluv,
   úřad 47 → 46, bez nové smlouvy; ponecháno beze změny.)
5. Po změně `content/smlouvy.html` spustit `python3 scripts/build.py`.
6. Zapsat běh do changelogu v kořenovém `README.md`, k příslušnému zdroji
   v `sources.json` a do tabulky „Stav sekcí" (viz `CLAUDE.md` → Konvence).
