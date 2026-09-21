# Instrukce k sekci: Kalendář (panel `kalendar`)

Referenční dokument pro práci na panelu `panel-kalendar` v
`content/kalendar.html` (generuje se do veřejné stránky `/kalendar/`,
viz `scripts/build.py`). Doplňuje obecné instrukce projektu (Project instructions
/ CLAUDE.md) — tohle je detail jen pro tuhle jednu sekci.

## Účel sekce
Klasický tabulkový kalendář s termíny týkajícími se města Pečky.
Aktuální seznam zapojených zdrojů je vždy v callout boxu pod mřížkou na
`/kalendar/` — nekopírovat počet/výčet sem do perexu ještě jednou, ať
nevznikají dva zdroje pravdy, co se rozejdou (viz „Seznam zdrojů pod
mřížkou musí být vždy kompletní" v „Jak to funguje" níže). Kalendář akcí
z webu města je plánovaný, ale ještě nezapojený (viz „Zdroje" níže).

Akce mají navíc vlastní podstránku **`/kalendar/akce/`**
(`content/kalendar-akce.html`, registrovaná v `EXTRA_PAGES` ve
`scripts/build.py` — má tam i šesté pole `lastmod`, díky kterému má stejně
jako běžné sekce vlastní „Aktualizováno" pod nadpisem): měsíční výpis
s místem, časem, pořadatelem a odkazem na zdrojový plakát. Odznak akce
v mřížce na ni vede kotvou `#<id akce>` — mřížka sama zdroj ani místo
neunese. Od 22. 9. 2026 ukazuje **vždy jen nadcházející akce** (žádný
přepínač Období) — odkaz z mřížky na už proběhlou akci se tak nemá na co
doscrollovat, to je vědomý kompromis, ne přehlédnutá chyba.

## Jak to funguje

- **`kalendar/scripts/update-kalendar.py`** — generátor. Sesbírá
  události ze všech zapojených zdrojů (viz „Zdroje" níže) do jednoho
  společného schématu a zapíše dva výstupy:
  - **`kalendar/udalosti.json`** — data pro klientské vykreslení,
    `content/kalendar.html` si je natahuje přes `fetch()` (stejný vzor
    jako Jednání/Lidé/Noviny).
  - **`kalendar/kalendar.ics`** — stejné události ve formátu iCalendar
    (RFC 5545), stažitelné/přihlašovatelné tlačítkem na stránce.
- **`content/kalendar.html`** — měsíční mřížka vykreslená v prohlížeči
  (žádný build-time HTML pro jednotlivé dny): navigace měsícem
  (◀ / Dnes / ▶), filtr podle pořadatele (chipy, generované z dat —
  samostatný filtr podle typu/kategorie od 22. 9. 2026 zrušen, viz
  changelog v kořenovém `README.md`), barevné odznaky v buňkách dne
  (zelená = Rada přes `--field`, bordó = Zastupitelstvo přes
  `--burgundy`) prolinkované na `/jednani/#{typ}-{datum}`. Pod mřížkou
  je callout **„Kalendář čerpá z těchto zdrojů"** — bulletkový seznam
  všech zapojených zdrojů, každý jako odkaz na svůj profil/web (viz
  „Zdroje" níže).
- **Seznam zdrojů pod mřížkou musí být vždy kompletní.** Přibude-li nový
  organizátor/zdroj do `akce.json` (nový pořadatel v
  `lide/organizations.json` + nová `evidence[].source` v
  `sources.json`), **ve stejném kroku** doplnit i řádek do tohohle
  seznamu v `content/kalendar.html` — jinak je stránka v rozporu se
  skutečnými daty, ze kterých vykresluje mřížku. Kontrolovat aspoň při
  každém zapojení nového zdroje z podsekce „Zdroje" níže (pomůcka: počet
  položek v seznamu = počet pořadatelů v `POŘADATEL:` filtru + Jednání +
  Volby). Jednotlivé položky odkazují přímo na zdroj (profil na
  Facebooku/Instagramu, web ČSÚ, archiv novin), ne jen pojmenovávají typ
  média — „Facebook" samo o sobě bez odkazu na konkrétní profil
  nedává návštěvníkovi nic k ověření.

Po jakékoli aktualizaci dat kteréhokoli zdroje (viz „Zdroje" níže)
spustit:
```
python3 kalendar/scripts/update-kalendar.py
python3 scripts/build.py
```
První příkaz přegeneruje `kalendar/udalosti.json` a `kalendar/kalendar.ics`
ze všech zapojených zdrojů najednou. Druhý je potřeba, jen pokud se
změnil `content/kalendar.html` samotný (data soubory build.py
nekopíruje ani neupravuje — GitHub Pages/`scripts/serve.py` je
servíruje přímo ze složky `kalendar/`).

## Schéma jedné události
Společné pro všechny budoucí zdroje (ne jen Jednání) — nový zdroj
zplošťuje svá specifika na tahle pole, detaily zůstávají dostupné přes
`link`/`source_ref` zpátky do mateřské sekce.

```json
{
  "id": "jednani-zastupitelstvo-2026-09-16",
  "title": "Zastupitelstvo 6/2026",
  "date": "2026-09-16",
  "date_end": null,
  "time": "16:30",
  "all_day": false,
  "category": "zastupitelstvo",
  "link": "/jednani/#zastupitelstvo-2026-09-16",
  "description": "23 bodů programu",
  "place": null,
  "organizer": "mesto-pecky",
  "organizer_name": "Město Pečky",
  "image": null,
  "note": null,
  "source_ref": "1e69bf60-aa81-11f1-b174-0242c0a80002"
}
```

- **`category`** — řízený výčet, u Jednání `rada`/`zastupitelstvo`
  (shoduje se se slugem v `link`). Řídí barvu odznaku v mřížce
  (`.kal-ev-rada`/`.kal-ev-zastupitelstvo` v `assets/styles.css`) a filtr
  Vše/Zastupitelstvo/Rada na stránce.
- **`date_end`** — u vícedenní akce poslední den (včetně). Mřížka
  (`content/kalendar.html` → `kalDateRange()`) event zapíše do
  `KAL_EVENTS_BY_DATE` pro každý den mezi `date` a `date_end`, takže
  odznak je vidět po celou dobu trvání, ne jen první den — dny 2+ mají
  třídu `.kal-ev-cont` (tlumenější, šrafovaný odstín). `null`/chybí u
  jednodenní akce.
- **`time`/`all_day`** — `time` je vyplněný, jen dokud jednani data mají
  pole `time` (viz `jednani/pecky-jednani.json`: objevuje se u jednání,
  které má zatím jen Pozvánku, mizí po doplnění zápisu) — jinak `all_day:
  true`. Web jinak přesný čas zahájení jednání nedrží.
- **`image`** — jen cesta k souboru, nikdy base64/inline data (stejná
  konvence jako `volby/2022/zastupitele/*.jpg`). U Jednání zatím `null`.
- **`description`** — krátký teaser (u Jednání počet bodů programu,
  u akcí místo konání), ne duplikát obsahu. Plný obsah zůstává na stránce,
  kam vede `link`.
- **`place`** — místo konání, vypisuje se jako `LOCATION` v `.ics`
  a v tooltipu odznaku v mřížce. U Jednání `null` (web místo konání
  strukturovaně nedrží).
- **`organizer`** — id pořadatele v `lide/organizations.json` (rejstřík
  organizací celého webu, kalendář si vlastní seznam nedrží). U Jednání
  `mesto-pecky`. Řídí čipy „Pořadatel" nad mřížkou i na `/kalendar/akce/`.
- **`organizer_name`** — jméno k tomu id (`short_name`, jinak `name`),
  dopsané generátorem, aby ho klient nemusel dohledávat druhým fetchem.
  U pořadatele mimo rejstřík (cizí soubor, soukromý pořadatel) je vyplněné
  samo a `organizer` je `null`.
- **`source_ref`** — ID v zdrojových datech (u Jednání `uuid` z
  `pecky-jednani.json`) — používá se i jako `UID` v `.ics`, musí zůstat
  stabilní napříč přegenerováními.

## Zdroje

Kalendář sbírá události z více zdrojů do jednoho společného schématu
(viz „Schéma jedné události" výše). Každý zdroj má v
`kalendar/scripts/update-kalendar.py` vlastní funkci `build_*_events()`
a tady vlastní záznam s popisem a aktualizačními instrukcemi — nový
zdroj se přidává přesně takhle (nová funkce ve skriptu, přidat její
volání do `main()`, doplnit záznam sem), aby zůstal jeden přehledný
seznam místo rozházených poznámek po repu.

### Jednání rady a zastupitelstva — aktivní

- **Data:** `jednani/pecky-jednani.json`, funkce `build_jednani_events()`.
- **Kategorie:** `rada`, `zastupitelstvo`.
- **Aktualizace:** automaticky jako krok 8b týdenní kontroly Jednání —
  viz `jednani/automation-kontrola-usneseni-cz.md` → „8b. Kalendář".
  Ručně po jakékoli úpravě `pecky-jednani.json`:
  ```
  python3 kalendar/scripts/update-kalendar.py
  ```

### Kulturní a společenské akce — aktivní

- **Data:** `kalendar/akce.json`, funkce `build_akce_events()`.
- **Pořadatel ≠ zdroj.** `organizer` je ten, kdo akci pořádá (id
  v `lide/organizations.json`); `evidence[].source` je ten, od koho o ní
  víme (id v kořenovém `sources.json`). Akci může pořádat spolek a ohlásit
  ji facebook města — slévat obojí do jednoho pole by tabulku rozbilo,
  jakmile přibude druhý zdroj.
- **Kategorie:** `akce` (jednorázové akce — přednášky, divadlo, koncerty,
  slavnosti) a `kurz` (cokoli opakující se v pravidelném rytmu — taneční
  kurzy a prodloužené KD, ale i celý týdenní rozvrh oddílů TJ Sokol:
  tréninky, cvičení, kroužky). Oddělené proto, že kurzů/tréninků je
  v mřížce řádově víc než jednorázových akcí a přebily by je — filtr
  „Kurzy/tréninky/pravidelné akce" je umí schovat. (Pozn.: dřív popsáno úžeji jen jako „taneční
  kurzy" — rozšířeno 21. 9. 2026 po zapojení TJ Sokol, viz níže.)
- **Zdroje** — plakáty a příspěvky pořadatelů, vždy obrázek bez textové
  vrstvy, čtený okem přes claude-in-chrome, ne scraperem. Každý zapojený
  zdroj má vlastní posloupnost/kvirky, zaznamenané tady, aby je nemusel
  příští běh znovu objevovat:

  - **Kulturní středisko** — [facebook.com/kspecky](https://www.facebook.com/kspecky).
    Program vychází vždy na několik měsíců dopředu jako souhrnný plakát
    (např. „Program 9–12/2026" ve dvou příspěvcích: září+říjen,
    listopad+prosinec), k jednotlivým akcím pak ještě samostatné plakáty,
    které souhrnný program občas upřesňují nebo přepisují (viz „Rozpory
    mezi zdroji" níže).
  - **Městská knihovna** — [facebook.com/knihovnapecky/photos](https://www.facebook.com/knihovnapecky/photos).
    Na rozdíl od KD skoro vždy jeden plakát = jedna akce. Výjimka jsou
    sezónní programy jako „Zimní semestr v pečecké knihovně" — jeden
    plakát bundluje víc přednáškových cyklů Virtuální univerzity třetího
    věku (VU3V) najednou, každý s vlastním dnem/časem; rozepsat je na
    jednotlivé termíny stejně jako kurzy KD (viz krok 6 v
    `automation-plakat-akce.md`), ale kategorie zůstává `akce`, ne `kurz`
    — ten je vyhrazený jen tanečním kurzům, i „kurz pro seniory" proto
    patří pod `akce`. Chybí-li na plakátu čas (jen periodicita typu
    „každých 14 dní v úterý"), nechat `time: null` (celodenní), nedopočítávat.
    Profil běžně přeposílá i příspěvky bez konkrétního termínu
    („další várka knih právě dorazila") — ty nejsou akce, viz krok 4 „Co
    vynechat". Několik příspěvků má u data štítek Facebooku „AI obsah"
    (zřejmě nástroj na tvorbu plakátu, ne pochybnost o akci samotné) —
    stojí za zmínku v `note`, ne za vynechání záznamu.
  - **TJ Sokol Pečky** — dva zdroje dohromady:
    [facebook.com/tjsokolpecky/photos](https://www.facebook.com/tjsokolpecky/photos)
    (zkontrolováno 20. 9. 2026: profil sám o sobě jen nábory bez
    konkrétního data — turnaj, florbal, kynologický kroužek atd., viz
    níže) a **Pečecké noviny** (`sources.json` → `pecky-noviny`,
    `evidence[].kind: "zpravodaj"`), konkrétně vydání 9/2026, str. 19,
    celostránkový „Rozvrh hodin sokolovny — školní rok 2026/2027" —
    týdenní rozpis oddílů po dnech a hodinách. Na rozdíl od 20. 9. 2026
    (kdy jsem u samotného Facebooku profilu usoudil „nic k zápisu",
    protože chyběl konec sezóny) **21. 9. 2026 přibylo 893 opakovaných
    záznamů** (kategorie `kurz`, pořadatel `tj-sokol-pecky`) — na žádost
    uživatele, který zadal i to, kde dohledat konec sezóny:

    - **Rozsah:** každá pravidelná aktivita z rozvrhu (23 řádků — tenis,
      cvičení rodičů s dětmi, všestrannost po věkových skupinách,
      basketbal, volejbal, badminton, nácviky, oddíl šachu/stolního
      tenisu, taneční oddíl, kynologický kroužek) se rozepsala na
      jednotlivé týdenní termíny od prvního výskytu v týdnu od 7. 9. 2026
      do konce školního roku **30. 6. 2027** — poslední den vyučování
      2026/2027 podle MŠMT
      ([archiv.msmt.gov.cz](https://archiv.msmt.gov.cz/vzdelavani/organizace-skolniho-roku-2026-2027-v-zs-ss-zus-a)),
      protože rozvrh samotný konec neuvádí, jen začátek („Začínáme
      v týdnu od 7. 9. 2026").
    - **Prázdniny vynechané** ze stejného zdroje (MŠMT) — podzimní
      (29.–30. 10. 2026), vánoční (23. 12. 2026 – 3. 1. 2027), pololetní
      (29. 1. 2027), jarní **pro okres Kolín konkrétně** (1.–7. 2. 2027 —
      liší se region od regionu, ověřit při přegenerování na příští
      školní rok), velikonoční (25. 3. 2027). Skutečné přerušení oddílů
      TJ Sokol o prázdninách není přímo potvrzené, jen odvozené z toho,
      že rozvrh je vázaný na školní rok — přiznaná mezera, ne tvrzený fakt.
    - **`time` je začátek bloku**, ne přesný rozsah — u dvouhodinových
      bloků (basketbal, oba volejbaly, oba čtvrteční badmintony) je celý
      rozsah v `note`.
    - **Text pod tabulkou doplňuje, ne opravuje** — chyba objevená
      22. 9. 2026 a opravená: „Rodiče a děti" je ve sloupci rozvrhu
      16–17 (pondělí večer) A ZÁROVEŇ žlutě zvýrazněná poznámka pod
      tabulkou zvlášť uvádí „pondělí DOPOLEDNE 9:30–10:30" — to je
      **druhá, samostatná skupina stejného názvu v jiný čas**, ne oprava
      tabulkového záznamu. Obě zapsány jako dva paralelní záznamy
      (`kurz-…-rodice-a-deti` večer 16:00, `kurz-…-rodice-a-deti-dopoledne`
      dopoledne 9:30), každý po celou sezónu. Stejné pravidlo platí pro
      všechny ostatní texty pod tabulkou (Oddíl šachu, Oddíl stolního
      tenisu, Kynologický kroužek…) — ty nejsou v hlavní mřížce Po–Pá
      vůbec, takže u nich k záměně nedošlo, ale liší se typicky místem
      konání (klubovna, galerie, zahrada) místo pouhého jiného sloupce v
      téže tabulce. Před dalším podobným rozvrhem vždy nejdřív ověřit,
      jestli položka pod tabulkou má, nebo nemá stejnojmenný protějšek
      v hlavní mřížce — a pokud ano, řešit ji jako druhý záznam, ne jako
      přepis prvního.
    - **Rozpor Facebook × noviny** rozhodnutý ve prospěch Facebooku
      (vlastní kanál pořadatele, viz „Rozpory mezi zdroji" níže): kynologický
      kroužek je podle Facebooku 1× za 14 dní, noviny periodicitu vůbec
      neuvádí (jen „středa 16–17:30", jako by byl týdenní); taneční oddíl má
      na Facebooku podrobnější rozdělení dětská/dospělá skupina (15–16 /
      16–17), noviny jen jeden souhrnný termín (16–17) — u obou `evidence[0]`
      je Facebook, noviny jako druhý doklad.
    - **Vynecháno:** „Tenis Spartak" (stejný blok 13–15/16 h každý den v
      týdnu, bez rozlišujícího textu — vypadá jako trvalá rezervace kurtu
      pro jiný subjekt než TJ Sokol, ne akce k zapsání pod `tj-sokol-pecky`)
      a „Basketbal — městská sportovní hala", u kterého rozvrh výslovně
      píše „rozpis samostatně" a žádný rozpis nedává.
    - **Nová sekce Zdroje v `sources.json`:** `pecky-noviny` (obecný zdroj
      pro celý měsíčník, ne jen tohle vydání — příští citace z novin do
      Kalendáře už novou položku nepotřebují, jen nový `evidence[]` záznam).

    Rozsah 893 nových záznamů (dohromady 910 „kurz" proti 60 „akce") je
    záměrně velký — je to skutečně 23 pravidelných termínů týdně po většinu
    školního roku, ne chyba přemnožení. Filtr „Kurzy/tréninky/pravidelné akce" a filtr pořadatele
    „TJ Sokol Pečky" existují přesně pro tenhle případ, viz kategorie výše.

    Str. 16 novin má navíc samostatný basketbalový nábor pro ročníky
    2021/2022 (úterý 16–17, sokolovna) — stejný den/čas/místo jako
    „Sportovní přípravka" v hlavním rozvrhu, nejspíš táž aktivita jinak
    pojmenovaná pro nábor; zvlášť nezapisováno, aby nevznikla duplicita.
  - **Hospoda na hřišti** — [instagram.com/hospoda_na_hristi_pecky](https://www.instagram.com/hospoda_na_hristi_pecky/),
    zapojeno 22. 9. 2026 na žádost uživatele. Soukromý podnik (`type:
    "firma"` v `lide/organizations.json`, IČO se nepodařilo dohledat),
    ne městská ani spolková organizace — první pořadatel svého druhu
    v `akce.json`. Instagram nedrží spolehlivě datum posledního
    příspěvku (stejná mezera jako u ostatních Instagram účtů, viz
    `sources.json` → `instagram-streetpeopleofpecky`), na čtení
    jednotlivých příspěvků okem přes claude-in-chrome to ale vliv nemá —
    kontrola prošla posledních ~5 příspěvků profilu (mřížka „Příspěvky"
    je řazená od nejnovějšího) a zapsala ty s konkrétním budoucím
    termínem:
    - **Turnaj Křížová sedma** — jednorázový, datum i čas jasné z
      plakátu, kategorie `akce`.
    - **Hospodský kvíz** — plakát dává jen první termín a periodicitu
      („pravidelně každou středu od 7. 10. od 19:00"), ne kdy série
      končí. Na rozdíl od TJ Sokol tu není žádná instituce (školní rok),
      o kterou by šlo konec opřít. Zapsán proto ve dvou vrstvách jistoty
      (na žádost uživatele, 22. 9. 2026): první termín (7. 10.) přímo
      z plakátu, kategorie `kurz`; k němu dalších **8 týdnů dopředu
      (do 2. 12., ~2 měsíce od prvního termínu)** dopočítaných jako
      pravidelné pokračování — každý s poznámkou **„Negarantováno"**,
      ať je v `/kalendar/akce/` i v tooltipu mřížky na první pohled
      jasné, že jde o odhad, ne o potvrzený termín ze zdroje. Přibude-li
      časem výslovné zrušení nebo potvrzení konkrétní středy, opravit
      podle aktuálního stavu profilu, ne slepě prodlužovat dalších
      8 týdnů při každé kontrole.
    - **Zbytek profilu byl už proběhlý** (koncert Mameluk 4. 9., šipkový
      turnaj 8. 8., zábava 25. 7. — vše před 22. 9. 2026) — nezapisováno
      zvlášť, protože kontrola cílila na to, co se dá ještě někam
      pozvat, ne na vyčerpávající historický zápis celého profilu (na
      rozdíl od `pececke-filmove-leto`, který má vlastní ucelenou řadu).
      Výjimka: `akce-2026-08-22-pececke-filmove-leto-ovce` (22. 8.,
      „Letní kino – Ovce žerou první") je vlastně stejná akce, jakou
      hospoda na svém profilu taky zmiňuje („u nás na hřišti") — doplněn
      jako druhý doklad `evidence[]` k existujícímu záznamu KD, ne nový
      záznam.
  - **Facebook města** — zatím nezapojený zdroj, počítá se s ním.

  Proto `evidence` pole a ne jedno pole se zdrojem — nový zdroj přibývá
  stejným způsobem jako výše.
- **Doklad (`evidence[]`)** je pole, ne jedna hodnota: tutéž akci ohlásí
  pořadatel na svém profilu, město ji přesdílí a zpravodaj o ní napíše —
  to není trojí akce, ale jeden záznam se třemi doklady. **První doklad je
  ten, podle kterého jsou zapsané údaje**, ostatní ho potvrzují. Každý
  doklad má `source` (id v `sources.json`), `kind` (`plakat` ·
  `prispevek` · `web` · `zpravodaj` · `tisk` · `ustni` — řídí, jak se
  odkaz pojmenuje ve sloupci Zdroj; `zpravodaj` se od 22. 9. 2026
  zobrazuje rovnou jako „Pečecké noviny", ne obecně jako „zpravodaj" —
  mapování v `content/kalendar-akce.html` → `DOKLAD`), `url`, `label`
  (název konkrétního plakátu, ne profilu), `published` a `retrieved`.
- **Aktualizace:** skillem `pecky-online-kalendar-plakat` (předhodí se mu
  obrázek plakátu nebo odkaz na příspěvek, akce rozpozná a zapíše).
  Ručně po jakékoli úpravě `akce.json`:
  ```
  python3 kalendar/scripts/update-kalendar.py
  ```
- **Co do `akce.json` nepatří:** jednání rady a zastupitelstva, i když je
  program kulturního domu uvádí (16. 9. 2026 „Zastupitelstvo města, Malý sál
  KD od 16:30") — ta má kalendář z `jednani/pecky-jednani.json` a zápisem
  sem by v mřížce vznikly dva odznaky na tentýž termín.
- **Rozpory mezi zdroji** rozhoduje pořadí: vlastní kanál pořadatele →
  oficiální web města → zpravodaj nebo tisk → přepis třetí strany. Mezi
  doklady téže úrovně vyhrává novější (u Slavností sv. Václava 2026 se
  samostatný plakát lišil od souhrnného programu časem i názvem).
  Poražený údaj patří do pole `note` u akce — na podstránce se vypíše
  kurzivou pod názvem.
- **Nový pořadatel** se nejdřív založí v `lide/organizations.json`
  (`type: "spolek"` u spolků, `"firma"` u soukromého podniku, viz
  `lide/SPEC.md`), teprve pak se na jeho id odkazuje. Přibylo tam takhle
  spolu s Kalendářem: spolky `tj-sokol-pecky` a `pececky-okraslovaci-spolek`
  (20. 9. 2026), firma `hospoda-na-hristi-pecky` (22. 9. 2026, IČO se
  nepodařilo dohledat — pořadatel i bez něj). Pro jednorázového
  pořadatele mimo rejstřík (cizí divadelní soubor) slouží `organizer:
  null` + `organizer_name: "…"` textem; zakládat kvůli jedné akci
  organizaci nemá smysl, ale ztratit pořadatele taky ne.

### Volby — aktivní

- **Data:** `kalendar/udalosti-rucni.json`, funkce `build_volby_events()`.
  Ručně psaný soubor bez vlastního scraperu — na rozdíl od Jednání a Akcí
  se termín voleb nemění často. Stejný soubor může v budoucnu nést
  i další jednorázové ručně psané termíny, ne jen volby.
- **Kategorie:** `volby`.
- **Zdroj termínu:** [csu.gov.cz/informace-k-aktualne-vyhlasenym-volbam](https://csu.gov.cz/informace-k-aktualne-vyhlasenym-volbam)
  → sekce „Aktuálně vyhlášené volby" (proklik na konkrétní ročník, např.
  `csu.gov.cz/volby-2026`) — viz `sources.json` →
  `csu-informace-vyhlasene-volby`. K 20. 9. 2026 odtud potvrzeno: volby
  do zastupitelstev obcí (a souběžně do Senátu) 9.–10. října 2026,
  vyhlášeny rozhodnutím prezidenta republiky č. 117/2026 Sb. — shoduje
  se s dřívějším zdrojem mv.gov.cz citovaným v `content/volby2026.html`.
  Záznam v `udalosti-rucni.json` má `date: "2026-10-09"` a
  `date_end: "2026-10-10"` (oba volební dny). Od 21. 9. 2026 mřížka
  víckadenní události skutečně rozkresluje na každý den v rozsahu
  (`kalDateRange()` v `content/kalendar.html`, viz „Schéma jedné
  události" → `date_end`) — odznak je vidět v pátek i sobotu, dny 2+
  mají tlumenější (šrafovaný) odstín, ať je jasné, že jde o pokračování,
  ne o novou samostatnou akci. Do `.ics` souboru se propisuje stejně
  jako dřív, jako dvoudenní událost.
- **Odkaz:** `/volby/2026/` (stránka voleb, ne samostatná podstránka
  jako u akcí — u jediné události navíc není co vypisovat).
- **Pořadatel:** `mesto-pecky` (Městský úřad Pečky je registrační úřad
  pro volby) — stejné id jako u Jednání, proto se objeví ve stejném
  čipu „Pořadatel", ne zvlášť.
- **Aktualizace:** ruční — termín voleb se nemění často, netřeba
  zapojovat do týdenní kontroly. Před zápisem/změnou data vždy ověřit
  proti zdroji ČSÚ výše, ne jen převzít z `content/volby2026.html`.
  Ručně po jakékoli úpravě `udalosti-rucni.json`:
  ```
  python3 kalendar/scripts/update-kalendar.py
  ```

### Kalendář akcí z webu města — plánováno, zatím nezapojeno

- **Data:** vyžaduje vlastní scraper webu města (obdoba
  `pecky-online-noviny-check`), zatím neexistuje.
- **Až se zapojí:** vlastní `build_akce_events()` + zdrojový JSON
  doplňovaný scraperem.
- **Aktualizace:** kandidát na vlastní projektový skill
  (`pecky-online-*-check`) zapojený do týdenní kontroly, obdoba
  Jednání výše — až bude scraper hotový.
