# pecky.online

Neoficiální, nezávislý občanský projekt zpřehledňující veřejně dostupné informace
o samosprávě města Pečky (okres Kolín, Středočeský kraj).

## Obsah složky

- **Vícestránkový statický web** (od migrace 30. 8. 2026 — viz
  `ARCHITEKTURA-MIGRACE.md`), bez runtime frameworku, bez závislostí
  kromě Google Fonts přes CDN. `content/<sekce>.html` (jen obsah dané
  sekce) + sdílené `templates/page.html`, `assets/nav.html`,
  `assets/footer.html`, `assets/styles.css`, `assets/common.js`,
  `assets/helpers.js` se skládají přes `scripts/build.py` do 16
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
| [Jednání](jednani/README.md) | týdně | 19. 9. 2026 | 19. 9. 2026 | přepočet `jednani/scripts/absence.py` doplněn jako vlastní krok 8c do `automation-kontrola-usneseni-cz.md` (POVINNÉ při každém běhu, stejně jako krok 8b u Kalendáře), zadal uživatel po dotazu, kdy a jak se docházka přepočítává — dřív to v týdenním postupu nebylo jako samostatný krok a přepočet se snadno zapomněl (viz `jednani/README.md` → „Absence na jednáních"); dřív (týž den): nad nadpis „Zápisy z jednání" doplněn odstavec s odkazem na Docházku („Kontrola docházky: Jak vás zastupitelé zastupují", `content/jednani.html`) — `/jednani/absence.html` je tak poprvé odněkud odkázaná; `noindex` z ní proto odebrán a stránka zařazena do `sitemap.xml` (šesté pole `lastmod` u záznamu `absence` v `EXTRA_PAGES`, `scripts/build.py`); zadal uživatel; dřív (týž den): stránka Absence (`/jednani/absence.html`) přepracovaná na „Docházku", zadal uživatel: titulek „Jak vás zastupitelé zastupují" (dřív „Kdo chybí na jednáních"), tabulka teď ukazuje jen aktuální volební období 2022–2026 (starší 2018–2022 zápisy na usneseni.cz pokrývají jen zčásti, srovnání by zkreslilo — v datech `absence.json` dál je, jen se nevykresluje), sloupce zjednodušené na Jméno/Docházka/Mandát (tvar „X / Y")/Poznámka — dřívější „chyběl při zahájení", „dorazil později" a „odešel dřív" jsou teď bodový seznam v poznámce místo vlastních sloupců; vysvětlující callout přesunutý z hlavního těla do záložky „Jak se to počítá"; datový model (`absence.py`/`absence.json`) beze změny, jde jen o přepočet na frontendu; následná úprava (týž den, zadal uživatel): záložky prohozené — Rada je teď první a výchozí, Zastupitelstvo druhé; tabulka řazená od nejmenší docházky místo od nejkratšího mandátu (`blok.radky.slice().sort((a,b)=>b.podil-a.podil)` v `content/absence.html`, mandát zůstal jen jako vedlejší sloupec); další úprava (týž den, zadal uživatel): perex zkrácen na jednu větu s odkazem na jednání („Docházka zastupitelů a radních na jednání. Zdrojem dat jsou zápisy z jednání.", druhý odstavec zahozen), popisný řádek nad tabulkou u obou záložek zrušen, nadpis „2022–2026 — 175 jednání" nahrazen větou „Rada města se ve volebním období 2022–2026 sešla 175 krát." (`sešla`/`sešlo` podle rodu orgánu); další úprava (týž den, zadal uživatel): poznámka má novou první položku „Přítomen"/„Přítomna": N" (reálná docházka, `mandat − nebyl`, vždy zobrazená) — gramaticky správně podle rodu osoby díky novému poli `gender` v `lide/people.json` a sdílené funkci `pcGendered()` v `assets/helpers.js` (implementace i u Lidé, viz jeho vlastní řádek níže); dřív (týž den): u jména v tabulce Absence teď je avatar a klik na jméno rozbalí stejnou vizitku osoby (bio, povolání, kontakt, timeline funkcí), jakou zobrazuje detail osoby v sekci Lidé — spárováno fuzzy přes jméno s `lide/people.json`; zadal uživatel. Vykreslení vizitky se přitom vytáhlo z `content/lide.html` do sdílené komponenty `pcAvatarHtml`/`pcDetailHtml`/`pcBuildTimeline` v `assets/helpers.js` (`lide/README.md` → „Vizitka osoby je sdílená komponenta"), Lidé na ni teď jen deleguje — čistý refaktor beze změny chování detailu osoby; dřív (18. 9. 2026): tři úpravy zobrazení zadané uživatelem: text „zápis zatím není k dispozici" na sbaleném řádku teď vypisuje bordovou barvou (`.no-minutes-warning`, viz `jednani/README.md` → „Upozornění na chybějící zápis"); odkaz „Pozvánka PDF" v rozbaleném řádku se zobrazuje jen u jednání, které ještě neproběhlo (u proběhlého ztrácí smysl, nahradí ho zápis a usnesení); doplněna podpora živého přenosu naplánovaného zastupitelstva — najde-li kontrola YouTube playlistu odkaz na nadcházející přenos, zapíše ho jako `links.livestream` a web ho ukáže na sbaleném řádku jako „Živé vysílání od HH:MM" a tlačítkem „Video" v rozbaleném řádku; nový krok 6b v `jednani/automation-kontrola-usneseni-cz.md` pro budoucí kontroly; dřív (16. 9. 2026): doplněn odkaz na video (YouTube) k dnešnímu **Zastupitelstvu 6/2026 (16. 9. 2026)** — živý přenos vyšel na kanálu města do hodiny od zasedání, ověřeno shodou čísla i data v popisku; zápis a usnesení zatím nejsou zveřejněné; dřív (13. 9. 2026): přibyla **Rada 33/2026 (14. 9. 2026)** zatím jen s Pozvánkou — 9bodový program vytažen z PDF pozvánky (mj. Smlouva o zřízení práva stavby – kolárna u ČD, změna termínu plnění UR-265-29/26, vyřazení nepotřebného DHM ZŠ); archiv má nově 289 jednání, počet usnesení beze změny (2 767); dřív (10. 9. 2026): Rada 32/2026 (7. 9.) doplněna o zápis a 12 usnesení (UR-282 až UR-293), vč. prezence, průběžných příchodů/odchodů a délek jednotlivých bodů; přibylo Zastupitelstvo 6/2026 (16. 9.) zatím jen s Pozvánkou a 23bodovým programem; přepočítána `jednani/absence.json`; dřív (9. 9. 2026): nová neprolinkovaná podstránka `/jednani/absence.html` — kolikrát který zastupitel a radní chyběl na jednání, zvlášť za zastupitelstvo a radu a zvlášť za volební období, opravené o pozdní příchody (odkaz zatím nikde, stránka má `noindex` a není v sitemapě); data generuje `jednani/scripts/absence.py` do `jednani/absence.json`; dřív (týž den): do datové sady doplněna průběžná prezence (`attendance.changes`) — příchody, odchody a distanční připojení během jednání, které scraper dosud zahazoval: 124 jednání, 218 událostí, zpětně z archivu skriptem `jednani/scripts/doplnit-prubeznou-prezenci.py`, 5 jednání novějších než archiv ověřeno ručně na usneseni.cz; bez toho vypadá pozdní příchod jako celodenní absence (u jednoho radního 59 % místo 31 %). Zatím jen v datech, v UI se nezobrazuje. Nový postup `jednani/INSTRUKCE-absence.md` (počítání absence zastupitelů) |
| [Lidé](lide/README.md) | na vyžádání | 19. 9. 2026 | 19. 9. 2026 | doplněno povinné pole `gender` (`"m"`/`"f"`) ke všem 258 osobám v `people.json`, zadal uživatel — podklad pro gramaticky správné skloňování textů o konkrétní osobě (přítomen/přítomna, zvolen/zvolena…) napříč webem, první využití v `jednani/absence.html` (viz jeho vlastní řádek výš); rod odvozen z křestního jména (105 unikátních jmen ručně roztříděno, zkřížově ověřeno proti příponě příjmení `-ová`/`-á` — 5 neshod byly nesklonná/cizí příjmení, ne chyba v rodu), ne z příjmení, které u cizích/nesklonných tvarů selhává; sdílená vykreslovací funkce `pcGendered()` v `assets/helpers.js`; `lide/validate.mjs` teď vyžaduje `gender` u každé osoby; podrobnosti `lide/README.md` → „České skloňování osob (gender)"; dřív (8. 9. 2026): doplněny fotky (`photos[]`, rok 2026) pěti kandidátů PEČKY PEČÁKŮM vystřižené z volebního plakátu — Martin Jedlička, Milan Pečenka, Šárka Jedličková, Pavel Sedláček, Alena Cihlářová; sloučeny záznamy Ivety Minaříkové a Dvořákové (jedna osoba, změna příjmení), staré `id` zůstává jako alias; povolání převedeno na `occupations[]` s ročníkem, doplněn ročník 2022 u 21 zvolených (Poradna pro obce); srovnán `<title>` a popis stránky s novým nadpisem; nový nadpis „Lidé města Pečky" a přepsaný perex (popisuje, co na stránce je, ne výklad o samosprávě); doplněn Ing. František Pospíšil jako první polistopadový starosta (1990–2002, tři období); doplněno 16 zaměstnanců úřadu z organizační struktury na pecky.cz (skupina „Úřad města" ze 6 na 22), rozšířeno pravidlo §6/4 o řadové zaměstnance; doplněno povolání všech 105 kandidátů z kandidátních listin 2026 (`volby/2026/data-export.csv`), v detailu osoby vč. ročníku listiny; doplněny e-maily všech 21 zastupitelů a služební telefony vedení (kancelář i mobil) z webu města, v detailu osoby jako odkazy `tel:`; doplněn portrét Ing. Martina Jedličky z webu města (nová složka `lide/foto/` na fotky mimo volební materiály); odstraněn souhrnný callout „O fotografiích" (původ fotek zůstává v detailu osoby), upraven placeholder hledání; při filtru podle role se skupiny pojmenují podle něj („Starosta — nyní / dříve") místo zavádějícího „Ostatní členové zastupitelstva"; doplněna historie vedení města: Milan Urban starostou 2006–2018 (3 období), rada 2014–2018 a vedení 2018–2022 v čele se starostkou A. Švejnohovou (14 nových vazeb, 1 nová osoba); vedení rozděleno na „Úřad města" (6) a „Městské organizace" (7) — vlastní skupiny i filtry role (`vedeni-urad` / `vedeni-organizace`); zrušeny čipy filtru podle uskupení (filtr zůstává přes URL a klik na kartičce); dřívější skupina „Kandidáti bez mandátu" zrušena, kandidáti zůstávají v datech, ale nevypisují se |
| [O webu](o-webu/README.md) | týdně | 19. 9. 2026 | 19. 9. 2026 | týdenní kontrola všech 15 sociálních sítí (Claude in Chrome) — počty sledujících se změnily u 5 účtů (Pečky NEXT FB 307 → 308, Pečky Pečákům 245 → 246, ODS a nezávislí 228 → 232, Instagram Pečky NEXT 130 → 131, Pečky srdcem 86 → 87); nová aktivita u 8 účtů (Město Pečky 18. 9., NAŠE PEČKY 19. 9., Alena Švejnohová 18. 9., Pečky NEXT FB 19. 9., ODS a nezávislí 18. 9., TJ Sokol Pečky 17. 9., YouTube Město Pečky 17. 9. — záznam ZM 6/2026 konečně zveřejněn na kanálu, FB skupina Lidé pro Pečky s podporou SPD 19. 9.); **oprava chybných dat z běhu 16. 9. 2026** — ten měl u 5 účtů (Pečky-Virtuálně, Kulturní středisko, Městská knihovna, Pečky Pečákům, Pečky srdcem) zapsané datum posledního příspěvku shodné s datem kontroly napříč prakticky všemi facebookovými účty najednou, což při ověření `creation_time` skriptem i vizuálně na stránce neodpovídalo realitě — skutečná poslední vlastní aktivita byla starší (4.–14. 9. 2026), teď opravena na ověřené datum; u obou instagramových účtů datum beze změny (známé omezení — `img[alt]` datum nečte od 2. 9. 2026); na úřední desce pecky.cz nic nového k volbám od 10. 9. 2026; dřív (18. 9. 2026): doplněn odkaz do quicklinks na Public Spending Data — neoficiální agregátor obecních financí s delší časovou řadou (2010–2025) než dosavadní zdroj v sekci Pokladna; doplněna i konkrétní URL na souhrnný rozpočet Monitoru státní pokladny (rozpočet/souhrnny?obdobi=2512&rad=t) k existujícímu záznamu v `sources.json` — oba zadal uživatel; dřív (16. 9. 2026): týdenní kontrola všech 15 sociálních sítí — počty sledujících se změnily u 5 účtů (ODS a nezávislí 224 → 228, TJ Sokol Pečky 223 → 224, Instagram Pečky NEXT 129 → 130, Instagram streetpeopleofpecky 1 215 → 1 216, YouTube Město Pečky 93 → 95 odběratelů); nová aktivita dnes u 12 z 15 účtů, mj. **Pečky-Virtuálně po 12 dnech ticha** (4. 9. → 16. 9., dárek městu k výročí — historická mapa) a pokračující kampaňová aktivita Pečky Pečákům (představování kandidátů); **oprava mezery u YouTube** — datum posledního videa se dřív četlo ze záložky „Videa“ kanálu (zavádějící, viz `o-webu/automation-socialni-site.md`), teď z domovské stránky/playlistu: aktuální je dnešní živý přenos ZM 6/2026, ne 27. 8.; na úřední desce pecky.cz nic nového k volbám od 10. 9. 2026; dřív (15. 9. 2026): počty sledujících u 6 účtů, nová aktivita u 7 účtů vč. FB skupiny Lidé pro Pečky po 18 dnech ticha |
| [Kalendář](kalendar/README.md) | na vyžádání | 19. 9. 2026 | 19. 9. 2026 | mřížka teď vykresluje skutečné události místo prázdné kostry — nový generátor `kalendar/scripts/update-kalendar.py` sesbírá 289 jednání rady a zastupitelstva z `jednani/pecky-jednani.json` do společného schématu (`kalendar/udalosti.json`) a zároveň vyrobí `kalendar/kalendar.ics` (RFC 5545, ke stažení/přihlášení do Google/Apple/Outlook kalendáře); `content/kalendar.html` teď natahuje data přes `fetch()` a vykresluje měsíc v prohlížeči (navigace měsícem, filtr Vše/Zastupitelstvo/Rada, barevné odznaky v buňkách) místo dřívější statické zářijové mřížky; dřív (týž den): nová sekce založena — kostra stránky, zatím jen prázdná mřížka bez událostí |
| [Volby 2026](volby/2026/README.md) | týdně | 19. 9. 2026 | 19. 9. 2026 | promítnuty aktualizované počty sledujících a datumy poslední aktivity u překrývajících se 7 sociálních sítí uskupení (zdroj: týdenní kontrola v `o-webu/README.md`, 19. 9. 2026) — ODS a nezávislí 228 → 232 (nová aktivita 18. 9.), Pečky Pečákům 245 → 246 (14. 9., oprava chybného data ze 16. 9.), Pečky NEXT FB 307 → 308 (nová aktivita 19. 9.), Instagram Pečky NEXT 130 → 131 (14. 9., beze změny data), Pečky srdcem 86 → 87 (13. 9., oprava chybného data ze 16. 9.); NAŠE PEČKY a FB skupina Lidé pro Pečky s podporou SPD beze změny počtu, jen nová aktivita (19. 9.); dřív (17. 9. 2026): do sloupečku „Poznámka" u každého uskupení doplněn rozbor politické zkušenosti kandidátů — kolik z 21 obhajuje aktuální funkci (starosta, místostarostové, radní, zastupitelé), kolik už dřív ve vedení města bylo (Alena Švejnohová starostkou 2018–2022, František Pospíšil starostou 1990–2002, Milan Urban starostou 2006–2018, Petr Zedník radním 2014–2018) a kolik kandiduje poprvé (44 ze 105 celkem, nejvíc u Lidí pro Pečky a Velké Chvalovice s SPD); data spárována z `lide/affiliations.json` (105 kandidátů 2026 už evidováno se svou dřívější historií funkcí); zrušen blok „Kde se volí" (volební okrsky) a callout „Aktuální stav" — oba dublovaly informace už jinde na stránce nebo přestaly být aktuální; dřív (16. 9. 2026): doplněny volební programy zbylých tří uskupení do záložky Předvolební sliby — NAŠE PEČKY A PEČKY NEXT a ODS a nezávislí Pečky vystřiženy z Pečeckých novin 9/2026 (str. 8 a 9), Lidé pro Pečky a Velké Chvalovice s podporou SPD ze str. 10; u NAŠE PEČKY navíc podkladové PDF s kompletním programem a portréty všech 21 kandidátů (`nase-pecky-noviny.pdf`, dodal uživatel); program teď dohledaný u všech pěti uskupení; dřív (týž den): aktualizovány počty sledujících a datumy poslední aktivity u překrývajících se 7 sociálních sítí uskupení v tabulce „Volební uskupení" (ODS a nezávislí 224 → 228, Instagram Pečky NEXT 129 → 130; nová aktivita dnes u 5 z 7 odkazů); na úřední desce pecky.cz nic nového k volbám od 10. 9. 2026 |
| [Pečecké noviny](noviny/README.md) | týdně | 16. 9. 2026 | 16. 9. 2026 | vydání 9/2026 doplněno do archivu (206. vydání celkem, 3160 stran) — nalezeno přímo na archivním rozcestníku pecky.cz (fungoval napoprvé, fallback nebyl potřeba); opraveny 2 zastaralé počty v poznámkách pod archivem (69 vydání 2020–2026, dřív 68; 137 vydání 2008–2019, dřív 132 — nesouviselo s dávkou 2012–2015, jen se to při jejím zapracování nepřepsalo); dřív (14. 9. 2026): dávka 2012–2015 od uživatele (44 vydání, 161→205, 3140 stran celkem) — celý ročník jsou čisté naskenované obrázky bez textové vrstvy, fulltext proto pochází z OCR (Tesseract, čeština) pro všech 44 vydání, ne jen pro pár čísel jako dřív; listopad 2012 a srpen 2015 v dodané dávce chybí; fyzická velikost stránky 618×888 pt (třetí odlišná velikost v archivu vedle A4 a A3), obálky vygenerovány přes `-scale-to-x` |
| [Tělocvična](telocvicna/README.md) | týdně | 16. 9. 2026 | 14. 9. 2026 | zkontrolováno, beze změny — Zastupitelstvo 6/2026 (dnes) má bod „Informace o stavební akci" na programu, ale zápis zatím nevyšel (jen Pozvánka), přesně jak `telocvicna/README.md` → „Co hlídat dál" očekávalo; dřív (14. 9. 2026): v dávce Pečeckých novin 2012–2015 od uživatele dohledáno 6 nových řádků do tabulky „Historie projektu“ (2014–2016) — zápis RM v PN 4/2015 nezávisle potvrzuje rok i zpracovatele (Ateliér A11) z tvrzení A. Švejnohové o „dokumentaci z roku 2015“, ale ne konkrétní číslo 8,5 m ani „kolaudační“ charakter dokumentu; dřív (10. 9. 2026): zápis RM 32/2026 (7. 9.) — externí pracovník na sanace budov, rozpočtové opatření +10 mil. Kč (cash flow, ne vícenáklad), rozhodne ZM 16. 9.; dřív (4. 9. 2026): zápis RM 31/2026 — Dodatek č. 1 ke SoD schválen, cena díla +6,15 mil. Kč bez DPH na 211,5 mil. vč. DPH |
| [Volby](volby/README.md) | odvozená | — | 9. 9. 2026 | odrážkový seznam ročníků nahrazen znovupoužitelnou komponentou „rozcestník ročníků" (`{{VOLBY_ROCNIKY}}`) — vystředěný řádek buttonů s plnou pergamenovou výplní, od nejnovějšího po nejstarší, první položka popisek „Volby:" (odkaz zpět na rozcestník, na `/volby/` samotném neklikací), aktivní ročník zvýrazněný plnou bordó výplní; stejná komponenta nově i nad nadpisem `/volby/2018/`, `/volby/2022/` a `/volby/2026/`; dřív (týž den): blok „Volební účast stoupá" bez rozbalovacího tlačítka (trvale viditelný), graf prohozen s vysvětlujícím odstavcem (teď nad ním), pod nadpis doplněna věta „K volebním urnám přichází pouze přibližně polovina oprávněných obyvatel." |
| [Volby 2018](volby/2018/README.md) | uzavřené | — | 9. 9. 2026 | nad nadpisem přidán rozcestník ročníků (`{{VOLBY_ROCNIKY}}`, viz `volby/README.md`) |
| [Volby 2022](volby/2022/README.md) | uzavřené | — | 9. 9. 2026 | nad nadpisem přidán rozcestník ročníků (`{{VOLBY_ROCNIKY}}`); blok „Volební účast stoupá" (SVG graf) přesunut ze záložky Rozbor na rozcestník `/volby/` — v panelu Volby 2022 už není, viz `volby/README.md` |
| [Smlouvy](smlouvy/README.md) | týdně | 16. 9. 2026 | 9. 9. 2026 | zkontrolováno, beze změny — žádná smlouva novější než WEBER HYDRAULIK (7. 9.); souhrnná čísla dál ponechána beze změny, nevysvětlený úbytek pokračuje (skupina 182 → 181 smluv, hodnota za úřad se posunula i při stejném počtu 47) — viz `smlouvy/README.md`; dřív (9. 9. 2026): 2 nové smlouvy do tabulky „Nejnovější smlouvy": dar hydraulického vyprošťovacího zařízení WEBER HYDRAULIK SP 49 od HZS Středočeského kraje (7. 9. 2026, 642 510 Kč) a dotace Středočeského kraje ZŠ Pečky na bezplatné školní stravování 2026/2027 (31. 8. 2026, 298 960 Kč) |
| [Pozemky](pozemky/README.md) | odvozená | 15. 9. 2026 | 5. 9. 2026 | oprava odkazu „řešilo se na: Jednání…" u všech řádků — mířil na `href="#"` s JS handlerem, který se na samostatné stránce Pozemky nikdy nenačetl (pozůstatek jednostránkové architektury); teď skutečný odkaz `/jednani/#rada-YYYY-MM-DD` |
| [Plán](plan/README.md) | na vyžádání | 2. 9. 2026 | 2. 9. 2026 | řádek „Nová tělocvična a učebny ZŠ": stav → zastaveno, odkaz na novou sekci Tělocvična |
| [Domů](domu/README.md) | odvozená | — | 24. 8. 2026 | brand header |
| [Zakázky](zakazky/README.md) | týdně | 16. 9. 2026 | 6. 8. 2026 | zkontrolováno, beze změny — 214 výsledků na Hlídači stejně jako 13. 9., žádné nové ID |
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

19. září 2026 (kontrola sociálních sítí, spuštěno ručně přes skill
`pecky-online-socialni-site-check`. Projito všech 15 odkazů přes
Claude in Chrome — počet sledujících a `creation_time` ze `<script>`
dat stránky, viz `o-webu/automation-socialni-site.md`. Počet
sledujících se změnil u 5 účtů: Pečky NEXT FB 307 → 308, Pečky
Pečákům 245 → 246, ODS a nezávislí 228 → 232, Instagram Pečky NEXT
130 → 131, Pečky srdcem 86 → 87. Nová aktivita u 8 účtů: Město Pečky
(18. 9.), NAŠE PEČKY (19. 9.), Alena Švejnohová (18. 9.), Pečky NEXT
FB (19. 9.), ODS a nezávislí (18. 9.), TJ Sokol Pečky (17. 9.),
YouTube Město Pečky (17. 9. — záznam Zastupitelstva 6/2026 konečně
zveřejněn na kanálu), FB skupina Lidé pro Pečky s podporou SPD
(19. 9.). **Zjištěna a opravena chyba v běhu 16. 9. 2026:** ten měl
u 5 účtů (Pečky-Virtuálně, Kulturní středisko, Městská knihovna,
Pečky Pečákům, Pečky srdcem) zapsané datum posledního příspěvku
shodné s datem kontroly napříč skoro všemi facebookovými účty
najednou — nápadná shoda, kterou dnešní ověření (`creation_time`
skript i vizuální kontrola stránky) nepotvrdilo: skutečná poslední
vlastní aktivita byla starší, 4.–14. 9. 2026, teď opravena na ověřené
datum. Beze změny zůstávají Facebook Město Pečky (2,9 tis.), Pečky-
Virtuálně (1,4 tis.), Instagram streetpeopleofpecky (1 216, datum
22. 8. trvá — Instagram od 2. 9. 2026 neumožňuje spolehlivě přečíst
datum z `img[alt]`, jen počet sledujících), Kulturní středisko (993),
Alena Švejnohová (956), Městská knihovna (483), TJ Sokol Pečky (224),
YouTube Město Pečky (95 odběratelů), FB skupina Lidé pro Pečky
s podporou SPD (40 členů). Překrývajících se 7 odkazů promítnuto
i do `/volby/2026/`. `python3 scripts/build.py` proběhl bez chyby,
ověřeno v prohlížeči na `/o-webu/` a `/volby/2026/`.)

16. září 2026 (týdenní kontrola zdrojů, spuštěno ručně přes nový
projektový skill `pecky-online-update` — nahrazuje starší
`pecky-online-daily-update`, který žil jen v datech appky Claude
(naplánovaná úloha), ne v repu; nový orchestrátor + dílčí skilly pro
Jednání/Noviny/Zakázky/Smlouvy/Tělocvičnu/sociální sítě žijí
v `.claude/skills/` (needituje se, celé v `.gitignore`). **Jednání:**
beze změny — Rada 33/2026 (14. 9.) a Zastupitelstvo 6/2026 (16. 9.,
dnes) nadále jen s Pozvánkou; YouTube i video_ts u nedávných jednání
v pořádku, historický dluh video_ts u 22 starších zastupitelstev
(2022–2025, žádná kapitola u žádného bodu) přetrvává — mimo rozsah
týdenní kontroly, k řešení jako samostatný úkol. **Tělocvična:**
zkontrolováno, beze změny — dnešní ZM 6/2026 má bod „Informace
o stavební akci“ na programu, zápis zatím nevyšel. **Smlouvy:**
zkontrolováno, beze změny — žádný nový podpis od WEBER HYDRAULIK
(7. 9.); pokračuje nevysvětlený úbytek v souhrnných číslech (skupina
182 → 181 smluv), čísla na stránce záměrně ponechána. **Zakázky:**
zkontrolováno, beze změny — 214 výsledků na Hlídači stejně jako 13. 9.,
žádné nové ID. **Pečecké noviny:** vydání 9/2026 doplněno do archivu
(206. vydání, 3160 stran) — nalezeno rovnou na archivním rozcestníku
pecky.cz, opraveny i 2 zastaralé počty v poznámkách pod starším
archivem. **O webu + Volby 2026:** zkontrolováno všech 15 sociálních
sítí, počty sledujících se změnily u 5 účtů, nová aktivita dnes u 12
z 15 (mj. Pečky-Virtuálně po 12 dnech ticha); opravena chyba v datu
posledního videa u YouTube kanálu Město Pečky — četlo se ze záložky
„Videa“ (zavádějící, viz `o-webu/automation-socialni-site.md“), teď ze
správného zdroje. `python3 scripts/build.py` proběhl bez chyby — 15
stránek + 1 neprolinkovaná podstránka, validace OK.)

15. září 2026 (týdenní kontrola zdrojů, spuštěno ručně přes skill
`pecky-online-daily-update` — pozn.: soubor skillu ještě mluví o „denní“
kontrole a režimu `denně`, ale repozitář (`README.md` → „Stav sekcí“,
`CLAUDE.md`) od 5. 9. 2026 běží na týdenním rytmu; podle vlastního
pravidla skillu platí repozitář, nesoulad k opravě v souboru skillu.
**Jednání:** beze změny — výpis na usneseni.cz (stav k 15. 9. 2026
15:55) identický se včerejškem, Rada 33/2026 (14. 9.) a Zastupitelstvo
6/2026 (16. 9.) nadále jen s Pozvánkou; YouTube playlist „Zasedání ZM“
beze změny (32 videí), známé mezery (video k reálnému ZM 3/2026
z 25. 5. 2026, video_ts u bodů 8–9 ZM 2/2026) trvají. **Tělocvična**
a **Pozemky:** zkontrolováno, beze změny — žádné nové jednání/usnesení
k vytěžení. **Smlouvy:** beze změny — Hlídač státu MCP potvrzuje přesně
stejná čísla jako 14. 9. (skupina 152 smluv / 95 486 533,66 Kč, úřad
47 / 33 473 888,05 Kč, nejnovější podpis nadále 7. 9. 2026). **Zakázky:**
beze změny — 176 unikátních ID formátu `P##V########` odpovídá přesně
baseline z 13. 9. Při té příležitosti průchod rozšířen na všech 5 stránek
výpisu (dřív se kontrolovaly 4) — objevilo se 18 dalších ID, ale všechna
mimo sledovaný formát (starší číselné/`Z`-prefixové položky z registru
před rokem 2016, nebo fulltextový šum jiných obcí jako u P22V00000346);
baseline soubor `pecky-zakazky-ids.json` proto zůstává nedotčen, jde jen
o potvrzení, že sledovaný formát je kompletní. **Pečecké noviny:**
beze změny — archiv na pecky.cz stále končí 7–8/2026. **O webu + Volby
2026:** zkontrolováno všech 15 sociálních sítí, viz řádky v tabulce
„Stav sekcí“ výše pro čísla; na úřední desce pecky.cz nic nového
k volbám od 10. 9. `python3 scripts/build.py` proběhl bez chyby —
15 stránek + 1 neprolinkovaná podstránka, validace OK.)

14. září 2026 (na žádost uživatele prohledána nová dávka Pečeckých
novin 2012–2015 (44 vydání) na zmínky relevantní pro sekci Tělocvična
— klíčová slova tělocvičn/kolaudac/pilot/základ/kuchyň/vývařovn/statik.
Většina zásahů byl falešný poplach, ale osm výtisků z let 2014–2016
vyplnilo mezeru v tabulce „Historie projektu“ mezi řádky 1. 9. 2008 a
červen 2016: PN 9/2014 (titulní článek o čekání na dotaci, tehdejší
odhad rozpočtu 78 mil. Kč), PN 10–11/2014 (Rada jedná s Ateliérem A11
o cenových návrzích a vybírá zpracovatele PD), **PN 4/2015 — nezávislé
potvrzení roku i zpracovatele (Ateliér A11) z tvrzení Aleny Švejnohové
o „dokumentaci z roku 2015“**, byť ne konkrétního údaje o délce pilot
(8,5 m) ani „kolaudačního“ charakteru dokumentu, PN 11/2015 (stavba
ještě neskončila) a PN 8/2016 („Vývařovna finišuje“). Promítnuto do
`content/telocvicna.html`: šest nových řádků tabulky, upravený úvodní
odstavec a gap-callout u „Historie projektu“, upravený první callout
v „Otevřené otázky“. Detaily v `telocvicna/README.md`.)

14. září 2026 (automatická kontrola usneseni.cz. **Jednání:** beze změny
— výpis na usneseni.cz (stav k 14. 9. 2026 08:26) ukazuje přesně to, co
už archiv má: **Zastupitelstvo 6/2026 (16. 9.)** a **Rada 33/2026
(14. 9.)** nadále jen s Pozvánkou, **Rada 32/2026 (7. 9.)** kompletní
od 10. 9. Žádné nové jednání, u žádného staršího nepřibyl zápis ani
usnesení; `pecky-jednani.json` nedotčen — archiv drží **289 jednání,
2 767 usnesení**. Playlist „Zasedání ZM" má 32 položek, beze změny proti
13. 9.: jediná novinka zůstává naplánovaný živý přenos **ZM 6/2026
(16. 9. 2026, 16:30)**, který se do `links.youtube` **nezapisuje** —
postup (krok 6) pracuje jen s jednáními v minulosti a odkaz se doplní
po zveřejnění záznamu. **Video k ZM 3/2026 z 25. 5. 2026 na kanálu
stále chybí**, známá mezera trvá. Časové značky bodů (`video_ts`)
prověřeny u všech zastupitelstev od ZM 2/2025: jediné chybějící jsou
„Volba pracovních komisí" (vlastní kapitolu v popisku nikdy nemá), body
8 a 9 u ZM 2/2026 a celé ZM 3/2026 bez videa — vše ověřené mezery, nic
k doplnění. **Tělocvična:** zkontrolováno, beze změny — nepřibylo
jednání, jehož program nebo usnesení by se stavby týkaly; bod
„Informace o stavební akci Dostavba učeben a tělocvičny v ZŠ Pečky"
z programu ZM 6/2026 je v sekci podchycen už od 10. 9. **Pozemky:**
žádné nové usnesení k prodeji/nákupu pozemku, `update-pozemky.py`
nespouštěn. Web přegenerován kontrolně (`scripts/build.py`), výstup
identický. Změněn jen tento changelog a datum kontroly u Jednání
a Tělocvičny v tabulce „Stav sekcí".)

13. září 2026 (týdenní kontrola zdrojů. **Jednání:** na usneseni.cz
přibylo jedno nové jednání — **Rada 33/2026 (14. 9. 2026)**, zatím jen
s Pozvánkou; zaznamenáno s programem o 9 bodech z pozvánkového PDF (mj.
Smlouva o zřízení práva stavby – kolárna u ČD, změna termínu plnění
usnesení UR-265-29/26 a souhlas s vyřazením nepotřebného DHM ZŠ Pečky).
U žádného staršího jednání nepřibyl zápis ani usnesení — Rada 32/2026
byla doplněná už 10. 9., Zastupitelstvo 6/2026 (16. 9.) má nadále jen
Pozvánku. Archiv má nově **289 jednání, 2 767 usnesení, 4 123 bodů
programu**. `jednani/absence.json` přepočítán, beze změny (nové jednání
zatím nemá prezenci). Playlist „Zasedání ZM" má 32 položek — proti
minulému běhu přibyl jen naplánovaný přenos ZM 6/2026 (16. 9. 2026),
žádný nový záznam; **video k ZM 3/2026 z 25. 5. 2026 na kanálu stále
chybí**, známá mezera trvá. Časové značky bodů (`video_ts`)
zkontrolovány — jediné nedoplněné jsou body 8 a 9 u ZM 2/2026, kde je
ověřeno, že vlastní kapitolu v popisku videa nemají.
**Tělocvična:** zkontrolováno, beze změny — program Rady 33/2026 žádný
bod ke stavbě, pilotám, statice ani dodatkům ke SoD neobsahuje (ověřeno
i u UR-265-29/26, na které se jeden bod odvolává: jde o oplocení
dětského hřiště na sídlišti, ne o tělocvičnu). **Pozemky:** nové
usnesení k prodeji/nákupu pozemku nepřibylo, `update-pozemky.py`
nespouštěn. **Pečecké noviny:** archiv pecky.cz nadále končí číslem
7–8/2026, zářijové vydání ještě nevyšlo. **Smlouvy:** konektor Hlídače
státu vrací **přesně stejná čísla jako 9. 9.** — skupina 152 smluv /
95 486 534 Kč, úřad 47 / 33 473 888 Kč, nejnovější podpis nadále
7. 9. 2026. Žádná nová smlouva, tabulky ani souhrny nedotčeny;
**nevysvětlený propad z 30. 8.–2. 9. (skupina 182 → 150) zůstává
nedorovnaný** a čísla v sekci jsou pošesté ponechána beze změny —
k rozhodnutí uživatele. **Zakázky:** diff proti
`zakazky/pecky-zakazky-ids.json` — **176 ID, 1 nové, 0 zmizelých**.
Nové ID `P22V00000346` je ale **fulltextový šum**: jde o zakázku
„Novostavba silnice III. třídy Nová Průběžná v obci **Zdiby** – PD"
zadavatele Středočeský kraj, s Pečkami nesouvisí. Do kontrolního snímku
zapsáno (aby se příště znovu nehlásilo), do tabulky „Nejnovější zakázky"
**ne**. Při té příležitosti zjištěno, že vyhledávání `Q=00239607` je
fulltext, ne filtr podle zadavatele — dopsáno jako pravidlo do
`zakazky/README.md` i do `sources.json`. Hlídač dnes hlásí 214 výsledků
celkem (dřív 193) při 176 unikátních ID. **Volby 2026:** na úřední desce
pecky.cz přibyly dva volební dokumenty, oba vyvěšené 10. 9. 2026 —
„Svolání prvního zasedání OVK" a „Školení k zásadám hlasování". Oba se
týkají okrskových volebních komisí, ne voličů; na stránku proto
nepromítnuty, jen hlášeny. **Sociální sítě (O webu + Volby 2026):**
zkontrolováno všech 15 účtů. Počty se změnily u 8: Alena Švejnohová
946 → 955, Kulturní středisko 992 → 993, Městská knihovna 482 → 483,
Pečky Pečákům 238 → 245, TJ Sokol Pečky 221 → 223, ODS a nezávislí
Pečky 217 → 221, Pečky srdcem 73 → 78, Instagram streetpeopleofpecky
1 218 → 1 216. Nová aktivita u 8 účtů: Město Pečky (13. 9.), NAŠE PEČKY
(12. 9.), Alena Švejnohová (13. 9.), Kulturní středisko (31. 8. →
10. 9.), Pečky NEXT FB (12. 9.), Pečky Pečákům (10. 9.), ODS a nezávislí
Pečky (13. 9.) a Pečky srdcem (28. 8. → 10. 9.). Měsíc před volbami jsou
tedy aktivní všechna volební uskupení kromě FB skupiny Lidé pro Pečky
s podporou SPD (nadále 27. 8. 2026). **Nová technická překážka
a její obejití:** Facebook od tohoto běhu nevykresluje datum příspěvku
ani jako zamíchané `<span>` znaky — značka je prázdný `<span>` doplněný
`<template>`, takže dosavadní postup (čtení znaků podle pozice na
obrazovce) vracel prázdno. Spolehlivě jde datum přečíst z
`creation_time`/`publish_time` ve `<script>` datech stránky; postup
ověřen proti relativnímu tvaru („7 h" u Města Pečky = 13. 9. 07:53)
a zapsán do `o-webu/automation-socialni-site.md`. U obou instagramových
účtů aktualizován jen počet sledujících — mezera v čtení data
posledního příspěvku (popsaná 2. 9.) **trvá**. `python3
scripts/build.py` proběhl bez chyby — 15 stránek + 1 neprolinkovaná
podstránka, validace OK. Vizuální kontrola na lokálním serveru v tomto
automatickém běhu neproběhla, nahradila ji strojová kontrola
vygenerovaných stránek.)

10. září 2026 (automatická kontrola usneseni.cz. **Jednání:** Rada
32/2026 (7. 9. 2026) doplněna o zápis a 12 usnesení (UR-282 až UR-293)
včetně prezence, průběžných příchodů/odchodů a délek jednotlivých bodů;
nově přibylo **Zastupitelstvo 6/2026 (16. 9. 2026)** zatím jen
s Pozvánkou — 23bodový program vytažen z PDF pozvánky. Archiv teď 288
jednání a 2 767 usnesení. Přepočítána `jednani/absence.json`. Playlist
„Zasedání ZM" — přibyl naplánovaný přenos ZM 6/2026 (16. 9. 2026), do
archivu zatím nezapsán (jednání ještě neproběhlo); **video k ZM 3/2026
z 25. 5. 2026 na kanálu stále chybí**, známá mezera trvá. Časové značky
bodů (`video_ts`) zkontrolovány — u ZM 2/2026 ověřeno v popisku videa,
že body 8 a 9 vlastní kapitolu nemají, takže tam nejde o mezeru.
**Tělocvična:** ze zápisu RM 32/2026 doplněny dvě věci — město přizvalo
externího pracovníka na sanace budov a připravuje vyjádření právní
kanceláře k dalšímu postupu; rozpočtová opatření č. 9/2026 zvyšují
letošní výdajovou položku stavby o 10 mil. Kč, podle důvodové zprávy ale
jako „předpoklad plateb v letošním roce", ne jako nově vyčíslené
vícenáklady (UR-288-32/26, 4 pro – 1 zdržel se; rozhodne ZM 16. 9.).
Přidán callout k programu ZM 6/2026, kde má stavba samostatný bod.
**Pozemky:** `update-pozemky.py` přegenerován, beze změny — obě nové
darovací smlouvy s General Property X (UR-291, UR-292) jsou bezúplatné
převody, které tabulky Nákup/Prodej nesledují.)

9. září 2026 (týdenní kontrola zdrojů. **Jednání:** na usneseni.cz nic
nového — Rada 32/2026 (7. 9. 2026) má nadále jen Pozvánku, zápis ani
usnesení zveřejněné nejsou; archiv beze změny (287 jednání, 2 755
usnesení). Playlist „Zasedání ZM" beze změny (31 videí, nejnovější
26. 8. 2026) — **video k ZM 3/2026 z 25. 5. 2026 na kanálu stále
chybí**, známá mezera trvá. Časové značky bodů (`video_ts`)
zkontrolovány, žádné jednání se zápisem i videem nezůstalo nedotažené.
**Tělocvična:** zkontrolováno, beze změny — v programu Rady 32/2026
(17 bodů z pozvánky) není žádný bod k dostavbě učeben a tělocvičny
ani k pilotám/statice; nový zápis, který by šlo vytěžit, nepřibyl.
**Pečecké noviny:** archiv pecky.cz nadále končí číslem 7–8/2026,
zářijové vydání ještě nevyšlo. **Zakázky:** diff proti
`zakazky/pecky-zakazky-ids.json` — 175 ID, 0 nových, 0 zmizelých,
soubor nedotčen. **Smlouvy:** konektor Hlídače státu vrátil **2 nové
smlouvy**, obě doplněny do tabulky „Nejnovější smlouvy" v
`content/smlouvy.html`: „Darovací smlouva — Město Pečky — zařízení
vyprošťovací hydraulické WEBER HYDRAULIK SP 49" (HZS Středočeského
kraje, podpis 7. 9. 2026, 642 510 Kč — přímo úřadu) a „S-4189/ŘDP/2026
— veřejnoprávní smlouva o poskytnutí dotace na bezplatné školní
stravování 2026/2027" (Středočeský kraj → ZŠ Pečky, podpis 31. 8. 2026,
298 960 Kč). Do tabulky „Největší smlouvy" ani jedna nepatří (nejmenší
tamní položka je 2,34 mil. Kč). Souhrny konektoru vzrostly **přesně
o tyto dvě smlouvy**: skupina 150 → 152 smluv a 94 545 064 →
95 486 534 Kč, úřad 46 → 47 a 32 831 378 → 33 473 888 Kč. To je poprvé
od 30. 8. pohyb nahoru a je beze zbytku vysvětlený — **nevysvětlený
zůstává starší propad** (16. 8.: skupina 182 / 102,4 mil., úřad 47 /
33,1 mil.), který se tímto nedorovnal. Souhrnná čísla v subject-boxu
a calloutu sekce Smlouvy proto **popáté ponechána beze změny** —
k rozhodnutí uživatele. **Volby 2026:** na úřední desce pecky.cz nic
nového k volbám — nejnovější volební dokument je nadále „Informace
o počtu a sídlech volebních okrsků" z 25. 8. 2026; nejnovější položka
desky vůbec je dopravní značení ze 7. 9. 2026. **Sociální sítě
(O webu + Volby 2026):** zkontrolováno všech 15 účtů (seznam v
`o-webu/automation-socialni-site.md` mluví o 14 — od 4. 9. 2026 přibyl
TJ Sokol Pečky, **nesoulad k opravě v automation dokumentu**). Změnily
se počty u 8 účtů: Alena Švejnohová 942 → 946, Městská knihovna
483 → 482, Pečky NEXT (FB) 291 → 306, ODS a nezávislí Pečky 213 → 217,
Instagram Pečky NEXT 120 → 128, Pečky srdcem 72 → 73, FB skupina Lidé
pro Pečky s podporou SPD 39 → 40 členů, Instagram streetpeopleofpecky
1 219 → 1 218. Nová aktivita u 8 účtů: Město Pečky (8. 9.),
Pečky-Virtuálně (4. 9.), NAŠE PEČKY (8. 9.), Alena Švejnohová (7. 9.),
Městská knihovna (8. 9.), Pečky NEXT FB (6. 9.), TJ Sokol Pečky (8. 9.)
a ODS a nezávislí Pečky (dnes 9. 9.). Nejvýraznější změna:
**Pečky Pečákům po třech měsících ticha zveřejnily 8. 9. vlastní
příspěvek** (5. 6. → 8. 9. 2026) — měsíc před volbami; ověřeno, že jde
o vlastní datum stránky, ne o datum sdíleného obsahu. U obou
instagramových účtů aktualizován jen počet sledujících — mezera
v čtení data posledního příspěvku (popsaná 2. 9. v
`o-webu/automation-socialni-site.md`) **trvá**. Datumy čteny
z absolutního tvaru, u relativních („16 h", „51 m") přepočteno vůči
9. 9. 2026 08:53. `python3 scripts/build.py` proběhl bez chyby —
15 stránek, validace OK. Vizuální kontrola na lokálním serveru v tomto
automatickém běhu neproběhla, nahradila ji strojová kontrola
vygenerovaných stránek.)

8. září 2026 (na žádost uživatele doplněno pravidlo do týdenní rutiny:
**bod jednání týkající se stavby tělocvičny musí aktualizovat i sekci
Tělocvična**, ne jen sekci Jednání, a **každý běh musí jmenovitě
vyreportovat, co změnil**. Zapsáno na čtyři místa: nový krok 9
„Tělocvična (pokud relevantní)" v `jednani/automation-kontrola-usneseni-cz.md`
(vč. seznamu hledaných formulací — nejen „tělocvična", ale i „Dostavba
učeben", „piloty", „statické zajištění", „Dodatek č. … k SoD" apod.;
následující kroky přečíslovány na 10 a 11, do kroku 11 přidán povinný
výpis změn); nová sekce „Pracovní postup: týdenní kontrola" v
`telocvicna/README.md` (kam který typ zjištění na stránce patří);
dvě nové odrážky v `CLAUDE.md` → „Konvence" (promítání bodů jednání do
věcně dotčených sekcí; povinný report změn). Režim sekce Tělocvična
v tabulce „Stav sekcí" změněn z `hlídat` na `týdně` — nově ji týdenní
rutina kontroluje sama, ne až na vyžádání; z legendy u režimu `hlídat`
proto odstraněn příklad „volby 2026". Obsah webu tato změna nemění,
jen postupy.)

