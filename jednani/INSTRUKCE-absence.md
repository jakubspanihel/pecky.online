# Instrukce: počítání absence jednotlivých zastupitelů

Postup pro zjištění, kolikrát který člen zastupitelstva (nebo rady) na
jednání chyběl. Sesterský dokument k `INSTRUKCE-analyza-hlasovani.md` —
ten řeší, **jak** kdo hlasoval, tenhle **jestli tam vůbec byl**.

> **Stav: hotové, zveřejněné bez odkazu.** 9. 9. 2026 jsme doplnili
> průběžnou prezenci do dat (§3), napsali `scripts/absence.py` a postavili
> stránku `/jednani/absence.html`. Stránka zatím nemá odkaz odnikud, není
> v sitemapě a nese `noindex` — čeká se na rozhodnutí, kam odkaz patří.
> Rozhodnutí a otevřené body na konci.

## 1. Zdroj dat

`jednani/pecky-jednani.json` → `meetings[].attendance`:

```json
"attendance": {
  "present": 17, "total": 21,
  "present_names": ["Václav Drška", "Ing. Petr Dürr", …],
  "absent_names": [{"name": "Ing. Martin Jedlička", "note": "omluven"},
                   {"name": "Pavel Sedláček", "note": "nepřítomen"}]
}
```

Původ pole popisuje `README.md` → „Jmenovité obsazení" (scraper bere
`minutes.presence.pritomni.names`, `…omluveni.names`, `…nepritomni.names`
z usneseni.cz).

Pokrytí ověřené 9. 9. 2026:

- **Zastupitelstvo:** 39 zasedání (16. 6. 2021 – 26. 8. 2026), všechna
  se jmény.
- **Rada:** 248 jednání (12. 4. 2021 – 7. 9. 2026), z toho 247 se jmény.
  Chybí Rada 32/2026 ze 7. 9. 2026 — město k ní zatím zveřejnilo jen
  pozvánku, zápis ne.

**Absenci lze na rozdíl od hlasování počítat i u Rady.** Omezení „jen
Zastupitelstvo" z `INSTRUKCE-analyza-hlasovani.md` platí pro *hlasování*
(u Rady usneseni.cz jména hlasujících neuvádí). Prezence je jmenná
u obou orgánů.

**Kontrola integrity před počítáním.** Pro každý záznam musí platit
`len(present_names) == present` a `present + len(absent_names) == total`,
a **žádné jméno se nesmí v jednom jednání objevit dvakrát**. Kontrola
9. 9. 2026 našla dva vadné záznamy, oba v Radě a oba vadné už u zdroje,
ne vinou scraperu:

- **Rada 27/2021 (22. 11. 2021)** — Jiří Katrnoška je zároveň mezi
  přítomnými (7) i nepřítomnými (1), dohromady 8 při sedmičlenné radě.
  Surový zápis to vysvětluje větou „Tito zastupitelé se (z)účastní
  distančně: Jiří Katrnoška" — účastnil se na dálku a systém ho zapsal
  do obou seznamů. Počítat ho jako přítomného.
- **Rada 24/2024 (24. 6. 2024)** — zápis vypisuje 4 přítomné a 3 omluvené
  (dohromady 7 = celá rada), ale v souhrnné větě tvrdí „Přítomno je 5
  členů". Jmenný rozpis je konzistentní, chybné je jen pole
  `attendance.present`; počítat podle jmen.

Obojí patří do výstupu jako přiznaná nesrovnalost, ne k tichému
přepsání. U všech 39 zasedání ZM kontrola prošla bez nálezu.

**Distanční účast.** Zápisy z covidového období (4/2021 až 9/2022)
u 23 jednání — 18× Rada, 5× Zastupitelstvo — obsahují navíc větu „Tito
zastupitelé se (z)účastní distančně: …". Scraper tuhle informaci
zahazuje úplně, v `pecky-jednani.json` po ní není stopa. Až na vadný
záznam Rady 27/2021 výše jsou všichni takoví lidé zapsaní zároveň mezi
přítomnými, takže se statistika nerozbíjí — ale rozlišit osobní
a distanční účast z `pecky-jednani.json` nejde.

## 2. Jmenovatel je mandát, ne počet všech jednání

Nejdůležitější past celého úkolu. Složení sboru se v čase mění, takže
„chyběl 17× ze 39" je u většiny lidí nesmysl.

