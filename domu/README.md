# Instrukce k sekci: Domů (panel `domu`)

Referenční dokument pro práci na panelu `panel-domu` v `content/domu.html`
(generuje se do kořenového `index.html`, viz `scripts/build.py`). Doplňuje obecné instrukce projektu (Project instructions /
CLAUDE.md) — tohle je detail jen pro tuhle jednu sekci.

## Účel sekce
Úvodní stránka webu funguje jako dashboard „Co je nového“: ukazuje
nejnovější obsah z ostatních sekcí a odkazuje do nich. Vlastní datový
zdroj nemá — jen přebírá, co už ověřily jednotlivé sekce, takže tu
neplatí `.stamp`/`.callout` na úrovni jednotlivých položek (ověření visí
na cílové sekci). PečkyBot (maskot webu) a kontakt na zpětnou vazbu jsou
ve sdílené patičce `assets/footer.html`, ne v tomhle panelu.

## Dashboard — jak funguje
`content/domu.html` obsahuje jen nadpis, perex a značku `{{DASHBOARD}}`.
Build ji nahradí výstupem `render_dashboard()` ve `scripts/build.py`
(blok „Dashboard na homepage“). **Dashboard se needituje ručně** — mění se
sám s daty sekcí při každém `python3 scripts/build.py`.

| Karta | Zdroj | Co ukazuje |
|---|---|---|
| Aktuality (dřív „Nadcházející akce“) | `kalendar/udalosti.json` → `events`, kategorie `akce`, `volby`, `svoz`, `zastupitelstvo` (kurzy by výpis zahltily) | až 20 karet po skupinách, pravidla viz „Aktuality — co se zobrazuje“ níže; odkaz „Celý kalendář“ v záhlaví a tlačítko „Další ...“ pod výpisem |
| Jednání rady, zastupitelstva a výborů | `jednani/pecky-jednani.json` + `jednani/vybory.json` → `meetings` | jen proběhlá jednání (ohlášená tu od 30. 9. 2026 nejsou): „Naposledy“: 3 poslední proběhlá jednání Rady/ZM s počtem usnesení, odkaz `/jednani/#rada-RRRR-MM-DD`; „Výbory — poslední zveřejněný zápis“ (od 29. 9. 2026): poslední proběhlé jednání finančního a kontrolního výboru zvlášť, odkaz `/jednani/#financni-vybor-RRRR-MM-DD` — výbory zveřejňují zápisy se zpožděním, mezi „Naposledy“ by se skoro nedostaly |
| Příští zastupitelstvo (samostatný pás nad mřížkou, od 30. 9. 2026) | `jednani/pecky-jednani.json` → nejbližší `Zastupitelstvo` s `date` ≥ dnes (Rada ne); bez ohlášeného ZM se nevygeneruje | titulek-odkaz „Příští zastupitelstvo za N dní“ (7 a víc dní) / „je v pátek“ (2–6 dní, název dne) / „je zítra“ / „je dnes“ (odkaz na jednání) + datum, čas, místo (odpočet počítá `assets/common.js` v prohlížeči; po proběhnutí ZM se pás schová) |
| └ Odkazy pod zasedáním | `agenda` (program z pozvánky), `links.livestream` + `time` | „Program jednání“ → detail jednání v `/jednani/` (jen je-li `agenda` neprázdná); „Živé vysílání od HH:MM ↗“ → livestream (jen je-li znám odkaz i čas) |
| └ Volby v pásu „Příští zastupitelstvo“ | `kalendar/udalosti.json` → nejbližší událost kategorie `volby` (konec ≥ dnes) | druhý řádek pásu „Volby už za N dní“ / „jsou už zítra“ / „právě probíhají“ (počítá se k prvnímu dni hlasování), odkaz `/volby/`; pás se schová, až nezbude žádná položka |
| Pečecké noviny | `noviny/pecky-noviny.json` → `editions` (nejvyšší `slug`) | titulní strana (`noviny/pages/<slug>/1.jpg`, je-li) + odkaz na PDF |
| Nově na webu (`#flashnews`) | `domu/flashnews.json` — ručně vedený seznam | banner 50 % šířky nad Nadcházejícími akcemi: jedna položka na řádku, po 5 s fade na další, klik rozbalí všechny pod sebe (zastaví střídání a pulzování) |

Počty a vybrané kategorie jsou konstanty `DASH_*` na začátku bloku v
`scripts/build.py`. Styl: `.dash-*` v `assets/styles.css`.

### Banner „Nově na webu“ (`#flashnews`, plně ruční správa od 7. 10. 2026)
Položky jsou v `domu/flashnews.json`: pole objektů
`{"emoji": "🗓️", "text": "Kalendář akcí", "url": "/kalendar/"}`; pořadí v souboru
= pořadí střídání. **Nic se neodvozuje automaticky** (ani z tabulky Stav sekcí,
sloupec Widget už neexistuje) — na co se odkazuje, vybírá vždy vlastník webu.
Na pokyn se jen zapíše text a odkaz.