5. září 2026 (na žádost uživatele překlopena automatická rutina z denní
na **týdenní** — běží v neděli večer, cron `0 18 * * 0` (fakticky
týdenní byla už dřív, jen se všude jmenovala „denní“). Sjednoceno
pojmenování: režim sekcí v tabulce „Stav sekcí“ i v legendě `denně` →
`týdně` (Jednání, O webu, Volby 2026, Pečecké noviny, Smlouvy,
Zakázky), přepsané postupy v `zakazky/README.md` (týdenní diff),
`smlouvy/README.md`, `o-webu/README.md`, `o-webu/automation-socialni-site.md`,
`volby/2026/README.md`, `jednani/automation-kontrola-usneseni-cz.md`
(nově upozorňuje, že za týden mohlo přibýt víc jednání najednou —
kontrolovat celé období od data v tabulce, ne jen poslední den)
a `telocvicna/README.md`. Na webu: `content/owebu.html` → sociální sítě
„aktualizuje se týdně“. Historické záznamy v tomto changelogu zmiňující
„denní kontrolu“ zůstávají beze změny — popisují běhy, které tak
skutečně proběhly.)

4. září 2026 (na žádost uživatele doplněn do `content/telocvicna.html`
obsah zápisu RM 31/2026 (Dodatek č. 1 ke smlouvě o dílo, viz zápis
usneseni.cz níže) — v době předchozích kontrol dostupný jen jako
pozvánka. Dodatek zahrnuje 13 změnových listů, mimo jiné „změny
související se statickým zajištěním stávajícího založení“ (piloty),
navyšuje cenu díla o 6 150 969 Kč bez DPH na 211,5 mil. Kč vč. DPH
(původně cca 205 mil.) — ale sám upozorňuje, že jde o vyúčtování už
uzavřených změn, ne odhad celkových nákladů na vyřešení pilot. Dopad
na harmonogram dodatek neřeší; radnice v něm výslovně uvádí, že jím
není dotčeno budoucí posouzení odpovědnosti zhotovitele/projektanta.
Promítnuto do stat-gridu, perexu, přepsaného řádku 31. 8. 2026
v tabulce „Zastavení stavby“ a nového callloutu v „Otevřené otázky“.
Detaily v `telocvicna/README.md`.)

