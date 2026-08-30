# SPEC: datová sada a UI sekce „Lidé"

Zadání pro přestavbu panelu `panel-lide` z ručně psaných kartiček na datově
řízený adresář. Doplňuje [`README.md`](README.md) této sekce — tam patří
provozní pravidla („jak přidám osobu"), sem návrh a rozhodnutí, proč to tak je.

**Stav:** fáze 1–4 hotové — panel `panel-lide` se generuje z dat v této složce,
má fulltext, filtry, rozbalovací detail s timeline, pohled na uskupení a vlastní
routing v hashi. Zbývá fáze 5 (rozšíření dat) a 6 (propojení se zbytkem webu).

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

Data, validátor i dokumentace žijí v **`pecky-lide/`**, stejným vzorem jako
`pecky-jednani/` a `pecky-noviny/`:

```
pecky-lide/
├── people.json          osoby
├── organizations.json   město + volební uskupení
├── affiliations.json    vazby osoba–organizace
├── validate.mjs         validátor (Node, bez závislostí)
├── README.md            provozní pravidla sekce
└── SPEC.md              tenhle dokument
```

**Fotky tady nejsou** a nebudou. Portréty patří k volebnímu ročníku, ve kterém
byli lidé zvoleni — `pecky-volby/2022/zastupitele/{prijmeni}.jpg` — a odkazuje
se na ně plnou cestou od kořene repa. Pravidlo je starší než tahle sekce, viz
[`pecky-volby/README.md`](../pecky-volby/README.md).

**Proč tři soubory a ne jeden `pecky-lide.json`:** `pecky-jednani` a
`pecky-noviny` mají jeden soubor, protože drží jednu entitu. Tady jsou entity
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
      "photo": "pecky-volby/2022/zastupitele/paluska.jpg",
      "photo_source": "Oficiální portrét z kandidátky ODS Pečky 2022 (…)",
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
| `email` / `phone` | string | — | jen pracovní kontakty, `""` když neznámé |
| `photo` | string | — | cesta od kořene repa; `""` → iniciálový avatar |
| `photo_source` | string | — | původ fotky; povinné, když je `photo` |
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
| `color` | `#RRGGBB` \| `null` | ✅ u `politicke` | z palety v [`pecky-volby/README.md`](../pecky-volby/README.md) |
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

`role_type`: `zastupitel` · `rada` · `starosta` · `mistostarosta` · `vedeni` ·
`zamestnanec` · `clen` · `komise` · `kandidatka` · `jine`.

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

Uskupení, za které byl někdo **zvolen**, je doložený fakt s datem a zdrojem
(výsledky ČSÚ) — patří tedy do vazby, `role_type: "kandidatka"`, `from` = den
voleb. Náhradník má vazbu na kandidátku od voleb, ale mandát až od složení
slibu; ta nesrovnalost je správně a je vidět.

**Členství ve straně** naproti tomu doložené není a do dat nepatří. Slug
uskupení zůstává i v `person.tags`, ale jen jako filtrovací zkratka odvozená
z kandidátky, ne jako tvrzení o stranické příslušnosti.

Doporučené jádro štítků: `zastupitel` · `rada` · `vedeni-mesta` ·
`byvaly-zastupitel` · `komise` · `urednik` · `skolstvi` · `kultura` · `sport` ·
`spolky` + slug uskupení.

---

## 4. Validace

`node pecky-lide/validate.mjs` z kořene repa. Exit 0 = čisté, 1 = chyby.
Kromě obecné integrity (unikátní id, existující reference, číselníky, formáty
dat, `current` vs `to`, IČO jako 8místný string) hlídá i **domenová pravidla
Peček**:

- aktuálních zastupitelů je 21, členů rady 7, starosta právě jeden,
- každý aktuální zastupitel má vazbu na nějakou kandidátku,
- dvě uskupení nemají tutéž barvu,
- soubor, na který ukazuje `photo`, existuje (chyba, ne varování — rozbitý
  obrázek na webu je vidět).

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
Členové finančního a kontrolního výboru z ustavujícího zasedání
(`UZ-98`…`UZ-111`), vedení příspěvkových organizací a městských firem, ročník
2018 jako historie (`current: false`). Doplnit chybějící kontakty z organizační
struktury úřadu.

### Fáze 6 — propojení se zbytkem webu
- jména v archivu jednání (`pecky-jednani`) prolinkovat na `#lide/osoba/{id}`,
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
- **Cache:** verzovat query stringem (`pecky-lide/people.json?v=2026-08-27`).

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
- [x] `node pecky-lide/validate.mjs` hlásí 0 chyb