Pravidla textu: **3–4 slova**, před textem jedno emoji, věcně a neosobně
(copywriting pravidla z CLAUDE.md), `url` klidně hlouběji než kořen sekce
(např. `/jednani/absence.html`, `/volby/2026/#sliby2026` pro záložku).
Počet položek není omezen; rendering `_dash_zmeny()` ve `scripts/build.py`,
střídání a rozbalení `assets/common.js`, styl `.dash-nove*` v `assets/styles.css`.

### Budoucí položky a zastarávání mezi buildy
Ohlášená jednání a akce nesou `data-until` (ISO datum konce). Build jich
vypíše víc, než je vidět (rezerva zhruba na týden, nadbytečné mají
`hidden`); `assets/common.js` v prohlížeči skryje ty, které už proběhly,
a odkryje další v pořadí až do `data-max` seznamu. Když nezbude žádná
akce, ukáže se hláška `.dash-empty`; prázdné „Příště“ u jednání zmizí
i s nadpisem.

Vícedenní akce, která v době buildu už běží, má text „probíhá do …“ —
ten se počítá při buildu, ne v prohlížeči.

### Aktuality — co se zobrazuje
Pravidla jsou na dvou místech, která musí zůstat shodná: build
(`_dash_kalendar()` v `scripts/build.py` — výchozí HTML) a prohlížeč
(`assets/common.js`, blok „Dashboard: karty událostí“ — přepočet podle
dnešního dne, ať stránka nezastará mezi buildy).

1. **Pořadí a skupiny:** nejdřív akce dnešního dne (v rámci dne ty s přesným
   časem napřed), pak skupina **Probíhající**, pak **Další akce**.
2. **Probíhající** = vícedenní akce, které začaly před dneškem. Nemají chip,
   místo data je „trvá do …“ (bez pomlčky). Vícedenní akce, která začíná dnes,
   patří mezi dnešní akce.
3. **Další akce** = události z **jediného dne**: nejbližšího dne po dnešku, na
   který nějaká akce zbývá (často zítřek, o víkendu i pondělí apod.). Další
   dny se nevypisují — jsou za tlačítkem „Další ...“ v Kalendáři.
   **Výjimka:** je-li dohromady (dnešní + probíhající + Další akce) méně než
   5 karet (`DASH_AKCE_MIN`), přidávají se další dny (celé), dokud jich není
   aspoň 5; kvůli tomu může jít o víc dní.
4. **Limit:** celkem 20 karet (`DASH_AKCE_VIDET`); z nich má „Probíhající“
   vyhrazeno až 5 míst (`DASH_AKCE_BEZI`), aby je akce s časem nevytlačily.
5. **Chip** (dnes / zítra / pozítří / za N dní) je u dnešních a dalších akcí;
   čas není v chipu, ale v řádku pod ním („13:00–16:00“, u jiných dnů
   „čt 8. 10. 18:00“); u dnešní jednodenní akce se datum nevypisuje.
6. **Barva karty** = barva pořadatele (`lide/organizations.json`); pořadatel
   bez barvy má neutrální kartu.
7. **Prázdné skupiny zmizí i s nadpisem.** Nic dnes ani zítra → výpis začíná
   „Probíhající“ nebo „Další akce“; nic v žádné skupině → hláška „Žádná
   nadcházející akce zatím není v kalendáři zapsaná.“ (tlačítko „Další ...“
   zůstává).
8. **Zásoba:** build vypíše zásobu událostí (cca týden dopředu); po delší
   době bez buildu se výpis ztenčí a nakonec zůstane jen hláška z bodu 7.

### Štítek DNES/ZÍTRA/POZÍTŘÍ (doplněno 29. 9. 2026 na žádost uživatele)
Každá `<li data-until="…">` v obou kartách („Nadcházející akce“ i
„Příště“ u Jednání — stejná značka, stejný mechanismus) dostane za
odkazem štítek `<span class="tag kal-dnes/kal-blizko">`, počítaný v
`assets/common.js` (ne při buildu — ze stejného důvodu jako mizení
proběhlých položek výš, ať zůstane platný i dny po buildu). Datum
začátku bere z `data-from`, je-li (jen vícedenní akce v kalendáři),
jinak z `data-until` — u jednání je vždy stejné jako konec (jednodenní).
Sdílí CSS třídy `.tag.kal-dnes`/`.tag.kal-blizko` se stejným štítkem
v Kalendáři → Seznam (`assets/styles.css`, `kalRelTag()` v
`content/kalendar.html`) — logika je záměrně duplikovaná (dashboard
běží nezávisle na `content/kalendar.html`), ne sdílená funkce.

### Přidání další karty
1. Ve `scripts/build.py` napsat funkci `_dash_<nazev>()` vracející
   `_dash_card(titulek, odkaz_sekce, text_odkazu, tělo)` a přidat ji do
   seznamu `karty` v `render_dashboard()`.
2. Brát data jen ze souborů sekce (JSON, Stav sekcí) — nic nepsat ručně
   do HTML. Chybějící nebo prázdná data mají shodit build s jasnou
   chybou (`SystemExit('CHYBA: dashboard - …')`), ne tiše vynechat kartu.
3. Budoucí položky označit `data-until`, u seznamů s limitem dát `data-max`.
4. Doplnit tabulku výš a spustit `python3 scripts/build.py`.