4. září 2026 (automatická kontrola usneseni.cz. **Jednání:** Rada
31/2026 (31. 8. 2026) už má zveřejněný zápis, podepsaný zápis
i přijatá usnesení — doplněna do `jednani/pecky-jednani.json` v plném
rozsahu: 11 bodů programu s délkami a předkladateli, důvodové zprávy
u bodů 3–8, prezence 6/7 (Ing. Petr Dürr nepřítomen na začátku,
dorazil v 15:45), délka jednání 2h13min a 6 usnesení UR-276 až
UR-281-31/26. Věcně největší z nich: UR-277 — Dodatek č. 1 k SoD
„Dostavba učeben a tělocvičny v ZŠ Pečky“ (změnové listy ZL 01–13,
+6 150 969,14 Kč bez DPH na 174 765 820,14 Kč bez DPH, přijato 5-0-1).
Zároveň na webu přibylo nové jednání **Rada 32/2026 (7. 9. 2026)**,
zatím jen s Pozvánkou — zaznamenáno s programem o 17 bodech
z pozvánkového PDF (mj. tři smlouvy s General Property X s.r.o.
a termín/program zasedání ZM 16. 9. 2026). Archiv má nově 287 jednání,
2 755 usnesení, 4 091 bodů programu; číselná řada usnesení Rady 2026
je 1–281 bez děr. **YouTube (kroky 6 a 7):** playlist „Zasedání ZM"
beze změny (31 videí, nejnovější 26. 8. 2026) — video k ZM 3/2026
z 25. 5. 2026 na kanálu nadále chybí. Doplňovat časové značky nebylo
kde: jediná mezera v éře kapitol jsou body 8 a 9 u ZM 2/2026
(22. 4. 2026) a ověřeno přímo v popisku videa, že tyto dva body
kapitolu vůbec nedostaly — zůstávají tedy prázdné. Vizuální kontrola
na lokálním serveru v tomto automatickém běhu neproběhla, nahradila ji
strojová kontrola dat.)

