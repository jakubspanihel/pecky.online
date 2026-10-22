# Instrukce: shrnutí jednání (Nejdůležitější témata + Shrnutí)

Postup, jak z jednoho záznamu v sekci Jednání připravit krátké shrnutí
podle probíraných bodů. Funguje pro zastupitelstvo, radu, komise, výbory
i školskou radu.

**Kdy se volá:** vždy, když se do seznamu jednání přidá nové jednání
(nebo se u existujícího doplní zápis/usnesení) — jako krok kontrol
Jednání, Komisí a Výborů (viz `automation-kontrola-usneseni-cz.md` →
krok 8f, `README.md` → postupy pro výbory a komise, skilly
`DoPecek-jednani-check`, `-komise-check`, `-vybory-check`).
Samostatně ji lze spustit i na přání nad libovolným záznamem.

**Vstup:** odkaz na konkrétní záznam jednání. **Výstup:** dva bloky,
**Nejdůležitější témata** a **Shrnutí**. Výstup se **vždy
uloží do nového souboru** `jednani/shrnuti/{datum}-{typ}.md` (§1b); u Rady města z něj web
sám sestaví banner na Domů (§9). Výstup se zároveň vypíše ve výpisu běhu.

## 1. Vstup: odkaz na jednání

Přijímané tvary odkazu:

| Tvar | Příklad | Význam |
|---|---|---|
| Web | `https://pecky.online/jednani/#rada-2026-10-12` | datum + typ z hashe |
| Web | `…/jednani/#zastupitelstvo-2026-10-07` | zastupitelstvo |
| Web | `…/jednani/#<id>` | komise/výbory/ŠR, např. `kontrolni-vybor-2026-08-28` |
| usneseni.cz | `https://mesto-pecky.usneseni.cz/verejne/<uuid>/zapis/` | `uuid` z URL (i z `…/usneseni/`) |
| Zkratka | „RM 36/2026“, „ZM 6/2026“ | typ + číslo + rok |

Odkaz se převede na záznam takto:

1. **Rada a Zastupitelstvo:** `jednani/pecky-jednani.json` → `meetings[]`,
   hledat podle `uuid`, nebo `type` + `date` (`#rada-RRRR-MM-DD` →
   `type: "Rada"`), nebo `type` + `number` + `year`.
2. **Komise, výbory, školská rada:** `jednani/komise.json`,
   `vybory.json`, `skolska-rada.json` → `meetings[]`, hledat podle `id`
   (shoduje se s hashem v URL).
3. **Starší jednání (do 2021):** `jednani/starsi-jednani.json` — záznam
   nemá agendu, jen `text` usnesení (často z OCR). Shrnout z něj, přiznat
   omezenou přesnost.

Když záznam nenajdu, **nic nehádat** — říct, co se hledalo, a požádat
o jiný odkaz. Když záznam existuje jen s pozvánkou (bez zápisu,
`resolutions` prázdné), shrnout jen program a výslovně uvést, že zápis
ještě není zveřejněn.

Bannery „Z rady města“ a „Ze zastupitelstva“ na Domů zobrazí i jednání, které má jen Pozvánku: u ní
je nad tlačítkem poznámka „Vybrané body z pozvánky. Zápis zatím není
k dispozici.“ (generuje build podle chybějícího `links.minutes`). Po
doplnění zápisu se shrnutí **celé přepíše** podle zápisu (stejný soubor,
bez ponechání bodů z pozvánky) a poznámka zmizí sama při dalším buildu.

## 1b. Kam se výstup ukládá

**Pro každé nové jednání vždy vytvoř nový soubor** (nikdy nepřepisuj
shrnutí jiného jednání):

```
jednani/shrnuti/{datum}-{typ}.md
```

Název **začíná datem** (`RRRR-MM-DD`), typ jednání je suffix — soubory se
tak v adresáři řadí chronologicky. `{typ}` je část hashe jednání na webu
bez data: `rada`, `zastupitelstvo`, `financni-vybor`, `kontrolni-vybor`,
`sportovni-komise`, `kulturni-komise`, `stavebni-komise`, `skolska-rada` …
(hash `kontrolni-vybor-2026-08-28` → `2026-08-28-kontrolni-vybor.md`).
Příklad: `jednani/shrnuti/2026-10-12-rada.md`. Soubor se commituje (na
rozdíl od `jednani/Data/`).

