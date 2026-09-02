# pecky.online

Neoficiální, nezávislý občanský projekt zpřehledňující veřejně dostupné informace
o samosprávě města Pečky (okres Kolín, Středočeský kraj).

## Obsah složky

- **Vícestránkový statický web** (od migrace 30. 8. 2026 — viz
  `ARCHITEKTURA-MIGRACE.md`), bez runtime frameworku, bez závislostí
  kromě Google Fonts přes CDN. `content/<sekce>.html` (jen obsah dané
  sekce) + sdílené `templates/page.html`, `assets/nav.html`,
  `assets/footer.html`, `assets/styles.css`, `assets/common.js`,
  `assets/helpers.js` se skládají přes `scripts/build.py` do 14
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
- `volby/` — vše k volebním ročníkům, jedna podsložka na ročník
  (`2018/`, `2022/`, `2026/`) s vlastním `README.md`. Součástí jsou i
  obrázky ročníku: skeny volební inzerce (`volebni-programy-2018/`,
  `volebni-programy-2022/`) a portréty zastupitelů zvolených 2022
  (`2022/zastupitele/`, používá je i panel Lidé).
- `img/` — jen celowebové obrázky, které nepatří žádné sekci:
  `img/favicons/` (ikony zdrojů) a `img/peckybot/`. Obrázky vázané na
  konkrétní sekci patří do složky té sekce.
- `zakazky/` — vše k sekci „Zakázky": `pecky-zakazky-ids.json`
  (kontrolní snímek ID zakázek pro denní diff, na webu se nezobrazuje)
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
nezastarala bez denního běhu. Restrukturalizace a refactory se sem
nezapisují, jen změny obsahu.

| Sekce | Režim | Kontrola | Změna | Co naposledy |
|---|---|---|---|---|
| [O webu](o-webu/README.md) | denně | 2. 9. 2026 | 2. 9. 2026 | Sociální sítě: aktualizovány počty (streetpeopleofpecky 1 218, Pečky NEXT FB 291, ODS 213, IG Pečky NEXT 119) a data poslední aktivity |
| [Volby 2026](volby/2026/README.md) | denně | 2. 9. 2026 | 2. 9. 2026 | tabulka uskupení: aktualizovány počty sledujících a data poslední aktivity u 7 sociálních profilů |
| [Tělocvična](telocvicna/README.md) | hlídat | 2. 9. 2026 | 2. 9. 2026 | předsedkyně Kontrolního výboru A. Švejnohová zveřejnila na Facebooku výzvu — vadná dokumentace kuchyně prý z roku 2015 (piloty 8,5 m vs. skutečných 6,5–6,6 m), viní tehdejší vedení Urban/Paluska |
| [Plán](plan/README.md) | na vyžádání | 2. 9. 2026 | 2. 9. 2026 | řádek „Nová tělocvična a učebny ZŠ": stav → zastaveno, odkaz na novou sekci Tělocvična |
| [Lidé](lide/README.md) | na vyžádání | 1. 9. 2026 | 1. 9. 2026 | fotka Ing. Petra Dürra (Facebook profil A. Švejnohové, doplnil uživatel) |
| [Jednání](jednani/README.md) | denně | 2. 9. 2026 | 31. 8. 2026 | fotky u lidí místo iniciál, rozbalovací body programu |
| [Volby 2018](volby/2018/README.md) | uzavřené | — | 31. 8. 2026 | tabulka Výsledky voleb: kandidáti nahrazeni avatary zvolených zastupitelů |
| [Volby 2022](volby/2022/README.md) | uzavřené | — | 31. 8. 2026 | tabulka Výsledky voleb: kandidáti nahrazeni avatary zvolených zastupitelů |
| [Pozemky](pozemky/README.md) | odvozená | 30. 8. 2026 | 27. 8. 2026 | regenerace tabulek Nákup/Prodej |
| [Pečecké noviny](noviny/README.md) | denně | 2. 9. 2026 | 24. 8. 2026 ? | vydání 7–8/2026 |
| [Domů](domu/README.md) | odvozená | — | 24. 8. 2026 | brand header |
| [Smlouvy](smlouvy/README.md) | denně | 2. 9. 2026 | 20. 8. 2026 | 2 nové smlouvy |
| [Zakázky](zakazky/README.md) | denně | 2. 9. 2026 | 6. 8. 2026 | 1 nová zakázka |
| [Pokladna](pokladna/README.md) | na vyžádání | 6. 8. 2026 | 6. 8. 2026 | blok Bankovní účty |

Režimy: **denně** = má zdroj, který kontroluje denní rutina · **hlídat** =
čeká se na událost (volby 2026) · **na vyžádání** = kontroluje se, jen když
o to někdo požádá · **odvozená** = nemá vlastní externí zdroj, mění se
s jinou sekcí · **uzavřené** = historický ročník, nový obsah se nečeká.
Pomlčka ve sloupci Kontrola znamená „nebylo co kontrolovat", ne opomenutí.

Tabulku aktualizuje každá instrukce, která sáhne na obsah některé sekce —
automatická denní rutina i ručně vyvolaná: přepíše řádek dotčené sekce
(datum kontroly, u reálné změny i datum změny a sloupec „Co naposledy")
a přesune ho na správné místo v řazení. Ostatní řádky nechá být.

`?` u data znamená nedoložený odhad — nahradit, až se zjistí přesné datum.

## Poslední aktualizace

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
