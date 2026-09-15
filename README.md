# pecky.online

Neoficiální, nezávislý občanský projekt zpřehledňující veřejně dostupné informace
o samosprávě města Pečky (okres Kolín, Středočeský kraj).

## Obsah složky

- `CHANGELOG.md` — historie kontrol, ověřování zdrojů a změn obsahu
  jednotlivých sekcí, nejnovější záznamy nahoře.
- `TROUBLESHOOTING.md` — známé bugy a obejití konkrétního provozního
  prostředí (sandbox, mounty, `preview_start`), odděleně od trvalých
  konvencí k datům v `CLAUDE.md`.
- **Vícestránkový statický web** (od migrace 30. 8. 2026 — viz
  `ARCHITEKTURA-MIGRACE.md`), bez runtime frameworku, bez závislostí
  kromě Google Fonts přes CDN. `content/<sekce>.html` (jen obsah dané
  sekce) + sdílené `templates/page.html`, `assets/nav.html`,
  `assets/footer.html`, `assets/styles.css`, `assets/common.js`,
  `assets/helpers.js` se skládají přes `scripts/build.py` do 15
  samostatných veřejných stránek (`index.html` na kořeni = Domů,
  `jednani/index.html`, `noviny/index.html`, `volby/2018/index.html`
  atd.) — needit vygenerované stránky přímo, vždy přes odpovídající
  `content/*.html` + `scripts/build.py`. Repo zatím nemá vlastní doménu
  (viz ARCHITEKTURA-MIGRACE.md), takže odkazy/assety počítají s GitHub
  Pages subcestou `/pecky.online/` (`SITE_BASE_PATH` ve `scripts/build.py`)
  — pro místní test proto místo `python3 -m http.server` spustit
  `python3 scripts/serve.py` (napodobí tu samou subcestu) a otevřít
  `http://localhost:8000/pecky.online/`. Několik sekcí (Jednání, Pečecké
  noviny, Lidé) si navíc data načítá přes `fetch()`, takže i bez ohledu
  na subcestu je lokální server nutný — otevření vygenerovaných stránek
  přímo ze souboru (`file://`) fetch v některých prohlížečích zablokuje.
- `jednani/` — vše k sekci „Jednání": `pecky-jednani.json` (odlehčený
  index pro fulltextové hledání na webu), `archive-2026-08-04.json`
  (kompletní datový snímek se všemi detaily vč. jmenovitých hlasování),
  `README.md`/`SPEC.md`/`automation-kontrola-usneseni-cz.md`/
  `automation-katastr-parcely.md` (zadání, rozhodnutí a postup průběžné
  aktualizace), `Data/{datum}/` (lokální archiv PDF zápisů a
  pozvánek — kvůli velikosti je v `.gitignore`, do repa se nenahrává)
  a `scripts/` (pomocné skripty, vč. `update-pozemky.py`).
- `noviny/` — vše k sekci „Pečecké noviny": archiv PDF, obálky,
  fulltextový index a nástroje (`download.py`, `render_pages.py`).
  Viz `noviny/README.md`.
- `volby/` — rozcestník komunálních voleb (`/volby/`) a vše k volebním
  ročníkům, jedna podsložka na ročník (`2018/`, `2022/`, `2026/`) s vlastním
  `README.md`. Součástí jsou i
  obrázky ročníku: skeny volební inzerce (`volebni-programy-2018/`,
  `volebni-programy-2022/`) a portréty zastupitelů zvolených 2022
  (`2022/zastupitele/`, používá je i panel Lidé).
- `img/` — jen celowebové obrázky, které nepatří žádné sekci:
  `img/favicons/` (ikony zdrojů) a `img/peckybot/`. Obrázky vázané na
  konkrétní sekci patří do složky té sekce.
- `zakazky/` — vše k sekci „Zakázky": `pecky-zakazky-ids.json`
  (kontrolní snímek ID zakázek pro týdenní diff, na webu se nezobrazuje)
  a `README.md` s pracovním postupem. Viz `zakazky/README.md`.
- Každá další sekce webu má vlastní složku `<sekce>/` s `README.md`
  (podrobnosti a datové soubory tam, kde nějaké má, vedle vygenerovaného
  `index.html`); u sekcí bez vlastních dat obsahuje složka jen krátký
  `README.md` + `index.html`. Přehled a odkazy viz kořenový `CLAUDE.md`
  → „Dokumentace jednotlivých sekcí".

## Zdroje dat