4. září 2026 (na žádost uživatele znovu zkontrolovány Aktuality města
Pečky na `pecky.cz/default/default/21395_aktuality` — beze změny oproti
2. 9. 2026, nejnovější položka zůstává „Uzavírka ulice K. Havlíčka
Borovského“ z 3. 6. 2026. Ani po facebookovém vyjádření vedení města
tam samostatná zpráva o zastavení stavby zveřejněná není. Bulletka u
„Co přesně říká radnice“ v `content/telocvicna.html` aktualizována na
nové datum kontroly.)

4. září 2026 (na žádost uživatele přečten nový příspěvek na
`facebook.com/mestopecky` — první veřejné vyjádření samotného vedení
města k pozastavení stavby tělocvičny, zveřejněné 4. 9. 2026 v 0:20
(dosud mlčelo, viz kontroly Aktualit i Facebooku k 2. 9. 2026 v
předchozích záznamech). Potvrzuje technické jádro ze zápisu ZM a
upřesňuje: sanace pilot pod kuchyní byla plánovaná od začátku
zakládání stavby, ale bourací práce odhalily pochybnosti o kvalitě a
délce i STÁVAJÍCÍCH pilot; statik proto zpochybnil délku i dalších
pilot, ne jen původně kontrolovaných; město zvažuje sanaci základů,
nebo přeprojektování statiky celé stavby; dohoda se zhotovitelem o
pozastavení prací šetří náklady města. Na konkrétní tvrzení Aleny
Švejnohové z 2. 9. 2026 (rok 2015, jména Urban/Paluska, odepřené
podklady) ale vyjádření vůbec nereaguje. Promítnuto do
`content/telocvicna.html`: nový callout a odkaz v „Co přesně říká
radnice“, poznámka v obou calloutech „Otevřené otázky“, nový řádek
4. 9. 2026 v tabulce „Zastavení stavby“ (nad řádkem Švejnohové) a
opravené pasáže, které dřív (platně k 2. 9.) tvrdily, že radnice mlčí.
Detaily v `telocvicna/README.md`.)

