# pecky.online

Neoficiální, nezávislý občanský projekt zpřehledňující veřejně dostupné informace
o samosprávě města Pečky (okres Kolín, Středočeský kraj).

## Obsah složky

- `index.html` — celá webová stránka (jeden soubor, HTML/CSS/JS, bez závislostí
  kromě Google Fonts přes CDN). Otevřete přímo v prohlížeči nebo nahrajte na
  GitHub Pages / jakýkoli statický hosting. Několik sekcí (Jednání, Pečecké
  noviny) si data načítá přes `fetch()`, proto je pro místní test potřeba
  spustit lokální server (např. `python3 -m http.server`), otevření
  `index.html` přímo ze souboru (`file://`) fetch v některých prohlížečích
  zablokuje.
- `pecky-jednani/` — vše k sekci „Jednání": `pecky-jednani.json` (odlehčený
  index pro fulltextové hledání na webu), `archive-2026-08-04.json`
  (kompletní datový snímek se všemi detaily vč. jmenovitých hlasování),
  `README.md`/`SPEC.md`/`automation-kontrola-usneseni-cz.md`/
  `automation-katastr-parcely.md` (zadání, rozhodnutí a postup průběžné
  aktualizace), `Data/{datum}/` (lokální archiv PDF zápisů a
  pozvánek — kvůli velikosti je v `.gitignore`, do repa se nenahrává),
  `scripts/` (pomocné skripty) a samostatná stránka `index.html`
  (stejný obsah bez hlavičky/navigace hlavního webu).
- `pecky-noviny/` — vše k sekci „Pečecké noviny": archiv PDF, obálky,
  fulltextový index, nástroje (`download.py`, `render_pages.py`) a
  samostatná stránka `index.html`. Viz `pecky-noviny/README.md`.
- `pecky-volby/` — vše k volebním ročníkům, jedna podsložka na ročník
  (`2018/`, `2022/`, `2026/`) s vlastním `README.md`. Součástí jsou i
  obrázky ročníku: skeny volební inzerce (`volebni-programy-2018/`,
  `volebni-programy-2022/`) a portréty zastupitelů zvolených 2022
  (`2022/zastupitele/`, používá je i panel Lidé).
- `img/` — jen celowebové obrázky, které nepatří žádné sekci:
  `img/favicons/` (ikony zdrojů) a `img/peckybot/`. Obrázky vázané na
  konkrétní sekci patří do složky té sekce.
- `pecky-zakazky/` — vše k sekci „Zakázky": `pecky-zakazky-ids.json`
  (kontrolní snímek ID zakázek pro denní diff, na webu se nezobrazuje)
  a `README.md` s pracovním postupem. Viz `pecky-zakazky/README.md`.
- Každá další sekce webu má vlastní složku `pecky-<sekce>/` s `README.md`
  (podrobnosti a datové soubory tam, kde nějaké má); u sekcí bez vlastních
  dat obsahuje složka jen krátký `README.md`. Přehled a odkazy viz kořenový
  `CLAUDE.md` → „Dokumentace jednotlivých sekcí".

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
  `pecky-jednani/archive-2026-08-04.json`; `pecky-jednani/pecky-jednani.json`
  je z něj odvozený odlehčený index pro hledání na webu. Viz
  `pecky-jednani/SPEC.md` pro popis původního exportu a
  `pecky-jednani/automation-kontrola-usneseni-cz.md` pro aktuální postup
  průběžného doplňování.

## Barevná paleta uskupení

Každé politické uskupení má na celém webu jednu pevně přiřazenou barvu — používá se
konzistentně u kartiček lidí, kartiček volebních programů, sloupcového grafu mandátů
i barevných teček (swatch) v tabulkách. Uskupení, které kandiduje opakovaně, si barvu
drží i při změně názvu.

**Tabulka barev se přesunula do [`pecky-volby/README.md`](pecky-volby/README.md)
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

1. **Vždy `pecky-jednani/archive-2026-08-04.json`, ne `pecky-jednani/pecky-jednani.json`.**
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

## Poslední aktualizace

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
2. Nahrajte `index.html` a složky sekcí (`pecky-jednani/`, `pecky-noviny/`,
   `pecky-zakazky/` a další) do kořene repozitáře
3. Settings → Pages → source: `main` branch, root
4. Web poběží na `https://<vaše-uživatelské-jméno>.github.io/pecky-online/`