- Základní fakta o městě: Wikipedie, oficiální web města (pecky.cz)
- Výsledky komunálních voleb 2022: Seznam Zprávy, Novinky.cz
- Jmenný seznam zastupitelstva (21/21 členů): pecky.cz — Složení ZM
- Složení rady města: pecky.cz, web ODS Pečky
- Smlouvy: Hlídač státu (konektor), IČO 00239607 — statický výřez, ne živá data
- Zakázky: Hlídač veřejných zakázek (veřejné vyhledávání, ne konektor), IČO 00239607 — statický výřez, ne živá data
- Pokladna (rozpočet a hospodaření): Monitor Státní pokladny (MF ČR), IČO 00239607 —
  vývoj příjmů/výdajů/salda 2023–2026, struktura výdajů, dluhová služba; dotace
  přes Registr dotací (Hlídač státu, 148 nalezených záznamů)
- Pokladna → Bankovní účty: Návrh závěrečného účtu 2025 (pecky.cz), konkrétně příloha
  Zpráva o přezkoumání hospodaření (auditorská zpráva cituje bankovní výpisy — 9 účtů
  u 5 bank) a přílohy Rekapitulace/Fondy (souhrnné zůstatky)
- Plán: Strategický plán rozvoje města Pečky 2016–2026 — souhrn (pecky.cz, PDF) —
  718 dílčích aktivit ve 4 prioritních oblastech, 360,8 mil. Kč celkem
- Pečecké noviny: pecky.cz — kompletní archiv PDF zpravodaje (68 vydání, 2020–2026)
- Jednání a usnesení: jednorázový strojově čitelný export webu
  mesto-pecky.usneseni.cz z 4. 8. 2026 — 281 jednání (243 Rada, 38
  Zastupitelstvo, 2021–2026), 2 731 usnesení. Kompletní snímek se všemi detaily
  (vč. jmenovitých hlasování a plných zápisů) je v
  `jednani/archive-2026-08-04.json`; `jednani/pecky-jednani.json`
  je z něj odvozený odlehčený index pro hledání na webu. Viz
  `jednani/SPEC.md` pro popis původního exportu a
  `jednani/automation-kontrola-usneseni-cz.md` pro aktuální postup
  průběžného doplňování.

## Barevná paleta uskupení

Každé politické uskupení má na celém webu jednu pevně přiřazenou barvu — používá se
konzistentně u kartiček lidí, kartiček volebních programů, sloupcového grafu mandátů
i barevných teček (swatch) v tabulkách. Uskupení, které kandiduje opakovaně, si barvu
drží i při změně názvu.

**Tabulka barev se přesunula do [`volby/README.md`](volby/README.md)
→ „Barevná paleta uskupení"** — je to pravidlo nejtěsněji svázané s volebními
panely, tak žije u nich. Najdeš tam CSS třídy `.person-card.party-*`, hex hodnoty,
ročníky a soupis nedodělků v paletě.

Pravidlo zůstává: při přidávání nového místa na webu, kde se zobrazuje uskupení
nebo jeho člen (nová kartička, graf, tabulka…), použij existující barvu z té
tabulky místo vymýšlení nové.

## Metodika ověřování (POVINNÉ)

Než o čemkoli prohlásíš, že to „v datech není“ nebo že se to „nestalo“, prověř to
**vždy ve všech zdrojích a v jejich plné podobě**. Zkratky vedly už k prokazatelně
chybným závěrům.

1. **Vždy `jednani/archive-2026-08-04.json`, ne `jednani/pecky-jednani.json`.**
   Druhý jmenovaný je odlehčený index (jen názvy a texty usnesení). Plný archiv
   obsahuje kompletní zápisy včetně diskuzí, důvodových zpráv a bodů programu —
   řádově víc textu. Pozn.: plný archiv nelze číst přes `mcp__workspace__bash`
   (mount hlásí „Resource deadlock avoided“) — použij nástroje Grep/Read, které
   běží na hostu.
2. **U dotací a smluv nikdy nespoléhej na prvních N záznamů.** Hlídač státu
   defaultně vrací malý vzorek; při řazení `DateAddedDesc` vypadnou starší roky.
   Projdi všechny stránky, nebo cíleně hledej klíčovým slovem k danému projektu.
3. **Zkoušej víc názvových variant.** Projekty se v dokumentech jmenují jinak než
   v plánu („kabiny AFK“ vs. „fotbalové kabiny“, „revitalizace rybníka“ vs.
   „odbahnění“). Jeden neúspěšný dotaz neznamená, že věc neexistuje.
