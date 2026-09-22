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
    (RFC 5545). Od 22. 9. 2026 na stránku přímo nelinkovaný (viz
    „Odebírání kalendáře" níže) — pořád se ale generuje a je dostupný
    na `/kalendar/kalendar.ics`, jen bez odkazu z UI.
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

## Odebírání kalendáře

Od 22. 9. 2026 (na žádost uživatele) první věta perexu `/kalendar/`
odkazuje rovnou na veřejný Google Calendar (embed pro zobrazení v
prohlížeči):
```
https://calendar.google.com/calendar/embed?src=a81de8fe68a5e6d118ceeea3614ba159febf695e65b164cade86b682d58ef726%40group.calendar.google.com&ctz=Europe%2FPrague
```
a ve stejné větě (v závorce „dostupné také jako iCal") ještě na
přímý `.ics` feed téhož Google kalendáře (pro přihlášení v Apple/Outlook
apod., ne pro zobrazení v prohlížeči):
```
https://calendar.google.com/calendar/ical/a81de8fe68a5e6d118ceeea3614ba159febf695e65b164cade86b682d58ef726%40group.calendar.google.com/public/basic.ics
```
Druhá věta perexu (popis mřížky + odkaz na `/kalendar/akce/`) je od
téhož data na vlastním řádku (`<br>` uvnitř stejného `<p class="lede">`,
ne nový odstavec — první věta je CTA, zbytek je popis stránky).

Dřív byl na stránce přímý odkaz na `/kalendar/kalendar.ics` (dole pod
mřížkou) — ten zůstal, `.ics` se pořád generuje na stejném místě, jen
z UI přímo nelinkovaný (viz „Jak to funguje" výše). Odkaz na `basic.ics`
v perexu je jiný soubor (feed samotného Google kalendáře, ne repo).

**Čím se ten Google kalendář plní:**
`kalendar/scripts/sync-google.py`. Bere hotový `kalendar/udalosti.json`
(ne `.ics`) a srovná s ním obsah kalendáře přes Google Calendar API:
co je nové založí, co se změnilo přepíše, co ze zdroje zmizelo smaže.
Běh je idempotentní — ID události v Googlu je `sha1` ze `source_ref`,
takže opakované spuštění nic nezduplikuje; o to větší důraz na to, že
`source_ref` musí zůstat stabilní (viz „Schéma jedné události" níže).
Skript sahá jen na události, které sám založil (poznávací značka
`extendedProperties.private.pecky`) — co si do kalendáře přidá člověk
ručně, nechá být.

Spouští se **ručně**, po `update-kalendar.py`:
```
python3 kalendar/scripts/update-kalendar.py
python3 kalendar/scripts/sync-google.py --dry-run   # co by se stalo
python3 kalendar/scripts/sync-google.py             # zápis
```
`--dry-run` jen vypíše plán a nic nezapíše, `--limit N` omezí počet
zápisů (opatrný běh), `--no-delete` vypne mazání.

**Kde je ten druhý příkaz zapsaný jako povinný krok:**
`kalendar/automation-plakat-akce.md` → krok 6 (zápis akcí z plakátu)
a `jednani/automation-kontrola-usneseni-cz.md` → krok 8b (týdenní
kontrola jednání). Obojí s podmínkou: **chybí-li klíč, běh synchronizaci
vynechá a napíše to do shrnutí** místo aby spadl — cloudový checkout
repozitáře `.google-calendar-api-key.json` nemá, protože je
v `.gitignore`. Takový běh tedy nechá Google pozadu záměrně a čeká,
až `sync-google.py` spustíš u sebe. Automatizovat i ten poslední krok
by znamenalo dostat klíč do GitHub Actions jako secret — zatím vědomě
neuděláno, synchronizace je ruční.

- **Závislost:** `pip3 install google-api-python-client google-auth` —
  jediná externí závislost v celém repu, ostatní skripty jedou na
  standardní knihovně. Bez ní `update-kalendar.py` i `build.py` fungují
  dál, spadne jen tenhle skript.
- **Přístup:** servisní účet `pecky-kalendar-sync@
  norse-sequence-509316-d9.iam.gserviceaccount.com` (bez zalomení),
  kterému je kalendář nasdílený s právem
  „Provádět změny v událostech". Klíč je v `.google-calendar-api-key.json`
  v kořeni repa, je v `.gitignore` a **do gitu nepatří** (repozitář je
  veřejný). Cesta jde přebít proměnnou `PECKY_GOOGLE_KEY`, ID kalendáře
  přes `PECKY_GOOGLE_CALENDAR` nebo `--calendar-id`.
- **Dva převody navíc oproti `.ics`:** Google nepřijme událost bez konce,
  takže akce s časem a bez uvedeného konce dostane délku 2 h
  (`DEFAULT_DURATION_MIN`); a událost se zapisuje jako `transparent`
  s vypnutými upomínkami, aby odběrateli neblokovala jeho vlastní čas
  a nerozesílala upozornění. Kategorie navíc řídí barvu události
  (`BARVY` ve skriptu, drží se barev mřížky).

Samotná aktualizace `kalendar.ics` přes `update-kalendar.py` do Google
kalendáře **nic nepropisuje** — bez druhého příkazu výš zůstane Google
na starých datech. Při jakékoli změně schématu (`source_ref`, časové
pásmo, kategorie) projít i tenhle skript.

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
  - **Kontrola sociálních sítí je samoobslužná vůči `sources.json` —
    ne seznam k ručnímu udržování.** (Pravidlo, doplněno 22. 9. 2026 na
    žádost uživatele.) Na začátku kontroly Akcí vždy nejdřív vytáhnout
    z kořenového `sources.json` **aktuální** seznam všech záznamů, jejichž
    `url` obsahuje `facebook.com`, a zvlášť těch, co obsahují
    `instagram.com` — bez ohledu na `status`/`category`/na to, jestli je
    zdroj politické uskupení, spolek, podnik nebo cokoli jiného. Přibude-li
    do `sources.json` kdykoli v budoucnu nový facebookový nebo
    instagramový zdroj (třeba kvůli úplně jiné sekci webu), patří do
    příští kontroly Akcí automaticky — nečekat, až ho sem někdo ručně
    dopíše. Projít **všechny** stejným postupem, žádný nevynechávat a
    žádný nezvýhodňovat:
    - **Facebook** — `facebook.com/<profil>/events` (u skupin
      `facebook.com/groups/<id>/events`) vždy první, teprve pak fotky.
      Kde organizátor Facebook Události zakládá, je to strukturovaná data
      (datum, čas, místo) bez čtení plakátu okem — rychlejší a
      spolehlivější než OCR z obrázku. Zajímá jen záložka „Nadcházející"
      (existuje-li — řada organizátorů Události nezakládá vůbec, jen
      postuje plakáty, pak `/events` ukáže jen „Uplynulé" nebo nic —
      u takových zdrojů rovnou pokračovat na fotky, ne se vracet k
      Událostem znovu příště). Cenné i jako křížová kontrola už zapsaných
      akcí, ne jen zdroj nových — takhle 22. 9. 2026 vyšla najevo změna
      termínu u knihovny (viz níže).
    - **Instagram** — nemá obdobu Událostí, jen mřížka příspěvků řazená
      od nejnovějšího. Projít okem přes claude-in-chrome (poslední
      ~5–10 příspěvků), stejná technika jako u „Hospoda na hřišti" níže.
    - **Co zapsat:** stejná pravidla jako u jiných zdrojů (žádná akce bez
      data, viz krok 4 „Co vynechat" v `automation-plakat-akce.md`) —
      obsah akce se **nefiltruje podle politického ani jiného tématu**.
      Rovné zacházení znamená zapsat, co je skutečně akce, u kteréhokoli
      zdroje stejně — ne cenzurovat nebo zvýhodňovat podle toho, kdo
      pořádá. (Dřív, 22. 9. 2026, tu bylo kritérium vynechávat „volební
      mítinky, debaty pořádané jako kampaň" — zrušeno týž den na žádost
      uživatele, viz `README.md` → „Stav sekcí" pro historii.)
    - **Organizátor** je vždy subjekt samotný (`organizer` = id v
      `lide/organizations.json`, `type: "politicke"` u uskupení), ne
      konkrétní osoba — „pořádá Alena Švejnohová" do `organizer` nepatří,
      viz „Nový pořadatel" níže.
    - **První běh podle tohohle pravidla (22. 9. 2026)** prošel všech 14
      tehdejších facebookových a 3 instagramové záznamy v `sources.json`
      — výsledky viz „Volební uskupení 2026" a jednotlivé organizátory
      níže. Příští běh může narazit na jiný soubor zdrojů, podle toho, co
      mezitím do `sources.json` přibylo jinde na webu.

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
    stojí za zmínku v `note`, ne za vynechání záznamu. **Má aktivně
    používané Facebook Události** (`facebook.com/knihovnapecky/events`)
    — 22. 9. 2026 odtud vyšla najevo „ZMĚNA TERMÍNU" u „S knížkou do
    života" (posun z 22. 9. na 30. 9. 2026), kterou původní
    plakát/pozvánka v `evidence[0]` neuváděl — opraveno, druhý doklad
    (`kind: "web"`, odkaz na `/events`) doplněn k záznamu.
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
  - **Vzdělávací centrum Pečky** — [vzcentrum.cz](https://www.vzcentrum.cz)
    (`sources.json` → `vzcentrum-cz`), zapojeno 22. 9. 2026 na žádost
    uživatele. Provoz Kulturního střediska (tatáž právnická osoba/IČO,
    viz `lide/organizations.json` → `kulturni-stredisko-pecky`), ale
    veden jako **vlastní pořadatel `vzdelavaci-centrum-pecky`** — jinak
    by ~1400 týdenních kroužků ve filtru „Pořadatel" splynulo s KD
    vlastním jednorázovým programem pod jedním čipem (generátor
    (`update-kalendar.py`) bere název čipu z registru podle `organizer`
    id, ne z `organizer_name` u jednotlivé události — ten se použije,
    jen když `organizer` chybí úplně).
    - **`/krouzky`** — 43 kroužků pro školní rok 2026/2027. Vynechány:
      „S kytarou za písničkou" (den/čas web neuvádí) a „Výletník"
      (měsíční celodenní výlety, web slibuje „termíny září–prosinec
      budou upřesněny v září", zatím žádné konkrétní datum) — case
      „akce bez data" z `automation-plakat-akce.md`. Sloučeno bez ztráty
      informace: 4× „Příprava na přijímačky" → 2 záznamy podle časového
      slotu (dvojkaři/trojkaři i gymnázia/jedničkáři běží ve stejný čas
      souběžně, zmíněno v `note`), taneční kurz 4× (dívky/chlapci ×
      odpolední/večerní) → 2 záznamy podle slotu (dívky a chlapci mají
      oddělenou kapacitu, ale tutéž fyzickou lekci). **Zbylých 37 sérií
      rozepsáno na jednotlivé týdenní termíny** od prvního výskytu dne
      v týdnu do konce školního roku **30. 6. 2027**, se stejným
      vynecháním prázdnin jako u TJ Sokol výše (podzimní, vánoční,
      pololetní, jarní pro okres Kolín, velikonoční). Web na rozdíl od
      TJ Sokol neuvádí explicitní „začínáme od" datum pro běžné kroužky
      — použit **stejný referenční týden jako u TJ Sokol (od 7. 9. 2026)**,
      přiznaná mezera, ne potvrzený fakt. **Taneční kurz** (organizátor
      zůstává `kulturni-stredisko-pecky`, ne Vzdělávací centrum — kontakt
      v popisu je `kspecky@seznam.cz`, jde o vlastní program KD jen
      cross-listovaný na vzcentrum.cz) má explicitní první lekci
      19. 9. 2026, plus tři prodloužené lekce a věneček na pevná data
      mimo pravidelný rozvrh (9./10., 30./31. 10., 20./21. 11.,
      11./12. 12. 2026, podle skupiny) — ty zapsány zvlášť jako
      jednorázové `akce`, ne jako další „kurz" výskyty.
    - **`/vikendovky` a `/klubko`** — k 22. 9. 2026 obsahují jen školní
      rok 2025/2026 (víkendovky 25. 9. 2025 – 4. 6. 2026, Klubko
      15. 9. 2025 – 4. 5. 2026), všechno proběhlé. Sezóna 2026/2027 tam
      zatím není zveřejněná — nic k zápisu. **Zkontrolovat znovu při
      každé další kontrole Kalendáře** (na žádost uživatele), ne čekat
      na zvláštní podnět. Klubko pro info: měsíční tematický kurz, vždy
      4 úterní termíny v měsíci, 18:00–19:30, potvrzeno z plakátů.
    - **`/tabory`** — prázdné („Počet nalezených táborů: 0"), typicky
      sezónní sekce plněná blíž k létu/prázdninám.
  - **ZUŠ Pečky** — [zuspecky.cz/rozvrh-hodin](https://zuspecky.cz/rozvrh-hodin/)
    (`sources.json` → `web-zuspecky-cz`, `organizer: zus-pecky`), zapojeno
    22. 9. 2026 na žádost uživatele. Stránka je výslovně označená
    „Předběžné rozvrhy hodin skupinových předmětů ve školním roce
    2026–2027" a „Změna vyhrazena!" — volnější status než u ostatních
    zdrojů, zapsáno i tak, ale beze snahy vydávat to za jistotu.
    Obsahuje jen **skupinové předměty** (individuální výuka nástroje na
    webu logicky není — rozvrh po jednotlivých žácích se nezveřejňuje):
    Přípravka (PHV), Hudební nauka po ročnících (1.–5.) a Hudební nauka
    se sborem (1.–3. roč.), a tři soubory (Small band, Pěvecký sbor,
    NeSoubor) — **10 řádků, 437 nových „kurz" záznamů** rozepsaných po
    týdnech od stejného referenčního startu jako u TJ Sokol/Vzdělávacího
    centra (7. 9. 2026 — web žádné konkrétní datum neuvádí) do konce
    školního roku 30. 6. 2027, stejné vynechání prázdnin. „Hudební nauka
    se sborem" **zapsána jako dva paralelní záznamy** (pondělí i úterý,
    na žádost uživatele) — stejný předmět, čas i vyučující, koná se
    ale dvakrát týdně, ne jen jednou. **Místo vždy s dovětkem
    „Základní umělecká škola Pečky"** (na žádost uživatele, stejné
    pravidlo jako „žádné zkratky" u Vzdělávacího centra výše) —
    `place` je „Učebna č. 7, Základní umělecká škola Pečky, Barákova 700,
    Pečky" nebo „Malý sál, Základní umělecká škola Pečky, Barákova 700,
    Pečky", ne jen „Učebna č. 7"/„Malý sál" samo o sobě. Vyučující
    v `description`, ne v `note` — jde o běžný, ne výjimečný údaj.
  - **ZŠ Pečky — Organizace školního roku 2026/2027** —
    [zspecky.cz](https://www.zspecky.cz/e_download.php?file=/data/uredni_deska/obsah243_2.pdf&original=Organizace_skolniho_roku_2026_2027_ZS_Pecky.pdf)
    (PDF na úřední desce, `sources.json` → `web-zspecky-cz`,
    `organizer: zs-pecky`), zapojeno 22. 9. 2026 na žádost uživatele.
    Na rozdíl od kroužků VCP/ZUŠ výše jde o **jednorázová a víceněnní
    data**, ne o týdenní rozvrh — zapsáno přímo z tabulky dokumentu,
    žádné dopočítávání. **14 nových `akce` záznamů:**
    - Prázdniny (podzimní, vánoční, pololetní, jarní pro okres Kolín,
      velikonoční, hlavní) — `place: null` (škola je zavřená, ne
      otevřená na nějakém místě), `time: null` (celodenní), vícedenní
      přes `date_end`. **Přímo potvrzuje termíny**, které se dřív u
      TJ Sokol/Vzdělávacího centra/ZUŠ odvozovaly obecně z
      archiv.msmt.gov.cz — tohle je od 22. 9. 2026 přednější, konkrétně
      pečecký zdroj pro stejné termíny.
    - Vydání výpisu vysvědčení (28. 1. 2027, konec 1. pololetí) a
      vydání vysvědčení (30. 6. 2027, konec školního roku) — jednotlivé
      dny, sloučeny s odpovídajícím „Ukončení X. pololetí" z dokumentu
      (stejný den, jedna událost, ne dvě).
    - Zápis do 1. ročníku — dva dny (27. a 28. 1. 2027) jako dva
      záznamy, různý čas i konec (12:30–17:00, resp. 12:30–15:00).
    - Třídní schůzky — tři termíny (3. 9. 2026, 12. 11. 2026,
      22. 4. 2027) v dokumentu, **první už proběhlý k datu kontroly**
      (nezapsán, stejné pravidlo jako u ostatních zdrojů). Zbylé dva
      zapsány jako **dva paralelní záznamy** (1. stupeň/2. stupeň, na
      žádost uživatele) — jiný čas (16:30/17:00), stejná budova.
    - **Vynecháno:** začátek vyučování 2026/2027 (1. 9., proběhlé),
      začátek vyučování 2027/2028 (1. 9. 2027, na žádost uživatele —
      mimo aktuální školní rok, o kterém dokument je), pedagogické rady
      (5 termínů — interní jednání sboru, ne veřejná akce), ředitelské
      volno (dokument sám říká, že zůstává jako rezerva bez
      konkrétního data).
  - **Volební uskupení 2026** — zapojeno 22. 9. 2026 na žádost uživatele,
    viz pravidlo „rovné zacházení" u kroku „U facebookových zdrojů vždy
    nejdřív zkontrolovat `/events`" výše. První kontrola všech pěti
    uskupení (22. 9. 2026):
    - **NAŠE PEČKY** — 2 nadcházející Události na
      [facebook.com/nasepecky/events](https://www.facebook.com/nasepecky/events)
      (debata s kandidátem do Senátu 29. 9. a **Hospodský kvíz o
      Pečkách a Velkých Chvalovicích** 6. 10., Bowling Bar Seňorita) a
      celá sekce „Akce" na [nasepecky.cz](https://nasepecky.cz/#akce) —
      dalších 5 položek, z toho 3 nové (Stand Up 25. 9., Benefiční
      koncert pro vitráže 28. 9., Slavnost v parku 3. 10.), zbylé dvě se
      s Událostmi kryjí. **Celkem 5 záznamů zapsáno**, žádný nevynechán
      pro politický obsah (viz „Co zapsat" výše — kritérium na vynechání
      kampaňového obsahu bylo 22. 9. 2026 zrušeno). Pečky NEXT (spojená
      kandidátka, vlastní FB profil) měla jen proběhlé Události, nic
      k zápisu navíc.
    - **ODS a nezávislí**, **Pečky Pečákům** — jen proběhlé/staré
      Události (ODS naposled 20. 9. 2026, Pečákům 2023), nic
      nadcházejícího.
    - **Lidé pro Pečky s podporou SPD** — FB skupina, ne stránka
      (`facebook.com/groups/<id>/events`, ne `/<profil>/events`) —
      výslovně „Žádné nadcházející události".
    - **Pečky srdcem** — Facebook Události vůbec nepoužívá, záložka na
      profilu chybí.
    - Žádné uskupení nebylo přeskočeno ani zvýhodněno — u čtyř z pěti
      nebylo co zapsat, ne že by se nekontrolovala.
    - **Druhá kontrola 22. 9. 2026** (test nového samoobslužného pravidla
      výše, zbylé dosud neprojité `facebook.com`/`instagram.com` záznamy
      ze `sources.json`): `facebook-svejnohova-osobni` má stejné dvě
      Události jako `facebook-nasepecky` (žádná nová), `facebook-lidovci-pecky`
      jen proběhlé — vč. „Rozloučení s létem!" 20. 9. 2026 (událost
      vytvořena „ODS a nezávislí Pečky"), ale to už je 2 dny stará akce,
      nezapisuje se zpětně. `facebook-mestopecky` a `facebook-tenis-spartak-pecky`
      bez nadcházejících Událostí. Nový instagramový zdroj
      **`instagram-nase-pecky`** (přibyl do `sources.json` mezitím, mimo
      tuhle kontrolu — přesně případ, na který samoobslužné pravidlo
      cílí) měl plakát „Pojďme se potkat — září a říjen 2026" — potvrzuje
      beze změny 4 už zapsané politické akce (termíny/časy sedí), zbylé
      4 položky plakátu (farmářské trhy 5. 9., káva s hejtmankou 8. 9.,
      beseda s pivovarníky 18. 9., Food festival 19. 9.) jsou k datu
      kontroly už proběhlé, nezapsány. `instagram-peckynext` má týž obsah
      jako `instagram-nase-pecky`, nic navíc. `instagram-streetpeopleofpecky`
      potvrzeně mimo téma (humorný/meme účet, ne akce).
  - **Facebook města** (`facebook-mestopecky`) — zatím nepřispěl žádnou
    akcí do `akce.json`; `/events` k 22. 9. 2026 ukazuje jen proběhlé
    (naposled Koncert 16. 4. 2025), žádná záložka „Nadcházející".
  - **FB skupina „Máme rádi Pečky"** (`facebook-group-mame-radi-pecky`,
    4,9 tis. členů, přidáno 22. 9. 2026) — na rozdíl od výše je to obecná
    komunitní nástěnka, ne profil jednoho pořadatele; záložka „Události"
    ukazovala jen jednu nadcházející akci, a tu sdílenou z jiné obce
    (Obnova krajiny Kolínska a Nymburska, Kostelní Lhota — mimo Pečky/
    Velké Chvalovice, nezapsáno). Feed „Diskuze" jinak samé nečitelné
    sdílené obrázky (`get_page_text` z nich nic nevytáhl) + repost už
    známého Hospodského kvízu. Nic k zápisu. Příště čekat spíš přesdílené
    cizí akce než vlastní obsah — u skupiny tohoto typu má smysl kouknout
    hlavně na záložku Události, hlubší scroll feedu se zatím nevyplatil.
  - **FB skupina „NAŠE PEČKY - komunita"** (`facebook-group-nase-pecky-komunita`,
    516 členů, přidáno 22. 9. 2026) — stejný vzorec jako u „Máme rádi
    Pečky" výše, i když je navázaná na uskupení NAŠE PEČKY: záložka
    „Události" měla jednu nadcházející akci, „Slavnosti podzimu a
    moštování" (3. 10. 2026), ale pořádá ji spolek Huslík v Poděbradech
    — mimo Pečky/Velké Chvalovice, nezapsáno. Feed měl navrchu jen
    nesouvisející AI reklamu na manikúru, dál se nenačetl. Nic k zápisu.

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