3. září 2026 (denní kontrola zdrojů. **Jednání:** na usneseni.cz nic
nového — Rada 31/2026 (31. 8. 2026) má nadále jen Pozvánku, archiv beze
změny (286 jednání). Nově se „Zvukový záznam" objevil i u ZM 4/2026
(24. 6. 2026), nejen u ZM 5/2026 — pole se tedy doplňuje zpětně
i ke starším zasedáním; archiv ho neeviduje, zatím jen poznámka
v `sources.json`. Playlist „Zasedání ZM" beze změny (31 videí,
nejnovější ZM z 26. 8. 2026) — **video k ZM 3/2026 z 25. 5. 2026 na
kanálu stále chybí**, známá mezera trvá. Časové značky bodů (`video_ts`)
zkontrolovány, žádné jednání se zápisem i videem nezůstalo nedotažené.
**Pečecké noviny:** archiv pecky.cz nadále končí číslem 7–8/2026,
zářijové vydání ještě nevyšlo. **Zakázky:** diff proti
`zakazky/pecky-zakazky-ids.json` — 175 ID, 0 nových, 0 zmizelých,
soubor nedotčen. **Smlouvy:** konektor Hlídače státu v této relaci nebyl
k dispozici, čísla proto ověřena z veřejného webového vyhledávání Hlídače
smluv (`holding:00239607` a `ico:00239607` — stejné dva pohledy jako
u konektoru). Žádná nová smlouva (nejnovější podpis nadále 23. 7. 2026)
a **pokles se dál neprohluboval** — skupina 150 smluv / cca 95 mil. Kč,
úřad 46 / cca 33 mil. Kč, tedy přesně hodnoty naměřené 2. 9. Zároveň to
**vyvrací domněnku, že jde o chybu konektoru** — stejná snížená čísla
ukazuje i webové rozhraní Hlídače, takže úbytek 179 → 150 z 2. 9. je
skutečný stav zdroje. Čísla v sekci Smlouvy proto **počtvrté ponechána
beze změny** — k rozhodnutí uživatele. **Volby 2026:** na úřední desce
pecky.cz nic nového (nejnovější dokument je nadále zápis ze ZM 5/2026
vyvěšený 28. 8. 2026). **Sociální sítě (O webu + Volby 2026):**
zkontrolováno všech 14 účtů. Změnily se počty: Alena Švejnohová
933 → 942, streetpeopleofpecky 1 218 → 1 219, Instagram Pečky NEXT
119 → 120; ostatní beze změny. Nová aktivita u pěti účtů — Město Pečky
(2. 9.), Alena Švejnohová (2. 9.), NAŠE PEČKY a Pečky NEXT (oba dnes
3. 9.) a zejména **Pečky-Virtuálně, které po dvou měsících ticha
zveřejnily 2. 9. dva vlastní příspěvky** (26. 6. → 2. 9. 2026);
ověřeno, že jde o vlastní sdílení stránky, ne o datum sdíleného obsahu.
U obou instagramových účtů aktualizován jen počet sledujících — mezera
v čtení data posledního příspěvku (popsaná 2. 9. v
`o-webu/automation-socialni-site.md`) **trvá**, znovu ověřeno, že `alt`
u obrázků mřížky vrací popisek místo data a `time[datetime]` se
odhlášené relaci nevykreslí. **Technická překážka:** `scripts/build.py`
se v tomto běhu nepodařilo spustit — připojená složka odmítala číst
`scripts/build.py`, `assets/styles.css`, `templates/page.html`,
`assets/nav.html` i `assets/footer.html` s `Resource deadlock avoided`
(opakováno cca 20× během 2 minut, bez úspěchu). Zdrojové
`content/owebu.html` a `content/volby2026.html` jsou aktualizované
správně; do vygenerovaných `o-webu/index.html` a `volby/2026/index.html`
byly ty samé řetězce zapsány ručně, aby web nezůstal nekonzistentní.
**Doporučeno spustit `python3 scripts/build.py` ručně, až bude složka
čitelná** — výstup by měl být identický, ale ověřit to je na místě.)