4. **Kontroluj časový rozsah zdroje.** Archiv usnesení začíná až 04/2021 — cokoli
   staršího v něm být nemůže. Dotace a Registr smluv sahají hlouběji, Pečecké
   noviny až do 2020.
5. **Křížově ověřuj mezi zdroji** (usnesení × dotace × smlouvy × zakázky ×
   noviny). Teprve shoda dvou nezávislých zdrojů je doklad.
6. **Pro obsah oficiálního webu města používej `pecky.as4u.cz`, ne `www.pecky.cz`.**
   Je to tentýž web bez bot-ochrany a bez JS renderování — čte se běžným
   `web_fetch`. Pozor, některé stránky jsou dlouhé a přetečou limit odpovědi;
   pak na uložený výstup použij Grep místo čtení celého souboru.

Konkrétní případ, kvůli kterému toto pravidlo vzniklo: rekonstrukce kabin AFK
(dotace NSA 4 753 860 Kč, 2023) a revitalizace rybníka Benešák (OPŽP 3 146 174 Kč,
2019) byly nejprve chybně označeny za nerealizované — kvůli hledání v odlehčeném
indexu, špatnému názvu projektu a vzorku pouhých 20 nejnovějších dotací.

## Známé mezery

- Tabulky smluv a zakázek jsou statický výřez z Hlídače státu, ne živě se obnovující
  data (chybí veřejné API volatelné přímo z prohlížeče).
- ~~Žádosti dle zákona 106/1999 Sb. nedohledány.~~ **VYŘEŠENO 6. 8. 2026** — zdroj
  nalezen na `pecky.as4u.cz` (výroční zprávy 2011–2024 + jednotlivé žádosti a
  odpovědi v PDF). Obsah zatím nevytěžen, na web nepromítnut.
- Srovnání plánu se skutečností (sekce Plán → Jak se plán plní?) je zatím hotové jen
  pro vybrané projekty. Zbytek ze 183 aktivit plánu nebyl proti plnému archivu
  a všem 148 dotacím systematicky prověřen — dokud se to nestane, netvrdit o nich,
  že se nerealizovaly.

## Stav sekcí

