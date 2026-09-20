# Instrukce k sekci: Lidé (panel `lide`)

Referenční dokument pro práci na panelu `panel-lide` v
`content/lide.html` (generuje se do veřejné stránky `/lide/`, viz
`scripts/build.py`). Doplňuje obecné instrukce projektu (Project instructions /
CLAUDE.md) — tohle je detail jen pro tuhle jednu sekci.

## Účel sekce
Kartičky členů zastupitelstva (21) a rady města (7) — kdo v nich sedí,
za jaké uskupení, případně fotka. Zdroj: jmenný seznam ZM/RM z pecky.cz,
doplňkově web ODS Pečky (viz kořenový `README.md` → „Zdroje dat").

Každé politické uskupení má na celém webu jednu pevně přiřazenou barvu
(CSS třídy `.person-card.party-*`) — používá se konzistentně napříč
sekcemi Lidé, Plán, Volby 2018/2022/2026. Tabulka barev je v
[`volby/README.md`](../volby/README.md) → „Barevná paleta
uskupení"; při přidávání nového uskupení nebo člena vždy použít
existující barvu z té tabulky, ne vymýšlet novou.

Známá mezera: kompletní seznam 21 zastupitelů se nedaří ověřit napřímo
(pecky.cz blokuje bot přístup) — viz kořenový `CLAUDE.md`.

## Lidé = aktuální stav, Volby = stav při ustavení
Tenhle panel ukazuje, kdo v zastupitelstvu a radě sedí **teď**. Jmenný
seznam zvolených po volbách je v subpanelu „Výsledky voleb" příslušného
ročníku — viz [`volby/README.md`](../volby/README.md) →
„Zvolení zástupci". **Oba seznamy jsou samostatné a už se rozcházejí:**
od ustavujícího zasedání 20. 10. 2022 se složení dvakrát změnilo —
Jaroslava Vosecká nastoupila za Lenku Třískovou (slib 11. 9. 2024) a
Ondřej Schulz za Bc. Ivetu Dvořákovou (slib 26. 2. 2025). Při další
rezignaci, kooptaci náhradníka nebo změně ve vedení se opraví **jen
tenhle panel**; historický seznam u Voleb 2022 zůstává, jaký byl.

## Fotky
Portréty na kartičkách (`img.avatar`) nejsou ve složce této sekce —
leží u volebního ročníku, ke kterému se váží: `volby/2022/zastupitele/
{prijmeni}.jpg` (42 souborů, příjmení bez diakritiky malými písmeny;
u shody příjmení i s křestním, např. `hruska-ivan.jpg`), od 30. 8. 2026
i `volby/2026/zastupitele/{prijmeni}.webp` (15 souborů, kandidátka ODS
z ods.cz — kandidátka nejde stáhnout jako jpg, formát ponechán webp).
Jeden člověk tak může mít fotky ve víc ročnících najednou — proto
`people.json` drží `photos` jako pole, ne jednu hodnotu, viz SPEC.md
§3.7. Po dalších volbách zakládat novou sadu ve složce nového ročníku,
staré nepřepisovat. Detaily viz [`volby/README.md`](../volby/README.md).

Výjimkou jsou portréty, které nepocházejí z voleb — ty leží v
`lide/foto/{prijmeni}.jpg`. Zatím jde o jediný případ: 2. místostarosta
Ing. Martin Jedlička, jehož fotka je z Rady města na oficiálním webu
(pecky.as4u.cz). Do složky volebního ročníku nepatří, protože ta je
popsaná jako portréty zvolených kandidátů z volebních materiálů — fotka
z webu radnice by tam o svém původu lhala.

## Datová sada

Ve složce leží strojově čitelný adresář osob, organizací a vazeb mezi
nimi. Návrh a rozhodnutí, proč je model takový, jsou v [`SPEC.md`](SPEC.md);
tahle kapitola je provozní — jak s daty pracovat.

```
foto/                portréty z jiných zdrojů než z voleb (viz níž)
people.json          266 osob (21 aktuálních zastupitelů + 2 bývalí s plným
                      profilem, 206 dalších kandidátů ze všech kandidátek
                      2018/2022/2026 s minimálním záznamem (SPEC.md §3.6),
                      13 vedení úřadu/příspěvkovek/firem (fáze 5b, §7),
                      8 nových jen kvůli členství v komisi RM/školské radě)
organizations.json   16 organizací (Město Pečky + 8 volebních uskupení +
                      7 příspěvkovek/firem — fáze 5b)
affiliations.json   485 vazeb osoba–organizace
validate.mjs         validátor
```

**Komise RM a školská rada** (doplněno 19. 9. 2026): pět iniciativních a
poradních komisí rady města (sportovní, kulturní, Sbor pro občanské
záležitosti, stavebně-dopravní a ŽP, sociální/zdravotní/bytová) plus
školská rada ZŠ Pečky. Modelováno jako vazby s `role_type: "komise"` —
stejný typ, jaký už měl předsednictví kontrolního výboru zastupitelstva —
ne jako nové organizace: komise nejsou samostatné právnické osoby, jde
o orgány zřízené radou (viz `Jednaci_rad_komisi.pdf` na pecky.cz), takže
vazby míří na existující `mesto-pecky` (pět komisí RM) nebo `zs-pecky`
(školská rada, protože jde o orgán školy, ne úřadu). Zdroj: podstránky
pecky.cz → Rada města → Komise RM; přesné datum jmenování tam není
uvedené, jen aktuální složení — vazby proto mají `from: null` a `note`
s vysvětlením. Členství v komisi teď počítá do `_office` stejně jako
`vedeni-urad`/`vedeni-organizace`/`zamestnanec` (viz `content/lide.html`
→ `lJoin`), jinak by přes 20 lidí, kteří v komisi sedí, ale nikdy
nekandidovali ani nepracují na úřadu, v adresáři vůbec nenaskočilo —
stejná past, jaké se předešlo u `vedeni-urad`/`vedeni-organizace`
(fáze 5b, viz odstavec výš). Panel proto má šestou skupinu „Komise rady
města a školská rada"; kdo má vedle komise i mandát, úřad nebo vedení
organizace, zůstává ve své dosavadní skupině — komise je pak vidět jen
v jeho detailu/timeline, ne jako duplicitní kartička.

**Vedení úřadu, příspěvkových organizací a městských firem** (`role_type:
"vedeni-urad"` a `"vedeni-organizace"`, doplněno 5. 9. 2026, fáze 5b
SPEC.md §7): tajemnice úřadu, 4
vedoucí odborů a velitel Městské policie (všichni jako vazba na
`mesto-pecky` — úřad je součástí téže právnické osoby jako obec, ne
samostatná organizace), plus ředitel/ka u každé ze 7 nově založených
organizací (MŠ MAŠINKA, ZŠ, ZUŠ, Kulturní středisko, Městská knihovna,
Pečovatelská služba, Pečecké služby s.r.o.). Zdroj: kontaktní stránky
pecky.cz, cross-ověřeno v Hlídači státu; u Pečeckých služeb (s.r.o.)
jednatelka dohledána přímo v obchodním rejstříku (justice.cz), protože
firemní web k datu ověření uváděl už neplatné jméno — viz `note` u
organizace `pececke-sluzby`. Aby se tihle lidé (bez mandátu v ZM/RM)
zobrazili i ve výchozím rozsahu „Jen aktuální“, `lInScope()` v
`content/lide.html` teď kromě `_mandate`/`_exec` počítá i s `_vedeni`.

**Panel `panel-lide` se z těchhle souborů generuje.** Kartičky v
`index.html` už nejsou — vytváří je `loadLide()` v posledním `<script>`
bloku. Personální změna se tedy dělá **jen v JSON**, do HTML nesahat.

Ručně psaný v panelu zůstává jen nadpis a úvodní odstavec; řádek se
statistikou nad kartičkami (`#lide-status`) se dopočítává z dat.

Souhrnný callout „O fotografiích" **na stránce už není** (odstraněn
5. 9. 2026). Původ každé fotky nese `photo_source` u příslušné položky
v `photos` a vypisuje se v detailu osoby s rokem. Cenou za to je, že
web už nikde nevysvětluje, **proč** u části lidí fotka chybí —
zdůvodnění (tři z pěti uskupení mají jen Facebook, kde nejdou fotky
spolehlivě spárovat se jmény) zůstalo jen v historii gitu a v
[`volby/2026/README.md`](../volby/2026/README.md).

