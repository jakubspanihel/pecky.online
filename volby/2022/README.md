# Instrukce k sekci: Volby 2022 (panel `volby2022`)

Referenční dokument pro práci na panelu `panel-volby2022` v `index.html`
webu pecky.online. Doplňuje obecné instrukce projektu i společný rozcestník
[`volby/README.md`](../README.md) — tohle je detail jen pro tenhle
ročník.

## Účel sekce
Výsledky komunálních voleb 2022 v Pečkách (vítěz NAŠE PEČKY s 30,29 %
hlasů / 7 z 21 mandátů, přesto bez křesla v radě — vysvětleno v záložce
„Rozbor" jako důsledek konstrukce voleb vedení obce, ne anomálie),
předvolební sliby uskupení (záložka „Předvolební sliby") a rozbor, jak se
naplnily. Zdroj výsledků: Seznam Zprávy, Novinky.cz (viz kořenový
`README.md` → „Zdroje dat").

Do voleb 2026 zůstává v čele města zastupitelstvo a rada zvolené v tomto
ročníku — viz i panel Lidé.

## Ustavující zasedání (zdroj pro „Výsledky voleb")

Volby proběhly **23.–24. 9. 2022**, nové zastupitelstvo se ustavilo na
**Zastupitelstvu č. 7/2022 dne 20. 10. 2022** — necelý měsíc po volbách.
Na tomhle jednání složili zvolení zastupitelé slib, ověřila se platnost
voleb a zvolilo se vedení města. Je to zdroj pro jmenný seznam v
subpanelu „Výsledky voleb" (pravidlo viz
[`volby/README.md`](../README.md) → „Zvolení zástupci").

Zvolené vedení a rada (7 členů), vč. poměru hlasů pro–proti–zdržel se:

| Funkce | Jméno | Usnesení | Hlasování |
|---|---|---|---|
| Starosta | Milan Paluska | `UZ-90-7/22` | 13–6–2 |
| 1. místostarosta (uvolněný) | Zdeněk Fejfar | `UZ-91-7/22` | 15–3–3 |
| 2. místostarosta (neuvolněný) | Ing. Martin Jedlička | `UZ-92-7/22` | 14–5–2 |
| Radní | Ing. Karel Krištoufek | `UZ-93-7/22` | 14–6–1 |
| Radní | Ing. Hana Kuprová | `UZ-94-7/22` | 16–2–3 |
| Radní | Ivana Trčková | `UZ-95-7/22` | 15–2–4 |
| Radní | Ing. Petr Dürr | `UZ-96-7/22` | 14–4–3 |

Ověřeno proti archivu jednání (`jednani/pecky-jednani.json`,
jednání `7/2022`, 33 usnesení `UZ-83-7/22`…`UZ-115-7/22`); každé usnesení
má v archivu i vlastní URL na mesto-pecky.usneseni.cz. Tamtéž jsou
usnesení o počtu uvolněných funkcí (`UZ-87`, `UZ-88`), o složení rady
(`UZ-89`) a volby předsedů a členů finančního a kontrolního výboru
(`UZ-98`…`UZ-111`) — ty se do „Výsledků voleb" hodí jako doplněk.

Zbylých 14 zastupitelů je v subpanelu vypsaných po uskupeních: NAŠE
PEČKY 7 (celý vítěz voleb skončil mimo radu), ODS a NK 1, SNK Pečky
Pečákům 2, SPD 3, ČSSD 1.

**Uskupení dvou zastupitelek je dopočítané, ne citované.** Usnesení
u jmen uskupení neuvádějí. U 19 lidí je známé z panelu Lidé; u
Bc. Ivety Dvořákové a Lenky Třískové, které zastupitelstvo mezitím
opustily, vychází z počtu mandátů jednotlivých uskupení (NAŠE PEČKY
mají 7, SPD 3) a z toho, že za obě nastoupil náhradník z téže
kandidátky. V `index.html` je to u tabulky přiznané.

## Změny složení po ustavení
Seznam ve „Výsledcích voleb" je zmrazený k 20. 10. 2022. Od té doby
nastaly dvě změny, obě ověřené v archivu jednání — panel **Lidé** je
proto dnes jiný než tenhle seznam:

| Odešel/odešla | Nastoupil/a | Kdy | Jednání |
|---|---|---|---|
| Lenka Třísková (SPD) | Jaroslava Vosecká | 11. 9. 2024 | ZM 4/2024, bod 1 „Složení slibu náhradníka J. Vosecké za uvolněný mandát" |
| Bc. Iveta Dvořáková (NAŠE PEČKY) | Ondřej Schulz | 26. 2. 2025 | ZM 1/2025, bod 1 „složení slibu nového člena ZM" |

Pozn.: usnesení jméno nastupujícího u ZM 1/2025 neuvádí — Ondřej Schulz
je doložený tím, že se na tomhle jednání poprvé objevuje v prezenci a
Bc. Iveta Dvořáková naposledy chybí; týmž jednáním ji ve funkci
předsedkyně kontrolního výboru vystřídala Mgr. Alena Švejnohová
(`UZ-3-1/25`). Lenka Třísková krátce po odchodu zemřela (Rada města to
konstatuje v `UR-363-37/24` z 21. 10. 2024, pamětní strom v lokalitě
Bačov řeší `UR-241-26/25`).

## Data ve složce
Textový obsah panelu žije v `content/volby2022.html` (žádná samostatná datová
sada). Ve složce ročníku jsou navíc dvě sady obrázků:

- `volebni-programy-2022/` — 6 skenů volební inzerce uskupení z
  Pečeckých novin 9/2022 (záložka „Předvolební sliby"), cesta
  `volby/2022/volebni-programy-2022/{uskupeni}.jpg`.
- `zastupitele/` — 42 portrétů zastupitelů zvolených v tomto ročníku,
  cesta `volby/2022/zastupitele/{prijmeni}.jpg`. Odkazuje se na ně
  ze **dvou** míst v `index.html`: kartičky v panelu Lidé
  (`.avatar`) a avatary u volby vedení města v tomto panelu
  (`.people-avatars .av-img`) — při přejmenování projít obě.
  (Řádky jednání v panelu Jednání portréty nepoužívají, mají jen
  iniciály `.av-init`.)

Jinak žádná další zvláštní pravidla nad rámec obecných konvencí v
kořenovém `CLAUDE.md` a v [`volby/README.md`](../README.md).
Doplnit sem, až nějaká vzniknou.