Rozcestník: kdy se u které sekce naposledy kontroloval zdroj a kdy se
naposledy změnil obsah. Řazeno od nejnověji změněné. Data jsou absolutní
datumy — stáří („před 6 dny") se dopočítává až při čtení, aby tabulka
nezastarala bez týdenního běhu. Restrukturalizace a refactory se sem
nezapisují, jen změny obsahu.

| Sekce | Režim | Kontrola | Změna | Co naposledy |
|---|---|---|---|---|
| [Pečecké noviny](noviny/README.md) | týdně | 14. 9. 2026 | 14. 9. 2026 | dávka 2012–2015 od uživatele (44 vydání, 161→205, 3140 stran celkem) — celý ročník jsou čisté naskenované obrázky bez textové vrstvy, fulltext proto pochází z OCR (Tesseract, čeština) pro všech 44 vydání, ne jen pro pár čísel jako dřív; listopad 2012 a srpen 2015 v dodané dávce chybí; fyzická velikost stránky 618×888 pt (třetí odlišná velikost v archivu vedle A4 a A3), obálky vygenerovány přes `-scale-to-x`; dřív (2. 9. 2026): dávka 2001/2005/2006 od uživatele (5 vydání, 156→161) — 2 vydání OCR (nečitelné dobové kódování fontů) |
| [Tělocvična](telocvicna/README.md) | týdně | 14. 9. 2026 | 14. 9. 2026 | v dávce Pečeckých novin 2012–2015 od uživatele dohledáno 6 nových řádků do tabulky „Historie projektu“ (2014–2016) — zápis RM v PN 4/2015 nezávisle potvrzuje rok i zpracovatele (Ateliér A11) z tvrzení A. Švejnohové o „dokumentaci z roku 2015“, ale ne konkrétní číslo 8,5 m ani „kolaudační“ charakter dokumentu; dřív (10. 9. 2026): zápis RM 32/2026 (7. 9.) — externí pracovník na sanace budov, rozpočtové opatření +10 mil. Kč (cash flow, ne vícenáklad), rozhodne ZM 16. 9.; dřív (4. 9. 2026): zápis RM 31/2026 — Dodatek č. 1 ke SoD schválen, cena díla +6,15 mil. Kč bez DPH na 211,5 mil. vč. DPH |
| [Jednání](jednani/README.md) | týdně | 14. 9. 2026 | 13. 9. 2026 | přibyla **Rada 33/2026 (14. 9. 2026)** zatím jen s Pozvánkou — 9bodový program vytažen z PDF pozvánky (mj. Smlouva o zřízení práva stavby – kolárna u ČD, změna termínu plnění UR-265-29/26, vyřazení nepotřebného DHM ZŠ); archiv má nově 289 jednání, počet usnesení beze změny (2 767); dřív (10. 9. 2026): Rada 32/2026 (7. 9.) doplněna o zápis a 12 usnesení (UR-282 až UR-293), vč. prezence, průběžných příchodů/odchodů a délek jednotlivých bodů; přibylo Zastupitelstvo 6/2026 (16. 9.) zatím jen s Pozvánkou a 23bodovým programem; přepočítána `jednani/absence.json`; dřív (9. 9. 2026): nová neprolinkovaná podstránka `/jednani/absence.html` — kolikrát který zastupitel a radní chyběl na jednání, zvlášť za zastupitelstvo a radu a zvlášť za volební období, opravené o pozdní příchody (odkaz zatím nikde, stránka má `noindex` a není v sitemapě); data generuje `jednani/scripts/absence.py` do `jednani/absence.json`; dřív (týž den): do datové sady doplněna průběžná prezence (`attendance.changes`) — příchody, odchody a distanční připojení během jednání, které scraper dosud zahazoval: 124 jednání, 218 událostí, zpětně z archivu skriptem `jednani/scripts/doplnit-prubeznou-prezenci.py`, 5 jednání novějších než archiv ověřeno ručně na usneseni.cz; bez toho vypadá pozdní příchod jako celodenní absence (u jednoho radního 59 % místo 31 %). Zatím jen v datech, v UI se nezobrazuje. Nový postup `jednani/INSTRUKCE-absence.md` (počítání absence zastupitelů) |
| [O webu](o-webu/README.md) | týdně | 13. 9. 2026 | 13. 9. 2026 | aktualizováno všech 15 sociálních sítí — počty sledujících se změnily u 7 účtů (Alena Švejnohová 946 → 955, Kulturní středisko 992 → 993, Městská knihovna 482 → 483, Pečky Pečákům 238 → 245, TJ Sokol 221 → 223, ODS a nezávislí 217 → 221, Pečky srdcem 73 → 78, Instagram streetpeopleofpecky 1 218 → 1 216), nová aktivita u 7 účtů (Město Pečky, NAŠE PEČKY, Alena Švejnohová, Kulturní středisko, Pečky NEXT FB, Pečky Pečákům, ODS a nezávislí, Pečky srdcem); u obou instagramových účtů opět jen počet sledujících — mezera v čtení data posledního příspěvku trvá; dřív (9. 9. 2026): aktualizováno všech 15 sociálních sítí — počty sledujících se změnily u 6 účtů (Alena Švejnohová 942 → 946, Městská knihovna 483 → 482, Pečky NEXT FB 291 → 306, ODS a nezávislí 213 → 217, Instagram Pečky NEXT 120 → 128, Pečky srdcem 72 → 73, FB skupina SPD 39 → 40 členů, Instagram streetpeopleofpecky 1 219 → 1 218), nová aktivita u 8 účtů (mj. Pečky Pečákům po třech měsících ticha, 5. 6. → 8. 9. 2026); u obou instagramových účtů opět jen počet sledujících — mezera v čtení data posledního příspěvku trvá |
| [Volby 2026](volby/2026/README.md) | týdně | 13. 9. 2026 | 13. 9. 2026 | aktualizovány počty sledujících a datumy poslední aktivity u 7 sociálních sítí uskupení v tabulce „Volební uskupení" (ODS a nezávislí 217 → 221, Pečky Pečákům 238 → 245, Pečky srdcem 73 → 78; nová aktivita u NAŠE PEČKY, Pečky NEXT FB, Pečky Pečákům, ODS a nezávislí, Pečky srdcem); na úřední desce pecky.cz přibyly dva volební dokumenty (svolání prvního zasedání OVK, školení k zásadám hlasování, oba 10. 9. 2026) — jsou procesní, na stránku nepromítnuty; dřív (9. 9. 2026): aktualizovány počty sledujících a datumy poslední aktivity u 7 sociálních sítí uskupení v tabulce „Volební uskupení" (ODS a nezávislí 213 → 217, Pečky NEXT FB 291 → 306, Instagram Pečky NEXT 120 → 128, Pečky srdcem 72 → 73, FB skupina SPD 39 → 40 členů; Pečky Pečákům po třech měsících ticha nový příspěvek 8. 9. 2026); dřív (týž den): u každého z pěti uskupení v tabulce „Volební uskupení" doplněn odkaz na jeho kompletní kandidátní listinu na volby.gov.cz (filtrováno na dané KL, ne obecný přehled); odstraněna dvojice `.stat-card` pod perexem (termín voleb + účast 2022 byly duplicitní s perexem a s grafem na `/volby/`), datum voleb místo toho tučně v samotném perexu; nad nadpisem přidán rozcestník ročníků (`{{VOLBY_ROCNIKY}}`, viz `volby/README.md`); dřív (8. 9. 2026): stránka přestavěna na podzáložky po vzoru Voleb 2018/2022 (dřív jedna plochá stránka) — nová záložka „Předvolební sliby" s volebními programy dvou z pěti uskupení (Pečky srdcem, Sdružení nezávislých kandidátů PEČKY PEČÁKŮM), soubory doplnil uživatel do `volby/2026/volebni-programy-2026/`; zbylá tři uskupení v mezeře, doplní se stejně jako u Voleb 2022; z plakátu PEČKY PEČÁKŮM vystřiženo a jmenovitě přiřazeno 5 avatarů (Jedlička, Pečenka, Jedličková, Sedláček, Cihlářová) do `volby/2026/zastupitele/`, zapsáno i do `lide/people.json` |
| [Volby](volby/README.md) | odvozená | — | 9. 9. 2026 | odrážkový seznam ročníků nahrazen znovupoužitelnou komponentou „rozcestník ročníků" (`{{VOLBY_ROCNIKY}}`) — vystředěný řádek buttonů s plnou pergamenovou výplní, od nejnovějšího po nejstarší, první položka popisek „Volby:" (odkaz zpět na rozcestník, na `/volby/` samotném neklikací), aktivní ročník zvýrazněný plnou bordó výplní; stejná komponenta nově i nad nadpisem `/volby/2018/`, `/volby/2022/` a `/volby/2026/`; dřív (týž den): blok „Volební účast stoupá" bez rozbalovacího tlačítka (trvale viditelný), graf prohozen s vysvětlujícím odstavcem (teď nad ním), pod nadpis doplněna věta „K volebním urnám přichází pouze přibližně polovina oprávněných obyvatel." |
| [Volby 2018](volby/2018/README.md) | uzavřené | — | 9. 9. 2026 | nad nadpisem přidán rozcestník ročníků (`{{VOLBY_ROCNIKY}}`, viz `volby/README.md`) |
| [Volby 2022](volby/2022/README.md) | uzavřené | — | 9. 9. 2026 | nad nadpisem přidán rozcestník ročníků (`{{VOLBY_ROCNIKY}}`); blok „Volební účast stoupá" (SVG graf) přesunut ze záložky Rozbor na rozcestník `/volby/` — v panelu Volby 2022 už není, viz `volby/README.md` |
| [Smlouvy](smlouvy/README.md) | týdně | 13. 9. 2026 | 9. 9. 2026 | 2 nové smlouvy do tabulky „Nejnovější smlouvy": dar hydraulického vyprošťovacího zařízení WEBER HYDRAULIK SP 49 od HZS Středočeského kraje (7. 9. 2026, 642 510 Kč) a dotace Středočeského kraje ZŠ Pečky na bezplatné školní stravování 2026/2027 (31. 8. 2026, 298 960 Kč); souhrnná čísla ponechána beze změny — viz nedořešený úbytek záznamů u Hlídače z 30. 8.–2. 9. |
| [Lidé](lide/README.md) | na vyžádání | 8. 9. 2026 | 8. 9. 2026 | doplněny fotky (`photos[]`, rok 2026) pěti kandidátů PEČKY PEČÁKŮM vystřižené z volebního plakátu — Martin Jedlička, Milan Pečenka, Šárka Jedličková, Pavel Sedláček, Alena Cihlářová; sloučeny záznamy Ivety Minaříkové a Dvořákové (jedna osoba, změna příjmení), staré `id` zůstává jako alias; povolání převedeno na `occupations[]` s ročníkem, doplněn ročník 2022 u 21 zvolených (Poradna pro obce); srovnán `<title>` a popis stránky s novým nadpisem; nový nadpis „Lidé města Pečky" a přepsaný perex (popisuje, co na stránce je, ne výklad o samosprávě); doplněn Ing. František Pospíšil jako první polistopadový starosta (1990–2002, tři období); doplněno 16 zaměstnanců úřadu z organizační struktury na pecky.cz (skupina „Úřad města" ze 6 na 22), rozšířeno pravidlo §6/4 o řadové zaměstnance; doplněno povolání všech 105 kandidátů z kandidátních listin 2026 (`volby/2026/data-export.csv`), v detailu osoby vč. ročníku listiny; doplněny e-maily všech 21 zastupitelů a služební telefony vedení (kancelář i mobil) z webu města, v detailu osoby jako odkazy `tel:`; doplněn portrét Ing. Martina Jedličky z webu města (nová složka `lide/foto/` na fotky mimo volební materiály); odstraněn souhrnný callout „O fotografiích" (původ fotek zůstává v detailu osoby), upraven placeholder hledání; při filtru podle role se skupiny pojmenují podle něj („Starosta — nyní / dříve") místo zavádějícího „Ostatní členové zastupitelstva"; doplněna historie vedení města: Milan Urban starostou 2006–2018 (3 období), rada 2014–2018 a vedení 2018–2022 v čele se starostkou A. Švejnohovou (14 nových vazeb, 1 nová osoba); vedení rozděleno na „Úřad města" (6) a „Městské organizace" (7) — vlastní skupiny i filtry role (`vedeni-urad` / `vedeni-organizace`); zrušeny čipy filtru podle uskupení (filtr zůstává přes URL a klik na kartičce); dřívější skupina „Kandidáti bez mandátu" zrušena, kandidáti zůstávají v datech, ale nevypisují se |
| [Pozemky](pozemky/README.md) | odvozená | 10. 9. 2026 | 5. 9. 2026 | oprava odkazu „řešilo se na: Jednání…" u všech řádků — mířil na `href="#"` s JS handlerem, který se na samostatné stránce Pozemky nikdy nenačetl (pozůstatek jednostránkové architektury); teď skutečný odkaz `/jednani/#rada-YYYY-MM-DD` |
| [Plán](plan/README.md) | na vyžádání | 2. 9. 2026 | 2. 9. 2026 | řádek „Nová tělocvična a učebny ZŠ": stav → zastaveno, odkaz na novou sekci Tělocvična |
| [Domů](domu/README.md) | odvozená | — | 24. 8. 2026 | brand header |
| [Zakázky](zakazky/README.md) | týdně | 13. 9. 2026 | 6. 8. 2026 | 1 nová zakázka |
| [Pokladna](pokladna/README.md) | na vyžádání | 6. 8. 2026 | 6. 8. 2026 | blok Bankovní účty |

