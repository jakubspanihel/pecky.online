# Odkazy na parcely (katastr) a tabulky Pozemky

Jak web propojuje zmínky o pozemcích/parcelách v usneseních s katastrem
nemovitostí (RUIAN) a jak se z nich generují tabulky Nákup/Prodej na
stránce Pozemky. Oboje řeší jeden skript,
`pecky-jednani/scripts/update-pozemky.py`, nezávisle na scraperu jednání
— spouští se poté, co se aktualizuje `pecky-jednani.json` (viz
[automation-kontrola-usneseni-cz.md](automation-kontrola-usneseni-cz.md)).

## Historie (přečíst, než se sáhne na cokoli s „katastr" v názvu)

Do 23. 8. 2026 web prolinkovával zmínky o parcelách přes
`pecky-jednani/katastr-odkazy.json` — globální mapu „číslo parcely →
URL" bez rozlišení katastrálního území, dohledanou přes REST API ČÚZK
(api-kn.cuzk.gov.cz, klíč `.katastr-api-key`), postup popsaný v
`katastr.md`. **Soubor byl smazán**, protože obsahoval prokázanou
chybu: číslo parcely je unikátní jen v rámci jednoho katastru, ale
mapa měla pro každé číslo jen jednu hodnotu. Potvrzený případ: parcela
„254" existuje jak v k.ú. Pečky (362 m², ID 1602232204 — to byla ta
uložená hodnota), tak jako 254/1 a 254/2 v k.ú. Velké Chvalovice (483
a 36 m²) — usnesení UZ-46-4/25/UR-274-30/25/UR-195-21/25 (prodej cca
36 m² ve Velkých Chvalovicích) se tak prolinkovalo na ŠPATNOU (Pečky)
parcelu. `katastr.md` a `katastr-parcely-v-usneseních.md` popisují tenhle
starý, opuštěný postup — ponechány jen jako historická poznámka,
needit se jimi řídit ani do nich nic doplňovat.

## Současný stav

Vše (tabulky Pozemky i obecné prolinkování „parc. NNNN" v Jednání)
generuje jediný skript, `pecky-jednani/scripts/update-pozemky.py` — viz
sekce „Tabulky Nákup/Prodej na stránce Pozemky" níže pro plný popis.
Skript sám dohledává katastr z kontextu KAŽDÉHO výskytu čísla zvlášť
(ne jen jednou globálně) a čísla, u kterých se katastr napříč výskyty
neshoduje (kolize) nebo se nepodaří určit vůbec, **záměrně vynechá** —
frontend (`jLinkParcely()` v `index.html` i `pecky-jednani/index.html`)
pak takové číslo prostě nepodlinkuje, což je bezpečné chování (žádný
ruční krok navíc není potřeba, nová/změněná jednání se promítnou příštím
spuštěním skriptu).

Výstupy skriptu pro tuhle část:
- `pecky-jednani/parcely-pozemky.json` — katastr-přesná cache
  „katastr|číslo" → RUIAN ID, zdroj pravdy pro obojí níže.
- `pecky-jednani/parcely-odkazy.json` — plochá mapa „číslo" → URL,
  načítá ji frontend pro obecné prolinkování v Jednání (nahrazuje
  smazaný `katastr-odkazy.json`).

## Tabulky Nákup/Prodej na stránce Pozemky — aktualizovat spolu s Jednáním

Panel „Pozemky" v kořenovém `index.html` (subpanely `subpanel-pozemky-nakup`
a `subpanel-pozemky-prodej`) je statický výřez sestavený z usnesení
o prodeji/nákupu pozemku, ne živě dotahovaná data — analogicky k sekci
Smlouvy. **Při každé aktualizaci `pecky-jednani.json` je proto potřeba
spustit i:**

```
python3 pecky-jednani/scripts/update-pozemky.py
```

Skript (spouštět z kořene repa) v jednom běhu:
1. Najde v `pecky-jednani.json` nová/změněná usnesení o prodeji/nákupu
   pozemku (stejná klíčová slova a metodika jako u ruční tabulky
   z 23. 8. 2026 — párování rada→zastupitelstvo, extrakce ceny).
2. Pro nová čísla parcel dohledá RUIAN ID přes vdp.cuzk.gov.cz **vždy
   s konkrétním katastrálním územím** (řádek v tabulce Pozemky katastr
   už zná), takže nemá riziko křížové kolize jako starý globální
   `katastr-odkazy.json`. Cache žije v `parcely-pozemky.json`
   (klíč `"katastr|číslo"`).
3. Přegeneruje obě HTML tabulky a nahradí jimi obsah zmíněných subpanelů
   přímo v `index.html`, ověří balanci HTML tagů.
4. Projde **úplně všechna** usnesení a body programu (ne jen ty
   o pozemcích), pro každou zmínku „parc. NNNN" zjistí katastr z jejího
   vlastního kontextu, sesbírá katastry napříč všemi výskyty daného
   čísla a dohledá/zapíše do `parcely-odkazy.json` jen čísla, kde se
   katastr shoduje; kolidující nebo neurčitelná čísla vynechá (nahlásí
   na stderr, viz sekce výše).

Katastrální území mimo pevný seznam v `KAT_CODES` (aktuálně Pečky,
Velké Chvalovice, Dobřichov, Plaňany, Blinka, Tatce, Radim u Kolína)
je třeba do skriptu doplnit ručně (kód přes vyhledání na
vdp.cuzk.gov.cz/vdp/ruian/parcely — pozor na víceznačné názvy, viz
příklad „Radim" vs „Radim u Kolína" — komentář přímo u `KAT_CODES`
ve skriptu). Číslo, které se nepodaří dohledat automaticky (rozdělená/
sloučená parcela apod.), skript nahlásí a je třeba jej doplnit do
`MANUAL_OVERRIDES` ve skriptu s odůvodněním (výměra/kontext z textu
usnesení).
