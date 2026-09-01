# Instrukce k sekci: O webu (panel `owebu`)

Referenční dokument pro práci na panelu `panel-owebu` v
`content/owebu.html` (generuje se do veřejné stránky `/o-webu/`, viz
`scripts/build.py`). Doplňuje obecné instrukce projektu (Project instructions /
CLAUDE.md) — tohle je detail jen pro tuhle jednu sekci.

## Účel sekce
Vysvětlení, co pecky.online je (neoficiální, nezávislý občanský projekt),
a rozcestník „Odkazy" — oficiální kanály města a související otevřená
data z `sources.json`.

Platí zde konvence z kořenového `CLAUDE.md`: každý nový zdroj přidaný do
`sources.json`, který nemá vlastní kontextovou citaci jinde na webu
(konkrétní tabulku nebo callout), se musí doplnit i jako odkaz do
quicklinks v této sekci → Odkazy — i když je jeho status zatím
„nevytěženo" (obsah nepoužit, ale odkaz má být dohledatelný).

Obsah panelu žije v `content/owebu.html` (žádná samostatná datová sada).

## Sociální sítě

Sekce „Sociální sítě" (druhý blok `div.quicklinks`) shrnuje všechny
facebookové/instagramové/YouTube účty zmiňované na webu, u každého počet
sledujících/členů/odběratelů a datum posledního příspěvku/videa (ukazatel
aktivity, ne datum naší kontroly). Aktualizuje se denně, postup viz
[automation-socialni-site.md](automation-socialni-site.md). Sedm z těchto
odkazů (volební uskupení) se zapisuje i do tabulky „Volební uskupení" na
[Volby 2026](../volby/2026/README.md) — postup pokrývá obě místa
najednou.

Zatím žádná další zvláštní pravidla nad rámec konvence výše. Doplnit sem,
až nějaká vzniknou.
