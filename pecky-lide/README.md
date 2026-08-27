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
sekcemi Lidé, Plán, Volby 2018/2022/2026. Tabulka barev je v
[`pecky-volby/README.md`](../pecky-volby/README.md) → „Barevná paleta
uskupení"; při přidávání nového uskupení nebo člena vždy použít
existující barvu z té tabulky, ne vymýšlet novou.

Známá mezera: kompletní seznam 21 zastupitelů se nedaří ověřit napřímo
(pecky.cz blokuje bot přístup) — viz kořenový `CLAUDE.md`.

## Lidé = aktuální stav, Volby = stav při ustavení
Tenhle panel ukazuje, kdo v zastupitelstvu a radě sedí **teď**. Jmenný
seznam zvolených po volbách je v subpanelu „Výsledky voleb" příslušného
ročníku — viz [`pecky-volby/README.md`](../pecky-volby/README.md) →
„Zvolení zástupci". **Oba seznamy jsou samostatné a už se rozcházejí:**
od ustavujícího zasedání 20. 10. 2022 se složení dvakrát změnilo —
Jaroslava Vosecká nastoupila za Lenku Třískovou (slib 11. 9. 2024) a
Ondřej Schulz za Bc. Ivetu Dvořákovou (slib 26. 2. 2025). Při další
rezignaci, kooptaci náhradníka nebo změně ve vedení se opraví **jen
tenhle panel**; historický seznam u Voleb 2022 zůstává, jaký byl.

## Fotky
Portréty na kartičkách (`img.avatar`) nejsou ve složce této sekce —
leží u volebního ročníku, ve kterém byli členové zvoleni:
`pecky-volby/2022/zastupitele/{prijmeni}.jpg` (42 souborů, příjmení bez
diakritiky malými písmeny; u shody příjmení i s křestním, např.
`hruska-ivan.jpg`). Po dalších volbách zakládat novou sadu ve složce
nového ročníku, ne přepisovat tuhle. Detaily viz
[`pecky-volby/README.md`](../pecky-volby/README.md).

Obsah panelu jinak žije přímo v `index.html` (žádná samostatná datová
sada). Zatím žádná další zvláštní pravidla nad rámec obecných konvencí v
kořenovém `CLAUDE.md`. Doplnit sem, až nějaká vzniknou.