**Formát souboru** (jednoduchý Markdown, web zvládá jen toto):

```markdown
## Nejdůležitější témata
1. **Název tématu** — jedna věta.
2. **…**

## Shrnutí
Hlavička jednou větou.

- **Štítek (UR-323-36/26):** text.
- **…**

*Shrnutí vychází z … ; zápis z diskuse nebyl čten.*
```

Žádné jiné značky (bez nadpisu `#`, tabulek, odkazů `[]()`). Zmínky
„RM 36/2026“, „UR-…/26“ web odkáže sám. Při doplnění zápisu k již
shrnutému jednání se soubor **přepíše novou verzí** (stejný název),
ne duplikuje.

## 2. Co se z záznamu čte

Pole u Rady a Zastupitelstva (`pecky-jednani.json`):

- `agenda[]` — `n`, `t` (název bodu), `predkladatel`, `duvodova_zprava`
  (nejlepší zdroj věcného obsahu), `duration_seconds`.
- `resolutions[]` — `n` (číslo usnesení), `item` (název bodu), `text`
  (znění), `pro` / `proti` / `zdrzel`.
- `attendance` — `present`, `total`, `present_names`, `absent_names`,
  `changes` (odchody a příchody během jednání).
- `venue`, `duration_seconds`, `links` (zápis, usnesení, pozvánka, PDF,
  audio).

U komisí, výborů a ŠR navíc `summary[]` (hotové věcné shrnutí z zápisu —
vychází se z něj, protože tato jednání často nehlasují) a `chair`.

Odkaz na zápis (`links.minutes`) se nenačítá automaticky. Přečíst ho
jen tehdy, když data nestačí (např. bod bez `duvodova_zprava` a bez
usnesení) — a pak to ve výstupu uvést.

## 3. Postup

1. Najít záznam (§1) a zapsat si hlavičku: typ, číslo/rok, datum, místo,
   délka, přítomnost.
2. Projít `agenda[]` bod po bodu. Procedurální body (určení zapisovatele,
   schválení programu, kontrola plnění usnesení, „různé“) **do shrnutí
   nepatří**, jen se zmíní délka diskuse, pokud je výrazná.
3. Ke každému věcnému bodu přiřadit usnesení (`resolutions[]` podle
   `item`) a výsledek hlasování.
4. Vybrat **nejdůležitější témata** (§4).
5. Napsat **Shrnutí** (§5).
6. Zkontrolovat výstup proti §7.

## 4. Výstup 1: Nejdůležitější témata

2 až 4 témata, seřazená podle významu (ne podle pořadí v programu).
Zformulovat jako krátký nadpis + jedna věta, proč je téma důležité.

**Co téma zvedá nahoru** (kritéria, ne vyčerpávající seznam):

- peníze: částky, dotace, rozpočet, rozpočtová opatření, zakázky nad
  750 000 Kč, odpisy a prodeje majetku;
- majetek a stavby: prodej/koupě pozemku, pronájem nebytových prostor,
  dostavba tělocvičny, větší opravy a investice;
- spory a nesouhlas: usnesení s hlasy proti nebo zdržením, delší
  diskuse, odložené nebo stažené body;
- dopad na veřejnost: poplatky, školství, doprava, bezpečnost, volby;
- délka: bod s mimořádně dlouhou diskusí (v `agenda[].duration_seconds`
  vyčnívá nad ostatní body) nebo celkově neobvykle dlouhé či krátké
  jednání (`duration_seconds`; porovnat s typickou délkou stejného typu
  jednání, ne odhadem). Délku uvést konkrétně v minutách a u bodu napsat,
  kolik z celku zabral;
- věci, které se promítají do jiných sekcí webu (Tělocvična, Pozemky,
  Prostory) — u nich to ve výstupu **vždy uvést**, viz `CLAUDE.md`
  (kapitola Konvence, „Body jednání se promítají do sekcí…“).

Bod bez usnesení může být důležitý (např. informace starosty) — pak ho
označit jako „bez usnesení“.

## 5. Výstup 2: Shrnutí

**Hlavička jednou větou:** typ a číslo jednání, datum, místo, délka
(u neobvykle dlouhého/krátkého jednání s porovnáním),
kolik členů bylo přítomno a kolik usnesení se přijalo (a jestli
jednomyslně).