Mechanicky se změny zjistí takhle: pro každé jednání sestavit sbor jako
`present_names ∪ absent_names`, seřadit jednání podle data a porovnávat
sousední dvojice. Rozdíl = nástup nebo odchod. Výsledek pak ověřit proti
životopisům v `lide/people.json` (pole `bio` u zastupitelů nástupy
náhradníků popisuje).

Změny v zastupitelstvu, které tímhle porovnáním vyšly (stav 9. 9. 2026):

| Datum | Změna |
|---|---|
| 15. 9. 2021 | Ing. Jan Korouš nastoupil za Mgr. Blanku Kozákovou |
| 10. 8. 2022 | Bc. Iveta Minaříková → Bc. Iveta Dvořáková — **táž osoba**, změna příjmení, ne výměna |
| 20. 10. 2022 | ustavující zasedání po volbách: 10 lidí odešlo, 10 nastoupilo |
| 11. 9. 2024 | Jaroslava Vosecká složila slib za uvolněný mandát Lenky Třískové |
| 26. 2. 2025 | Ondřej Schulz nastoupil jako náhradník po Bc. Ivetě Dvořákové |

Dvě konkrétní pasti, které z toho plynou:

- **Ondřej Schulz má dvě oddělená období.** Zastupitelem byl už
  2021–2022, po ustavujícím zasedání 2022 mandát neobhájil a vrátil se
  až 26. 2. 2025. V prezencích se objevuje na 22 z 39 zasedání — sečíst
  to do jednoho čísla by smíchalo dvě různá období s dírou uprostřed.
- **Minaříková a Dvořáková je jeden člověk.** Normalizace jmen tuhle
  dvojici nespojí (viz §5).

Pravidlo: jmenovatel = jednání konaná v době trvání mandátu dané osoby,
a **počítat zvlášť po volebních obdobích** (hranice drží
`jednani/volebni-obdobi.json`).

## 3. Co „absence" ve zdroji doopravdy znamená

Prezence v zápisech je **úvodní**, tedy stav při zahájení. Zapisovatel
ji ve všech 38 zasedáních ZM v archivu uzavírá větou „Přítomno je N z M
členů a zastupitelstvo je usnášeníschopné" a hned za ní časem zahájení;
záhlaví se v čase změnilo — 30 starších zápisů má „Prezence:", 8 zápisů
od 25. 6. 2025 „Úvodní prezence:". Kdo dorazil po zahájení, zůstane
v `absent_names`, přestože se jednání zúčastnil.

Ověřeno křížem proti jmenným hlasováním v `archive-2026-08-04.json`:
**12 případů na 10 zasedáních ZM**, kdy člověk chybí v úvodní prezenci,
ale později hlasoval. Doložené případy:

| Zasedání | Kdo hlasoval, ač chybí v prezenci |
|---|---|
| 3/2021 (20. 10. 2021) | Ing. Martin Jedlička, Ing. Petr Dürr |
| 4/2021 (10. 11. 2021) | Ing. Stanislav Jiran |
| 2/2022 (30. 3. 2022) | Ing. Stanislav Jiran |
| 5/2022 (10. 8. 2022) | Mgr. Jaroslava Heroldová |
| 6/2022 (21. 9. 2022) | Ing. Petr Dürr |
| 9/2022 (14. 12. 2022) | Ing. Petr Dürr |
| 6/2023 (8. 11. 2023) | Ing. Martin Jedlička, Bc. Iveta Dvořáková |
| 1/2025 (26. 2. 2025) | Milan Pečenka |
| 5/2025 (12. 11. 2025) | Tomáš Růžička |
| 1/2026 (4. 3. 2026) | Lubomír Metelák |

Počty účastníků jednotlivých hlasování se navíc v rámci jednoho zasedání
liší (např. 6/2023: mezi 18 a 20 hlasujícími), takže lidé odcházejí
i uprostřed jednání.

### Průběžná aktualizace prezence — pole, které scraper zahazuje

**Tohle je nejzávažnější zjištění celého rozboru.** Zapisovatel v textu
zápisu vede příchody a odchody během jednání a pokaždé vypíše nový stav:

> V 15:45:53 přišel Ing. Petr Dürr, přítomno 7 z 7 radních.
> Aktualizovaný stav prezence: Přítomni: (7) …
>
> V 16:28:59 odešel Ing. Karel Krištoufek, přítomno 6 z 7 radních.
> Aktualizovaný stav prezence: Přítomni: (6) … Nepřítomni: (1) Ing. Karel
> Krištoufek
>
> — Rada 31/2026 (31. 8. 2026), ověřeno přímo na `/zapis/` stránce

