# Instrukce k sekci: Smlouvy (panel `smlouvy`)

Referenční dokument pro práci na panelu `panel-smlouvy` v `index.html`
webu pecky.online. Doplňuje obecné instrukce projektu (Project instructions
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

Obsah panelu žije přímo v `index.html` (žádná samostatná datová sada).
Zatím žádná další zvláštní pravidla nad rámec obecných konvencí v
kořenovém `CLAUDE.md`. Doplnit sem, až nějaká vzniknou.
