# Instrukce k sekci: Volby 2018 (panel `volby2018`)

Referenční dokument pro práci na panelu `panel-volby2018` v `index.html`
webu pecky.online. Doplňuje obecné instrukce projektu i společný rozcestník
[`volby/README.md`](../README.md) — tohle je detail jen pro tenhle
ročník.

## Účel sekce
Výsledky komunálních voleb 2018 v Pečkách (šest kandidujících uskupení,
vítěz SNK NAŠE PEČKY s 39,60 % hlasů / 9 z 21 mandátů), předvolební sliby
uskupení (záložka „Předvolební sliby") a rozbor, jak se naplnily (záložka
„Rozbor") — vč. zajímavosti o soudem napadených volbách. Zdroj výsledků:
dobový tisk / Seznam Zprávy, Novinky.cz (viz kořenový `README.md` →
„Zdroje dat").

## Ustavující zasedání — mezera v datech
Pravidlo „Zvolení zástupci patří do Výsledků voleb"
([`volby/README.md`](../README.md)) se u tohoto ročníku dá naplnit
jen částečně. Ustavující zasedání po volbách 2018 (a stejně tak 2014) se
konalo dřív, než kam sahá systém usneseni.cz — ten začíná až **dubnem
2021**, takže archiv jednání ho neobsahuje. Nedohledatelný je proto jak
přesný poměr hlasů pro/proti/zdržel se při volbě starostky a radních,
tak číslo a datum samotného zasedání; dobový tisk je neuvádí.

Jména zvoleného vedení lze doplnit z dobového tisku a z webu města, ale
**hlasování ne** — takový údaj neodhadovat ani nedopočítávat, označit ho
jako mezeru (`.callout`) podle metodiky v kořenovém `README.md`.

## Data ve složce
Textový obsah panelu žije v `content/volby2018.html` (žádná samostatná datová
sada). Ve složce ročníku je navíc `volebni-programy-2018/` — 6 skenů
volební inzerce uskupení z Pečeckých novin 9/2018, zobrazovaných v
záložce „Předvolební sliby". V `index.html` se na ně odkazuje cestou
`volby/2018/volebni-programy-2018/{uskupeni}.jpg`.

Jinak žádná další zvláštní pravidla nad rámec obecných konvencí v
kořenovém `CLAUDE.md` a v [`volby/README.md`](../README.md).
Doplnit sem, až nějaká vzniknou.