Scraper tyhle věty do 9. 9. 2026 vědomě zahazoval — `attendance` se brala
výslovně jen ze zahájení. Rozdíl, který to dělá, není kosmetický: Ing. Petr
Dürr chybí v úvodní prezenci u 102 ze 174 jednání rady 2022–2026, ale u 49
z nich zápis zaznamenal jeho pozdější příchod — skutečně nepřítomen byl
u 53, tedy 31 % místo 59 %.

**Od 9. 9. 2026 jsou tyhle údaje v datech** jako `attendance.changes`
(tvar a pokrytí popisuje `README.md` → „Průběžná prezence"): 124 jednání,
218 událostí. Doplnil je `scripts/doplnit-prubeznou-prezenci.py` zpětně
z archivu, pět jednání novějších než snímek archivu jsme ověřili ručně na
`/zapis/`; nová jednání sbírá `automation-kontrola-usneseni-cz.md`, krok 4.

Opačným směrem to platí taky: Tomáš Růžička nechyběl v úvodní prezenci
ani jednou, ale u 13 z 27 zasedání zápis zaznamenal jeho dřívější odchod.
Statistika postavená jen na úvodní prezenci ho ukáže jako bezchybného.

Proto: **hlavní číslo počítat z úvodní prezence opravené o zaznamenané
příchody**, ne ze samotné úvodní prezence. Odchody vykazovat zvlášť, ne
je míchat do absence — sedět na jednání do konce není povinnost a délku
docházky zápis nedovoluje spočítat přesně.

Příchod v `changes` neznamená vždy pozdní příchod: někteří lidé během
jednání odejdou a vrátí se, takže mají příchod, i když v úvodní prezenci
byli. Jako opravu absence proto brát příchod **jen u toho, kdo je zároveň
v `absent_names`** téhož jednání.

Ještě jemnější míru — účast na jednotlivých hlasováních — nabízí archiv
v `meetings[].minutes.agenda_items[].votes[]` (jména v blocích
`pro`/`proti`/`zdrzel_se`/`nehlasoval`). Platí pro ni stejná omezení jako
u analýzy hlasování: jen Zastupitelstvo a jen do data snímku archivu.

**Omluven vs. nepřítomen.** Pole `note` rozlišuje dva stavy a ve
statistice patří každý zvlášť: v zastupitelstvu 88 omluv proti
17 nepřítomnostem bez omluvy, v radě 180 proti 106 (stav 9. 9. 2026).
Web tenhle rozdíl zatím ukazuje jen v tooltipu avatara. Do výstupu ho
vzít, ale nehodnotit — zápis neuvádí, proč se kdo omluvil ani proč se
neomluvil.

## 4. Co se počítá

Rada a Zastupitelstvo se počítají **zvlášť** a nesčítají se do jednoho
čísla — rada zasedá zhruba šestkrát častěji a absence v ní znamená něco
jiného. Uvnitř každého orgánu se počítá zvlášť za volební období.

Pro každou osobu:

- **jednání v mandátu** (jmenovatel podle §2),
- **chyběl při zahájení** = `absent_names`, rozpad na **omluven**
  a **nepřítomen bez omluvy**,
- **dorazil později** (příchody podle §3),
- **nebyl vůbec** = chyběl při zahájení a příchod není zaznamenaný →
  **hlavní číslo statistiky**,
- **odešel dřív** — vykazovat samostatně, nesčítat s absencí.

Procenta uvádět jen tam, kde je jmenovatel aspoň 10 jednání; u kratších
mandátů psát absolutní čísla, jinak z pěti jednání vyskočí „40 %
absence".

### Řazení a poznámky

Řadit **vzestupně podle počtu jednání v mandátu**, ne podle procent.
Nahoře tak stojí lidé s nejkratším mandátem — přesně ti, u kterých
procento klame nejvíc — a čtenář narazí na jejich malý jmenovatel dřív,
než začne srovnávat. Uvnitř stejného počtu jednání řadit sestupně podle
sloupce „nebyl vůbec".

Ke každému řádku, který se vymyká, patří **poznámka přímo v tabulce**, ne
pod ní. Vymykají se tři situace: kratší mandát než u zbytku sboru (nástup
náhradníka, konec mandátu), velký rozdíl mezi „chyběl při zahájení"
a „nebyl vůbec" (hodně pozdních příchodů) a hodně dřívějších odchodů při
nízké absenci. Poznámka uvádí fakt ze zdroje, ne výklad: „náhradnice od
11. 9. 2024", ne „nestíhá".

### Ukázka výstupu

Prvních pět řádků propočtu z 9. 9. 2026 — Zastupitelstvo, období
2022–2026, 28 zasedání (20. 10. 2022 – 26. 8. 2026). Slouží jako
referenční hodnoty: až skript vznikne, musí u těchhle lidí vyjít
stejná čísla.

| Zastupitel | Jednání | Chyběl při zahájení | Dorazil později | Nebyl vůbec | % | Odešel dřív | Poznámka |
|---|---:|---:|---:|---:|---:|---:|---|
| Ondřej Schulz | 11 | 0 | 0 | 0 | 0 % | 0 | náhradník, slib 26. 2. 2025 |
| Jaroslava Vosecká | 14 | 7 | 0 | 7 | 50,0 % | 1 | náhradnice, slib 11. 9. 2024 |
| Lenka Třísková | 14 | 6 | 0 | 6 | 42,9 % | 4 | mandát skončil 19. 6. 2024 |
| Bc. Iveta Dvořáková | 17 | 3 | 1 | 2 | 11,8 % | 0 | mandát skončil 26. 2. 2025; dříve Minaříková |
| Lubomír Metelák | 28 | 9 | 1 | 8 | 28,6 % | 3 | — |

Prvním čtyřem řádkům stojí procento na kratším mandátu než zbytku sboru;
proto jsou nahoře a proto k nim patří poznámka.

## 5. Párování jmen

Jména jsou v prezencích verbatim včetně titulů a nekonzistentní
interpunkce. Normalizovat přes `jNameKey()` (`assets/helpers.js`) —
odstraní tituly i diakritiku a porovnává jen „jméno příjmení". Stejnou
funkci používá výpis jednání pro dohledání fotek.

- Napříč 39 zasedáními ZM je 34 unikátních jmen a normalizace u nich
  nespojila dvě různé podoby téhož jména (ověřeno 9. 9. 2026). U Rady to
  ale nestačí — viz dvě pasti níže.
- **Nezlomitelná mezera.** Rada 12/2021 a 13/2021 nesou
  `Mgr. Blanka Kozáková` s U+00A0 místo obyčejné mezery (verbatim
  zásada scraperu ji zachovává). `jNameKey()` v JS to ustojí, protože
  `\s` v regulárním výrazu nezlomitelnou mezeru pokrývá; v Pythonu
  `str.split()` taky, ale explicitní `replace(' ',' ')` je
  bezpečnější.
- **Poznámka přilepená ke jménu.** V Radě 9/2021 zdroj uvádí
  `Mgr. Alena Švejnohová - jednání na Krajském úřadě Stř. kraje` — důvod
  nepřítomnosti skončil uvnitř jména. Před porovnáním useknout všechno
  od prvního oddělovače `mezera-pomlčka-mezera`.
- **Minaříkovou a Dvořákovou žádná normalizace nespojí.** Tuhle dvojici
  spárovat ručně přes `lide/people.json` (záznam `dvorakovai`, který
  změnu příjmení popisuje v `bio`). Ve výstupu psát novější tvar jména.
- `people.json` nepokrývá zastupitele období 2018–2022 (viz jeho
  `meta.note`) — u nich žádné `id` ani fotka nebude, jméno z prezence
  zůstane jediným identifikátorem.

## 6. Technické poznámky

- Velký `archive-*.json` se z připojené složky občas nedá číst přímo
  (`OSError: [Errno 35]`). Nejdřív `cp` do `/tmp`, pak pracovat s kopií.
- Archiv má **jinou strukturu** než `pecky-jednani.json`: orgán je
  `body_type_raw` (ne `type`), datum `date_iso` (ne `date`). Filtrovat
  zastupitelstvo podstringem `astupitel` v `body_type_raw`.

**Kam co patří (rozhodnuto 9. 9. 2026):**

- Sběr průběžné prezence z archivu obstarává
  `jednani/scripts/doplnit-prubeznou-prezenci.py` (spuštěn 9. 9. 2026,
  data jsou doplněná).
- Samotný propočet dělá `jednani/scripts/absence.py` → `jednani/absence.json`.
  Skript implementuje tenhle dokument, ne naopak: hranice období, ruční
  sloučení Minaříková/Dvořáková, vyřazení vadného záznamu Rady 27/2021
  i poznámky ke kratším mandátům jsou v něm jako pojmenované konstanty
  nahoře. **Při změně pravidel tady se mění i skript.**
- `absence.json` se nepřepočítává sám — po každém novém jednání skript
  spustit znovu.
- Jeho výstupem je **strojové JSON v `jednani/`**, ne rovnou HTML;
  stránku z něj vykreslí `content/jednani.html` stejně, jako to dělá
  s `pecky-jednani.json`.
- JSON drží Radu a Zastupitelstvo jako oddělené větve a uvnitř nich
  oddělená volební období — struktura kopíruje členění z §4, ať se
  nesčítá, co se sčítat nemá.
- Do JSON patří i `meta` s datem propočtu, rozsahem dat (do kdy jsou
  jednání započtená) a rozsahem opravy o průběžnou prezenci — ta dnes
  končí dřív než data sama (§3).

## 7. Ověření před odevzdáním

- Namátkou u 3–5 osob dohledat uvedená čísla přímo v zápisech na
  `/verejne/<uuid>/zapis/`.
- Zkontrolovat součty oběma směry: součet absencí přes osoby se musí
  rovnat součtu `total − present` přes jednání.
- Ověřit, že poslední jednání v datech je opravdu poslední zveřejněné
  (viz `automation-kontrola-usneseni-cz.md`) — jinak statistika mlčky
  končí dřív, než čtenář čeká.
- Zkontrolovat, že žádná osoba nemá jmenovatel větší než počet jednání
  jejího mandátu.

## 8. Zásady výstupu

Platí obecné konvence webu (kořenový `CLAUDE.md`): žádná vymyšlená data,
každý údaj dohledatelný ve zdroji, mezery se přiznávají.

Absence je **popisný údaj, ne hodnocení**. Zápis neuvádí důvody, takže
z čísel nejde odvodit, kdo bere mandát vážně — a text to nesmí naznačovat.
Nutné výhrady, které patří přímo k tabulce, ne do poznámky pod čarou:
úvodní prezence není účast na celém jednání (§3), část chybějících
později dorazila a část přítomných odešla dřív, a omluvená absence se od
neomluvené liší jen tím, jak ji zapsal zapisovatel.

Nikdy nepublikovat samotné číslo z úvodní prezence. U konkrétních lidí
znamená skoro dvojnásobek skutečné absence — u Ing. Petra Dürra 59 %
místo 31 % — a je to rozdíl, který se opravou později už nedožene.
Zdrojová data tuhle opravu od 9. 9. 2026 umožňují (§3), takže není důvod
sáhnout po nekorigovaném čísle.

## Rozhodnutí (9. 9. 2026)

- **Rada a Zastupitelstvo se počítají zvlášť** a zvlášť se i zveřejní;
  nesčítat je do jednoho čísla za osobu.
- **Nespojovat s `INSTRUKCE-analyza-hlasovani.md`.** Docházka a hlasování
  zůstávají oddělené postupy i oddělené výstupy — smíchat „jak hlasuje"
  s „jak často chybí" do jednoho hodnocení osoby není záměr.
- Skript patří do `jednani/scripts/`, jeho výstupem je JSON v `jednani/`
  (podrobnosti v §6).

## Otevřené otázky

- Kde se to na webu zobrazí: sekce Jednání (u jednání), nebo Lidé
  (u osoby)? Případně obojí — tabulka v Jednáních a jeden řádek v profilu
  zastupitele.
- **Kam patří odkaz na `/jednani/absence.html`.** Stránka existuje, ale
  nevede na ni nic. Na výběr: sekce Jednání (u výpisu jednání), Lidé
  (u profilu osoby), nebo obojí. Až se to rozhodne, odkaz doplnit
  a v `scripts/build.py` přesunout položku z `EXTRA_PAGES` do `MANIFEST`
  (tím zmizí `noindex` a stránka se dostane do sitemapy).
- Provázat jména v tabulce s profily v sekci Lidé (přes `jNameKey()`,
  stejně jako to dělá výpis jednání u fotek).
- Zobrazit průběžnou prezenci i ve výpisu jednání. Řádek s avatary pořád
  ukazuje jen stav ze zahájení, takže kdo dorazil později, visí mezi
  nepřítomnými — data pro odlišení už v `attendance.changes` jsou.
- Zveřejňovat období 2018–2022? Data začínají až 16. 6. 2021 (ZM)
  a 12. 4. 2021 (Rada), takže to není celé období. Stránka to teď přiznává
  calloutem pod tabulkou; druhá možnost je starší období vypustit.
