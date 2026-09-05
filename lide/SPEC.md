# SPEC: datová sada a UI sekce „Lidé"

Zadání pro přestavbu panelu `panel-lide` z ručně psaných kartiček na datově
řízený adresář. Doplňuje [`README.md`](README.md) této sekce — tam patří
provozní pravidla („jak přidám osobu"), sem návrh a rozhodnutí, proč to tak je.

**Stav:** fáze 1–4 hotové — panel `panel-lide` se generuje z dat v této složce,
má fulltext, filtry, rozbalovací detail s timeline, pohled na uskupení a vlastní
routing v hashi. Probíhá fáze 5 (rozšíření dat), viz §3.6 a §7 — cílem je
doplnit **všechny kandidáty ze všech kandidátních listin** (2018, 2022, 2026),
zatím v minimální podobě (jméno, příjmení, vazba na kandidátku). Zbývá i
fáze 6 (propojení se zbytkem webu).

---

## 1. Cíl

Nahradit ručně psané `.person-card` v `index.html` třemi oddělenými entitami:

- **osoba** (`person`) — kdo to je,
- **organizace** (`organization`) — město a volební uskupení,
- **vazba** (`affiliation`) — samostatný záznam spojující osobu s organizací,
  s rolí a časovým rozsahem.

Rozdělení na tři entity je záměrné. Dnešní kartička slepuje tři různé věci do
jedné: *mandát v zastupitelstvu*, *funkci v radě* a *kandidátku, za kterou byl
člověk zvolen*. Každá z nich má vlastní začátek, konec a vlastní zdroj —
Ondřej Schulz má mandát od 26. 2. 2025, ale kandidoval v roce 2022; Alena
Švejnohová je zastupitelkou od ustavení, ale předsedkyní kontrolního výboru
až od února 2025. V jedné kartičce to zapsat nejde, ve třech vazbách ano.

Vedlejší efekt, který je vlastně hlavní: **historie přestane mizet.** Dnes se
při rezignaci kartička přepíše a informace, že v zastupitelstvu seděl někdo
jiný, zmizí. Ve vazbách se jen doplní `to` a záznam zůstane.

---

## 2. Uložení dat

Data, validátor i dokumentace žijí v **`lide/`**, stejným vzorem jako
`jednani/` a `noviny/`:

```
lide/
├── people.json          osoby
├── organizations.json   město + volební uskupení
├── affiliations.json    vazby osoba–organizace
├── validate.mjs         validátor (Node, bez závislostí)
├── README.md            provozní pravidla sekce
└── SPEC.md              tenhle dokument
```

**Fotky z volebních materiálů tady nejsou.** Portréty z kandidátek patří
k volebnímu ročníku, ve kterém byli lidé zvoleni —
`volby/2022/zastupitele/{prijmeni}.jpg` — a odkazuje se na ně plnou cestou
od kořene repa. Pravidlo je starší než tahle sekce, viz
[`volby/README.md`](../volby/README.md). Podsložka `lide/foto/` je na
portréty, které se k žádným volbám neváží (typicky z webu radnice) —
podrobně v §3.7.

**Proč tři soubory a ne jeden `lide.json`:** `jednani` a
`noviny` mají jeden soubor, protože drží jednu entitu. Tady jsou entity
tři a edituje se každá jinak často — osoby zřídka, vazby po každých volbách a
personální změně. Oddělené soubory znamenají čitelný diff a menší riziko
konfliktu.

**Proč vůbec externí JSON a ne data v `index.html`:** adresář poroste, Git diff
u datové změny nemá míchat obsah s kódem a stejný vzor už v projektu funguje.
Jednosouborovost `index.html` zůstává zachovaná ve smyslu, který projekt
dodržuje: žádný build, žádné npm, jen statické soubory.

**Načítání** — lazy, cache guard, přesně jako `loadJednani()` / `loadNoviny()`:

```js
let LIDE_DB = null;
let LIDE_LOADING = null;
async function loadLide() { /* Promise.all nad třemi fetchi, join, render */ }
```

V `applyPanel()` přibude `if (valid === 'lide') loadLide();`.

**Důsledek:** panel přestane fungovat z `file://` (CORS) — stejně jako už dnes
Jednání a Pečecké noviny. Lokálně `python3 -m http.server`.

---

## 3. Datový model

### 3.1 Konvence ID

- `id` je **slug**, nikdy pořadové číslo. Přeuspořádání pole nesmí nic rozbít.
- Osoba: příjmení + iniciála křestního bez diakritiky → `paluskam`,
  `svejnohovaa`. Při kolizi druhá iniciála nebo číslice.
- Organizace: zkrácený název bez diakritiky → `mesto-pecky`, `nasepecky`,
  `snk-pecky-pecakum`.
- Vazba: `{person_id}--{organization_id}--{pořadí}` → `paluskam--mesto-pecky--2`.
  Pořadí rozlišuje víc vazeb téže dvojice.
- Povolené znaky: `a–z`, `0–9`, `-`.
- **ID je neměnné.** Po zveřejnění se nepřejmenovává — odkazuje na něj URL i
  všechny vazby.

### 3.2 `people.json`

```json
{
  "meta": { "updated": "2026-08-27", "count": 23, "source": "…", "note": "…" },
  "people": [
    {
      "id": "paluskam",
      "first_name": "Milan",
      "last_name": "Paluska",
      "title_before": "",
      "title_after": "",
      "email": "",
      "phone": "",
      "photos": [
        {
          "year": 2026,
          "url": "/volby/2026/zastupitele/paluska.webp",
          "photo_source": "Oficiální portrét z kandidátní listiny ODS a nezávislí kandidáti, Pečky 2026 (ods.cz/os.kolin/volby2026/komunalni/3715-pecky)"
        },
        {
          "year": 2022,
          "url": "/volby/2022/zastupitele/paluska.jpg",
          "photo_source": "Oficiální portrét z kandidátky ODS Pečky 2022 (…)"
        }
      ],
      "bio": "Starosta města. Do funkce ho zastupitelstvo zvolilo…",
      "tags": ["zastupitel", "rada", "vedeni-mesta", "ods"],
      "sources": [{ "label": "Ustavující zasedání ZM 7/2022 — zápis", "url": "https://…" }],
      "verified": "2026-08-27"
    }
  ]
}
```

| Pole | Typ | Povinné | Poznámka |
|---|---|---|---|
| `id` | slug | ✅ | unikátní, neměnné |
| `first_name` / `last_name` | string | ✅ | `last_name` je řadicí klíč |
| `title_before` / `title_after` | string | — | `""` místo `null` |
| `email` | string | — | jen pracovní adresa, `""` když neznámá |
| `phone` | string | — | jedno nebo víc čísel oddělených `" · "`, každé ve tvaru `+420 123 456 789`; pořadí kancelář → mobil. `""` když neznámé |
| `photos` | objekt[] | — | `[]` → iniciálový avatar. Jeden člověk může mít fotku za víc let (kandidátka se opakuje, fotka se mění) — pole, ne jedna hodnota, viz §3.7 |
| `bio` | string | — | prostý text, bez HTML |
| `tags` | string[] | ✅ | viz §3.5 |
| `sources` | objekt[] | ✅ | `{label, url}`; min. 1 u každé osoby s funkcí |
| `verified` | `YYYY-MM-DD` \| `null` | ✅ | `null` = neověřeno → **žádný stamp v UI** |

### 3.3 `organizations.json`

```json
{
  "id": "nasepecky",
  "name": "NAŠE PEČKY A PEČKY NEXT",
  "short_name": "NAŠE PEČKY",
  "type": "politicke",
  "ico": null,
  "address": "",
  "web": "",
  "color": "#4A4A4A",
  "css_class": "party-nasepecky",
  "former_names": ["SNK NAŠE PEČKY (2018)", "NAŠE PEČKY (STAN + nezávislí) (2022)"],
  "note": "2018: 39,60 % / 9 mandátů. 2022: 30,29 % / 7 mandátů…",
  "sources": [],
  "verified": "2026-08-27"
}
```

| Pole | Typ | Povinné | Poznámka |
|---|---|---|---|
| `id` | slug | ✅ | |
| `name` | string | ✅ | **aktuální** oficiální název |
| `short_name` | string | — | pro badge a úzké sloupce; fallback = `name` |
| `type` | enum | ✅ | `urad` · `prispevkova` · `firma` · `spolek` · `politicke` · `skola` · `jine` |
| `ico` | string \| `null` | — | 8 číslic jako **string** (vedoucí nuly); prolinkuje na Hlídač státu |
| `color` | `#RRGGBB` \| `null` | ✅ u `politicke` | z palety v [`volby/README.md`](../volby/README.md) |
| `css_class` | string \| `null` | ✅ u `politicke` | `party-*`, existující třída v `index.html` |
| `former_names` | string[] | ✅ | dřívější názvy s ročníkem; může být `[]` |

**Uskupení jsou jedna organizace napříč ročníky**, i když se jim mění název —
proto `former_names`. Barva je vlastnost uskupení, ne kartičky: paleta dnes
existuje jen v `index.html` a v README voleb, a tímhle polem dostane jedno
strojově čitelné místo. Validátor hlídá, že dvě uskupení nemají tutéž barvu.

### 3.4 `affiliations.json` — jádro modelu

```json
{
  "id": "paluskam--mesto-pecky--2",
  "person_id": "paluskam",
  "organization_id": "mesto-pecky",
  "role": "starosta",
  "role_type": "starosta",
  "from": "2022-10-20",
  "to": null,
  "current": true,
  "note": "Zvolen na ustavujícím zasedání ZM 7/2022, usnesení UZ-90-7/22, hlasování 13–6–2 (pro–proti–zdržel se).",
  "sources": [{ "label": "Usnesení UZ-90-7/22", "url": "https://…" }],
  "verified": "2026-08-27"
}
```

| Pole | Typ | Povinné | Poznámka |
|---|---|---|---|
| `person_id` / `organization_id` | slug | ✅ | musí existovat |
| `role` | string | ✅ | zobrazovaný text, volný |
| `role_type` | enum | ✅ | pro filtrování, viz níže |
| `from` / `to` | `YYYY-MM-DD` \| `YYYY` \| `null` | ✅ | `null` = neznámé / trvá |
| `current` | boolean | ✅ | zdroj pravdy pro „aktuální", **neodvozovat z dat** |

`role_type`: `zastupitel` · `rada` · `starosta` · `mistostarosta` ·
`vedeni-urad` · `vedeni-organizace` · `zamestnanec` · `clen` · `komise` ·
`kandidatka` · `jine`.

Vedení je rozdělené na dva typy, protože jde o dvě různé věci: **`vedeni-urad`**
je aparát radnice (tajemnice, vedoucí odborů, velitel městské policie) — vazba
vždy na `mesto-pecky`, protože úřad není samostatná právnická osoba a do funkce
jmenuje starosta; **`vedeni-organizace`** jsou ředitelé příspěvkových organizací
a jednatelé městských firem, které rada zřizuje a jejichž vedení jmenuje. Panel
Lidé je vypisuje jako dvě samostatné skupiny a validátor hlídá, že typ role
odpovídá `organization.type`.

**Pravidla:**

1. `current: true` a zároveň vyplněné `to` = **chyba validace**.
2. Jedna osoba může mít libovolně mnoho vazeb s `current: true`. To je smysl
   modelu, ne chyba — každý zastupitel má aspoň dvě (mandát + kandidátka),
   členové rady tři.
3. Ukončení funkce = nastavit `to` a `current: false`. Záznam se **nikdy
   nemaže**.
4. `current` je ruční příznak schválně: u části vazeb nebude známé datum konce
   a automatické odvození z `to` by tiše ukazovalo neaktuální lidi jako aktivní.

### 3.5 Kandidátka jako vazba, členství jako štítek

Uskupení, za které někdo **kandidoval**, je doložený fakt s datem a zdrojem
(kandidátní listina) — patří tedy do vazby, `role_type: "kandidatka"`, i když
daný člověk nezískal mandát. Model původně počítal jen se zvolenými (`from` =
den voleb), fáze 5 (§3.6) ho rozšiřuje na **všechny kandidáty všech
kandidátek** — zvolení i nezvolení. Náhradník má vazbu na kandidátku od voleb,
ale mandát až od složení slibu; ta nesrovnalost je správně a je vidět.

`from` u vazby `kandidatka`:
- 2018 a 2022 (volby proběhly): den voleb (`2018-10-05`, `2022-09-23`).
- 2026 (volby ještě neproběhly): datum registrace kandidátní listiny
  registračním úřadem (`2026-08-18`), ne datum voleb — to by tvrdilo něco, co
  se ještě nestalo. `role` u těchto vazeb popisné, např. „Kandidát/ka do
  zastupitelstva 2026", ne „zvolen/a".

**Členství ve straně** naproti tomu doložené není a do dat nepatří. Slug
uskupení zůstává i v `person.tags`, ale jen jako filtrovací zkratka odvozená
z kandidátky, ne jako tvrzení o stranické příslušnosti.

Doporučené jádro štítků: `zastupitel` · `rada` · `vedeni-mesta` ·
`byvaly-zastupitel` · `kandidat` · `komise` · `urednik` · `skolstvi` ·
`kultura` · `sport` · `spolky` + slug uskupení. `kandidat` patří lidem bez
jiné role — čistě filtrovací zkratka pro záznamy z §3.6.

### 3.6 Minimální záznam kandidáta (fáze 5)

Cíl: **v `people.json` je každý, kdo byl na kandidátní listině voleb 2018,
2022 nebo 2026** — ne jen současní/bývalí zastupitelé. K 30. 8. 2026 je stav
23 z 228 unikátních kandidátů napříč třemi ročníky (viz `content/volby2018.html`,
`content/volby2022.html`, `content/volby2026.html`, tabulka „Volební
uskupení" → sloupec „Lidé").

Pro člověka, který **nikdy nedržel žádnou funkci** (jen kandidoval), zatím
stačí minimální záznam — zbytek polí z §3.2 zůstává na výchozích prázdných
hodnotách, dokud se nedohledá zdroj:

```json
{
  "id": "novakj",
  "first_name": "Jan",
  "last_name": "Novák",
  "title_before": "", "title_after": "",
  "email": "", "phone": "",
  "photo": "", "photo_source": "",
  "bio": "",
  "tags": ["kandidat", "nasepecky"],
  "sources": [],
  "verified": null
}
```

a k němu jedna (nebo víc, kandidoval-li opakovaně) vazba — `current: true`
a `to: null` podle stávající konvence u `kandidatka` (je to fakt, který
netrvá jako funkce, ale ani „nekončí" — proto zůstává `current`, stejně jako
u dnešních 55 vazeb tohoto typu; `role_type: kandidatka` navíc validátor
nikdy nepočítá do 21 zastupitelů ani 7 radních, takže `current: true` tady
nic nerozbíjí):

```json
{
  "id": "novakj--nasepecky--1",
  "person_id": "novakj",
  "organization_id": "nasepecky",
  "role": "Kandidát do zastupitelstva 2022",
  "role_type": "kandidatka",
  "from": "2022-09-23",
  "to": null,
  "current": true,
  "note": "",
  "sources": [{"label": "Kandidátní listina, volby 2022", "url": "https://volby.gov.cz/…"}],
  "verified": "2026-08-31"
}
```

`role` je záměrně neutrální „Kandidát/ka do zastupitelstva {rok}", ne
„zvolen/a" — o zvolení a mandátu vypovídá samostatná vazba `zastupitel`
(pokud existuje), tahle jen dokládá účast na listině.

**Proč je to takhle a ne přísněji podle §3.2/§3.4:**
- `sources: []` na osobě je v pořádku — zdroj (kandidátní listina) je na
  vazbě, ne na osobě; §3.2 už dnes vyžaduje zdroj „jen u osoby s funkcí" a
  kandidát bez mandátu funkci nemá.
- `verified: null` na osobě neznamená chybu dat, jen že samotné jméno+příjmení
  nikdo dodatečně neověřoval nad rámec kandidátky — `.stamp` v UI se u ní
  neukáže, což je žádoucí (nepřehánět jistotu).

**Co dělat, když kandidát == osoba už v `people.json`:** nezakládat druhý
záznam osoby. Najít podle jména (diakritika i tituly se běžně liší mezi
zdroji — porovnávat jen jádrem jména), doplnit jen chybějící vazbu
`kandidatka` k existujícímu `person_id`. Typicky se to týká lidí, co
kandidovali víckrát (např. součást vedení města 2022 kandidující znovu 2026).

**Kolize `id`:** při 228 lidech běžná. Pravidlo z §3.1 (druhá iniciála,
případně číslice) platí beze změny — např. dva „Novák M." → `novakm`,
`novakm2`.

**Mimo rozsah zatím:** fotky, bio, kontakty, přesné tituly z listiny (kde se
liší od jiných zdrojů) — to všechno může doplnit až další průchod, jakmile
bude zdroj. Tenhle krok řeší jen dohledatelnost (fulltext, filtr podle
uskupení), ne úplnost profilu.

### 3.6b `phone` — víc čísel v jednom poli

Město u části funkcionářů uvádí kancelář i služební mobil. Obě čísla nesou
smysl (na jedno se dovoláš v úředních hodinách, na druhé jindy), takže se
zapisují obě do jednoho řetězce oddělené `" · "`:

```json
"phone": "+420 321 785 050 · +420 606 609 572"
```

Proč ne pole jako u `photos`: čísla nemají žádná další metadata (rok, zdroj,
popisek), takže by pole přineslo jen zanoření navíc. Oddělovač je dokumentovaný
a strojově zpracovatelný — `lPhoneLinks()` na něm dělí a z každého čísla dělá
vlastní odkaz `tel:` (v `href` bez mezer, ty některé telefony ve vytáčení
nezvládají). Validátor kontroluje tvar každého čísla zvlášť.

Ústředna `+420 321 785 051` se jako osobní kontakt nezapisuje — u lidí, kterým
telefonní seznam uvádí jen ji, zůstává `phone` prázdný nebo nese přímé číslo
z odborové stránky. Fax se nezapisuje vůbec.

### 3.7 `photos` — víc fotek na osobu

Jedna osoba může kandidovat opakovaně a fotka na kandidátce se mezi lety mění
(jiný portrét, jiná strana, žádná). Proto `person.photos` je pole, ne jedna
hodnota — každá položka je fotka za jeden ročník:

```json
{
  "year": 2026,
  "url": "/volby/2026/zastupitele/paluska.webp",
  "photo_source": "Oficiální portrét z kandidátní listiny ODS a nezávislí kandidáti, Pečky 2026 (ods.cz/os.kolin/volby2026/komunalni/3715-pecky)"
}
```

| Pole | Typ | Povinné | Poznámka |
|---|---|---|---|
| `year` | number | ✅ | ročník, ke kterému fotka patří (kandidátka nebo volební období toho roku, ne datum pořízení) |
| `url` | string | ✅ | cesta od kořene repa — viz pravidlo o umístění níž |
| `photo_source` | string | ✅ | původ fotky (strana, kandidátka, URL) |

**Kam fotka patří** podle toho, odkud je:

- **z volebního materiálu** (kandidátní listina, volební inzerce) →
  `volby/{rok}/zastupitele/…`, protože se váže k tomu ročníku;
- **z jiného veřejného zdroje** — typicky oficiální web města, kde má
  fotku vedení a úředníci bez vazby na volby → `lide/foto/…`.

Původní pravidlo znělo „fotky nikdy neleží v `lide/`" a platilo v době, kdy
všechny pocházely z kandidátek. Portrét 2. místostarosty Martina Jedličky
z pecky.as4u.cz do složky volebního ročníku nepatří — ta je popsaná jako
portréty *zvolených kandidátů z volebních materiálů* a strčit tam fotku
z webu radnice by o jejím původu lhalo.

**Pravidla:**
- Pole se řadí `year` sestupně (nejnovější první) — validátor i UI na tom
  spoléhají, `lPersonCard()` bere `photos[0]` jako aktuální avatar.
- Víc fotek za **stejný** rok nedává smysl (jedna kandidátka, jeden portrét)
  — validátor to hlásí jako chybu.
- Prázdné pole `[]` = žádná fotka nikdy nedohledána → iniciálový avatar,
  stejně jako dřív `photo: ""`.
- Detail osoby (`lPersonDetail()`) ukazuje všechny fotky s rokem a zdrojem,
  ne jen tu aktuální — i stará fotka je doklad, ne šum.
- Když se najde fotka za nový rok u někoho, kdo už fotku má, **stará
  položka se neodstraňuje**, jen přibude nová — stejná filozofie jako
  u vazeb v §3.4 (historie nemizí).

**Zdroje fotek za 2026 (ověřeno 31. 8. 2026):** dohledatelné jen u
uskupení, která si pro kampaň udělala vlastní web s portréty kandidátů
— ODS a nezávislí kandidáti (ods.cz) a NAŠE PEČKY A PEČKY NEXT
(nasepecky.cz), 36 fotek dohromady. Zbylá tři uskupení (Sdružení
nezávislých kandidátů PEČKY PEČÁKŮM, Lidé pro Pečky a Velké Chvalovice
s podporou SPD, Pečky srdcem) mají jen Facebook — stránku/skupinu jde
bez přihlášení projít jen omezeně a fotky v příspěvcích nemají jmenný
popisek, takže spárování se jménem by bylo nespolehlivé (riziko záměny
osoby). Nezkoušet znovu stejným postupem, dokud tahle tři uskupení
nezaloží vlastní web nebo nevyjde volební inzerce v Pečeckých novinách.

---

## 4. Validace

`node lide/validate.mjs` z kořene repa. Exit 0 = čisté, 1 = chyby.
Kromě obecné integrity (unikátní id, existující reference, číselníky, formáty
dat, `current` vs `to`, IČO jako 8místný string) hlídá i **domenová pravidla
Peček**:

- aktuálních zastupitelů je 21, členů rady 7, starosta právě jeden,
- každý aktuální zastupitel má vazbu na nějakou kandidátku,
- dvě uskupení nemají tutéž barvu,
- soubor, na který ukazuje `url` každé položky `photos`, existuje (chyba,
  ne varování — rozbitý obrázek na webu je vidět), a `photos` nemá dvě
  položky se stejným `year`.

Varování nejsou blokující: neověřený záznam, osoba bez vazby, ukončená vazba
bez data konce, `meta.example: true`.

---

## 5. UI sekce „Lidé"

Zachovat vizuální jazyk projektu — `--parchment` / `--ink` / `--burgundy` /
`--gold` / `--line`, Fraunces pro nadpisy, IBM Plex Mono pro metadata,
`.callout` a `.stamp` beze změny. Barvy kartiček brát z `organization.color`
a `organization.css_class`, ne z nové palety.

### 5.1 Rozvržení panelu

```
h2.title.display        Lidé, kteří řídí město
p.lede                  (stávající text)
div.stat-grid           [21 zastupitelů] [7 radních] [5 uskupení] [poslední aktualizace]
div.lide-controls       hledání · filtry · přepínač zobrazení
div#lide-results        mřížka karet, výchozí seskupení Rada / Ostatní
div.callout             o fotografiích + přiznané mezery
```

Výchozí stav panelu musí vypadat jako dnešní — Rada města (7) a Ostatní
členové zastupitelstva (14). Filtry jsou nadstavba, ne náhrada.

### 5.2 Ovládací lišta

- **Fulltext** — jedno pole přes jméno, roli, název organizace i `bio`. Použít
  existující `jNorm` / `jStripDiacritics` (hledání „svejnohova" musí najít
  „Švejnohová"). Debounce 150 ms.
- **Filtr uskupení** — čipy z organizací typu `politicke` obarvené `color`.
- **Filtr role** — čipy podle `role_type`, vícenásobný výběr.
- **Přepínač „jen aktuální / včetně historie"** — výchozí **jen aktuální**.
  Po přepnutí přibudou Bc. Iveta Dvořáková a Lenka Třísková.
- **Vymazat filtry** + počet výsledků („7 z 21 zastupitelů").

Kombinace filtrů = AND mezi skupinami, OR uvnitř skupiny.

### 5.3 Karta osoby

Zachovat stávající `.person-card` včetně `.avatar` / `.avatar-fallback`
(iniciály na barvě uskupení — dnes inline, nově z `organization.color`).
Přibude jen `data-person="{id}"` a rozbalovací detail.

### 5.4 Detail osoby

Rozbalení pod kartou vzorem `.exp-row` / `.exp-detail[hidden]` s přepínáním
`+`/`−`, ne modál — kvůli sdílení odkazu a tisku. Obsah:

- `bio`,
- **timeline vazeb** — všechny vazby osoby řazené `from` sestupně, aktuální
  nahoře a zvýrazněné `--field`, ukončené tlumené `--ink-soft`; formát
  `role · organizace · 2022 – dosud`,
- poznámka u vazby (`note`) — právě tam žije hlasování při volbě do rady,
- zdroje jako odkazy s `↗`, `target="_blank" rel="noopener"`,
- `<span class="stamp">ověřeno</span>` **jen** když `verified !== null`.

### 5.5 Pohled na uskupení

Klik na název uskupení → filtr se přepne a nad výsledky se vypíše hlavička:
název, `former_names`, výsledky z `note`, a seznam rozdělený „aktuálně" /
„dříve". U organizace s `ico` odkaz na Hlídač státu.

### 5.6 URL a odkazovatelnost

Hash je zdroj pravdy, konzistentně se zbytkem webu:

```
#lide                            panel bez filtru
#lide/osoba/paluskam             otevřený detail osoby
#lide/uskupeni/nasepecky         uskupení
#lide?q=novak&org=nasepecky      aktivní filtry
```

Zpět/Vpřed musí fungovat. Neznámé ID → panel + `.callout` „Osobu se nepodařilo
najít."

### 5.7 Stavy a přístupnost

- **Načítání** — kostra karet, ne spinner.
- **Chyba fetche** — `.callout` s `border-left-color:var(--burgundy)` a odkazem
  na surový JSON. Zbytek webu to nesmí rozbít.
- **Nula výsledků** — text + „Vymazat filtry".
- Filtry jsou `<button aria-pressed>`, výsledky `aria-live="polite"` s počtem,
  detail má `aria-controls` + `aria-expanded`.
- Mobil: mřížka na jeden sloupec, ovládací lišta sbalená pod „Filtry".

---

## 6. Etika a ochrana údajů

Patří do `.callout` v patě sekce (částečně tam už je — „O fotografiích"):

1. Jen údaje z **veřejných zdrojů** — úřední deska, oficiální web města,
   obchodní rejstřík, zápisy zastupitelstva, výsledky voleb.
2. **Pouze pracovní kontakty.** Žádné soukromé adresy, mobily, data narození,
   rodinné vazby.
3. Každá funkce má **zdroj**. Bez zdroje se nezveřejňuje — přiznaná mezera je
   lepší než nedoložené tvrzení. Kde je údaj dopočítaný, musí to být v `note`
   napsané (viz uskupení Dvořákové a Třískové).
4. Zveřejňují se lidé ve **veřejné funkci**, ne řadoví zaměstnanci úřadu.
5. Kontakt na opravu a vyřízení do 14 dnů. Opravit fakt, nemazat historii.
6. `noindex` na detaily osob **nedávat** — smyslem je dohledatelnost; místo
   toho hlídat přesnost.

---

## 7. Plán implementace

### ✅ Fáze 1 — data (hotovo)
`people.json` (21 aktuálních + 2 bývalí), `organizations.json` (město + 8
uskupení z voleb 2018/2022/2026), `affiliations.json` (55 vazeb), `validate.mjs`,
README. Ověřeno proti `index.html`: 21 jmen, uskupení i cest k fotkám sedí.

### ✅ Fáze 2 — načtení a základní render (hotovo)
`loadLide()` v posledním `<script>` bloku `index.html`: `Promise.all` nad třemi
fetchi, `lJoin()` spojí osoby s vazbami a rozvinutými organizacemi, `lRender()`
vykreslí mřížku se seskupením Rada města / Ostatní členové zastupitelstva.
Zobrazují se jen vazby s `current: true`, filtry zatím žádné.

Detaily implementace:

- barva kartičky z `organization.css_class`, barva iniciálového avataru
  z `organization.color` — paleta se už nikde nepíše ručně,
- na kartičce se ukazuje funkce v radě, a když žádná není, mandát; přívlastek
  „(uvolněný)" se z popisku ořezává, v datech zůstává,
- `#lide-status` a `#lide-photo-count` se dopočítávají z dat, aby čísla
  v textu nezastarala,
- při selhání `fetch` se vykreslí `.callout` s odkazy na surové JSON a zmínkou
  o `file://`; chyba se nepropaguje výš, aby `applyPanel()` nekončil
  nezachyceným odmítnutím Promise,
- `data-goto` uvnitř generovaného HTML má vlastní posluchač — globální běží
  jen jednou při startu a na dodatečně vložené uzly nedosáhne.

*Ověřeno:* headless běh celé stránky v jsdom — 21 kartiček, obě skupiny se
správnými počty, 13 fotek s existujícími soubory, 8 iniciálových avatarů,
`data-goto` přepne na Volby 2022, cache guard nepřekresluje, a při 404 se
zobrazí chybový callout, aniž se rozbije zbytek webu.

### ✅ Fáze 3 — hledání a filtry (hotovo)
Stav filtrů drží `L_STATE = {q, orgs:Set, roles:Set, scope}`, `lMatches()`
rozhoduje o jedné osobě, `lRenderResults()` překresluje. Skupiny Rada / Ostatní
/ Bývalí zůstávají i při filtrování — prázdná skupina prostě zmizí, takže
nevznikly dva různé režimy vykreslování.

- **Fulltext** nad předpočítaným `p._haystack` (jméno, `bio`, `tags`, role
  všech vazeb, názvy organizací **včetně `former_names`**) — normalizuje
  `jNorm`, takže „svejnohova" najde Švejnohovou a „SNK NASE PECKY" najde
  dnešní NAŠE PEČKY. Víc slov = AND. Debounce 150 ms.
- **Čipy uskupení** se generují z organizací typu `politicke`, které mají
  aspoň jednu vazbu; barva tečky i orámování aktivního čipu jde z
  `organization.color` (`--chip`).
- **Čipy rolí** z `role_type` přítomných v datech, popisky v `L_ROLE_LABELS`.
- **AND mezi skupinami, OR uvnitř** — ODS + NAŠE PEČKY dá 13 lidí, po přidání
  čipu „Radní" zbydou 3.
- **Rozsah** `current` / `all`; ve výchozím stavu bývalí členové nejsou vidět
  ani přes hledání, po přepnutí přibude třetí skupina a štítek `do 26. 2. 2025`.
- **Prázdný výsledek** má vlastní `.callout` s tlačítkem „vymaž filtry" a
  připomínkou přepínače rozsahu.

Přístupnost: čipy jsou `<button aria-pressed>`, oba řádky `role="group"`
s `aria-label`, status má `aria-live="polite"` (na kartičkách schválně ne —
při psaní by čtečku zahltilo překreslování 21 karet).

*Ověřeno:* headless běh v jsdom — hledání bez diakritiky, hledání podle role
i historického názvu uskupení, OR uvnitř skupiny, AND mezi skupinami, přepnutí
rozsahu, prázdný stav a obě cesty k vymazání filtrů.

### ✅ Fáze 4 — detaily a URL (hotovo)

**Routing.** `currentHashPanel()` v jádru webu bere jen první segment hashe,
takže `#lide/osoba/paluskam?scope=all` pořád aktivuje panel Lidé. Tvary:

```
#lide                            adresář
#lide/osoba/{id}                 otevřený detail
#lide/uskupeni/{id}              pohled na uskupení
#lide?q=…&org=…&role=…&scope=all filtry
```

`lApplyRoute()` je jediné místo, kde se stav nastavuje — klik nikdy nemění
`L_STATE` a nevykresluje přímo, jen přepíše hash a nechá se zavolat routerem.
Otevření detailu a vstup na uskupení jdou přes `location.hash` (nová položka
v historii, Zpět funguje), změna filtru přes `history.replaceState` — jinak by
každé písmeno v hledání přidalo krok do historie.

**Dvě úpravy v jádru webu, které si to vyžádalo:**

- `applyPanel()` scrolluje nahoru jen při skutečné změně panelu. Bez toho by
  otevření detailu (hashchange uvnitř téhož panelu) utíkalo na začátek stránky.
  Klik na už aktivní záložku scrolluje dál — dostal explicitní `{scroll: true}`.
- Odkaz na Volby 2022 v generovaném callloutu má `href="#volby2022"` místo
  `href="#"`. Kdyby `preventDefault()` nestihl zabrat, prohlížeč přejde na
  správný panel místo aby hash vymazal.

**Detail** se rozbaluje pod kartičkou uvnitř mřížky (`grid-column: 1 / -1`),
ne v modálu — kvůli sdílení odkazu a tisku. Obsahuje `bio`, kontakty, timeline
všech vazeb a patičku se zdroji a razítkem „ověřeno". Timeline řadí aktuální
vazby nahoru, uvnitř podle váhy funkce (`L_TL_ORDER`) a teprve pak podle data —
starosta i mandát začaly týmž dnem a čistě chronologické řazení by nahoru
vytáhlo náhodné z nich. Neověřená vazba má v řádku období příznak „neověřeno",
`note` nese poměr hlasů při volbě do rady.

**Pohled na uskupení** ukazuje hlavičku s názvem, `former_names`, poznámkou
(volební výsledky), odkazem na web a u organizace s `ico` na Hlídač státu.
Vstupuje se do něj klikem na uskupení na kartičce nebo v timeline.

**Chybové stavy:** neznámé `id` v hashi vypíše callout a vykreslí zbytek
adresáře, místo aby tiše spadlo na prázdno.

**Přístupnost:** kartička je `role="button"` s `tabindex="0"`, `aria-expanded`
a `aria-controls`; ovládá se Enterem, mezerníkem a zavírá Escapem. Uskupení na
kartičce je klikací jen myší a *není* samostatný tab stop — vnořený ovládací
prvek uvnitř `role="button"` by mátl čtečky. Pro klávesnici a čtečky vede na
uskupení čip ve filtru a pravý odkaz v timeline.

*Ověřeno:* headless běh v jsdom — přímý odkaz na osobu i uskupení, filtry z URL,
timeline aktuálních i ukončených vazeb, poměr hlasů a příznak „neověřeno",
odkaz na Hlídač státu, neznámé `id`, klik → hash → Zpět → obnovený detail,
zavření, psaní do hledání bez zaplevelení historie, a přechod na jiný panel,
který podcestu zahodí.

### Fáze 5 — rozšíření dat

**5a — všichni kandidáti všech kandidátek (aktuální priorita).** Viz §3.6 pro
formát záznamu a pravidla. Rozsah k 30. 8. 2026:

| Ročník | Kandidátů | Uskupení |
|---|---|---|
| 2018 | 125 (6 uskupení × 20–21) | SNK NAŠE PEČKY, Sdružení ODS a NK, KSČM, PEČKY PEČÁKŮM, ČSSD, LIDOVCI A NEZÁVISLÍ |
| 2022 | 126 (6 × 21) | NAŠE PEČKY, ODS a NK, SNK Pečky Pečákům, Lidé pro Pečky (SPD), ČSSD a sjednocená levice, Lidovci a nezávislí |
| 2026 | 105 (5 × 21) | ODS a NK, PEČKY PEČÁKŮM, NAŠE PEČKY A PEČKY NEXT, Lidé pro Pečky a VCH (SPD), Pečky srdcem |

228 unikátních jmen napříč ročníky (někteří kandidovali víckrát), 23 už
v `people.json` → **205 nových záznamů**. Organizace (§3.3) není třeba
zakládat, všech 9 (město + 8 uskupení) už existuje se správným
`former_names` pokrytím napříč lety. Zdroj jmen: tabulka „Volební uskupení"
v `content/volby2018.html` / `volby2022.html` / `volby2026.html` (sloupec
„Lidé", `title` atribut každého `av-init`/`av-img`), případně přímo
volby.gov.cz — u 2026 konkrétně [Jmenné seznamy ČSÚ](https://volby.gov.cz/app/kv2026/cs/20261009/name-lists/!_0_1_2100_2104_537641).

Po doběhnutí 5a zvýšit `meta.count` v `people.json` (23 → 228) a
`affiliations.json` (55 → přibližně 260, 205 nových `kandidatka` vazeb + pár
pro lidi, kteří kandidovali víckrát a v datech už jsou), spustit
`node lide/validate.mjs` a v `README.md` → „Stav sekcí" zapsat řádek se
změnou.

**5b — zbytek (po 5a).** Členové finančního a kontrolního výboru z
ustavujícího zasedání (`UZ-98`…`UZ-111`), vedení příspěvkových organizací a
městských firem, doplnění `bio`/foto/`sources` u kandidátů z 5a, kde se
zdroj najde. Doplnit chybějící kontakty z organizační struktury úřadu.

### Fáze 6 — propojení se zbytkem webu
- jména v archivu jednání (`jednani`) prolinkovat na `#lide/osoba/{id}`,
- organizace s `ico` → Hlídač státu a panel Smlouvy,
- avatary u volby vedení v panelu Volby 2022 brát z `people.json` místo
  ručních cest.

Fáze 1–4 tvoří použitelný celek; 5 a 6 jsou přírůstkové.

---

## 8. Výkon

Zlom nastává kolem **~300 osob**; při dnešních 23 stačí nejjednodušší řešení.

- **Do ~300 osob:** filtrovat celé pole při každé změně, překreslovat
  `innerHTML` kontejneru. Bez optimalizací.
- **Nad ~300:** předpočítat normalizovaný index při načtení (`{id, haystack}`),
  aby `jStripDiacritics` neběžel při každém stisku; render přes
  `DocumentFragment`; stránkovat po 50.
- **Fotky:** `loading="lazy"` (už je), `width`/`height` proti CLS.
- **Cache:** verzovat query stringem (`lide/people.json?v=2026-08-27`).

---

## 9. Definition of done (fáze 2–4)

- [x] Panel „Lidé" se plní výhradně z JSON, žádné natvrdo psané kartičky
- [x] Výchozí zobrazení je vizuálně shodné s původním
- [x] Fulltext funguje bez ohledu na diakritiku
- [x] Filtry kombinovatelné, počet výsledků a vymazání filtrů funkční
- [x] Detail s timeline rozlišuje aktuální a ukončené vazby
- [x] `#lide/osoba/{id}` funguje jako přímý odkaz, Zpět/Vpřed drží stav
- [x] Stamp „ověřeno" jen u `verified !== null`, zdroje u každé funkce
- [ ] Mobil 360 px bez vodorovného scrollu — **neověřeno v prohlížeči**
- [x] Chybějící nebo vadný JSON nerozbije zbytek webu — jen `.callout` v panelu
- [x] `node lide/validate.mjs` hlásí 0 chyb
