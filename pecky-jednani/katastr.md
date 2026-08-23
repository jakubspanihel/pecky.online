# Katastr nemovitostí — zadání pro API dotazy

Pracovní dokument pro přípravu zadání na dotazy do API katastru
nemovitostí (ČÚZK). Zatím prázdné — obsah doplníme průběžně.

## Zadání

Většinou budeme pracovat s těmito katastrálními územími (okres Kolín):

- Pečky — kód 718823
- Velké Chvalovice — kód 778842

**Cíl:** k zadanému číslu parcely (text ve stylu „č. parc. 1680" nebo
„č. parc. 1467/1") získat URL odkaz na detail parcely na Nahlížení do
KN / VDP, např. `https://vdp.cuzk.gov.cz/vdp/ruian/parcely/1603936204`
— a pokud to API umožní, i informaci o vlastníkovi. Typický kontext
použití: nákup, prodej nebo pronájem pozemku (např. k usnesení
zastupitelstva/rady).

**⚠️ Vlastník — mezera (prověřeno, řešení není automatizovatelné):**
API `Parcely` vrací jen odkaz na LV (`lv.cislo` — číslo listu
vlastnictví), ne jméno vlastníka ani podíly — schéma `Parcela` žádné
pole pro vlastníka/osobu neobsahuje (`Podil` je ve specifikaci
definovaný, ale používá se jen u `Jednotka`, ne u `Parcela`). To není
chyba, ale záměr — bezplatné REST API (api-kn.cuzk.gov.cz) osobní údaje
o vlastníkovi neposkytuje vůbec.

Možnosti, jak jméno vlastníka přesto zjistit — žádná není vhodná pro
automatizaci v rámci tohoto projektu:
1. **Nahlížení do KN** (nahlizenidokn.cuzk.gov.cz) — od 30. 12. 2025
   zobrazuje údaje o vlastníkovi jen po přihlášení (Identita občana).
   I po přihlášení podmínky užití výslovně zakazují automatizované
   vytěžování dat — jen interaktivní použití člověkem. Nescrapovat.
2. **Dálkový přístup (DP/WSDP)** — oficiální placená služba s
   registrovaným účtem, umožňuje mj. vyhledání dle vlastníka; platba
   za každý výstup. Vhodné jen při opakovaném/objemnějším využití.
3. **Dálkový přístup pro neregistrované** (dpn.cuzk.gov.cz) — nákup
   jednotlivého úředního výpisu z KN (vč. vlastníka) bez registrace,
   ale s ověřením přes Identitu občana u některých listin; každý
   výpis je jednotlivý platební nákup — nelze automatizovat (platby
   dělá vždy Jakub sám).
4. Neoficiální weby (např. ikatastr.cz) zobrazují jméno vlastníka
   zdarma při kliknutí do mapy — nejde o oficiální zdroj ČÚZK,
   nepoužívat jako "ověřeno" na transparentním webu.

**Praktický závěr pro projekt:** jméno vlastníka parcely necháme jako
manuální krok mimo automatizaci — pokud bude u konkrétního
usnesení/smlouvy potřeba, Jakub ho dohledá sám (přihlášením do
Nahlížení do KN nebo koupí výpisu) a dodá text/screenshot k ověření.

**⚠️ VDP URL — k ověření:** `Parcela.id` (,,Unikátní identifikátor
objektu v ISKN") pravděpodobně odpovídá ID v URL
`vdp.cuzk.gov.cz/vdp/ruian/parcely/{id}`, ale nebylo zatím ověřeno
reálným voláním s klíčem — ověřit až budeme mít první test.

## Poznámky k API

- API klíč je uložený lokálně v `.katastr-api-key` (v .gitignore, nikdy
  nejde do gitu) — před použitím ho odtud načíst, needit znovu žádat.
- Zdroj: REST API dálkového přístupu k datům KN (ČÚZK)
  - Popis: <https://api-kn.cuzk.gov.cz/Popis>
  - Swagger (OpenAPI 3.0, podrobná specifikace): <https://api-kn.cuzk.gov.cz/swagger/index.html>
    (JSON: `https://api-kn.cuzk.gov.cz/swagger/v1.0/swagger.json`)
- Metoda: pouze HTTP GET. Autentizace: `ApiKey` v HTTP hlavičce každého
  požadavku (viz `.katastr-api-key`).
- Struktura odpovědi (mimo `/AplikacniSluzby`): objekt s daty + seznam
  zpráv (např. "nenalezeno") + provozní info (aktuálnost dat, počet
  volání za období).
- Objekty typu `*Def` (např. `ParcelaDef`) jsou jen základní definice —
  pro úplná data nutné zavolat konkrétní endpoint s ID objektu.
- Endpointy s ID objektu vrací 404, když nenajdou; vyhledávací
  endpointy (`/Vyhledani`) vrací 200 s prázdným seznamem. Každé volání
  (i nenalezené) se počítá do limitu — stav účtu přes
  `/AplikacniSluzby/StavUctu`.

### Dostupné okruhy endpointů

- `AplikacniSluzby` — obslužné: číselník zpráv, aktuálnost dat,
  provozní info, stav účtu (limit volání), health
- `CiselnikyISKN` — číselníky ISKN (druhy pozemků, způsoby určení
  výměry, typy jednotek/staveb, způsoby využití, způsoby ochrany,
  pracoviště resortu)
- `CiselnikyUzemnichJednotek` — obce, části obcí, katastrální území,
  okresy, kraje (vyhledání podle kódu i seznamy)
- `Jednotky` — vyhledání jednotky (bytu) podle ID ISKN nebo přirozené
  identifikace
- `Parcely` — vyhledání parcely podle ID, sousední parcely, vyhledání
  podle přirozené identifikace nebo podle polygonu (definiční body)
- `PravaStavby` — právo stavby podle ID, podle parcely, podle stavby
- `Rizeni` — řízení podle ID, vyhledání podle identifikace, seznam
  přijatých řízení za den
- `Stavby` — vyhledání stavby podle ID, přirozené identifikace, kódu
  adresního místa, nebo podle polygonu

### Vyhledání parcely podle čísla (`GET /api/v1/Parcely/Vyhledani`)

Relevantní endpoint pro naše zadání (parsování textu typu „č. parc.
1467/1"). Povinné query parametry:

| parametr | hodnota u nás |
|---|---|
| `KodKatastralnihoUzemi` | 718823 (Pečky) nebo 778842 (Vel. Chvalovice) |
| `TypParcely` | `PKN` (parcela KN — běžný případ) nebo `PZE` (zjednodušená evidence) |
| `DruhCislovaniParcely` | `2` = pozemková parcela (běžné „č. parc. …"), `1` = stavební parcela (číslo s prefixem „st.") |
| `KmenoveCisloParcely` | část čísla před lomítkem, např. u „1467/1" → `1467`, u „1680" → `1680` |
| `PoddeleniCislaParcely` | část za lomítkem, např. u „1467/1" → `1` (nepovinné, u „1680" se vynechá) |

Vrací `ParcelaListVysledekZpracovani`: pole `data` (seznam `Parcela`),
`zpravy` (seznam zpráv/chyb), `aktualnostDatK`, `provedenoVolani`.
Nenalezeno → HTTP 200 s prázdným `data`.

Schéma `Parcela` obsahuje mj. `id` (unikátní ISKN identifikátor),
`vymera`, `druhPozemku`, `zpusobVyuziti`, `katastralniUzemi`, `lv`
(`LVDef`: jen `id` + `cislo` LV, bez vlastníka).

### Hromadné doplnění URL — celý katastr-parcely-v-usneseních.md (22. 8. 2026)

Doplněn nový sloupec „URL na detail parcely (VDP)" pro všech 285
řádků (172 unikátních čísel parcel). Výsledek: **169/172 (98 %)
dohledáno**, ověřeno spotovou kontrolou 4 náhodných výsledků přímo na
vdp.cuzk.gov.cz (2007/2, 172/4, 164/Dobřichov, 360/1/Radim u Kolína —
všechny sedí přesně). Spotřeba: 409/500 volání dne 22. 8. 2026.

**Postup (finální, opravený oproti pilotu):**
1. Pro každé unikátní číslo parcely zkusit **všechny 4 kombinace**
   `TypParcely` (PKN/PZE) × `DruhCislovaniParcely` (1/2) — pilotní test
   zkoušel jen PKN+pozemková, což vedlo k falešné shodě (viz níže).
2. Pokud existuje jasný kontext v textu usnesení (`text_verbatim` z
   `pecky-jednani.json`) pro jiné k.ú. než Pečky/Velké Chvalovice,
   hledat **jen v tom k.ú.** — nekaskádovat automaticky přes další
   obce jen proto, že v Pečkách/V.Ch. nic nebylo. Necílená kaskáda přes
   více k.ú. dala falešnou shodu (parcela 531, viz níže).
3. Bez explicitního kontextu: zkusit Pečky, pak Velké Chvalovice; když
   ani jedno nevrátí žádnou ze 4 kombinací, nechat jako mezeru
   (nehádat další obce naslepo).
4. Kódy k.ú. mimo Pečky/V.Ch. použité v tomto běhu (z celého číselníku
   13 453 k.ú., staženého jednou a prohledávaného offline):
   - Dobřichov — 627801 (parcely 164, 500, 213/12)
   - Tatce — 765171 (462/57)
   - Blinka — 721361 (327)
   - Plaňany — 721387 (527/3)
   - Radim u Kolína — 737780 (183/22, 360/1, 388/140)
   - Čáslav — 618349 (v tomto běhu nakonec nepoužito — parcely
     „od Státního statku Čáslav" v UR-93-7/21/UZ-9-1/21 byly nalezeny
     rovnou v Pečkách)

**Chyby odhalené a opravené během běhu — poučení pro příště:**
- **531** (UZ-9-1/23, text explicitně „v obci a k.ú. Pečky") se
  jednoduchým hledáním (jen PKN/pozemková) v Pečkách nenašel, ale
  naivní kaskáda přes další obce ho „našla" v Tatcích — **falešná
  shoda** (jiná reálná parcela náhodou se stejným číslem). Po opravě
  (4 kombinace, žádná kaskáda bez kontextu) zůstává 531 jako opravdová
  mezera — v Pečkách ani Velkých Chvalovicích v žádné kombinaci
  neexistuje (pravděpodobně přečíslována/sloučena pozemkovou úpravou
  po roce 2023).
- **254** a **347** byly mylně zařazeny do „jiné k.ú." podle doslovné
  četby textu („v obci Pečky a k.ú. Velké Chvalovice"), ale API je
  najde jen v Pečkách (PKN/pozemková) — text usnesení je zavádějící
  (nebo chybný), API je zde autoritativní zdroj. **347** navíc není
  ani skutečným předmětem usnesení UR-354-38/22 — objevuje se jen v
  názvu smlouvy („…kNN č. parc. 347"), skutečná dotčená parcela je
  348/3 (Velké Chvalovice).
- **1595** (UR-3-1/21) — potvrzeno z pilotu: chyba extrakce, jde ve
  skutečnosti o 1622/1 (viz `text_verbatim`, číslo 1595 je jen v
  názvu bodu programu, ne v těle usnesení).

**Zbývající mezery (2 unikátní čísla, nedohledáno v žádné kombinaci
Pečky/Velké Chvalovice):**
- **531** (UZ-9-1/23) — viz výše.
- **2169/13** (UR-186-20/25, UR-230-25/25, UR-259-28/25, UR-256-27/26)
  — text vždy explicitně „v obci a k.ú. Pečky", zahrádkářská kolonie u
  ČOV, 190 m². Možná nedávno vzniklá parcela ještě mimo aktuální data
  API, nebo překlep za 2169/1 (ta existuje a je hojně užívaná jinde v
  dokumentu) — nelze rozhodnout bez dalšího zdroje, ponecháno jako
  mezera, needit hádat.

### Prolinkování na webu — celý korpus, ne jen souhrnná tabulka (22. 8. 2026)

Na žádost doplněno hypertextové prolinkování zmínek „č. parc. …" přímo
v zobrazených záznamech jednání (`index.html` i
`pecky-jednani/index.html`), ne jen v pomocné tabulce
`katastr-parcely-v-usneseních.md`. Mapování číslo→URL je uložené v
`pecky-jednani/katastr-odkazy.json` (klíč `parcely`), frontend ho
načítá při startu a prolinkuje regexem `parc\.?\s*(\d{1,5}(?:\/\d{1,3})?)`
v textu usnesení, bodu programu i výsledků hledání — funkce
`jLinkParcely`/`jLinkedText`/`jHighlightLinked` v obou HTML souborech.

Kontrola úplnosti ukázala, že `katastr-parcely-v-usneseních.md` (a
tedy i moje předchozí dohledávání jen z něj) **nepokrývala celý
korpus** — v `pecky-jednani.json` je 217 unikátních zmínek „parc. N",
tabulka jich měla jen 172. Chybějících 45 (typicky sourozenecká čísla
ve výčtech, např. 172/2, 172/3, 172/6 vedle už známého 172/4) jsem
dohledal stejnou metodou (k.ú. odhadnuté ze sourozeneckého čísla se
stejným kmenovým číslem, 4 kombinace typ/druh, bez slepé kaskády).
Výsledek: **212/217 (98 %) pokryto**, zbylých 5 jsou zdokumentované
mezery: 1595 (chyba extrakce, viz výše), 531, 2169/13, a nově
**497/40** a **554/70** (sourozenci již vyřešených 497/2 a 554/1,36,68
— v Pečkách ani Velkých Chvalovicích nenalezeny v žádné kombinaci).

Spotřeba API za 22. 8. 2026 celkem: 470/500 volání.

**Neúplné řádky (parcely uvedené jen částečně, „+N" ve zdroji):**
UR-93-7/21 / UZ-9-1/21 (Státní statek Čáslav, +24 parcel) a UR-219-21/21
(+1 parcela) mají v `katastr-parcely-v-usneseních.md` jen částečný
výčet — doplněny URL jen pro uvedené parcely, zbytek needit
vymýšlet. Podobně UR-293-33/25 má v tabulce zkrácený výčet (jen
„832/35, 360/1") oproti plnému textu usnesení (7+2 parcel) — týká se
zřejmě více řádků v dokumentu, oprava zdrojové tabulky je samostatný
úkol, ne součást tohoto doplnění URL.

Duplicitní záznamy RM+ZM (stejná parcela schválená radou i
zastupitelstvem) logicky vedou ke stejné URL.

### Postup, když se parcela nenajde v Pečkách ani Velkých Chvalovicích

1. Nejdřív ověřit v `pecky-jednani.json` / `archive-2026-08-04.json`
   (`text_verbatim` usnesení) skutečné číslo parcely a k.ú. — název
   bodu programu (`agenda_item_raw`) se občas s tělem usnesení
   neshoduje (viz případ 1595/1622/1 výše).
2. Pro číslo, které v textu sedí, zkusit v cílovém k.ú. všechny 4
   kombinace `TypParcely`×`DruhCislovaniParcely` (ne jen PKN/pozemková
   — viz případ 531 výše).
3. Kód k.ú. podle názvu: `GET /api/v1/CiselnikyUzemnichJednotek/KatastralniUzemi`
   vrací **celý seznam** (13 453 k.ú. v ČR, bez filtru/parametrů) —
   stáhnout jednou, uložit lokálně a dál jen prohledávat offline podle
   názvu.
4. Bez jasného kontextu pro jiné k.ú. nekaskádovat naslepo přes další
   obce — riziko falešné shody (viz 531). Raději nechat jako mezeru a
   označit k dohledání.