Režimy: **týdně** = má zdroj, který kontroluje týdenní rutina (neděle
večer) · **hlídat** =
čeká se na událost · **na vyžádání** = kontroluje se, jen když
o to někdo požádá · **odvozená** = nemá vlastní externí zdroj, mění se
s jinou sekcí · **uzavřené** = historický ročník, nový obsah se nečeká.
Pomlčka ve sloupci Kontrola znamená „nebylo co kontrolovat", ne opomenutí.

Tabulku aktualizuje každá instrukce, která sáhne na obsah některé sekce —
automatická týdenní rutina i ručně vyvolaná: přepíše řádek dotčené sekce
(datum kontroly, u reálné změny i datum změny a sloupec „Co naposledy")
a přesune ho na správné místo v řazení. Ostatní řádky nechá být.

`?` u data znamená nedoložený odhad — nahradit, až se zjistí přesné datum.

## Poslední aktualizace

Historie kontrol a změn obsahu sekcí je v samostatném souboru
[`CHANGELOG.md`](CHANGELOG.md) (nejnovější záznamy nahoře).

## Publikování na GitHub Pages

1. Vytvořte nový repozitář (např. `pecky-online`)
2. Před nahráním spusťte `python3 scripts/build.py` — vygeneruje
   `index.html`, `jednani/`, `noviny/`, `volby/2018/` atd. ze
   `content/*.html`. Nahrajte celý výsledek (vygenerované stránky,
   `assets/`, složky sekcí jako `jednani/`, `noviny/`,
   `zakazky/` a další) do kořene repozitáře
3. Settings → Pages → source: `main` branch, root
4. Web poběží na `https://<vaše-uživatelské-jméno>.github.io/pecky-online/`
