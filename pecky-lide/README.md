# Instrukce k sekci: Lidé (panel `lide`)

Referenční dokument pro práci na panelu `panel-lide` v `index.html` webu
pecky.online. Doplňuje obecné instrukce projektu (Project instructions /
CLAUDE.md) — tohle je detail jen pro tuhle jednu sekci.

## Účel sekce
Kartičky členů zastupitelstva (21) a rady města (7) — kdo v nich sedí,
za jaké uskupení, případně fotka. Zdroj: jmenný seznam ZM/RM z pecky.cz,
doplňkově web ODS Pečky (viz kořenový `README.md` → „Zdroje dat").

Každé politické uskupení má na celém webu jednu pevně přiřazenou barvu
(CSS třídy `.person-card.party-*`) — používá se konzistentně napříč
sekcemi Lidé, Plán, Volby 2018/2022/2026. Tabulka barev je v kořenovém
`README.md` → „Barevná paleta uskupení"; při přidávání nového uskupení
nebo člena vždy použít existující barvu z té tabulky, ne vymýšlet novou.

Známá mezera: kompletní seznam 21 zastupitelů se nedaří ověřit napřímo
(pecky.cz blokuje bot přístup) — viz kořenový `CLAUDE.md`.

Obsah panelu žije přímo v `index.html` (žádná samostatná datová sada).
Zatím žádná další zvláštní pravidla nad rámec obecných konvencí v
kořenovém `CLAUDE.md`. Doplnit sem, až nějaká vzniknou.