Protože se data načítají `fetch`em, panel **nefunguje z `file://`** —
stejně jako Jednání a Pečecké noviny. Lokálně `python3 -m http.server`.

### Odkazovatelné adresy

Panel má vlastní routing v hashi, takže na konkrétního člověka i uskupení
jde poslat odkaz:

```
#lide/osoba/paluskam               detail starosty
#lide/uskupeni/nasepecky           uskupení a jeho lidé
#lide?org=ods&role=rada            radní za ODS
#lide?q=svejnohova&scope=all       hledání včetně bývalých členů
```

Adresy stojí na `id` z JSON — proto se `id` po zveřejnění nemění.

### Vizitka osoby je sdílená komponenta (od 19. 9. 2026)

Vykreslení detailu osoby (`lPersonDetail` v `content/lide.html`) i avatar
kartičky delegují na `pcDetailHtml`/`pcAvatarHtml`/`pcBuildTimeline`
v `assets/helpers.js` — čistě formátovací a vykreslovací funkce bez závislosti
na routingu nebo filtrech téhle sekce. Vznikly proto, aby stejnou vizitku šlo
znovu použít i mimo Lidé: první uplatnění je jméno v tabulce Jednání →
Absence (`/jednani/absence.html`, viz `jednani/README.md` →
„Avatar a vizitka osoby u jména"), kde se klikem na jméno rozbalí přesně
tahle karta. `content/lide.html` si drží krátké aliasy (`lFullName`,
`lRoleLabel` apod.) na `pc*` funkce, ať se nemusí přepisovat zbytek souboru —
při úpravě formátování (datum, telefon, timeline) měnit vždy `pc*` verzi
v `assets/helpers.js`, ne kopírovat logiku zpátky sem.

### Tři entity, ne jedna kartička

Dnešní kartička slepuje tři různé věci dohromady. V datech jsou oddělené,
protože každá má vlastní začátek, konec a zdroj:

| Vazba | `role_type` | Od kdy | Zdroj |
|---|---|---|---|
| mandát v zastupitelstvu | `zastupitel` | složení slibu | zápis ustavujícího zasedání |
| funkce v radě | `starosta`, `mistostarosta`, `rada` | volba na ustavujícím zasedání | usnesení `UZ-90-7/22`…`UZ-96-7/22` |
| kandidátka, za kterou byl zvolen | `kandidatka` | den voleb | výsledky ČSÚ |

Proto má každý zastupitel nejméně dvě vazby a člen rady tři. Že je
někdo zároveň radní i zastupitel, **není duplicita**.

Náhradník má vazbu na kandidátku od voleb 2022, ale mandát až od složení
slibu — Ondřej Schulz od 26. 2. 2025, Jaroslava Vosecká od 11. 9. 2024.
Ten rozdíl je správně a je vidět v timeline.

### Co panel vypisuje a co ne

Šest skupin v tomhle pořadí: **Rada města**, **Ostatní členové
zastupitelstva**, **Úřad města** (`vedeni-urad`), **Městské organizace**
(`vedeni-organizace`), **Komise rady města a školská rada** (`komise`,
doplněno 19. 9. 2026) a — až po přepnutí rozsahu na „Včetně historie" —
**Dřívější vedení a bývalí zastupitelé**. Volení lidé nahoře, jmenovaní
pod nimi, historie nakonec.

Poslední skupina není jen o lidech, kteří odešli uprostřed období. Patří
do ní každý s doloženou ukončenou funkcí a bez aktuální — tedy i starostové,
místostarostové a radní minulých volebních období.

**Se zapnutým filtrem podle role se skupiny pojmenují podle něj** —
„Starosta — nyní" a „Starosta — dříve" — a výchozí pětice se nevykreslí.
Důvod: seskupení podle *dnešního* postavení přestává dávat smysl ve chvíli,
kdy filtr matchuje i minulé funkce. Hledání starostů s historií vracelo
Milana Urbana a Alenu Švejnohovou pod nadpisem „Ostatní členové
zastupitelstva" s popiskem „Bez funkce v radě" — pravdivé o jejich dnešním
postavení, ale mlčící o tom, proč se v seznamu octli. Kartička dál ukazuje
současné postavení, celý průběh je v detailu.

Filtr rolí míří na `role_type`, ne na členství v radě jako orgánu.
Místostarosta je člen rady, ale má vlastní `role_type`, takže pod „Radní"
nespadá — Zdeněk Fejfar se proto objeví v „Radní — dříve" (radním byl
2014–2018, dnes je místostarosta). Je to důsledek modelu, ne chyba.