**Bulletky:** 5 až 10 odrážek, jedna na věcný bod nebo téma.
Pořadí podle programu. Každá odrážka:

- začíná tučným štítkem tématu (např. **Logopedie (UR-323-36/26):**),
- obsahuje konkrétní údaje (částka, plocha, termín, jméno nájemce,
  výsledek hlasování), které jsou doložitelné z dat,
- u usnesení uvádí číslo (`UR-…` / `UZ-…`).

**Závěrečná poznámka** (1 věta): z čeho shrnutí vychází (program,
důvodové zprávy, usnesení) a že zápis z diskuse nebyl čten, pokud tomu
tak je.

## 6. Pravidla textu

Platí `CLAUDE.md` → Konvence:

- **Česky, srozumitelně pro širokou veřejnost.** Zkratky a odborné
  pojmy při prvním výskytu rozepsat (JPO II. = jednotka požární
  ochrany).
- **Žádné „my“** (máme, jsme, našli jsme) ani interní slang. Psát
  věcně a neosobně.
- **Konkrétní časové údaje** (žádné „dlouho“, „často“) — vždy číslo
  nebo období.
- **Žádná vymyšlená data.** Každý údaj musí být v záznamu. Co chybí,
  se přizná („důvodová zpráva k bodu není“), nedomýšlí se.
- **Zmínky jednání jako odkazy** při použití na webu: „RM 36/2026“ →
  `/jednani/#rada-2026-10-12`, usnesení „UR-323-36/26“ → odkaz na
  jednání, na kterém bylo přijato. V chatové odpovědi stačí prostý text.
- **Soukromí:** údaje zakryté ve zdroji (`███…`, jména soukromých osob
  v nájmech) nerekonstruovat ani nehádat; psát „nájemkyně“, „nájemce“.
  Nepravomocně rozhodnuté věci konkrétních zaměstnanců a podobné citlivé
  detaily do shrnutí nedávat (stejně jako v datech, viz README sekce
  Komise).
- **Nehodnotit.** Shrnutí popisuje, co se projednalo a jak se
  hlasovalo, bez vlastního názoru a bez politických soudů.
- **Datum a budoucí termíny:** budoucí datum na webu má vždy chip
  s relativním údajem (`.fut-chip`), viz `CLAUDE.md`.

## 7. Kontrola před odevzdáním

- Všechny částky, plochy, data a čísla usnesení opsané ze záznamu a
  ověřené zpětným porovnáním.
- Počet usnesení a hlasování odpovídá `resolutions[]` (`pro`/`proti`/
  `zdrzel`); u rady počítat `present` v době hlasování (viz
  `attendance.changes` — odchod člena mění počet hlasů).
- Žádný bod z programu s usnesením nechybí, procedurální body nejsou
  vypisovány.
- U bodů, které patří do sekcí Tělocvična / Pozemky / Prostory, je to
  uvedeno.
- `grep -iE "\b(máme|jsme|naše|našich|nám|nás)\b"` na výstupu nic
  nenajde (kromě citací).

## 8. Vzorový výstup

Rada města 36/2026 (12. 10. 2026) — viz záznam
`#rada-2026-10-12`.

> **Nejdůležitější témata**
> 1. **Stavba tělocvičny u ZŠ** — kontrolní den, sanace školní kuchyně,
>    přizvaný soudní znalec z ČVUT (bez usnesení; promítá se do sekce
>    Tělocvična).
> 2. **Nebytové prostory** — nový nájemce logopedie ve zdravotním
>    středisku a ukončení nájmu vinotéky v Domě služeb (sekce Prostory).
> 3. **Oplocení dětského hřiště na sídlišti** živým plotem.
>
> **Shrnutí**
> Rada se sešla 12. 10. 2026 v obřadní síni radnice, jednání trvalo
> 1 h 54 min, přítomno bylo 6 ze 7 členů. Přijala 5 usnesení,
> všechna jednomyslně.
> - **Aktuální informace starosty (bez usnesení):** výsledky voleb do
>   zastupitelstva a do třetiny Senátu, stav stavby tělocvičny,
>   dotace Středočeského kraje 150 000 Kč na dýchací přístroje pro
>   JPO II.
> - **Logopedie (UR-323-36/26):** nájem 38,3 m² ve zdravotním středisku
>   čp. 292 od 30. 10. 2026 na dobu neurčitou, 5 100 Kč měsíčně
>   (při využití 2 dny v týdnu 1 020 Kč) + 2 000 Kč zálohy na služby.
> - **Dětské hřiště (UR-324-36/26):** živý plot z tavolníků s dřevěnými
>   vrátky a tříletou péčí, realizace březen–květen 2027, přímé
>   zadání s průzkumem trhu (do 750 000 Kč bez DPH).
> - **Vinotéka, Dům služeb čp. 184 (UR-325-36/26):** nájem skončí
>   dohodou k 31. 12. 2026 (výpověď podána 2. 10. 2026).
> - **MŠ Mašinka (UR-326-36/26):** provoz přerušen od 23. 12. 2026
>   do 3. 1. 2027, úplata se nesnižuje.
>
> *Shrnutí vychází z programu, důvodových zpráv a usnesení; zápis
> z diskuse nebyl čten.*

