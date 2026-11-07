# DoPeček.cz

Neoficiální, nezávislý občanský projekt zpřehledňující veřejně dostupné informace
o samosprávě města Pečky (okres Kolín, Středočeský kraj).

## Technické řešení
Vícestránkový statický web — žádný
runtime framework, žádné externí závislosti (ani webová písma — jen systémová,
viz proměnné `--font-*` v `assets/styles.css`). Jediný
"build krok" je lokální generovací skript `scripts/build.py`, jeho
výstup jsou čisté statické soubory pro GitHub Pages.

## Metodika ověřování (POVINNÉ)

Než o čemkoli prohlásíš, že to „v datech není“ nebo že se to „nestalo“, prověř to
**vždy ve všech zdrojích a v jejich plné podobě**. Zkratky vedly už k prokazatelně
chybným závěrům.

1. **Vždy `jednani/archive/`, ne `jednani/pecky-jednani.json`.**
   Druhý jmenovaný je odlehčený index (jen názvy a texty usnesení). Plný archiv
   obsahuje kompletní zápisy včetně diskuzí, důvodových zpráv a bodů programu —
   řádově víc textu. Plný archiv čti nástroji Grep/Read, ne shellem
   (viz `TROUBLESHOOTING.md`).
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
6. **Aktuální obsah oficiálního webu města čti z `pecky.cz`** (přes
   claude-in-chrome; `web_fetch` kvůli bot-ochraně a JS často vrací prázdno).
   Starý web `pecky.as4u.cz` je od cca 3/2026 zamrzlý — hodí se jen pro
   starší a archivní obsah (úřední deska tam končí únorem/březnem 2026).
   Dlouhé stránky ulož a prohledávej Grepem, ne čtením celého výstupu.

