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

## Struktura stránky (podzáložky)

Stránka je jeden seznam zdrojů se dvěma skupinami (`.owebu-group`) a filtrem
nahoře: vlevo `h3` s počtem zobrazených zdrojů (počet `a.qlink` ve viditelných
skupinách, dopočítá JS na konci `content/owebu.html`), vpravo přepínač
(segmented-control) **Vše** (výchozí) / **Webové stránky** / **Sociální sítě**.
Odkaz na skupinu: `/o-webu/#owebu-odkazy`, `/o-webu/#owebu-socialni`.
(Do 3. 10. 2026 šlo o podzáložky; „Historie změn na webu“ se přesunula na
samostatnou stránku, viz níže, a tabulka „Zdroje a stav sekcí“ se zrušila:
zdroje jsou uvedeny přímo u dat na stránkách sekcí — nový zdroj proto vždy
citovat tam, ne centrálně.)

1. **Webové stránky** (`#subpanel-owebu-odkazy`, `data-group="odkazy"`) —
   oficiální kanály a otevřená data + další nezávislé zdroje, dva
   bloky `div.quicklinks` bez vlastních nadpisů.
2. **Sociální sítě** (`#subpanel-owebu-socialni`, `data-group="socialni"`)

## Historie změn na webu (`/o-webu/changelog.html`)

Samostatná podstránka (`EXTRA_PAGES['changelog']` v `scripts/build.py`,
zdroj `content/changelog.html`) s tabulkou „Stav sekcí“ (`{{STAV_SEKCI}}`),
kterou build generuje z tabulky v kořenovém `README.md` → „Stav sekcí“.
Odkaz je v patičce každé stránky (`assets/footer.html`), na stránku se
neodkazuje z podzáložek O webu. Datum „Aktualizováno“ je nejnovější datum
„Změna“ ze „Stav sekcí“ (`lastmod: 'auto'`) a stránka je v sitemapě.
Ručně se do ní nezapisuje — zápis běhu = přepsání řádku ve „Stav sekcí“
v `README.md` (viz `CLAUDE.md`) a `python3 scripts/build.py`.

Obecný disclaimer (`div.footer-note`, „Tento web nezastupuje Město
Pečky…") je záměrně mimo skupiny (za poslední `.owebu-group`), aby byl
vidět nezávisle na vybrané záložce.

## Sociální sítě

Sekce „Sociální sítě" (skupina `subpanel-owebu-socialni`, blok
`div.quicklinks`) shrnuje všechny
facebookové/instagramové/YouTube účty zmiňované na webu, u každého počet
sledujících/členů/odběratelů a datum posledního příspěvku/videa (ukazatel
aktivity, ne datum naší kontroly). Aktualizuje se týdně, postup viz
[automation-socialni-site.md](automation-socialni-site.md). Sedm z těchto
odkazů (volební uskupení) se zapisuje i do tabulky „Volební uskupení" na
[Volby 2026](../volby/2026/README.md) — postup pokrývá obě místa
najednou.

Zatím žádná další zvláštní pravidla nad rámec konvence výše. Doplnit sem,
až nějaká vzniknou.