2. září 2026 (na žádost uživatele prohledán `facebook.com/svejnohova`
— nalezen čerstvý veřejný příspěvek předsedkyně Kontrolního výboru
Aleny Švejnohové (v době kontroly ~13 minut starý): tvrdí, že vadná
dokumentace, podle níž byla zkolaudována kuchyň ZŠ a která posloužila
i jako podklad pro stavbu tělocvičny, je z roku 2015 — uváděla piloty
8,5 m, kontrolní zkoušky po poškození 3 pilot při bourání potvrdily
skutečnou délku jen 6,5–6,6 m. Jmenuje tehdejší vedení města (starosta
Milan Urban, místostarosta Milan Paluska — dnešní starosta) a popisuje,
že jí město jako předsedkyni výboru dokumenty nejprve odepřelo
(„Kontrolní výbor na ně nemá právo“), pak tvrdilo, že „ještě nejsou
dohledané“; vyzývá k trestnímu oznámení pro podezření z podvodu a
zmiňuje možný střet zájmů starosty Palusky. Promítnuto do
`content/telocvicna.html` jako důsledně odlišené, jednostranné tvrzení
volené zastupitelky pod jejím jménem — ne jako nezávisle ověřený závěr
(nový řádek „2015“ v tabulce „Historie projektu“, nový řádek „2. 9.
2026“ v tabulce „Zastavení stavby“, přepsané „Otevřené otázky“, přesná
čísla pilot doplněna k citaci radnice). Zároveň upřesněna dřívější
formulace „dokumentace sahá k 2008, ne 2015“ — obě data jsou reálná a
netýkají se stejného dokumentu (2008 = správní rozhodnutí o rozdělení
stavby na etapy, 2015 = dle Švejnohové kolaudační dokumentace kuchyně
s vadnými údaji o pilotách). Detaily v `telocvicna/README.md`.)

2. září 2026 (denní kontrola zdrojů. **Jednání:** na usneseni.cz nic
nového — Rada 31/2026 (31. 8. 2026) má nadále jen Pozvánku, archiv beze
změny (286 jednání). Nově web u ZM 5/2026 nabízí i „Zvukový záznam"
(dosud jen zápis a usnesení); archiv toto pole neeviduje, zatím jen
poznámka v `sources.json`. Playlist „Zasedání ZM" beze změny —
**video k ZM 3/2026 z 25. 5. 2026 na kanálu stále chybí**, známá mezera
trvá. Časové značky bodů (`video_ts`) zkontrolovány, žádné jednání se
zápisem i videem nezůstalo nedotažené. **Pečecké noviny:** archiv
pecky.cz nadále končí číslem 7–8/2026, zářijové vydání ještě nevyšlo.
**Zakázky:** diff proti `zakazky/pecky-zakazky-ids.json` — 175 ID, sada
shodná s baseline (ověřeno porovnáním SHA-256 seřazeného seznamu),
0 nových, 0 zmizelých, soubor nedotčen. **Smlouvy:** žádná nová smlouva
(nejnovější podpis nadále 23. 7. 2026), ale **nevysvětlený úbytek
záznamů u skupiny se prohloubil** — Hlídač státu teď vrací 150 smluv /
94 545 064 Kč místo 179 / 102 075 674 Kč z 30. 8. a 1. 9. (tedy −29
záznamů a −7,5 mil. Kč za dva dny), zatímco samotný úřad se drží na
46 / 32 831 378 Kč. Čísla v sekci Smlouvy proto **potřetí ponechána beze
změny**; dvojí pokles bez jediné nové smlouvy vypadá spíš na změnu
indexace skupiny na straně Hlídače než na skutečné stažení smluv
z registru — k rozhodnutí uživatele. **Volby 2026:** na úřední desce
pecky.cz nic nového k volbám (nejnovější dokument je zápis ze ZM 5/2026
z 28. 8. 2026). **Sociální sítě (O webu + Volby 2026):** zkontrolováno
všech 14 účtů. Změnily se počty: streetpeopleofpecky 1 220 → 1 218,
Pečky NEXT (FB) 290 → 291, ODS a nezávislí Pečky 210 → 213, Pečky NEXT
(Instagram) 118 → 119; ostatní beze změny. ODS a nezávislí Pečky má nový
příspěvek z dnešního dne (2. 9.). Při té příležitosti **opraveny tři
datumy poslední aktivity, které byly o den novější než skutečnost** —
Kulturní středisko 1. 9. → 31. 8., Pečky srdcem 29. 8. → 28. 8.,
FB skupina Lidé pro Pečky s podporou SPD 28. 8. → 27. 8.; příčinou byl
dopočet z relativního tvaru („4 d"), dnes už se čte absolutní datum
přímo z Facebooku. **Dvě nové technické překážky u sociálních sítí,
obě zapsané do `o-webu/automation-socialni-site.md`:** (1) Facebook u
části stránek rozsypal datum příspěvku do desítek jednoznakových
`<span>` promíchaných s návnadovými znaky — prosté čtení textu vrací
nesmysl nebo datum komentáře místo příspěvku; obchází se čtením znaků
v pořadí podle jejich pozice na obrazovce (`getBoundingClientRect`,
hotový skript je v automation dokumentu). (2) **Instagram přestal
prozrazovat datum posledního příspěvku** — atribut `alt` u obrázků
mřížky teď v české lokalizaci obsahuje popisek příspěvku místo dřívějšího
`"Photo by … on September 01, 2026."`, `?hl=en` to nezmění, `time[datetime]`
ani odkazy `/p/<kód>/` se odhlášené relaci nevykreslí a
`/api/v1/users/web_profile_info/` vrací HTML místo JSON; u obou
instagramových účtů proto aktualizován jen počet sledujících a datum
poslední aktivity ponecháno na hodnotě z posledního úspěšného čtení.)

2. září 2026 (na žádost uživatele prohledán celý archiv jednání —
`jednani/archive-2026-08-04.json` (2021–7/2026) a `jednani/pecky-
jednani.json` pro srpen 2026, mimo záběr staršího archivu — a fulltext
Pečeckých novin 2008–2026, hledání zmínek o projektu tělocvičny pro
sekci Tělocvična. Do `content/telocvicna.html` doplněny: (1) nová
podsekce „Historie projektu (2008–2022)“ — zápis Rady z 1. 9. 2008
(starosta Milan Urban) dělí „II. etapu dostavby ZŠ“ na vývařovnu a
tělocvičnu/aulu se zhotovitelem PD Ateliér A11 Hradec Králové; táž
firma znovu 2017; nová smlouva s OV ARCHITEKTI s.r.o. 2018 (studie od
nuly); zhotovitelem PD je 2022 už třetí kancelář, Atelier A99 s.r.o.
Dokumentace tak nesahá k roku 2015, jak se traduje mezi občany (a jak
tvrdí i needitovaná výzva v `telocvicna/vyzva.html`), ale minimálně
k roku 2008 — nikde v archivu do 8/2026 se přitom neobjevuje zmínka o
pilotách. (2) 3 nové řádky časové osy ze zápisů Rady, které dosud
sekce nepokrývala: RM 28/2026 (10. 8.) — nejstarší dohledaná zmínka o
„utržených pilotách“, 16 dní před zápisem ZM; RM 29/2026 (17. 8.) —
svolání mimořádného ZM právě kvůli tomu; RM 30/2026 (24. 8.) —
„opatření vyvolaná pozastavením stavby“, tedy stavba byla zastavená
ještě před zápisem ZM. Přidán i řádek o RM 31/2026 (31. 8., bod
„Dodatek č. 1 k SoD“) s poznámkou, že zápis/usnesení k tomu zatím
nejsou zveřejněné. Detaily a zdroje v `telocvicna/README.md`.)

2. září 2026 (na žádost uživatele odebrán blok „Veřejná výzva“ z
`content/telocvicna.html` — panel sekce Tělocvična je teď čistě věcný,
stejně jako zbytek webu. Osobní výzva místo toho žije v novém
samostatném souboru `telocvicna/vyzva.html`: needitovaný přepis
uživatelova původního podkladu (jen připojena hlavička/patička webu),
záměrně **mimo strukturu webu** — není v `scripts/build.py` MANIFEST,
nikde na ni nevede odkaz, není v `sitemap.xml`, má `<meta
name="robots" content="noindex, nofollow">`. Detaily v
`telocvicna/README.md`.)

2. září 2026 (přidána nová sekce **Tělocvična** (`/telocvicna/`) —
stavba „Dostavba učeben a tělocvičny ZŠ Pečky“ (205 mil. Kč, zahájena
3. 6. 2026) je od 26. 8. 2026 částečně zastavená: při obnažování šesti
původních pilot podpírajících sousední budovu kuchyně a jídelny se u
tří z nich zjistilo zkrácení cca 2 m a zkoušky PIT nepotvrdily délku
pilot dle zhotovovacích protokolů. Podklad dodal uživatel (návrh
veřejné výzvy), obsah před publikací nezávisle ověřen proti oficiálnímu
zápisu ze zasedání ZM 5/2026 (usneseni.cz, čteno přes claude-in-chrome
kvůli bot-ochraně) a proti videozáznamu na YouTube kanálu města — zápis
potvrzuje technické jádro (6 pilot, PIT zkoušky, dočasné zastavení
prací, i to, že Alena Švejnohová jako předsedkyně kontrolního výboru
byla na jednání omluvena), ale neobsahuje uživatelovu výzvu ani
přisouzení viny konkrétním osobám (Urban, Paluska, Švejnohová) — ty
zůstávají v samostatném bloku „Veřejná výzva“ výslovně označené jako
osobní názor autora webu, ne ověřené tvrzení. Sekce zařazena do
navigace za Plán, `scripts/build.py` MANIFEST/README_TO_SLUG doplněny,
web teď generuje 14 stránek.)

1. září 2026 (denní kontrola zdrojů. **Jednání:** na usneseni.cz nic
nového — Rada 31/2026 (31. 8. 2026) má nadále jen Pozvánku, zápis ani
usnesení zveřejněné nejsou; archiv proto beze změny (286 jednání).
Playlist „Zasedání ZM" na YouTube zkontrolován: nejnovější video je ZM
z 26. 8. 2026, které archiv už má, a **k jednání ZM 3/2026 z 25. 5. 2026
video na kanálu stále chybí** — známá mezera trvá. **Pečecké noviny:**
nejnovější číslo v archivu pecky.cz je nadále 7–8/2026, zářijové vydání
ještě nevyšlo. **Zakázky:** diff proti `zakazky/pecky-zakazky-ids.json` —
175 nalezených ID, 0 nových, 0 zmizelých, soubor nedotčen. **Smlouvy:**
žádná nová smlouva (nejnovější podpis nadále 23. 7. 2026) a souhrnná
čísla z Hlídače státu se drží na snížené úrovni zjištěné 30. 8. 2026
(skupina 179 smluv / 102 075 674 Kč, úřad 46 / 32 831 378 Kč) — pokles
proti 16. 8. (182/47) zůstává nevysvětlený, čísla v sekci Smlouvy proto
i tentokrát **záměrně ponechána beze změny**; k rozhodnutí uživatele.
**Volby 2026:** na úřední desce pecky.cz nalezen nový dokument
„Informace o počtu a sídlech volebních okrsků" (podepsal starosta Milan
Paluska 25. 8. 2026, vyvěšeno 25. 8. 2026) — do sekce přidán blok „Kde
se volí" se **6 okrsky** a jejich sídly (Kulturní středisko, ZŠ Tř. Jana
Švermy 342 pro okrsky 2 a 5, ZUŠ Barákova, Městská knihovna, knihovna
Velké Chvalovice) a poznámkou, že přiřazení ulic k okrskům dokument
neobsahuje; z téhož dokumentu doplněno, že se ve stejných dnech volí
i do třetiny Senátu. PDF je sken, adresy přepsány ručně (OCR vrstva má
překlepy). Zdroj zapsán do `sources.json`. **O webu → Sociální sítě:**
kontrola dnes neopakována — proběhla už dřív téhož dne (14 účtů, viz
předchozí záznam), opakovaný běh po pár hodinách by u malých lokálních
účtů nepřinesl nic nového.)