Nad kartičkami je jediný řádek filtrů, **podle role**. Čipy podle uskupení
tam byly a jsou pryč — řádek s pěti stranami nad jednadvaceti lidmi zabíral
víc místa, než přinášel. **Filtrování podle uskupení ale nezmizelo**, jen
nemá vlastní tlačítka: pořád funguje přes URL (`#lide?org=ods`), přes klik
na uskupení na kartičce a přes pohled `#lide/uskupeni/{id}`. Kdo by chtěl
čipy zpátky, vrátí je v `lBuildChips()` — `L_STATE.orgs` i větev v
`lMatches()` zůstaly na místě.

Kdo nespadá ani do jedné, se **nevypisuje a nezapočítává** do statistiky nad
kartičkami. V praxi jde o lidi, o kterých z dat víme jen to, že byli na nějaké
kandidátní listině (`role_type: "kandidatka"` a nic dalšího) — dnes přes dvě
stovky záznamů z ročníků 2018/2022/2026. V `people.json` zůstávají a používají
je sekce Volby, panel Lidé je ale nezobrazuje.

Dřív je sbírala skupina „Kandidáti bez mandátu". Ten nadpis byl zavádějící:
padali do něj i vedoucí odborů a ředitelé městských organizací, kteří do
zastupitelstva nikdy nekandidovali. Proto mají teď vlastní skupinu a nadpis,
který o nich mluví pravdivě.

