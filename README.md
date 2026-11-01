# pecky.online

Neoficiální, nezávislý občanský projekt zpřehledňující veřejně dostupné informace
o samosprávě města Pečky (okres Kolín, Středočeský kraj).

## Obsah složky

- **Vícestránkový statický web** bez runtime frameworku, bez externích
  závislostí (jen systémová písma). `content/<sekce>.html` (jen obsah dané
  sekce) + sdílené `templates/page.html`, `assets/nav.html`,
  `assets/footer.html`, `assets/styles.css`, `assets/common.js`,
  `assets/helpers.js` se skládají přes `scripts/build.py` do 16
  samostatných veřejných stránek (`index.html` na kořeni = Domů,
  `jednani/index.html`, `noviny/index.html`, `volby/2018/index.html`
  atd.) — needit vygenerované stránky přímo, vždy přes odpovídající
  `content/*.html` + `scripts/build.py`. Web běží na vlastní doméně
  `dopecek.cz` na kořeni (`CNAME` v rootu repa, GitHub Pages — viz
  „Publikování na GitHub Pages“ níže), odkazy/assety jsou proto
  kořenově-absolutní bez subcesty (`SITE_BASE_PATH = ''` ve
  `scripts/build.py`) — pro místní test proto místo `python3 -m
  http.server` spustit `python3 scripts/serve.py` a otevřít
  `http://localhost:8000/`. Několik sekcí (Jednání, Pečecké noviny,
  Lidé) si navíc data načítá přes `fetch()`, takže lokální server je
  nutný i tak — otevření vygenerovaných stránek přímo ze souboru
  (`file://`) fetch v některých prohlížečích zablokuje.
- `jednani/` — vše k sekci „Jednání": `pecky-jednani.json` (odlehčený
  index pro fulltextové hledání na webu), `archive/`
  (kompletní datový snímek po jednáních se všemi detaily vč. jmenovitých hlasování),
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
  718 dílčích úkolů ve 4 prioritních oblastech, 360,8 mil. Kč celkem (po aktualizaci 2020: 697 úkolů, 558,5 mil. Kč; stavy plnění 2016–2020 jen v Excelu s aktualizací)
- Pečecké noviny: pecky.cz — kompletní archiv PDF zpravodaje (70 vydání, 2020–2026)
- Jednání a usnesení: jednorázový strojově čitelný export webu
  mesto-pecky.usneseni.cz z 4. 8. 2026 — 281 jednání (243 Rada, 38
  Zastupitelstvo, 2021–2026), 2 731 usnesení. Kompletní snímek se všemi detaily
  (vč. jmenovitých hlasování a plných zápisů) je v
  `jednani/archive/` (jedno jednání = jeden soubor); `jednani/pecky-jednani.json`
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

1. **Vždy `jednani/archive/`, ne `jednani/pecky-jednani.json`.**
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
  pro vybrané projekty. Zbytek ze 197 aktivit plánu (183 v původní verzi) nebyl proti plnému archivu
  a všem 148 dotacím systematicky prověřen — dokud se to nestane, netvrdit o nich,
  že se nerealizovaly.

## Stav sekcí

