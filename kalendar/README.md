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
mřížkou musí být vždy kompletní" v „Jak to funguje" níže).

Celá sekce žije na jediné stránce **`/kalendar/`** (`content/kalendar.html`)
ve dvou pohledech — mřížka a Seznam, přepínatelné bez reloadu (viz
„Přepínač „Zobrazit jako"" níže). Samostatná podstránka `/kalendar/akce/`
existovala do 24. 9. 2026 (`content/kalendar-akce.html`, měsíční tabulka
akcí) — na žádost uživatele zrušena, protože ji plně nahradil pohled
Seznam. **Odkazy na jednotlivou akci/kurz uvnitř webu neexistují vůbec**
(zrušeno 24. 9. 2026, druhá žádost uživatele týž den) — název akce/kurzu
teď odkazuje přímo na zdroj, ze kterého vznikl, viz „Odkaz na akci/kurz
vede rovnou na zdroj" v „Jak to funguje" níže.

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
  - **Přepínač „Zobrazit jako: Kalendář / Seznam"** (`segmented-control`,
    doplněno 24. 9. 2026 na žádost uživatele, na stejném řádku jako
    navigace měsícem, zarovnané vpravo přes `margin-left:auto`) —
    Kalendář je výchozí, stejná mřížka jako dřív. Seznam přepne na
    výpis vybraného měsíce (`#kal-list`) — od 25. 9. 2026 (na žádost
    uživatele) místo tabulky jako **bloky** (`.akce-blok` v
    `.akce-bloky`): první řádek den v týdnu + datum (u vícedenních
    rozsah) a čas (když ho zdroj nemá, o čase se nepíše nic), na
    konci téhož řádku pořadatel jako barevný chip (`.akce-poradatel`,
    jen u akcí/kurzů/svozů), pod ním název jako odkaz na detail se
    štítkem `kurz`/`svoz`, pak popis (`description`), místo
    a poznámka; levý okraj bloku nese barvu pořadatele, u jednání
    a voleb barvu kategorie jako v mřížce — nad daty z `kalendar/udalosti.json` (`KAL_ALL_EVENTS`),
    ne z `akce.json`, takže zahrnuje i jednání a volby, ne jen
    akce/kurzy. Bez vlastního sloupce Zdroj (v `udalosti.json` není
    `evidence[]`) — přiznaný rozdíl oproti zrušené `/kalendar/akce/`,
    ne opomenutí; místo toho název akce/kurzu sám odkazuje rovnou na
    zdroj, viz „Odkaz na akci/kurz" níže. Navigace měsícem i filtr
    pořadatele fungují v obou pohledech přes společnou funkci
    `kalShowView()`, která podle `KAL_VIEW` přepne viditelnost
    `#kal-grid`/`#kal-list` a zavolá odpovídající vykreslení — nová
    cesta (navigace, filtr, přepínač samotný) proto nesmí volat
    `kalRenderGrid()` přímo, jinak by se v pohledu Seznam neprojevila.
  - **Stav v URL** (doplněno 25. 9. 2026 na žádost uživatele) — měsíc
    a pohled se zapisují do hashe: `#RRRR-MM` = mřížka daného měsíce,
    `#RRRR-MM/seznam` = pohled Seznam. Příchod na `/kalendar/` bez hashe
    ho hned doplní na aktuální měsíc (`/kalendar/#2026-09`), takže jde
    konkrétní měsíc/pohled nasdílet nebo uložit do záložek. Zápis dělá
    `kalWriteHash()` uvnitř `kalShowView()` přes `history.replaceState`
    (stejně jako podzáložky v `assets/common.js`, listování měsíci tedy
    neplní historii prohlížeče); čtení `kalReadHash()` při načtení
    a v posluchači `hashchange` (ruční úprava adresy, odkaz zvenku).
    Neplatný hash (`#nesmysl`, `#2026-13`) se ignoruje a přepíše
    aktuálním stavem.
  - **Odkaz „Filtr"** (`#kal-filter-toggle`, doplněno 24. 9. 2026 na
    žádost uživatele, na řádku navigace měsícem hned za tlačítkem „Dnes" —
    přesunuto tamtéž ze zprvu zvolené pozice za přepínačem „Zobrazit jako",
    na druhou žádost uživatele týž den) — jen schovává/ukazuje panel filtrů
    (`#kal-filter-org`), samotné filtrování dál řídí checkbox a čipy
    pořadatele uvnitř. Sémanticky `<button>`, vizuálně obyčejný textový
    odkaz (`.text-toggle` v `assets/styles.css`: bez rámečku/pozadí,
    podtržený, barva `--burgundy`/`--burgundy-deep` v aktivním stavu — na
    žádost uživatele nahradilo původní stylování jako `.year-btn`). Ne přes
    sdílený `.toggle-details` vzor z `assets/common.js` — ten by na klik
    přepisoval text tlačítka na „Méně informací", což pro „Filtr" nedává
    smysl; stav nese `aria-expanded` + `.active` s vlastním handlerem. Panel
    je defaultně skrytý (`hidden`) a leží **těsně před tabulkou/seznamem**
    (`#kal-status`), ne u navigace měsícem — přesunuto z původního umístění
    24. 9. 2026 na žádost uživatele spolu s přidáním tlačítka Filtr.
  - **Panel filtrů `#kal-filter-org`** — obsahuje dva prvky, oba se
    zapisují do sdíleného stavu čteného oběma pohledy (mřížka i Seznam):
    - **Checkbox „Pravidelné akce, kurzy a tréninky"** (`#kal-show-kurz`,
      doplněno 24. 9. 2026 na žádost uživatele, přesunuto do panelu
      filtrů týž den při přidání tlačítka Filtr) — zaškrtnutý je výchozí
      stav (`KAL_SHOW_KURZ = true`, kurzy vidět jako dřív); odškrtnutím
      zmizí kategorie `kurz` z obou pohledů (mřížka i Seznam), ať jde
      kalendář prohlédnout bez tisícovek pravidelných termínů (934 TJ
      Sokol + 1390 VCP + 437 ZUŠ + 232 Pečovatelská služba + 79 Pramínek
      k 24. 9. 2026 — viz čísla u jednotlivých zdrojů níže). Filtr
      kategorie kombinuje s filtrem pořadatele (obě podmínky zároveň),
      sdílený mezi pohledy stejně jako `KAL_ORG` — přes společnou funkci
      `kalVidet(e)`, kterou volají `kalRenderGrid()` i `kalRenderList()`.
      Jediný checkbox kategorie na webu — kategorie `svoz` (Pečecké
      služby) měla krátce vlastní checkbox „Svoz odpadu" (`#kal-show-svoz`),
      **zrušený týž den na žádost uživatele** jako zbytný: pořadatel
      „Pečecké služby" má jen tuhle jednu kategorii, takže ho beze zbytku
      skryje/ukáže i čip pořadatele v sekci níž — dva filtry na totéž.
    - **Čipy pořadatele** — vykreslené `kalRenderOrgChips()` do vnořeného
      `#kal-org-chips-inner` (ne přímo do `#kal-filter-org`, aby render
      nesmazal sousední checkbox); viditelnost samotného panelu řídí
      výhradně tlačítko Filtr, ne počet pořadatelů — s < 2 pořadateli
      `kalRenderOrgChips()` vykreslí prázdný `#kal-org-chips-inner`
      (checkbox zůstává).
    - CSS pozn.: `.filter-chips{display:flex}` v `assets/styles.css`
      přebíjí výchozí UA pravidlo `[hidden]{display:none}` (autorský
      styl na `display` má přednost bez ohledu na atribut `hidden`) —
      proto explicitní `.filter-chips[hidden]{display:none;}` hned pod
      tím, jinak by byl panel viditelný i se zavřeným Filtrem.
  - **Odkaz na akci/kurz vede rovnou na zdroj, ne na interní kotvu.**
    Do 24. 9. 2026 mířil na `/kalendar/#<id>` (podstránku `/kalendar/akce/`,
    pak přepnutí do pohledu Seznam s doscrolováním) — **zrušeno na
    žádost uživatele**, žádné odkazy na jednotlivé události uvnitř
    webu už nejsou. `build_akce_events()` v `update-kalendar.py`
    dává do `link` přímo `evidence[0]['url']` — první (nejsilnější)
    doklad té konkrétní akce v `akce.json`, ten samý zdroj, ze kterého
    záznam vznikl. Jednání a volby si `link` na interní cestu
    (`/jednani/#…`, `/volby/2026/`) drží dál beze změny — jen akce/kurz
    teď míří ven. V mřížce (`kalRenderGrid()`) i Seznamu
    (`kalRenderList()`) se `http(s)://` odkaz pozná regexem a dostane
    `target="_blank" rel="noopener"`, interní cesta zůstává v témže okně;
    `link` bez hodnoty (akce bez `evidence[]`, v praxi se nestává) se
    v Seznamu vykreslí jako prostý text, ne odkaz na nic.
    Stejná hodnota jde beze změny i do `kalendar.ics` (`URL:`) a do
    Google kalendáře přes `sync-google.py` (`source.url`) — obojí mělo
    dřív natvrdo `SITE_DOMAIN + link`, což by u externí URL vyrobilo
    zdvojený řetězec typu `https://dopecek.cz/https://facebook.com/…`;
    obě místa mají teď vlastní `abs_url()` (link už absolutní → beze
    změny, jinak SITE_DOMAIN dopsat). `sync-google.py` navíc titulek
    zdroje „Do Peček . cz" v Google Kalendáři píše, jen když je `link`
    fakt náš (`url_je_nas`) — u cizí URL ho radši vynechá, ať si Google
    název domény odvodí sám, než aby tvrdil, že cizí web je „Do Peček . cz".
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
spustit (zápasy AFK Pečky předtím stáhnout
`python3 kalendar/scripts/fetch-afk-zapasy.py`, viz „Zápasy AFK Pečky"):
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
Druhá věta perexu (popis mřížky + odkaz na `/kalendar/akce/`) byla od
téhož data na vlastním řádku (`<br>` uvnitř stejného `<p class="lede">`)
— **zrušena 24. 9. 2026 na žádost uživatele** spolu s celou podstránkou;
perex teď má jen tu jednu větu s odkazem na Google kalendář.

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

## Barvy pořadatelů

Od 24. 9. 2026 má každý výrazný pořadatel vlastní barvu. Stejný mechanismus
jako u politických uskupení: barva je vlastnost **organizace** v
[`lide/organizations.json`](../lide/organizations.json) (pole `color` +
`color_bg`), `scripts/build.py` z nich generuje `assets/org-colors.css`
s proměnnými `--org-<id>` a `--org-<id>-bg`. Kalendář je čte podle pole
`organizer` u události — žádnou vlastní paletu nemá.

| Pořadatel (`id`) | Barva | Pozadí | Akcí v datech (9/2026) |
|---|---|---|---|
| Vzdělávací centrum (`vzdelavaci-centrum-pecky`) | `#177568` petrolejová | `#D5E6E4` | 1 390 |
| TJ Sokol (`tj-sokol-pecky`) | `#2F62B5` modrá | `#DAE3F2` | 934 |
| ZUŠ (`zus-pecky`) | `#7550A8` fialová | `#E6E0EF` | 437 |
| Pečovatelská služba (`pecovatelska-sluzba-pecky`) | `#727A10` olivová | `#E6E7D4` | 232 |
| Kulturní středisko (`kulturni-stredisko-pecky`) | `#B5561C` rezavá | `#F2E1D6` | 135 |
| Pramínek / Maminky sobě (`maminky-sobe`) | `#1580A0` azurová | `#D5E8EE` | 79 |
| AFK Pečky (`afk-pecky`) | `#1010E0` královská modrá | `#D8D8F9` | 42 |
| Pečecké služby (`pececke-sluzby`) | `#6D1F4F` vínová | `#E5D7DF` | 186 svozů |

Ostatní pořadatelé barvu nemají a padají na neutrální fallback (akce
`--gold-deep`, kurz šedý proužek). Město Pečky barvu záměrně nemá — jeho
události jsou jednání a volby, které se barví podle kategorie.

**Jak se barva používá.** Mřížka `/kalendar/`: akce plnou barvou pořadatele,
kurzy světlým pozadím (`-bg`) s proužkem v barvě pořadatele; jednání
a volby dál podle kategorie. Pohled Seznam: barevný chip pořadatele (`.akce-poradatel`) na konci řádku s datem.
Čipy filtru pořadatele: tečka v barvě (`--chip`) slouží zároveň jako
legenda.

**Výběr barev.** Tlumené tóny ladící s pergamenem, bílé písmo na plné barvě
s kontrastem ≥ 4,5 : 1 (WCAG AA), vzájemný rozdíl CIEDE2000 ≥ 17 a odstup
od barev uskupení a kategorií kalendáře. Nejtěsnější dvojice: Kulturní
středisko × SPD (ΔE 11) — v kalendáři se nepotkají, SPD je jen ve
volbách. AFK Pečky (24. 9. 2026): klubová modrobílá, jenže modrou
oblast už drží TJ Sokol, ODS, Pramínek a `--slate` — žádný tlumený modrý
odstín nedal ΔE ≥ 17, splnila to až sytá královská modrá `#1010E0`
(nejbližší ODS 17,3 a ZUŠ 17,4, kontrast s bílou 9,7 : 1). Je o poznání
výraznější než zbytek palety — vědomý kompromis ve prospěch klubové barvy.
Pečecké služby (24. 9. 2026, kvůli svozu odpadů): vínová `#6D1F4F`,
nejbližší SNK Pečky Pečákům 18,0 a `--burgundy` 18,5, kontrast s bílou
10,7 : 1. Novou barvu zkontrolovat stejně; validátor
`node lide/validate.mjs` hlídá formát a duplicitu hexu.

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
  `mesto-pecky`. Řídí čipy „Pořadatel" nad mřížkou i nad pohledem Seznam.
- **`organizer_name`** — jméno k tomu id (`short_name`, jinak `name`),
  dopsané generátorem, aby ho klient nemusel dohledávat druhým fetchem.
  U pořadatele mimo rejstřík (cizí soubor, soukromý pořadatel) je vyplněné
  samo a `organizer` je `null`.
- **`source_ref`** — ID v zdrojových datech (u Jednání `uuid` z
  `pecky-jednani.json`) — používá se i jako `UID` v `.ics`, musí zůstat
  stabilní napříč přegenerováními.

## Pracovní postup: týdenní kontrola

Od 24. 9. 2026 (na žádost uživatele) má Kalendář v `README.md` → „Stav
sekcí" režim `týdně` — spouští ho skill `pecky-online-update` přes tenhle
postup. Týdenní kontrola pokrývá jen zdroje, které se dají projít
spolehlivě a rychle; ostatní pořadatelé (plakáty, Facebook, Instagram)
zůstávají na vyžádání přes skill `pecky-online-kalendar-plakat`.

1. **Zápasy AFK Pečky:** `python3 kalendar/scripts/fetch-afk-zapasy.py`.
   Skript vypíše změny oproti minulému běhu (nové zápasy, přeložené
   termíny, zmizelé nadcházející zápasy, nové výsledky). Skončí-li
   „ZASTAVENO", ověř rozpis ručně na afkpecky.cz — `--force` jen když
   tým opravdu nemá žádné zápasy (konec sezóny, zrušené družstvo),
   nikdy naslepo; jinak sekci přeskoč a nahlas to ve shrnutí.
2. **Aktuality AFK Pečky** (`afkpecky.cz/co-se-u-nas-deje/`): projít
   články od data minulé kontroly Kalendáře. Klubová akce s konkrétním
   termínem (posvícení, turnaj, kemp, nábor s datem) → zapsat do
   `kalendar/akce.json` podle schématu a konvencí skillu
   `pecky-online-kalendar-plakat`. „Víkendový program" porovnat s
   rozpisem z kroku 1 — rozpor (jiný čas, přeložení, které rozpis ještě
   nemá) nahlásit, do dat nepsat ručně (přepsal by ho příští běh).
3. **Přegenerovat:** `python3 kalendar/scripts/update-kalendar.py`
   (a `python3 scripts/build.py`, jen pokud se změnil `content/kalendar.html`).
4. **Výpis a Stav sekcí** podle `CLAUDE.md` → „Konvence": změny
   z kroku 1 a 2 jednou větou, jinak „zkontrolováno, beze změny".
   Nové výsledky odehraných zápasů se počítají jako změna obsahu.

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
  **Konec bez uvedeného data:** nemá-li pravidelný `kurz` u zdroje jasný
  konec sezóny, defaultní horizont je **konec školního roku 30. 6. 2027**
  (pravidlo, 23. 9. 2026 na žádost uživatele — „zapiš dle termínů
  školního roku, takhle to dělej vždycky, když nebude znám konec").
  Platí i pro zdroje bez vazby na školní docházku (např. Pramínek
  Dobřichov níže) — školní rok je jen sdílený, dostatečně dlouhý
  horizont, ne tvrzení, že aktivita je školní. Výjimka: **Senior klub
  Pečovatelské služby** (do 31. 12. 2027) — zadáno explicitně před tímhle
  pravidlem, ponecháno beze změny, nový default se týká až budoucích
  případů.
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
    **Vlastní web knihovny [pececko.cz](https://www.pececko.cz)**
    (`sources.json` → `web-knihovna-pecky`) přidán ke kontrole 22. 9. 2026
    na žádost uživatele (konkrétně z `/noc-literatury/`, archivní stránky
    ročníků akce) — **kontrolovat i domovskou stránku** (záložky
    Aktuality/Informace/Akce/Výstavy dole vypisují to samé, co web
    zveřejní jako nejnovější, bez nutnosti dolovat z Facebooku). K datu
    zapojení web jen potvrdil, co už bylo zapsané (Noc literatury,
    Bookstart/S knížkou do života, Digitální odysea, VU3V) — žádná nová
    akce, ale odhalil starou **duplicitu**: „Noc literatury 2026" byla
    zapsaná dvakrát (jednou obecně z programu KD, podruhé podrobně
    z vlastního plakátu knihovny) — sloučeno do jednoho záznamu s třemi
    doklady `evidence[]`, ne dva samostatné. Web sám k jedné položce
    (Noc literatury) přiřazuje záložku „Výstavy", ne „Akce" — nespoléhat
    na jeho vlastní kategorizaci, řídit se obsahem.
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
      ať je v pohledu Seznam i v tooltipu mřížky na první pohled jasné,
      že jde o odhad, ne o potvrzený termín ze zdroje. Přibude-li
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
    - **`evidence[].url` musí mířit na detail konkrétního kroužku**
      (`vzcentrum.cz/krouzky/<id>-<slug>`, viditelné na kartě kroužku
      na `/krouzky` po kliknutí), **ne na obecný rozcestník
      `vzcentrum.cz/krouzky`** — týž odkaz pro všech ~1400 kroužků byl
      chyba prvního zápisu 22. 9. 2026, opravena 25. 9. 2026 na žádost
      uživatele (odkaz z kalendáře jinak vždy skončil na stejné obecné
      stránce místo na konkrétním kurzu). Slug se v čase nemění (`id-`
      prefix je interní ID webu vzcentrum.cz), ale při přidání dalšího
      kroužku z tohoto zdroje ho znovu dohledat kliknutím na kartu, ne
      odhadovat podle vzoru — číslování ID není souvislé podle abecedy.
      Výjimka: **„Příprava na přijímací zkoušky" (14:00 i 16:00)** —
      každý čas ve skutečnosti pokrývá dvě běžící skupiny naráz
      (dvojkaři/trojkaři + gymnázia/jedničkáři, viz výše), proto má
      `evidence[]` dva doklady — dvojkaři/trojkaři jako `evidence[0]`
      (ten dává `link` v kalendáři), gymnázia/jedničkáři jako druhý,
      rozhodl uživatel 25. 9. 2026 bez principiálního důvodu pro jinou
      volbu.
    - **`/vikendovky` a `/klubko`** — k 22. 9. 2026 obsahovaly jen školní
      rok 2025/2026 (víkendovky 25. 9. 2025 – 4. 6. 2026, Klubko
      15. 9. 2025 – 4. 5. 2026), všechno proběhlé. Sezóna 2026/2027 tam
      zatím nebyla zveřejněná. **Zkontrolovat znovu při každé další
      kontrole Kalendáře** (na žádost uživatele), ne čekat na zvláštní
      podnět. Klubko pro info: měsíční tematický kurz, vždy 4 úterní
      termíny v měsíci, 18:00–19:30, potvrzeno z plakátů.
      - **25. 9. 2026 (na žádost uživatele, konkrétní odkaz):** první
        položka sezóny 2026/2027 se ve `/vikendovky` objevila —
        [vzcentrum.cz/vikendovky/92-atelier](https://www.vzcentrum.cz/vikendovky/92-atelier),
        „sobotní Ateliér" s Františkem Hálou. Datum vedle nadpisu na
        detailu stránky (v tomto případě „25.09.2026") **není datum
        akce** — je to zjevně datum vydání/publikace příspěvku (loňský
        ročník téže položky má stejný popisek a datum „25.09.2025",
        rok předtím; ověřeno srovnáním na `/vikendovky` listingu).
        Skutečné termíny jsou jen na plakátu (obrázek, ne text stránky):
        **4 soboty 9:00–16:00, 200 Kč/osoba, pro děti i dospělé — 26. 9.,
        31. 10., 28. 11., 19. 12. 2026.** Doplňuje mezeru zapsanou u
        pravidelného středečního Ateliéru výše („otevřen i každou
        poslední sobotu v měsíci, konkrétní termíny web neuvádí") —
        zapsáno jako 4 samostatné `kurz` záznamy `kurz-<datum>-atelier-sobotni`,
        title „Ateliér (sobotní blok)" (odlišeno od středečního
        `kurz-<datum>-atelier"), stejný pořadatel a místo. Zbytek
        `/vikendovky` (smyslohraní, keramika s Ivanem Sagačem, rodinné
        neděle, výlety) je k 25. 9. 2026 pořád jen loňská sezóna,
        proběhlá — nezapisovat, dokud nevyjde nová.
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
  - **Pečovatelská služba města Pečky** —
    [pspecky.cz](https://www.pspecky.cz/) (`sources.json` →
    `web-pspecky-cz`, `organizer: pecovatelska-sluzba-pecky`), přidáno
    ke kontrole 22. 9. 2026 na žádost uživatele (kvůli případným
    plakátům v sekci Akce/Aktuality — žádná samostatná „Akce" stránka
    na webu ale neexistuje, `/akce/` vrací 404; web nemá ani vlastní
    Facebook). K datu zapojení jediný nalezený obsah:
    **`/senior-klub-pecky/`** — celoroční harmonogram 4 pravidelných
    aktivit (Trénink paměti, Tvořivá dílna, Cvičení na židli,
    Muzicírování pro radost — poslední 1× za 2 týdny, web přesně
    neuvádí které úterky, zapsáno od nejbližšího nadcházejícího).
    **232 nových `kurz` záznamů**, na rozdíl od TJ Sokol/VCP/ZUŠ **bez
    vazby na školní rok** (senior klub běží celoročně, ne podle
    školního kalendáře) — rozepsáno od 23. 9. 2026 (zítřek od kontroly,
    ať dnešní úterní termíny nejsou nejistě zapsané jako „ještě
    proběhnou") **do 31. 12. 2027 na žádost uživatele**, „ať to sedí
    s horizontem ostatních zdrojů". **Žádné prázdniny nevynechány** —
    na rozdíl od školních zdrojů tu není zdroj, o který by se dalo
    přerušení opřít; možné vánoční/letní pauzy jsou tak přiznaná
    mezera, ne tvrzený fakt. Aktuality sekce k datu kontroly jediný
    příspěvek (odstávka střediska hygieny léto 2026) — nebyla akce,
    nezapsáno.
  - **MŠ MAŠINKA Pečky** — [msmasinkapecky.cz/akce-skoly](https://www.msmasinkapecky.cz/akce-skoly/)
    (`sources.json` → `web-msmasinkapecky-cz`, `organizer: msmasinka-pecky`),
    zapojeno 22. 9. 2026 na žádost uživatele. Vlastní stránka „Akce
    školy" existuje (na rozdíl od pspecky.cz) a k datu kontroly měla
    přesně 2 položky, obě zapsány — **2 nové `akce` záznamy**:
    - **Bramboriáda** (22. 9. 2026, dnes v době zápisu) — podzimní
      potlach pro rodiny, hlasování o nejlepší bramborovou specialitu.
      Zapsáno i přesto, že datum je totožné se dnem kontroly (ne
      zpětně doplňovaná akce, ale aktuální/nadcházející v okamžiku
      zápisu).
    - **Canisterapie** (26.–27. 10. 2026) — první návštěva
      canisterapeutického psa, novinka školního roku. Web píše, že pes
      bude chodit „pravidelně", ale žádné další termíny neuvádí —
      zapsán jen tenhle první, žádné vymýšlené opakování.
  - **SŽM Pečky** — [szmpecky.webnode.cz/kalendar-akci](https://szmpecky.webnode.cz/kalendar-akci/)
    (`sources.json` → `web-szmpecky-cz`, `organizer: szm-pecky`), zapojeno
    24. 9. 2026 na žádost uživatele. Stránka je fotogalerie, ne
    strukturovaný kalendář — dva plakáty: souhrnný „Výstavy 2026" s
    celoročním rozpisem 9 víkendů výstav modelových kolejišť (zpravidla
    první víkend v měsíci, vždy sobota 9–17 a neděle 9–15) a podrobný
    plakát k nejbližšímu termínu (k datu zapojení 3.–4. říjen 2026, s
    cenami vstupného a programem). Zapsáno všech 9 termínů z ročního
    plakátu jako samostatné `akce` záznamy (29.–31. 5. jako třídenní
    „největší výstava modelových kolejišť v ČR", ostatní dvoudenní); u
    nejbližšího termínu doplněn i druhý doklad z podrobného plakátu.
    **Kontrola:** stránka nemá RSS ani archiv verzí, nový rok se objeví
    jen přepsáním stejné fotogalerie stejnými odkazy — při každé kontrole
    znovu projít oba plakáty okem přes claude-in-chrome (kliknout na
    náhledy, otevřou se ve zvětšeném náhledu/lightboxu) a srovnat s už
    zapsanými termíny; změna data/nový rok přepíše existující záznam se
    stejným `id`, ne duplicitní zápis.
  - **Minigolfclub Dráčata Pečky** — [minigolf-pecky.webnode.cz](https://minigolf-pecky.webnode.cz/)
    (`sources.json` → `web-minigolf-pecky`, `organizer: minigolfclub-dracata-pecky`),
    zapojeno 24. 9. 2026 na žádost uživatele. Web nemá kalendář akcí —
    čerpá se ze tří míst:
    - **/turnaje/** — rozpis ligových turnajů roku po měsících. Data mají
      jen domácí dubnové turnaje (12. 4. Oblastní přebor, 18.–19. 4. MČR
      dětí a mládeže Junior Trophy, 26. 4. Bohemia Tour 1. liga) — zapsány
      jako `akce`, s druhým dokladem z Pečeckých novin 5/2026, str. 11.
      Venkovní turnaje (Praha, Varšava, Děčín, Radotín…) se nezapisují —
      nejsou v Pečkách. Domácí zářijový turnaj 2. ligy („září: Pečky",
      noviny 9/2026 „v září na domácím hřišti") nemá datum — **nezapsán,
      přiznaná mezera**. Nadpis „turnaj pro veřejnost 2026" je na webu
      prázdný.
    - **Úvodní stránka** — otvírací doba veřejného hřiště („otevřeno do
      1. 10. 26, každou So + Ne 14–18"). Zapsáno jako `kurz` jen od data
      zapojení (26. a 27. 9. 2026); řádek „Hřiště bude pro veřejnost
      zavřené:" je prázdný. Při každé kontrole ověřit, jestli nepřibyla
      nová sezóna/doba.
    - **/o-nas/ + /sluzby/** — trénink dětí každé pondělí 14–16 (shodně
      i Pečecké noviny 11/2025) → `kurz` od 28. 9. 2026 do 30. 6. 2027
      (výchozí horizont). Podstránka Služby → **Nábory** uvádí rozporně
      čtvrtek 14–17 a otevření „od června do září" — vypadá neudržovaně,
      nepoužito, rozpor přiznán v `note` záznamů.
    **Kontrola:** Aktuality i RSS jsou mrtvé (jediná zpráva z 27. 1. 2014),
    datum změny stránek web neukazuje — při každé kontrole projít
    `/turnaje/` a úvodní stránku (stačí `curl`, statické HTML Webnode,
    claude-in-chrome netřeba) a srovnat se zapsanými záznamy. Aktuálnější
    zprávy (výsledky, plány turnajů) píše předsedkyně Věra Šuková do
    rubriky Spolky/Sport v Pečeckých novinách — kontrolovat i tam.
  - **Pečecká desítka** — [pecky10km.cz](https://www.pecky10km.cz)
    (`sources.json` → `web-pecky10km-cz`, `organizer: bk-pecky`), zapojeno
    25. 9. 2026 na žádost uživatele. Tradiční silniční běh na 10 km
    (Memoriál Jardy Kvačka), pravidelně **druhá sobota v březnu** — termín
    ověřený nezávisle za roky 2023 (11. 3.), 2024 (9. 3.), 2025 (8. 3.) a
    2026 (14. 3.); zapsáno 5 termínů (43.–47. ročník), vč. už oznámeného
    47. ročníku 13. 3. 2027 (bez propozic, viz `note` u záznamu).
    **Kontrola nového ročníku (POVINNÉ při každém běhu):** hlavní stránka
    pecky10km.cz má vpravo blok „Krátce“ s aktuálním datem nejbližšího
    závodu a stavem registrace — nejrychlejší způsob, jak zjistit, jestli
    přibyl nový ročník nebo se up­řesnily propozice (startovné, kapacita,
    čas startu). Web má nespolehlivé routování (odkazy z domovské stránky
    občas vedou zpět na ni, přímé URL typu `/index.php/propozice-2026`
    fungují nekonzistentně) — při potížích zkusit Facebook
    (`facebook-pececkadesitka`) nebo dohledat přes Google. Jakmile web
    zveřejní propozice na další ročník (obvykle na podzim předchozího
    roku), doplnit/upřesnit záznam (čas startu, startovné se nezapisuje).
  - **Street Food Festiválek Pečky** (17. 10. 2026, Kulturní dům) —
    zapsáno 23. 9. 2026 přímo z odkazu na Facebook událost, který zadal
    uživatel. Pořádá externí firma **City Event** (celostátní přehlídka
    street food festivalů, 235 uplynulých událostí jinde), ne Kulturní
    středisko — `organizer: null`, `organizer_name: "City Event"` (jde
    o hostující pořadatele mimo rejstřík, stejný vzor jako u cizích
    divadelních souborů, viz krok 3b v `automation-plakat-akce.md`).
    Nový zdroj `facebook-event-street-food-festivalek-pecky` v
    `sources.json` — jednorázový, nekontroluje se dál pravidelně (na
    rozdíl od ostatních zdrojů v týhle sekci).
  - **Kalendář událostí na webu města** —
    [pecky.cz/default/events](https://pecky.cz/default/events)
    (`sources.json` → `pecky-cz`), přidáno k pravidelné kontrole
    23. 9. 2026 na žádost uživatele. Měsíční mřížka, jednotlivé záznamy
    na `/default/report/<id>_<slug>` mají vlastní datum/čas i plakát
    jako přílohu a časovou značku „Zveřejněno" — cenné i jako křížová
    kontrola už zapsaných akcí, ne jen zdroj nových (23. 9. 2026 tudy
    vyšlo najevo potvrzení přesunu Bookstart na 30. 9., zveřejněné týž
    den ráno — doplněno jako čtvrtý doklad k existujícímu záznamu).
    Zahrnuje i akce mimo Pečky (typicky „Platí pro: Celé město" u všech
    záznamů bez rozdílu, ne spolehlivý filtr). Zjevně regionální
    položky bez vazby na Pečky (jiné obce — Sokoleč, Nová Ves I. u
    Kolína) do kalendáře nepatří.
  - **Pramínek Dobřichov** — zapojeno 23. 9. 2026 na žádost uživatele
    („akce z Dobřichova budeme také evidovat"), objeveno přes
    `pecky.cz/default/events`. Komunitní/mateřské centrum v sousední
    obci Dobřichov (Dobřichov 24), ne Pečky samo — ale realizuje ho
    spolek **Maminky sobě, z.s.** (IČO 27033431, `organizer:
    maminky-sobe`) ve spolupráci s **Farností Pečky**, což vazbu na
    Pečky dává. Vlastní web [mcpraminek.cz](https://www.mcpraminek.cz)
    (`sources.json` → `web-mcpraminek-cz`) má rubriku „Program a akce"
    (jednotlivé akce na `/products/<slug>/`, datum/čas jen v textu, bez
    vlastního pole) a „Kroužky" — **4 nové `akce` záznamy** z plakátů
    nalezených přes pecky.cz:
    - **Postav si draka** (29. 9. 2026) — „první část" dílny, může
      pokračovat.
    - **Kaštanová mast** (2. 10. 2026) — plakát říká „první setkání",
      možná sezónní série; další termíny zatím nezveřejněné.
    - **Kožedělná dílna** (4. 10. 2026) a **Komunitní kavárna otevřena**
      (4. 10. 2026, „v Pramínku") — jednorázové.
    - **Nenalezeno na webu:** vlastní `kalendar-akci/` rubrika prázdná
      („V této rubrice nejsou žádné články"); „Program a akce" má 5
      stránek archivu, prošla jen první — přiznaná mezera pro příští
      kontrolu.
    - **Objeveno navíc na `/program-a-akce/`, doplněno 23. 9. 2026** —
      dva pravidelné kroužky, **75 nových `kurz` záznamů** (na žádost
      uživatele, „zapiš dle termínů školního roku" — viz defaultní
      pravidlo u kategorie `kurz` výše, teď platí obecně):
      - **Zálesák** (děti od 7 let) — úterý 17:00–18:30, od potvrzeného
        začátku 15. 9. 2026 do 30. 6. 2027.
      - **Hrátky s batolátky** (rodiče s batolaty) — čtvrtek 9:00–12:00;
        web přesný začátek sezóny neuvádí, zapsáno od nejbližšího
        nadcházejícího čtvrtku po datu kontroly (24. 9. 2026) do
        30. 6. 2027.
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
  - **Hostinec „U Stříkačky"** (`facebook-hostinec-u-strikacky`, 517
    sledujících, přidáno uživatelem 24. 9. 2026) — soukromá hospoda,
    V. B. Třebízského 84, Pečky. Záložka Události má jen dvě staré
    položky (Uzená kýta 9/2024, Svatomartinská Husa 11/2023), žádná
    záložka „Nadcházející". Posledních ~5 příspěvků profilu jsou
    výhradně denní jídelní lístky („JÍDELNÍ LÍSTEK — ČTVRTEK 24. 9.
    2026" apod.) bez vazby na jednorázovou akci — case „akce bez data"
    z `automation-plakat-akce.md`, ne akce k zapsání. Nic k zápisu.
    Organizaci v `lide/organizations.json` zatím nezakládat (žádná
    akce, kterou by měla pořádat) — první výskyt konkrétní akce založí
    pořadatele podle kroku 3b v `automation-plakat-akce.md`.
  - **FitPecky.cz** (`facebook-fitpecky-cz`, 1,2 tis. sledujících,
    přidáno uživatelem 25. 9. 2026) — prodejna zdravé výživy, bezobalu
    a ekodrogerie s občerstvením, Masarykovo náměstí / V. B. Třebízského
    656, Pečky (`lide/organizations.json` → `fitpecky-cz`, provozovatelka
    Radana Honsová, tatáž osoba jako u Nejen kavárna u Radu níže, jiná
    provozovna). Záložka Události má jen proběhlé přednášky a workshopy
    (naposled „Imagine Medicine" a „Umění degustace", dál zpět „Aby záda
    nebolela", „Reflexní terapie pro každý den", „Jóga se snídaní",
    cyklovýlet, běžecká akce), žádná záložka „Nadcházející"; poslední
    vlastní příspěvek 5. 7. 2026. Podnik přednášky/workshopy občas
    pořádá, jen zrovna žádnou nemá ohlášenou — nic k zápisu, zkontrolovat
    znovu při další kontrole.
  - **Nejen kavárna u Radu** (`instagram-nejenkavarnauradu`, 508
    sledujících, přidáno uživatelem 25. 9. 2026) — kavárna, V. B.
    Třebízského 656, Pečky (`lide/organizations.json` →
    `nejen-kavarna-u-radu`, provozovatelka Radana Honsová). Mřížka má
    několik plakátů na vlastní akce, všechny ale s termínem v minulosti:
    „Podzim a péče o sebe" (ajurvédská přednáška) na plakátu uvádí jen
    „22. října" bez roku — **popisek příspěvku (čtený přes meta tagy
    stránky, plakát samotný rok neuvádí) potvrzuje 22. 10. 2025, ne
    2026** (dobrá připomínka nespoléhat na plakát samotný, je-li rok
    nejistý); „Povídání o Mongolsku" 4. 10. 2025; „Becherovka Park
    Lounge" 18. 4. 2026; „Poznávačka" (spoluúčast s KC Pramínek a
    Pečeckým okrašlovacím spolkem) odkazovala na termíny 13. a 19. 9.
    2026 — všechny k datu kontroly proběhlé. Ajurvédská přednáška se
    koná opakovaně na podzim („Tradičně netradiční") — vydání pro podzim
    2026 zatím neohlášené, zkontrolovat znovu při další kontrole. Nic
    aktuálního k zápisu.
  - **PEČKY město v Polabí** (`facebook-pecky-mesto-v-polabi`, 1,5 tis.
    sledujících, přidáno uživatelem 25. 9. 2026) — regionální komunitní
    stránka (vede Michal Müller), **výslovně ne oficiální profil MÚ
    Pečky**, hlavně sdílí příspěvky jiných stránek. Záložka Události má
    jen minulé (naposledy 2023), nic nadcházejícího. Z fotogalerie (8
    fotek celkem) jeden nový nález: plakát náboru **„VLCI Pečky“** —
    basketbalový oddíl TJ Sokol Pečky, trénink každý pátek 15:00–16:00
    v Park Hale Pečky (sportovní hala), trenér Zdeněk Fejfar, pro
    ročník 2017–2020 — **doplňuje dřív zjištěnou mezeru** „Basketbal —
    městská sportovní hala: rozpis samostatně" z Pečeckých novin 9/2026
    (viz `kalendar/akce.json`, 35 týdenních záznamů `kurz` do 30. 6.
    2027, organizer `tj-sokol-pecky`); přesné datum zahájení tréninků
    plakát neuvádí, zapsáno od nejbližšího pátku k datu zjištění.
    Zbytek fotogalerie beze změny k zápisu: dvě už proběhlé přednášky
    Kulturního střediska (23. 9., 9. 9.), pozvánka na zasedání ZM
    6/2026 (16. 9., pokrývá Jednání) a Postřižinská Dočesná — pivovarní
    festival v Nymburku, mimo Pečky/Dobřichov.
  - **Studio Anet** (`web-studioanet-cz` + `facebook-studioanett`, 595
    sledujících na FB, přidáno uživatelem 25. 9. 2026) — taneční studio
    DSA Plaňany, z.s. (`lide/organizations.json` → `dsa-planany`, sídlo
    v Tatcích, IČO 17387884). Polovina skupin trénuje v Tatcích, ale
    **úterní a čtvrteční skupiny (Junioři B, Juniorky A, BOMBY/rodiče,
    Hlaváci) trénují v Kulturním středisku Pečky** — proto v rozsahu
    webu i přes sídlo mimo Pečky/Dobřichov (viz i BK Pečky výše, stejný
    princip: pořadatel odjinud, akce v Pečkách). Rozpis pro sezónu
    2026/2027 z domovské stránky webu (potvrzený plakátem náboru na FB)
    — 4 skupiny × úterý/čtvrtek = **288 týdenních záznamů** `kurz` do
    30. 6. 2027. Podstránka `/kalendar-akci` webu je jen historický
    archiv do roku 2025, sezóna 2026/2027 v ní zatím není; přesné datum
    zahájení pravidelných tréninků po náboru (8. a 15. 9. 2026) web
    neuvádí, zapsáno od nejbližšího úterý/čtvrtku k datu zjištění.
  - **DC GLOW** (`web-dcglow-cz` + `facebook-dcglow`, 544 sledujících na
    FB, přidáno uživatelem 25. 9. 2026) — taneční skupina založená 2009
    přímo pod záštitou Kulturního středisku města Pečky
    (`lide/organizations.json` → `dc-glow`, IČO 21862184). **Přiznaná
    mezera, nic nezapsáno:** klub je prokazatelně aktivní (Facebook má
    čerstvý příspěvek o letním soustředění v Harcově, titulní foto
    zmiňuje umístění na soutěži v Příbrami), ale ani jeden zdroj
    neposkytl aktuální den/čas pravidelného tréninku pro zápis do
    `kalendar/akce.json` — web (`/kalendar-akci/`, `/aktuality/`,
    `/dokumenty-ke-stazeni/`) má dynamický obsah neaktualizovaný od
    sezóny 2022/2023, FB záložka Události končí náborem z května 2023
    a fotogalerie má jen fotky ze soustředění, žádný plakát s rozpisem.
    **Kontrola při příštím běhu:** zkusit znovu FB feed (nedonačetl se
    dál než na jeden příspěvek, stejné technické omezení jako jinde
    v repu) a hlavně sledovat září/říjen na plakát náboru pro další
    sezónu — přesně to, co u Studio Anet a VLCI Pečky fungovalo.

  Proto `evidence` pole a ne jedno pole se zdrojem — nový zdroj přibývá
  stejným způsobem jako výše.
- **Doklad (`evidence[]`)** je pole, ne jedna hodnota: tutéž akci ohlásí
  pořadatel na svém profilu, město ji přesdílí a zpravodaj o ní napíše —
  to není trojí akce, ale jeden záznam se třemi doklady. **První doklad je
  ten, podle kterého jsou zapsané údaje**, ostatní ho potvrzují. Každý
  doklad má `source` (id v `sources.json`), `kind` (`plakat` ·
  `prispevek` · `web` · `zpravodaj` · `tisk` · `ustni`), `url`, `label`
  (název konkrétního plakátu, ne profilu), `published` a `retrieved`.
  **`evidence[]` od 24. 9. 2026 (zrušení `/kalendar/akce/`) nikde ve
  veřejném UI nevidět** — zůstává jen data pro budoucí použití/audit,
  ne zdroj pro nějaký sloupec Zdroj; mapování `kind` → čitelný název
  (dřív `DOKLAD` v `content/kalendar-akce.html`, `zpravodaj` →
  „Pečecké noviny") s tím zrušené stránky zmizelo, nemá se kde
  uplatnit.
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
  nepodařilo dohledat — pořadatel i bez něj), spolek `szm-pecky`
  (24. 9. 2026), spolek `minigolfclub-dracata-pecky` (24. 9. 2026), spolek
  `bk-pecky` (25. 9. 2026, IČO 27031250 dle Hlídače státu), spolek
  `dsa-planany` (25. 9. 2026, IČO 17387884 dle Hlídače státu — sídlo
  v Tatcích, ale tréninky dvou dní v týdnu v Pečkách). Pro jednorázového
  pořadatele mimo rejstřík (cizí divadelní soubor) slouží `organizer:
  null` + `organizer_name: "…"` textem; zakládat kvůli jedné akci
  organizaci nemá smysl, ale ztratit pořadatele taky ne.

### Zápasy AFK Pečky — aktivní (od 24. 9. 2026)

- **Data:** `kalendar/afk-zapasy.json`, stahuje ho
  `kalendar/scripts/fetch-afk-zapasy.py` (jediný zdroj kalendáře se
  skutečným scraperem — web klubu jde číst prostým HTTP, bez
  claude-in-chrome), do kalendáře promítá `build_afk_events()`.
  `update-kalendar.py` sám nic nestahuje, pracuje s posledním uloženým
  souborem — proto ho bez obav spouští i krok 8b kontroly Jednání.
- **Zdroj:** `sources.json` → `web-afkpecky-cz`, stránky
  `afkpecky.cz/<tým>/zapasy/` všech 7 týmů (A tým, B tým, starší dorost,
  starší a mladší žáci, starší a mladší přípravka). Tabulka „Mistrovská
  utkání" (případně „Přátelská utkání") aktuální sezóny: datum, čas
  výkopu, domácí, hosté, skóre; hřiště z modálního okna „Info o hřišti".
  Stránky `/<tým>/kalendar/` jsou jen JS překreslení téže tabulky, iCal
  export web nemá. Veřejný Google kalendář „Rozpis UMT" ze stránky Areál
  **nepoužívat** — rezervace umělé trávy na tréninky, ne veřejné akce.
- **Rozsah (rozhodl uživatel 24. 9. 2026):** domácí zápasy **všech**
  týmů. Soubor drží všechny zápasy (i venkovní, příznak `home`), filtr
  dělá až `build_afk_events()` podle `in_pecky` — **rozhoduje hřiště,
  ne pořadí týmů**: 15. 9. 2026 hrála mladší přípravka „Čechie Tuklaty :
  AFK Pečky" na hřišti „Barákova ul., Pečky"; takový zápas v kalendáři
  je, s poznámkou. Venkovní zápasy by šly zapnout úpravou filtru bez
  nového stahování.
- **Kategorie:** `akce` (veřejná jednorázová událost pro diváky, ne
  trénink) — checkbox „Pravidelné akce, kurzy a tréninky" je neschová.
- **Pořadatel:** `afk-pecky` (Amatérský fotbalový klub Pečky, z.s.,
  IČO 62994417). **Odkaz:** stránka zápasů daného týmu (jednotlivý zápas
  vlastní URL na webu klubu nemá). **UID:** `afk-<tým>-<id modálu>` —
  číslo zápasu v systému klubu, drží se i po přeložení termínu.
- **Odehrané zápasy** zůstávají v kalendáři s výsledkem v popisu
  (skóre v pořadí domácí:hosté, jak ho uvádí web). Po přepnutí webu na
  novou sezónu (léto) je skript ponechá ze starého souboru, historie se
  neztratí; nadcházející zápas, který z webu zmizí, se nepřenáší (zrušení)
  a jen se vypíše.
- **Pojistky / kvirky parseru:** tým bez jediného zápasu → zápis se
  zastaví (`--force` až po ručním ověření). U B týmu chybí na webu třída
  `hometeam`, domácí se proto pozná podle názvu „AFK Pečky…" v první
  buňce. Modální okno bez údaje o hřišti nesmí převzít hřiště ze
  sousedního okna (parsuje se po jednotlivých oknech).
- **Klubové akce mimo rozpis** (Zlaté pondělí, turnaje, kempy) nejsou
  v tabulkách zápasů — ty se čtou z Aktualit (`/co-se-u-nas-deje/`)
  a zapisují ručně do `kalendar/akce.json` (evidence `web-afkpecky-cz`,
  `kind: "web"`), stejně jako u ostatních pořadatelů. První: Zlaté
  pondělí 28. 9. 2026 od 14:00. Víkendové programy v Aktualitách jen
  opakují rozpis — slouží ke křížové kontrole (24. 9. 2026 souhlasily).
- **Aktualizace:** týdně, viz „Pracovní postup: týdenní kontrola" níže.

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

### Svoz odpadů — aktivní (od 24. 9. 2026)

- **Data:** `kalendar/svoz-odpadu.json`, funkce `build_svoz_events()`.
  Soubor drží jeden záznam na typ svozu (`types[]`: `id`, `title`,
  `place`, `rule` = text legendy z PDF, `dates[]`); generátor ho rozepíše
  na **jednu celodenní událost na typ a den** (rozhodl uživatel — ne
  sloučeně po dnech). `id`/`source_ref` = `svoz-<typ>-<datum>`.
- **Zdroj:** `sources.json` → `pecky-cz-harmonogram-svozu-2026` —
  jednostránkové PDF „Harmonogram svozu odpadů z domácností 2026" na
  pecky.cz, stažitelné běžným curl. Odkaz u každé události vede přímo na
  to PDF (`meta.evidence.url`).
- **Pořadatel:** `pececke-sluzby` (Pečecké služby, s.r.o.). **PDF
  pořadatele neuvádí** — zadal ho uživatel 24. 9. 2026, poznamenáno
  v `meta.organizer_note`. Doloží-li se odjinud, doplnit doklad.
- **Kategorie:** `svoz` — bez vlastního checkboxu (krátce ho měla, `#kal-show-svoz`
  v panelu Filtr, **zrušen 24. 9. 2026 na žádost uživatele** jako zbytný:
  pořadatel „Pečecké služby" má jen tuhle kategorii, takže totéž dělá čip
  pořadatele). V mřížce stejně tlumeně jako `kurz` (světlé pozadí + proužek
  v barvě pořadatele, `.kal-ev-svoz`), v Seznamu štítek `svoz`, v Google
  kalendáři `colorId` 3 (Grape).
- **Rozsah 2026:** 186 termínů ve 111 dnech, celý rok (rozhodl uživatel,
  i zpětně) — komunální sever 34, jih 34, sídliště 52, BIO 42, plast 12,
  papír 12. Nepravidelnosti převzaté z PDF tak, jak jsou: sever navíc
  28. 12. (mimo 14denní rytmus), svoz jede i 6. 4. a 28. 9. (svátky),
  BIO v lednu a únoru jen jednou měsíčně, poslední 1. 12.
- **Vytěžení:** termíny jsou v PDF jen **barvou buňky**, text dne je
  u všech dní stejný — ručně přepisovat nemá smysl. Skript
  `kalendar/scripts/extract-svoz-odpadu.py <pdf> <rok>` (potřebuje poppler:
  `pdftotext`, `pdftoppm`) vezme polohy čísel z textové vrstvy, dopočítá
  datum (kontroluje proti dni v týdnu sloupce) a přečte barvu pozadí;
  zapíše jen `dates[]` do existujících `types[]`. Souřadnice sloupců
  a barvy odpovídají šabloně 2026.
- **Aktualizace:** jednou ročně, až město vyvěsí harmonogram na další rok —
  nové PDF, nový záznam v `sources.json`, zkontrolovat okem, jestli
  sedí šablona (sloupce/barvy/legenda), pak skript, `update-kalendar.py`
  a `sync-google.py`. Změna během roku (např. mimořádný svoz) se píše
  ručně do `dates[]`.

### Kalendář akcí z webu města — zapojeno 23. 9. 2026

Původně plánované jako vlastní scraper (`build_akce_events()` nad
zdrojovým JSON) — místo toho zapojeno stejně jako ostatní zdroje výše:
`pecky.cz/default/events` čtené ručně přes claude-in-chrome (ne
automatizovaný scraper), nálezy přepsané do `kalendar/akce.json` skillem
`pecky-online-kalendar-plakat`. Viz vlastní bullet „Kalendář událostí na
webu města" v „Zdroje" výše pro detaily a kvirky.