**Když někoho přidáš a on se neobjeví**, chybí mu vazba mimo kandidátku —
mandát (`zastupitel`), funkce v radě, `vedeni` nebo `zamestnanec`.

### Validace

Z kořene repa, před každým commitem datové změny:

```bash
node lide/validate.mjs
```

Exit 0 = čisté, 1 = chyby. Kromě obecné integrity hlídá i pravidla
Peček: 21 zastupitelů, 7 radních, právě jeden starosta, každý zastupitel
má kandidátku, dvě uskupení nemají tutéž barvu, a soubor, na který
ukazuje `url` každé položky `photos`, existuje.

### Historie vedení města

| Období | Starosta/ka | Místostarostové | Zdroj |
|---|---|---|---|
| 1990–2002 | Ing. František Pospíšil | — | kandidátní listina 2026 · Příběhy našich sousedů · Pečecké noviny 12/2019 |
| 2006–2018 | Milan Urban (Sdružení ODS a NK) | — | Kolínský deník 29. 9. 2018 |
| 2014–2018 | Milan Urban | Milan Paluska | Kolínský deník 29. 9. 2018 |
| 2018–2022 | Mgr. Alena Švejnohová | Bc. Iveta Minaříková, Mgr. Blanka Kozáková | Pečecké noviny 12/2018, str. 3 |
| 2022–dosud | Milan Paluska | Zdeněk Fejfar, Ing. Martin Jedlička | usnesení ZM 7/2022 |

