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
| Nadcházející akce | `kalendar/udalosti.json` → `events`, jen kategorie `akce` a `volby` (kurzy a svoz odpadu by výpis zahltily) | 5 nejbližších akcí, odkaz na měsíc `/kalendar/#RRRR-MM/seznam`; DNES/ZÍTRA/POZÍTŘÍ štítek u toho, co je v dohledu (viz níže) |
| Jednání rady, zastupitelstva a výborů | `jednani/pecky-jednani.json` + `jednani/vybory.json` → `meetings` | „Příště“: ohlášená jednání Rady/ZM (max 2), i s DNES/ZÍTRA/POZÍTŘÍ štítkem; „Naposledy“: 3 poslední proběhlá jednání Rady/ZM s počtem usnesení, odkaz `/jednani/#rada-RRRR-MM-DD`; „Výbory — poslední zveřejněný zápis“ (od 29. 9. 2026): poslední proběhlé jednání finančního a kontrolního výboru zvlášť, odkaz `/jednani/#financni-vybor-RRRR-MM-DD` — výbory zveřejňují zápisy se zpožděním, mezi „Naposledy“ by se skoro nedostaly |
| Pečecké noviny | `noviny/pecky-noviny.json` → `editions` (nejvyšší `slug`) | titulní strana (`noviny/pages/<slug>/1.jpg`, je-li) + odkaz na PDF |
| Naposledy aktualizováno | `README.md` → „Stav sekcí“, sloupec „Změna“ (bez Domů) | 5 naposledy změněných sekcí; sloupec „Co naposledy“ se záměrně nepoužívá (je to interní pracovní log) |

Počty a vybrané kategorie jsou konstanty `DASH_*` na začátku bloku v
`scripts/build.py`. Styl: `.dash-*` v `assets/styles.css`.

### Budoucí položky a zastarávání mezi buildy
Ohlášená jednání a akce nesou `data-until` (ISO datum konce). Build jich
vypíše víc, než je vidět (rezerva zhruba na týden, nadbytečné mají
`hidden`); `assets/common.js` v prohlížeči skryje ty, které už proběhly,
a odkryje další v pořadí až do `data-max` seznamu. Když nezbude žádná
akce, ukáže se hláška `.dash-empty`; prázdné „Příště“ u jednání zmizí
i s nadpisem. Datum „Naposledy aktualizováno“ se přepočítává na stáří
(„aktualizováno včera“) stejnou funkcí `relDatum` jako tabulka Stav sekcí.

Vícedenní akce, která v době buildu už běží, má text „probíhá do …“ —
ten se počítá při buildu, ne v prohlížeči.

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