## 9. Zobrazení na webu: banner „Z poslední Rady města“

Shrnutí se **nezobrazuje** v detailu jednání v sekci Jednání (tam je
program, usnesení a zápis). Využívá se jen takto:

- **Rada města a zastupitelstvo:** soubory `{datum}-rada.md` a
  `{datum}-zastupitelstvo.md` se zobrazí v bannerech **„Z rady města“**
  (bordó) a **„Ze zastupitelstva“** (modrý) na Domů (blok *Nejdůležitější témata*,
  tlačítko s číslem jednání → `/jednani/#rada-RRRR-MM-DD` resp.
  `#zastupitelstvo-RRRR-MM-DD`, odkaz „Všechna jednání“). Oba bannery jsou v levém
  sloupci mřížky Domů pod sebou, **nahoře je ten s novějším jednáním** (podle
  data konání). Generuje je `_dash_shrnuti()` v `scripts/build.py`; šipky v záhlaví
  listují ke starším jednáním. V HTML Domů je 5 nejnovějších, ostatní se při
  listování načtou z `jednani/rada-shrnuti.json` / `zm-shrnuti.json` (generuje
  build, needitovat). Po vytvoření souboru stačí `python3 scripts/build.py`.
  - **Budoucí jednání a jednání jen s pozvánkou:** nemá-li jednání zápis
    (`links.minutes`) ani soubor shrnutí, build samo vezme první věcné body programu
    z pozvánky (`agenda[]`, bez rutinních bodů) a slide označí chipem „za N dní“
    a poznámkou „Vybrané body z pozvánky“. Soubor shrnutí z pozvánky psát jen
    tehdy, když má být výběr témat kurátorský; po doplnění zápisu se shrnutí
    napíše (nebo přepíše) podle zápisu.
  - Shrnutí pro zastupitelstvo jsou zatím psaná pro jednání 4/2026 až 7/2026
    (24. 6.–7. 10. 2026); starší zastupitelstva se v banneru nezobrazují.
- **PečkyBot (všechna jednání):** `python3 scripts/build.py` načte každý
  soubor `jednani/shrnuti/*.md` do znalostí PečkyBota — fulltext
  (`chunks_shrnuti()` v `scripts/peckybot_sources.py`, úryvky „Shrnutí
  jednání — …“) i dokumentu jednání, který vrací nástroj `cti_dokument`
  (pole `shrnuti_jednani` s `temata` a `shrnuti`, viz
  `scripts/build_peckybot_tools.py`). Nic se nedělá ručně; stačí soubor
  uložit se správným názvem (§1b) a pustit build. Závěrečná kurzívní
  poznámka o zdroji se do PečkyBota nepřenáší.
- **Ostatní jednání** (výbory, komise, ŠR): na webu se
  shrnutí zatím nezobrazuje, jen se předá PečkyBotovi (viz výše).

Vizuálně je to sdílený `.banner` (výchozí bordó, v levém sloupci mřížky Domů nad Pečeckými novinami, seznam
`.banner-topics` v `assets/styles.css`). Hotové 15. 10. 2026 (první soubor
`2026-10-12-rada.md`). Zpětné doplnění starších jednání je volitelné.

## 10. Otevřené body

- Pro zápisy bez `duvodova_zprava` (hlavně starší jednání) zvážit
  načtení PDF zápisu; zatím se jen přiznává neúplnost.