**František Pospíšil** byl prvním polistopadovým starostou Peček, rovněž tři
období po sobě (1990, 1994, 1998). Do vedení města nastoupil už 1989 jako
tajemník a poté předseda městského národního výboru — to je ale jen z jednoho
zdroje (životopis Příběhů našich sousedů), proto je ta část jen v `note`, ne
jako samostatná vazba. Samotné starostování 1990–2002 potvrzují tři nezávislé
zdroje, z toho jeden úřední: kandidátní listina 2026 u jeho jména uvádí
„starosta města 1990-2002".

**Mezera 2002–2006 zůstává.** Jaroslav Tvrz je v Pečeckých novinách doložený
jako starosta v roce 2005 a začátkem 2006, ale kdy nastoupil, doložené není —
v adresáři proto zatím není.

Milan Urban byl starostou **tři volební období po sobě (2006, 2010, 2014)**,
dvanáct let. Ve volbách 2018 už nekandidoval a v zastupitelstvu 2018–2022
není; vrátil se až mandátem z voleb 2022. Přesné datum nástupu v roce 2006
se nepodařilo doložit (archiv Pečeckých novin má mezeru mezi dubnem 2006
a prosincem 2007), proto je `from` uložené jen jako rok.

Rada 2014–2018: Ing. Petr Zedník, Martin Homan, Ing. arch. Pavel Švanda
M.Sc. (KDU-ČSL), Šárka Horynová (KDU-ČSL), Zdeněk Fejfar.
Rada 2018–2022: Šárka Horynová, Tomáš Vodička, Jiří Katrnoška,
Jaroslav Železný (+ starostka a obě místostarostky).

**Ještě nedoplněno:** řadoví zastupitelé období 2014–2018 a 2018–2022.
Oba jmenné seznamy jsou doložené (Kolínský deník má u roku 2014 i uskupení
u každého jména; soupis „Naši zastupitelé" v Pečeckých novinách 12/2018 má
sloupce v PDF promíchané, takže přiřazení uskupení k jménům z něj **nelze
brát jako ověřené**). Většina těch lidí už v `people.json` je — jako
kandidáti — takže jde o doplnění vazeb, ne osob.

### Když se ukáže, že dva záznamy jsou jedna osoba

Stává se to hlavně při změně příjmení. Postup (poprvé použit 8. 9. 2026 na
Ivetě Minaříkové → Dvořákové):

1. Ponechat záznam s **dnešním** příjmením, druhý smazat.
2. Do ponechaného doplnit `former_last_names` (dřívější příjmení; jde i do
   fulltextu, takže se člověk najde pod oběma) a `aliases` se **starým `id`**.
3. Vazby zrušeného záznamu přepojit na `person_id` ponechaného a přečíslovat
   jejich `id` podle konvence `{person_id}--{organization_id}--{pořadí}`.
4. Sloučit `sources`, `tags`, případně `photos`; přepsat `bio`, aby popisovalo
   celou dráhu.

Alias je tam proto, že SPEC §3.1 označuje `id` za neměnné — starý odkaz
`#lide/osoba/minarikovai` se nesmí rozbít. Router ho tiše přesměruje na
platné `id` a přepíše URL na kanonickou. Validátor hlídá, že se alias nekryje
s existujícím `id` (to by znamenalo nedotažené sloučení) ani s jiným aliasem.

### Jak přidat osobu

1. **`people.json`** — `id` je příjmení + iniciála křestního bez
   diakritiky (`paluskam`, `svejnohovaa`).