Rozcestník: kdy se u které sekce naposledy kontroloval zdroj a kdy se
naposledy změnil obsah. Řazeno od nejnověji změněné. Data jsou absolutní
datumy — stáří („před 6 dny") se dopočítává až při čtení, aby tabulka
nezastarala bez týdenního běhu. Restrukturalizace a refactory se sem
nezapisují, jen změny obsahu.

Tabulku build od 3. 10. 2026 vykresluje i na samostatné stránce
[Historie změn na webu](o-webu/changelog.html) (`/o-webu/changelog.html`,
zdroj `content/changelog.html`, odkaz na konci stránky O webu) — zapisuje
se sem, na stránku samotnou se nic ručně nepíše.

| Sekce | Režim | Kontrola | Změna | Co naposledy |
|---|---|---|---|---|
| [Lidé](lide/README.md) | na vyžádání | 1. 11. 2026 | 1. 11. 2026 | tajemnice Bc. Pavlína Nepovímová: doplněno, že její mobil je telefonní kontakt v době zasedání zastupitelstva (podle pozvánek ZM 2022–2026) |
| [Jednání](jednani/README.md) | týdně | 31. 10. 2026 | 31. 10. 2026 | zápis a usnesení RM 38/2026 (26. 10. 2026; 7 usnesení UR-331 až UR-337-38/26, délky bodů, docházka s příchodem v 15:45) a nová Pozvánka RM 39/2026 (2. 11. 2026, 8 bodů); komise, výbory a školská rada beze změny |
| [O webu](o-webu/README.md) | týdně | 1. 11. 2026 | 1. 11. 2026 | Monitoring Facebooku města (kontrola 1. 11. 2026): říjen 2026 dokončen, 35 příspěvků (5 nových z 27.–30. 10.), počty reakcí obnoveny; archiv 96 měsíců, 2 103 příspěvků; sociální sítě (kontrola 1. 11. 2026, projito 55 z 55 odkazů): Instagram Nejen kavárna u Radu 518 → 517 |
| [Volby 2026](volby/2026/README.md) | týdně | 1. 11. 2026 | 31. 10. 2026 | promítnuty účty (kontrola 31. 10. 2026): Pečky NEXT FB 328 → 327, Pečky Pečákům 255 → 256, ODS 265 → 266, Pečky srdcem 126 → 128 (poslední příspěvek 27. → 28. 10.), skupina SPD 56 → 57 členů, ostatní beze změny (NAŠE PEČKY FB i IG, Pečky NEXT IG) |
| [Kalendář](kalendar/README.md) | týdně | 31. 10. 2026 | 31. 10. 2026 | nová akce Vánoční jarmark v MŠ Mašinka (9. 12. 2026, 17:00) z Aktualit města a událost Rada 39/2026 (2. 11. 2026) |
| [Voda](voda/README.md) | na vyžádání | 31. 10. 2026 | 31. 10. 2026 | dvě nové události: havárie vodovodu na Masarykově náměstí (30. 10. 2026) a plánovaná odstávka 2. 11. 2026 (J. A. Komenského, Chvalovická, V Kaštánkách, Nymburská, areál TONA, U Měnírny, Velké Chvalovice; Aktuality města a Pečeckých služeb), 60 událostí / 72 zdrojů |
| [Tělocvična](telocvicna/README.md) | týdně | 31. 10. 2026 | 31. 10. 2026 | 26. 10. 2026 RM 38/2026, bod 3: starosta informoval o sanačních pracích, zabezpečení stavby před zimou a opravě střechy školní kuchyně (bez usnesení); Aktuality města bez zmínky o zastavení stavby |
| [Smlouvy](smlouvy/README.md) | týdně | 31. 10. 2026 | 31. 10. 2026 | skupina 185 smluv / 104,6 mil. Kč (úřad 49 / 33,9 mil. Kč), přidána investiční dotace Středočeského kraje z Fondu JSDH a složek IZS (150 000 Kč, 27. 10. 2026) |
| [Dotace od města](dotace/README.md) | na vyžádání | 25. 10. 2026 | 25. 10. 2026 | nová stránka `/dotace/` (sekundární menu za Pokladnou): skládaný sloupcový graf dotací po letech 2016–2026 a příjemcích (77 smluv, 13 dodatků, 17,94 mil. Kč), blok Investiční akce Sokola 2019 (3,6 mil. Kč, smlouva č. 30/2019) a tabulka dodatků ke smlouvám (2 navýšení: AFK 2018 +20 000 Kč, Sokol 2025 +110 000 Kč) |
| [Obchvat](obchvat/README.md) | na vyžádání | 25. 10. 2026 | 25. 10. 2026 | nová stránka `/obchvat/` (hlavní menu před Tělocvičnou): blok „Obchvat města“ přesunut ze stránky Plán, přidán perex a situační mapa; oddíl „Co o obchvatu říká územní plán“ (2 km, 1,71 ha, S9,5/70, napojení, limity, doprava 2010 podle výroku ÚP po změně č. 2, 04/2024), dva řádky časové osy (2010, 04/2024), oddíl „Zástavba, která s obchvatem počítá“ (lokality Z08, Z09, Z11), upřesněná věta o koridoru v územním plánu a nový zdroj; z archivu jednání (2001–2026) a Pečeckých novin (2005–2026) doplněno 10 nových řádků časové osy a rozšířeno dalších 6 (2008, 10/2008 článek o 2,13 km a 85 mil. Kč, 2014 korespondence s krajem, 2016, 2017, 2019, 9. 2021, 2022–2024, 12/2025), oprava RM 10. 1. 2022 (usnesení ukládá doprojektování protihlukové stěny, ne schválení strategie výkupu), hlasování ZM 20. 10. 2021 (12:0:6), nové oddíly „Obchvat ve volebních programech“ a „Stará silnice II/329 a přechod u hřbitova“, odkazy na jednání a noviny |
| [Plán](plan/README.md) | na vyžádání | 25. 10. 2026 | 25. 10. 2026 | projity všechny dokumenty ze sekce „Strategický plán“ na pecky.cz (Souhrn, plné znění, Excel aktualizace 2020, 3 dodatky, Akční plán 2024–2026, Adaptační strategie, Zásady pro investory): nový výklad plnění plánu (Excel s aktualizací 2020: 197 z 339 úkolů 2016–2020 splněno, od 2021 stav chybí; původní Souhrn: 13 splněno), čísla 697 úkolů / 558,5 mil. Kč po aktualizaci 2020 vedle původních 718 / 360,8 mil. Kč, callouty Aktualizace plánu (dodatky 6/2020, 12/2020, 9/2021) a Jak se verze liší; řádky tabulky Sociální pracovník, Stacionář, Tělocvična (178 mil. Kč v Akčním plánu), Obchvat, Mlýnský náhon (2. etapa splněna 2018, 15 mil. Kč v Akčním plánu) a Veřejné WC doplněny; nová tabulka Další položky Akčního plánu 2024–2026 včetně srovnání částek původního plánu a Akčního plánu (tělocvična 140 → 178 mil. Kč, náhon 5,4 → 15 mil. Kč, kabiny 6 → 9,7 mil. Kč, městská policie, workout, cyklostezky, Benešák, WC, obchvat, vodojem); nahrazen odkaz na Adaptační strategii a Zásady pro investory shrnutím |
| [Volby 2018](volby/2018/README.md) | uzavřené | — | 25. 10. 2026 | oprava tématu Obchvat ve srovnání uskupení: 6 z 6 (dřív 5 z 6) — Sdružení ODS a nezávislých kandidátů má v programu (PN 9/2018, s. 10) bod „aktivnější zapojení do jednání se Středočeským krajem o dokončení obchvatu“ |
| [Na oběd](naobed/README.md) | denně | 1. 11. 2026 | 31. 10. 2026 | zpětně doplněno z historických fotografií na Facebooku: U Marka 29. 9.–2. 10. a 29.–30. 10. 2026, Siňorita 26. a 29. 9. 2026, U Stříkačky 29.–30. 9. a 29. 10. 2026 |
| [Pozemky](pozemky/README.md) | odvozená | 21. 10. 2026 | 18. 10. 2026 | nové fulltextové vyhledávání v tabulkách Nákup/Prodej (hledaný výraz v URL `?q=`, tlačítko Kopírovat odkaz); do tabulek doplněno 133 bodů ze starších jednání 2013–3/2021 (82 jednání z úřední desky a archivu města; po sloučení rady a zastupitelstva nákup 95 a prodej 44 unikátních obchodů; odebrány součty cen pod tabulkami; katastr z textu bodu nebo kontextu zápisu; nový `extract_rows_starsi()` v `update-pozemky.py`) |
| [Pro přespolní](okolo/README.md) | na vyžádání | 17. 10. 2026 | 17. 10. 2026 | nová stránka `/okolo/` (sekundární menu): SVG mapa devíti obcí správního obvodu Peček s názvy a zvýrazněnou obcí Pečky (hranice z OpenStreetMap, generátor `okolo/update-mapa.py`, data `okolo/mapa.json`) |
| [Prostory](prostory/README.md) | odvozená | 21. 10. 2026 | 15. 10. 2026 | ordinace logopedie (čp. 292): po usnesení UR-323-36/26 stav „pronajato od 30. 10. 2026“ (5 100 Kč/měsíc, při využití 2 dny v týdnu 1 020 Kč, + služby 2 000 Kč, na dobu neurčitou), banner „Na programu“ odstraněn; vinotéka v Domě služeb (čp. 184): UR-325-36/26 — smlouva ukončena dohodou k 31. 12. 2026 |
| [Volby](volby/README.md) | odvozená | — | 10. 10. 2026 | graf „Volební účast stoupá“ doplněn o sloupec 2026 (53,68 %, 1 964 lidí), upraven text pod grafem a zdroje |
| [Volby 2014](volby/2014/README.md) | uzavřené | — | 10. 10. 2026 | nová stránka `/volby/2014/`: výsledky pěti uskupení, tabulka 21 zvolených podle osobních hlasů s funkcemi (ČSÚ, Pečecké noviny 11/2014 a 12/2014), tlačítko ročníku 2014 v rozcestníku; nadpis „Výsledky voleb“ nad kartami uskupení (2014, 2018, 2022), z rozcestníku odebrán popisek „Volby:“ |
| [Volby 2022](volby/2022/README.md) | uzavřené | — | 10. 10. 2026 | nový blok „Kolik kdo dostal hlasů od voličů?“: tabulka 21 zvolených zastupitelů podle osobních hlasů (zápis o výsledku voleb) s pořadím na kandidátce, funkcemi a legendou uskupení; zkrácený perex a texty kolem karet; chipy koalice/opozice v rohu karty, `party-body` v pravé polovině karty na velkých obrazovkách; odstraněn blok „Kdo byl zvolen“ |
| [Pečecké noviny](noviny/README.md) | týdně | 31. 10. 2026 | 26. 10. 2026 | vydání 10/2026 (Říjen 2026, 16 stran) doplněno do archivu (207. vydání celkem, 3176 stran) — PDF z pecky.cz, nahráno 26. 10. 2026; předchozí číslo 9/2026 přesunuto do roku 2026 v gridu, počet vydání v poznámce pod archivem 70; tiráž (redakce Alena Brantová, rada Zavřel, Kusá, Hartman) beze změny |
| [Domů](domu/README.md) | odvozená | — | 8. 10. 2026 | widget Pečecké noviny přepracován na zelený banner (`.banner--green`, `.banner--media`): obálka posledního čísla vlevo, počet vydání v archivu, tlačítko „Hledat v novinách“ a odkaz „Redakce“ |
| [PečkyBot](peckybot/README.md) | odvozená | 8. 10. 2026 | 8. 10. 2026 | index doplněn o 72 starších jednání z úřední desky (zápisy rady 2015–2016, usnesení ZM 2015–2021; ≈ 900 úryvků) a podstránky Kdo vede Pečecké noviny, Zhlédnutí záznamů, Odpracované hodiny, Nejdelší body jednání; rejstřík 1,6 → 2,0 MB (6 020 úryvků) |
| [Zakázky](zakazky/README.md) | týdně | 31. 10. 2026 | 6. 8. 2026 | zkontrolováno, beze změny — 193 výsledků na Hlídači stejně jako 5. 10., žádné nové ID |
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

## Historie změn

Podrobný deník běhů a úprav (nejnovější nahoře) je v
[`HISTORIE.md`](HISTORIE.md). Do tohoto souboru se zapisuje jen aktuální
stav; datovaný zápis běhu patří do `HISTORIE.md`.

## Publikování na GitHub Pages

Web běží na **https://dopecek.cz** z GitHub Pages tohoto repa
(`jakubspanihel/pecky.online`). Nasazení je automatické, žádné vlastní
workflow v repu není (`.github/workflows/` neexistuje).

**Jak se web dostane ven:**
1. Úprava zdroje: `content/<sekce>.html`, `assets/*`, data sekce atd.
2. Lokálně `python3 scripts/build.py`. Na GitHubu build **neběží** —
   vygenerované stránky (`index.html`, `<sekce>/index.html`,
   `sitemap.xml`, `robots.txt`) se commitují hotové. Bez buildu zůstane
   na webu stará verze, i když je upravený zdroj v repu.
3. Commit a push do `main` (přímo, nebo merge PR).
4. GitHub po každém pushi do `main` sám spustí vestavěnou akci
   **„pages build and deployment"** a obsah `main` zkopíruje na web.
   Trvá to zhruba 3 minuty. Běhy a jejich výsledek jsou v záložce
   [Actions](https://github.com/jakubspanihel/pecky.online/actions).

**Nastavení, na kterém to stojí:**
- Settings → Pages → Build and deployment: *Deploy from a branch*,
  větev `main`, složka `/ (root)`.
- `CNAME` v kořeni repa (`dopecek.cz`) určuje vlastní doménu. Nemazat
  — bez něj Pages spadnou zpět na `jakubspanihel.github.io/pecky.online/`,
  kde by kořenově-absolutní odkazy (`SITE_BASE_PATH = ''` ve
  `scripts/build.py`) nefungovaly.
- `.nojekyll` v kořeni vypíná Jekyll: soubory se servírují tak, jak
  jsou, včetně složek a souborů začínajících podtržítkem.

Lokální náhled před pushem: `python3 scripts/serve.py`
a `http://localhost:8000/` (viz začátek tohoto README).