Konkrétní případ, kvůli kterému toto pravidlo vzniklo: rekonstrukce kabin AFK
(dotace NSA 4 753 860 Kč, 2023) a revitalizace rybníka Benešák (OPŽP 3 146 174 Kč,
2019) byly nejprve chybně označeny za nerealizované — kvůli hledání v odlehčeném
indexu, špatnému názvu projektu a vzorku pouhých 20 nejnovějších dotací.

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
| [Na oběd](naobed/README.md) | denně | 7. 11. 2026 | 7. 11. 2026 | denní menu U Marka z 7. 11. 2026 a jídelníček školní jídelny na 9.–13. 11. 2026 |
| [Kalendář](kalendar/README.md) | týdně | 6. 11. 2026 | 6. 11. 2026 | Degustace moldavských vín (13. 11.): čas 20:00–23:00 a malý sál KD podle aktuality pecky.cz z 5. 11., doklad z pecky.cz jako první; nová stránka posledních přidaných akcí (nelinkovaná) |
| [O webu](o-webu/README.md) | týdně | 6. 11. 2026 | 6. 11. 2026 | sociální sítě (kontrola 6. 11. 2026, 52 účtů): počet sledujících se změnil u 7 účtů (např. FB skupina Pravoslavná obec +5, Pečky srdcem +2), nová aktivita u 12 účtů |
| [Jednání](jednani/README.md) | týdně | 6. 11. 2026 | 6. 11. 2026 | Zhlédnutí záznamů zastupitelstva na YouTube: 9 845 zhlédnutí u 34 záznamů (+77), ZM 8/2026 má 623 zhlédnutí |
| [Tělocvična](telocvicna/README.md) | týdně | 6. 11. 2026 | 4. 11. 2026 | 2. 11. 2026 Pečecké noviny 11/2026, s. 3: v první polovině října jednání se soudním znalcem, termín obnovení stavebních prací zatím nelze stanovit; RM 39/2026, bod 3: dozdívání atik, zateplení jídelny a schůzka se soudním znalcem 9. 11. 2026 (bez usnesení) |
| [Pečecké noviny](noviny/README.md) | týdně | 4. 11. 2026 | 4. 11. 2026 | nová podstránka Pečecké noviny pro sociální sítě (`/noviny/insta.html`): banner posledního čísla jako obrázek 1:1, 4:5, 3:4; odkaz sdílecí ikonou v bloku Poslední číslo |
| [Smlouvy](smlouvy/README.md) | týdně | 4. 11. 2026 | 4. 11. 2026 | skupina 156 smluv / 97,0 mil. Kč (úřad 49 / 33,9 mil. Kč) podle Hlídače státu k 4. 11. 2026 (dřív 185 / 104,6 mil. Kč, úbytek u zdroje), žádná nová smlouva |
| [Volby 2026](volby/2026/README.md) | na vyžádání | 3. 11. 2026 | 3. 11. 2026 | z tabulky uskupení odstraněny odkazy na sociální sítě a počty sledujících, ponechán odkaz na kandidátní listinu |
| [Lidé](lide/README.md) | na vyžádání | 1. 11. 2026 | 1. 11. 2026 | doplněno 19 fotek kandidátů 2018 (NAŠE PEČKY str. 8, ODS str. 10) z Pečeckých novin 9/2018 |
| [Voda](voda/README.md) | na vyžádání | 31. 10. 2026 | 31. 10. 2026 | dvě nové události: havárie vodovodu na Masarykově náměstí (30. 10. 2026) a odstávka 2. 11. 2026; celkem 60 událostí / 72 zdrojů |
| [Dotace od města](dotace/README.md) | na vyžádání | 25. 10. 2026 | 25. 10. 2026 | nová stránka `/dotace/`: sloupcový graf dotací po letech 2016–2026 a příjemcích (77 smluv, 17,94 mil. Kč), investiční akce Sokola 2019 a tabulka dodatků ke smlouvám |
| [Obchvat](obchvat/README.md) | na vyžádání | 25. 10. 2026 | 25. 10. 2026 | nová stránka `/obchvat/`: blok přesunut z Plánu, přidána situační mapa, oddíl o územním plánu, časová osa 2001–2026 z archivu jednání a Pečeckých novin, zástavba lokalit Z08/Z09/Z11, obchvat ve volebních programech a oddíl o staré silnici II/329 |
| [Plán](plan/README.md) | na vyžádání | 25. 10. 2026 | 25. 10. 2026 | projity všechny dokumenty strategického plánu na pecky.cz: nový výklad plnění plánu (Excel 2020: 197 z 339 úkolů 2016–2020 splněno), čísla 697 úkolů / 558,5 mil. Kč po aktualizaci 2020, tabulka dalších položek Akčního plánu 2024–2026 a srovnání částek |
| [Volby 2018](volby/2018/README.md) | uzavřené | — | 25. 10. 2026 | oprava tématu Obchvat ve srovnání uskupení: 6 z 6 (dřív 5 z 6) — Sdružení ODS a nezávislých kandidátů má v programu (PN 9/2018, s. 10) bod „aktivnější zapojení do jednání se Středočeským krajem o dokončení obchvatu“ |
| [Pozemky](pozemky/README.md) | odvozená | 21. 10. 2026 | 18. 10. 2026 | fulltextové vyhledávání v tabulkách Nákup/Prodej (`?q=` v URL, Kopírovat odkaz); doplněno 133 bodů ze starších jednání 2013–3/2021 (nákup 95, prodej 44 unikátních obchodů) |
| [Pro přespolní](okolo/README.md) | na vyžádání | 17. 10. 2026 | 17. 10. 2026 | nová stránka `/okolo/` (sekundární menu): SVG mapa devíti obcí správního obvodu Peček s názvy a zvýrazněnou obcí Pečky (hranice z OpenStreetMap, generátor `okolo/update-mapa.py`, data `okolo/mapa.json`) |
| [Prostory](prostory/README.md) | odvozená | 4. 11. 2026 | 15. 10. 2026 | ordinace logopedie (čp. 292): po UR-323-36/26 pronajato od 30. 10. 2026 (5 100 Kč/měsíc + služby); vinotéka v Domě služeb (čp. 184): smlouva ukončena dohodou k 31. 12. 2026 |
| [Volby](volby/README.md) | odvozená | — | 10. 10. 2026 | graf „Volební účast stoupá“ doplněn o sloupec 2026 (53,68 %, 1 964 lidí), upraven text pod grafem a zdroje |
| [Volby 2014](volby/2014/README.md) | uzavřené | — | 10. 10. 2026 | nová stránka `/volby/2014/`: výsledky pěti uskupení, tabulka 21 zvolených podle osobních hlasů s funkcemi, tlačítko ročníku v rozcestníku |
| [Volby 2022](volby/2022/README.md) | uzavřené | — | 10. 10. 2026 | nový blok „Kolik kdo dostal hlasů od voličů?“: tabulka 21 zvolených zastupitelů podle osobních hlasů s pořadím na kandidátce, funkcemi a legendou uskupení; odstraněn blok „Kdo byl zvolen“ |
| [Domů](domu/README.md) | odvozená | — | 8. 10. 2026 | widget Pečecké noviny přepracován na zelený banner (`.banner--green`, `.banner--media`): obálka posledního čísla vlevo, počet vydání v archivu, tlačítko „Hledat v novinách“ a odkaz „Redakce“ |
| [PečkyBot](peckybot/README.md) | odvozená | 8. 10. 2026 | 8. 10. 2026 | index doplněn o 72 starších jednání z úřední desky (≈ 900 úryvků) a podstránky Noviny, Zhlédnutí, Odpracované hodiny, Nejdelší body; rejstřík 6 020 úryvků |
| [Zakázky](zakazky/README.md) | týdně | 4. 11. 2026 | 6. 8. 2026 | zkontrolováno, beze změny — 193 výsledků na Hlídači stejně jako 5. 10., žádné nové ID |
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

Lokální náhled před pushem: `python3 scripts/serve.py` a
`http://localhost:8000/`. Prostý `python3 -m http.server` ani otevření
stránek ze souboru (`file://`) nestačí: odkazy jsou kořenově-absolutní
a sekce Jednání, Pečecké noviny a Lidé si data načítají přes `fetch()`.
Struktura složek a seznam sekcí jsou v `CLAUDE.md` → „Struktura“.