2. **`organizations.json`** — jen pokud uskupení nebo organizace ještě
   chybí. U uskupení povinně `color` a `css_class` **z palety** v
   [`volby/README.md`](../volby/README.md), ne nová barva.
3. **`affiliations.json`** — mandát, případná funkce v radě, kandidátka.
   `id` ve tvaru `{person_id}--{organization_id}--{pořadí}`.
4. Zvýšit `meta.count` a `meta.updated` ve všech změněných souborech.
5. Spustit validátor.

**`id` se po zveřejnění nikdy nemění** — bude na něj odkazovat URL
(`#lide/osoba/paluskam`) i všechny vazby.

### Jak ukončit funkci

Vazbu **nemazat.** Nastavit `to` na datum konce a `current` na `false`.
Právě proto sekce existuje — z ručních kartiček historie mizí, z vazeb ne.
Bc. Iveta Dvořáková a Lenka Třísková jsou v datech přesně z tohohle
důvodu: ve výchozím zobrazení nejsou vidět, po přepnutí rozsahu na
„Včetně historie" se objeví ve třetí skupině se štítkem, do kdy mandát
trval.

### Kdo do adresáře patří

Volení funkcionáři (zastupitelé, rada), jmenované vedení (úřad, městské
organizace), **i řadoví zaměstnanci úřadu** — referentky, účetní, matrikářka
— a od 19. 9. 2026 i **členové komisí rady města a školské rady ZŠ Pečky**
(`role_type: "komise"`, viz „Datová sada" výš). U zaměstnanců se ale vede
**jen to, co radnice sama zveřejňuje jako služební spojení**: jméno, funkce,
pracovní e-mail a telefon. Nic dalšího se k nim nedohledává. Podrobně
a s odůvodněním v SPEC.md §6, bod 4.

Do 8. 9. 2026 platilo pravidlo opačné („ne řadoví zaměstnanci") a změnilo se
na pokyn autora webu při doplňování kontaktů z organizační struktury na
pecky.cz.

Kandidáti bez mandátu jsou v datech, ale panel je nevypisuje — to je jiná věc,
viz „Co panel vypisuje a co ne".

**Organizace bez vazeb na osoby.** Od 20. 9. 2026 jsou v
`organizations.json` i dva spolky — `tj-sokol-pecky` a
`pececky-okraslovaci-spolek` (`type: "spolek"`, identifikace a IČO z Hlídače
státu). Žádné vazby v `affiliations.json` nemají a v adresáři Lidí se
nezobrazují: rejstřík organizací slouží celému webu, ne jen téhle sekci, a
sekce Kalendář se na jejich id odkazuje jako na pořadatele akcí
(`kalendar/akce.json` → `organizer`, viz `kalendar/README.md`). Vazby na
konkrétní lidi se k nim doplní, až pro ně bude doložený zdroj.

### Povolání

`occupations` je pole seřazené od nejnovějšího ročníku, každá položka nese
`year`, `value` a `source`. Text si **vyplňuje kandidát sám** ve volebních
podkladech — není ověřený a mezi volbami se mění (Paluska 2022 „podnikatel",
2026 „starosta města"). Detail proto vypisuje všechny ročníky s rokem.
Podrobnosti v SPEC.md §3.6c.

Pokrytí: 111 osob, z toho 15 má oba ročníky. Zdroje — `volby/2026/data-export.csv`
(105 kandidátů 2026) a Poradna pro obce (21 zvolených 2022).

### Fotky a jejich původ

`photos` je pole, ne jedna hodnota — jeden člověk může kandidovat víckrát
a fotka na kandidátce se mezi lety mění (viz SPEC.md §3.7). Každá položka:
`year` (ročník kandidátky nebo volební období), `url` (cesta od kořene
repa — `volby/{rok}/zastupitele/…` u fotek z voleb, `lide/foto/…`
u ostatních), `photo_source` (původ — kandidátka ods.cz, inzerát
v Pečeckých novinách, web města…). Karta osoby ukazuje vždy nejnovější
(`photos[0]`, pole je řazené sestupně), detail osoby všechny. Kdo fotku
nemá, má `photos: []` a v UI dostane iniciálový avatar na barvě
uskupení — viz kapitola „Fotky" výš.

Při nálezu nové fotky za další ročník se **stará položka neodstraňuje**,
jen přibude nová — stejně jako u vazeb historie nemizí.

### České skloňování osob (gender)

Doplněno 19. 9. 2026, zadal uživatel — vzniklo z textu „Přítomen: N"
v poznámce `jednani/absence.html` (mužský tvar u žen gramaticky špatně,
např. „Ivana Trčková … Přítomen" místo „Přítomna"). Řešení je obecné pro
celý web: kdekoli se generuje text o konkrétní osobě z přídavného jména/
příčestí (přítomen/přítomna, zvolen/zvolena, jmenován/jmenována…),
používá stejný mechanismus.

`people.json` nese u každé osoby povinné pole `gender` (`"m"` / `"f"`,
SPEC.md §3.2). U všech 258 záznamů odvozeno ze **jména** (ne příjmení —
česká křestní jména jsou téměř bezvýhradně rodově jednoznačná, na rozdíl
od příjmení, kde selhávají cizí/nesklonná tvary jako „Middleditch" nebo
„Vaz Santos"): 105 unikátních jmen ručně roztříděno a zkřížově ověřeno
proti příponě příjmení (`-ová`/`-á`) — 5 shod nesedělo kvůli právě
takovým nesklonným příjmením, ne kvůli špatně určenému rodu. `validate.mjs`
kontroluje, že `gender` je u každé osoby `"m"` nebo `"f"`.

Vykreslení: `pcGendered(p, masc, fem)` v `assets/helpers.js` — vrátí `fem`
jen když `p.gender === 'f'`, jinak `masc` (i když `p` chybí, tedy osobu
se nepodařilo spárovat — bezpečný výchozí mužský tvar). Použití v
`jednani/absence.html` → `poznamkaHtml(r, p)`: `pcGendered(p, 'Přítomen',
'Přítomna')`. Při dalším místě na webu, kde bude potřeba skloňovat text
o konkrétní osobě, použít stejnou funkci, ne psát tvary napevno.

### Přiznané mezery v datech

- **Kontakty má 33 z 243 osob** (21 zastupitelů, 6 vedení úřadu, 6 vedení
  městských organizací). Zdroje: [Zastupitelstvo
  města](https://pecky.as4u.cz/cs/mesto/zastupitelstvo-mesta/) (e-maily
  všech 21, tvar `jmeno.prijmeni@pecky.cz` bez diakritiky),
  [Telefonní seznam](https://pecky.as4u.cz/cs/mestsky-urad/telefonni-seznam-5.html)
  a stránky odborů. Telefon má jen ten, komu web uvádí **vlastní linku** —
  ústředna `+420 321 785 051` se jako osobní kontakt nezapisuje, fax taky ne.
  Kdo má kancelář i služební mobil, má obě čísla v jednom poli oddělená
  `" · "` (SPEC.md §3.6b); v detailu osoby z každého vede odkaz `tel:`.
  Kandidáti bez funkce kontakt nemají a mít nebudou: nejsou veřejní
  funkcionáři a město jejich spojení nezveřejňuje.
- **Čtyři lidé z ekonomicko-správního odboru sdílejí linku `+420 721 183 560`
  a tři z investic `+420 606 753 278`** — je to číslo odboru, ne osobní.
  Zapsané je (lepší než nic), ale každá taková vazba to má v `note`.
- **Při rozporu mezi zdroji platí pecky.cz, ne pecky.as4u.cz.** Starý web se
  od jara 2026 neaktualizuje. Konkrétně: Jiří Moravec má na pecky.cz
  `+420 724 125 367`, na as4u.cz `+420 724 885 367` — platí to první.
  „Nina Husová" je na as4u.cz vedená jako „Nina Vlčková"; vypadá to na změnu
  příjmení, ale doložené to není, takže je v datech jen pod aktuálním jménem.
- ~~Uskupení Bc. Ivety Dvořákové a Lenky Třískové je dopočítané~~ —
  uzavřeno 8. 9. 2026. Výsledky voleb 2022 na Poradně pro obce uvádějí
  kandidátku přímo u jména, obě vazby jsou teď doložené.
- **Výbory jsou zatím jen dva záznamy** (předsednictví kontrolního
  výboru). Zbytek členů finančního a kontrolního výboru je v archivu
  jednání pod `UZ-98`…`UZ-111` — doplnit ve fázi 5b.
- **Komise RM a školská rada nemají doložené datum jmenování** — pecky.cz
  u nich ukazuje jen aktuální složení, ne kdy ho rada schválila. Vazby
  mají `from: null` a `verified` na datum, kdy bylo složení ověřené na
  webu (19. 9. 2026), ne na datum vzniku funkce. Přesné datum by šlo
  dohledat v usneseních RM, zatím nedohledáno.
- **Z ustavujícího zasedání po volbách 2018 je v datech jen vedení**
  (starostka, obě místostarostky a rada), ne všech 21 zastupitelů.
  Zasedání je starší než archiv usneseni.cz (začíná dubnem 2021), viz
  [`volby/2018/README.md`](../volby/2018/README.md), takže zdrojem jsou
  Pečecké noviny 12/2018 — a **poměry hlasů při volbě starostky se
  dohledat nedaří**. Jmenný soupis „Naši zastupitelé" v témž článku má
  v PDF promíchané sloupce, takže přiřazení uskupení k jménům z něj nelze
  brát jako ověřené; proto zatím nedoplněno.
- **Kandidatury mají v datech `current: true` a `to: null`**, přestože jde
  o jednorázovou událost. Panel to obchází zobrazením — `lActive()` je za
  aktivní nepovažuje a v timeline je vypisuje jako „volby 5. 10. 2018",
  jinak by dávno skončená kandidatura přebila skutečné funkce. Správně by
  to měla řešit data; změna se dotkne přes 350 vazeb, proto zatím čeká.
- **206 kandidátů (fáze 5a, SPEC.md §3.6) má zatím jen minimální
  záznam** — jméno, příjmení, vazba na kandidátku. Bez `bio`, fotky,
  kontaktů a `sources` na osobě (zdroj je jen na vazbě). Doplnění je
  fáze 5b, postupně a jen tam, kde se najde veřejný zdroj.
- **Fotky za 2026 ověřeny 31. 8. 2026, dohledatelné jen u 2 z 5
  uskupení.** ODS a nezávislí kandidáti (ods.cz) a NAŠE PEČKY A PEČKY
  NEXT (nasepecky.cz) si pro tyhle volby udělaly vlastní web s portréty
  kandidátů — viz §3.7 SPEC.md. Sdružení nezávislých kandidátů PEČKY
  PEČÁKŮM, Lidé pro Pečky a Velké Chvalovice s podporou SPD a Pečky
  srdcem mají jen Facebook (stránku/skupinu) — bez přihlášení jde
  projít jen omezeně a fotky v příspěvcích nejsou jmenovitě popsané,
  takže je nejde spolehlivě spárovat s konkrétním kandidátem. Nejde
  o nedostatek hledání, ale o to, že takový zdroj u těchhle uskupení
  reálně neexistuje — needit to zkoušet znovu, dokud web/inzerce
  nevznikne.

Textový obsah panelu jinak žije v `content/lide.html`. Další zvláštní
pravidla doplnit sem, až nějaká vzniknou.