30. srpna 2026 (**architektura webu přepracována z jednosouborového
`index.html` na vícestránkový statický web** — plán v
`ARCHITEKTURA-MIGRACE.md`, motivace: web přerostl jednosouborovou
strukturu a chyběly trvalé odkazy na jednotlivé sekce i záložky uvnitř
nich. Obsah rozřezán do `content/<sekce>.html` (13 souborů), sdílené
části do `templates/page.html`, `assets/nav.html`, `assets/footer.html`,
`assets/styles.css`, `assets/common.js` (nav, tabulky, subtaby — teď
s trvalým odkazem na konkrétní záložku přes hash, např.
`/pozemky/#prodej`, dřív subtaby neměly URL vazbu vůbec) a
`assets/helpers.js` (funkce sdílené mezi Jednáním/Novinami/Lidmi:
`jEscapeHtml`, `jNorm`, `jHighlight`, `jInitials`). Nový
`scripts/build.py` skládá z těchto částí všech 13 veřejných stránek
(`/`, `/jednani/`, `/noviny/`, `/lide/`, `/plan/`, `/volby/2018/`,
`/volby/2022/`, `/volby/2026/`, `/smlouvy/`, `/zakazky/`, `/pozemky/`,
`/pokladna/`, `/o-webu/`) + `sitemap.xml`/`robots.txt` a validuje
HTML/JS. Staré odkazy typu `pecky.online/#pozemky` přesměrovává redirect
v `content/domu.html` na novou adresu (mapovací tabulka pro 5 sekcí, kde
se nová cesta liší od starého `data-panel` slugu: `zpravodaj`→`/noviny/`,
`owebu`→`/o-webu/`, `volby2018/2022/2026`→`/volby/RRRR/`). Zjištěná
a opravená chyba při migraci: `lApplyRoute()` v Lidé očekávala vždy hash
začínající `lide` (na jednostránkovém webu tam vždy byl), na samostatné
stránce `/lide/` bez hashe proto adresář vůbec nevykreslila — opraveno
uvolněním podmínky. Ověřeno jsdom smoke testem (13 stránek bez JS chyb,
fetch dat v Jednání/Novinách/Lidech, deep link na osobu, subtaby s
hashem) a samostatným testem redirect logiky (19+7 testů, vše OK) i
kontrolou, že všech 524 statických odkazů/src na vygenerovaných
stránkách míří na existující soubory. Staré duplicitní samostatné
stránky `pecky-jednani/index.html` a `pecky-noviny/index.html` smazány
(nahradily je plnohodnotné `/jednani/` a `/noviny/`). `update-pozemky.py`
upraven, aby psal do `content/pozemky.html` místo přímo do `index.html`
— dokumentace (`CLAUDE.md`, `pecky-jednani/automation-katastr-parcely.md`,
`pecky-jednani/README.md`, `pecky-noviny/README.md`,
`pecky-pozemky/README.md`, `pecky-zakazky/README.md` a další sekce)
aktualizována. Nepublikováno na GitHub — čeká na výslovné „Publikuj".)

30. srpna 2026 (denní kontrola čtyř zdrojů. **Jednání:** na usneseni.cz
přibyla Rada 31/2026 (31. 8. 2026) — zatím jen s Pozvánkou, přidána do
`pecky-jednani/pecky-jednani.json` jako záznam s `resolutions: []`,
`links.minutes`/`resolutions`/`pdf` = `null`, `time: "15:00"`, `venue`
a 11 body agendy vytaženými z PDF pozvánky přes pdf.js v prohlížeči
(postup viz `pecky-jednani/README.md` → „Jednání jen s Pozvánkou").
Při té příležitosti **přepočteny hodnoty v `meta`**, které se rozešly se
skutečností: `resolutions_count` 2743 → 2749 a `agenda_items_count`
4062 → 4074 (počítáno ze samotných dat, dřívější čísla nezahrnovala
přírůstek Rady 30/2026). Ověřeno, že usnesení ZM 5/2026 je na webu
nadále jediné (UZ-33-5/26) a že v playlistu „Zasedání ZM" stále chybí
video k ZM 3/2026 (25. 5. 2026) — známá mezera trvá. **Pečecké noviny:**
nejnovější číslo v archivu pecky.cz je 7–8/2026, tedy beze změny.
**Zakázky:** diff proti `pecky-zakazky/pecky-zakazky-ids.json` — 175
nalezených ID, 0 nových, 0 zmizelých, soubor nedotčen. **Smlouvy:**
žádná nová smlouva (nejnovější podpis je nadále 23. 7. 2026, už na webu),
ale konektor Hlídače státu vrací u téhož dotazu **méně** záznamů než při
kontrole 16. 8. 2026 — skupina 179 smluv / 102 075 674 Kč místo 182 /
102 416 276 Kč, samotný úřad 46 / 32 831 378 Kč místo 47 / 33 132 977 Kč.
Souhrnná čísla v sekci Smlouvy proto **záměrně ponechána beze změny** —
úbytek záznamů v registru není vysvětlený a přepsat ho naslepo by bylo
horší než přiznaná datace snímku; k rozhodnutí uživatele.)

25. srpna 2026 (pravidlo naplněno u Voleb 2022: do subpanelu „Výsledky voleb"
přidán blok „Kdo byl zvolen" — tabulka vedení a rady (7) s uskupením a
poměrem hlasů, každý řádek odkazuje na vlastní usnesení, a tabulka zbylých
14 zastupitelů po uskupeních, plus odkazy na zápis, všech 33 usnesení a
videozáznam ustavujícího zasedání. Při přípravě zjištěno, že **složení se
od ustavení dvakrát změnilo**, takže panel Lidé a Výsledky voleb 2022 se
už rozcházejí: Jaroslava Vosecká složila slib za uvolněný mandát Lenky
Třískové (ZM 4/2024, 11. 9. 2024) a Ondřej Schulz nastoupil po
Bc. Ivetě Dvořákové (ZM 1/2025, 26. 2. 2025). Obě změny popsány v
`pecky-volby/2022/README.md`; dřívější tvrzení v `pecky-lide/README.md`,
že se složení nezměnilo, opraveno. Uskupení Dvořákové a Třískové není
v usneseních uvedeno — dopočítáno z počtu mandátů a z kandidátky
náhradníků, na webu přiznáno jako odvozený údaj.)

25. srpna 2026 (nové pravidlo pro volební panely: subpanel „Výsledky voleb"
má u proběhlých ročníků uvádět jmenovitě zvolené vedení, radu i zbytek
zastupitelstva, zdrojem je ustavující zasedání ZM, ne výsledky voleb.
Zapsáno do `pecky-volby/README.md` vč. rozlišení „Lidé = aktuální stav,
Volby = stav při ustavení"; do `pecky-volby/2022/README.md` doplněna
konkrétní kotva — ZM 7/2022 z 20. 10. 2022 (volby 23.–24. 9. 2022) a
tabulka 7 zvolených členů vedení a rady s usneseními `UZ-90-7/22` až
`UZ-96-7/22` a poměry hlasů, ověřeno proti archivu jednání. U ročníku
2018 popsána mezera (usneseni.cz sahá jen do dubna 2021, ustavující
zasedání 2018 tam není), u 2026 poznámka hlídat ustavující zasedání
cca v listopadu 2026. Samotný obsah do `index.html` zatím nedoplněn —
jmenný seznam je nadále jen v panelu Lidé.)

24. srpna 2026 (tabulka „Barevná paleta uskupení" přesunuta z kořenového
`README.md` do `pecky-volby/README.md`, kde je pravidlo nejblíž práci
s volebními panely; v kořeni zůstal odkaz a samotné pravidlo, odkaz
opraven i v `pecky-lide/README.md`. Při přesunu tabulka ověřena proti
`index.html` a **opravena chyba**: NAŠE PEČKY měly uvedeno `#E20514` /
`#F9CDD2`, skutečnost je `#4A4A4A` / `#DADADA` (staré hexy se na webu
nevyskytovaly vůbec). Tabulka doplněna o KSČM (`#C1272D`, 2018), Pečky
srdcem (`#2E7D32`, 2026), sloupec s ročníky, názvy uskupení napříč
ročníky a názvy uskupení napříč ročníky. Zároveň doplněny chybějící CSS
definice v `index.html`: `.person-card.party-kscm` (`#F1CFD1`/`#C1272D`),
`.person-card.party-peckysrdcem` (`#D1E2D2`/`#2E7D32`) a
`party-peckypecakum` přivěšená ke sdruženému selektoru s `party-snk`.
Odstíny pozadí dopočítané stejným poměrem (78 % bílé), jakým vznikly
stávající — vzorec sedí na existující hodnoty na desetinu přesně.
Kontrolou pokrytí ověřeno, že všech 8 tříd použitých v HTML má teď
pravidlo. Kartičky programů (`.promise-card`) barvu uskupení nepřebírají
záměrně, barvu tam nese jen tečka `.swatch`.)

24. srpna 2026 (dokončeno stěhování obrázků k sekcím: 54 souborů z kořenové
`img/` přesunuto do složek volebních ročníků — `img/volebni-programy-2018/`
→ `pecky-volby/2018/volebni-programy-2018/`, `img/volebni-programy-2022/`
→ `pecky-volby/2022/volebni-programy-2022/` a `img/zastupitele/` (42
portrétů) → `pecky-volby/2022/zastupitele/`. Všech 67 odkazů v `index.html`
přepsáno na nové cesty a ověřeno, že se všechny lokální odkazy ve všech
třech stránkách rozklíčují na existující soubory. V kořenové `img/`
zůstávají jen celowebové `favicons/` a `peckybot/`. Umístění obrázků
zdokumentováno v `pecky-volby/README.md`, `pecky-volby/2018|2022/README.md`
a `pecky-lide/README.md`.)

24. srpna 2026 (soubor `pecky-zakazky-ids.json` přesunut z kořenové složky
`data/` do `pecky-zakazky/`, stejná konvence jako `pecky-jednani/`
a `pecky-noviny/`; `data/` tím zaniká. Pracovní postup denního diffu ID
zakázek, popis struktury souboru a známé mezery přesunuty z pole `note`
uvnitř JSONu do `pecky-zakazky/README.md`, které je nově hlavním
referenčním dokumentem sekce. Historické záznamy níže popisující starší
cestu `data/pecky-zakazky-ids.json` jsou ponechány beze změny jako dobový
záznam.)

21. srpna 2026 (na žádost uživatele: do archivu `pecky-jednani.json` doplněna 2 jednání,
která mají na usneseni.cz zatím jen Pozvánku — Zastupitelstvo 5/2026 z 26. 8. a Rada
30/2026 z 24. 8., archiv nyní 285 jednání; agenda obou vytažena přímo z PDF pozvánky
přes pdf.js v prohlížeči, ne jen odkaz. Dále opraven nesoulad v číslování videí na
YouTube kanálu města: jednání 3/2026 (25. 5. 2026) nemá záznam vůbec, video s titulkem
„ZM Pečky č. 3/2026" patří ve skutečnosti jednání 4/2026 — obě jednání teď mají pole
`video_note` s vysvětlením, viditelné i v panelu Jednání na webu. Detaily viz
`pecky-jednani/README.md`.)

21. srpna 2026 (sekce Jednání přesunuta do vlastní složky `pecky-jednani/`,
stejná konvence jako `pecky-noviny/` — `pecky-jednani.json` a
`archive-2026-08-04.json` přesunuty ze `sources/`, které tím zaniklo,
`README.md`/`SPEC.md`/`AUTOMATION.md` přesunuty se souborem archivu; nové
prázdné `Data/` a `img/` vyhrazené pro budoucí lokální archiv; nová
samostatná stránka `pecky-jednani/index.html` se stejným obsahem jako panel
Jednání. Všechny odkazy na staré cesty (`data/pecky-jednani.json`,
`sources/*`) v `index.html` a tomto souboru aktualizovány — historické
záznamy níže popisující starší cesty jsou ponechány beze změny jako
dobový záznam.)

20. srpna 2026 (kontrola zdrojů na výslovnou žádost uživatele: do `data/pecky-jednani.json`
doplněna 2 nová jednání Rady města — 28/2026 z 10. 8. 2026 (5 usnesení UR-259 až UR-263) a
29/2026 z 17. 8. 2026 (6 usnesení UR-264 až UR-269); archiv nyní čítá 283 jednání / 2 742
usnesení, promítnuto i do statických zmínek počtu v sekcích Plán a O webu. Mimoto zjištěno a
opraveno, že smlouvy zachycené při běhu 16. 8. 2026 (dar — zdravotnický batoh; spolupráce
Digitální odysea 26/27) byly zapsané v README/sources.json, ale chyběly v samotném
`index.html` — doplněny se stejnými částkami jako tehdy zaznamenané. Pečecké noviny a Zakázky
zkontrolovány, beze změny. Pozn.: nový plný snímek `sources/archive-2026-08-20.json` podle
`sources/SPEC.md` nebyl vytvořen kvůli velikosti souboru v tomto prostředí — aktuální je jen
odvozený index `data/pecky-jednani.json`; kompletní snímek doplnit při příštím spuštění
plného scraperu.)

16. srpna 2026 (sekce Zpravodaj přesunuta do vlastní složky `pecky-noviny/`
— obálky, fulltext, lokální kopie PDF i samostatná stránka na jednom místě;
přidány náhledy jednotlivých stránek u výsledků fulltextového hledání,
generované `pecky-noviny/render_pages.py`.)

16. srpna 2026 (denní kontrola zdrojů: do sekce Smlouvy doplněny 2 nové smlouvy
zachycené konektorem Hlídače státu — „Dar — zdravotnický batoh" 10 381 Kč
(Krajské ředitelství policie Středočeského kraje, 22. 7. 2026) a „Smlouva o
spolupráci — Digitální odysea 26/27" bez ceny (Sdružení knihoven ČR, Městská
knihovna Svatopluka Čecha, 14. 7. 2026); součty aktualizovány na 182 smluv ve
skupině (102 416 276 Kč) a 47 smluv jen za úřad (33 132 977 Kč). Jednání a
usnesení, Pečecké noviny a Zakázky zkontrolovány, beze změny — viz poznámka
u příslušných zdrojů v sources.json.)

6. srpna 2026 (nový zdroj knihovnapecky.cz → odhalil `pecky.as4u.cz`, čitelnou verzi
oficiálního webu města bez bot-ochrany. Uzavřena mezera u zákona 106/1999 Sb.
Oba zdroje zapsány do sources.json, doplněno pravidlo č. 6 do metodiky ověřování.)

6. srpna 2026 (na stránku Plán přidána sekce „Jak se plán plní?“ — spárování
vybraných položek plánu s archivem usnesení, dotacemi a Pečeckými novinami:
8 projektů se stavem, zjištění o dotačně řízených prioritách a explicitní
poznámka o hranicích srovnání. Zároveň do README doplněna povinná metodika
ověřování.)

6. srpna 2026 (přidána nová stránka Plán — souhrn Strategického plánu rozvoje
města Pečky 2016–2026: perex, klíčová čísla, konkrétní projekty a zjištění,
že sledování plnění aktivit se v dokumentu po roce 2017 přestalo aktualizovat.
Zařazena do navigace hned za stránku Lidé.)

6. srpna 2026 (denní kontrola zdrojů: do sekce Zakázky doplněna 1 nová zakázka
nalezená diffem proti `data/pecky-zakazky-ids.json` — P26V00002056, Obnova
dětského hřiště Sídliště, 18. 6. 2026, cena neuvedena. Jednání/usnesení,
Pečecké noviny a Smlouvy/dotace přes Hlídače státu zkontrolovány, beze změn.)

6. srpna 2026 (do sekce Pokladna přidán blok Bankovní účty — 9 konkrétních čísel
účtů u 5 bank dohledaných v auditorské zprávě k Závěrečnému účtu 2025, plus
souhrnné zůstatky a poznámka, že žádný účet není „transparentní")

6. srpna 2026 (přidána sekce Zakázky — výřez veřejných zakázek Města Pečky
z Hlídače veřejných zakázek, 193 nalezených záznamů)

6. srpna 2026 (přidána sekce Pokladna — rozpočet a hospodaření města z Monitoru
Státní pokladny a přehled dotací z Registru dotací)

5. srpna 2026 (doplněn jmenný seznam zastupitelstva a kompletní archiv
Pečeckých novin z pecky.cz — obě dřívější mezery vyřešeny procházením webu
přes prohlížeč, který bot ochranu neblokuje)

## Publikování na GitHub Pages

1. Vytvořte nový repozitář (např. `pecky-online`)
2. Před nahráním spusťte `python3 scripts/build.py` — vygeneruje
   `index.html`, `jednani/`, `noviny/`, `volby/2018/` atd. ze
   `content/*.html`. Nahrajte celý výsledek (vygenerované stránky,
   `assets/`, složky sekcí jako `jednani/`, `noviny/`,
   `zakazky/` a další) do kořene repozitáře
3. Settings → Pages → source: `main` branch, root
4. Web poběží na `https://<vaše-uživatelské-jméno>.github.io/pecky-online/`
