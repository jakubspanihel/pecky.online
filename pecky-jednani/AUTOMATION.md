# AUTOMATION.md — rozšíření na automatizovaný/inkrementální export

Spec pro budoucí automatizaci jednorázového exportu (viz SPEC.md, volba
„Jednorázový full export s MD specifikací"). Nic z tohoto zatím není
implementováno; scraper je na to ale připraven.

## Detekce nových jednání

1. Stáhnout **jen 1. stránku výpisu** (`/verejne/`) — nová jednání přibývají
   nahoře. Porovnat UUID proti `work/meetings-index.json`.
2. Nová UUID ⇒ `fetch --uuids <nové>` + `parse` + `assemble` (vznikne nový
   datovaný snímek vedle starých).
3. Jednou za čas (např. měsíčně) projít celý výpis pro jistotu — položky se
   teoreticky mohou měnit zpětně (opravy zápisů). Změnu obsahu odhalí diff
   raw HTML ve `work/` (bytes v `fetch-log.jsonl`).

**Pozor:** stránkování se posouvá s každým novým jednáním — `?page=N` není
stabilní adresa; jediný stabilní klíč je UUID jednání a `detail_id` usnesení.

## Stabilní klíče a relace

- Jednání: UUID (v URL všech dokumentů).
- Usnesení: `detail_id` (numerické, z popup URL `/verejne/usneseni/<id>`)
  + `number_raw` (např. `UR-254-27/26`; formát ročníku kolísá: `…/26` i `…/2026`).
- **Detail endpoint je globální pro celou platformu** (vrací i usnesení jiných
  měst, tenant se nekontroluje) — při každém stažení detailu ověřit shodu
  čísla usnesení s očekávaným (implementováno jako `detail_number_mismatch`).
- Filtr orgánů: `GET /verejne/?type=<zastupitelstvo|rada|financni-vybor|kontrolni-vybor>`
  (ověřeno; výbory k 2026-08-04 prázdné — nová jednání výborů by se objevila
  v hlavním výpisu, ale filtr je vhodná kontrola úplnosti).

## Ověřené parametry běhu (2026-08-04)

- Tempo 3–8 s (dokumenty) / 2–5 s (detaily přes in-page `fetch()`) prošlo
  celý den **bez jediného Cloudflare challenge**: 19 stránek výpisu + 843
  dokumentů + 2 731 detailů.
- Reálné časy: discover ~3 min, fetch 281 jednání ~1,5 h, fetch-details
  2 731 stránek ~2,5 h; parse+assemble offline ~2 min.
- Pozvánky: web je generuje jen pro jednání od ~06/2026; starší vrací flash
  „Neočekávaná chyba" → trvalý `site_error`, nemá smysl opakovat.

## Změny oproti jednorázovému běhu

- `discover` umí přírůstkový režim: zastavit se na první stránce, kde jsou
  všechna UUID známá (nyní prochází vždy vše).
- `assemble` generuje vždy nový snímek `archive-YYYY-MM-DD.json` — diff dvou
  snímků = změnová zpráva. Doporučený nástroj: `jq` + `diff`, nebo porovnat
  `resolutions[].detail_id` množiny.
- Plánování: launchd/cron na Macu; běh vyžaduje GUI session (viditelné Chrome
  kvůli Cloudflare) — bezhlavý server NEBUDE fungovat bez vyřešení CF
  (např. placený scraping proxy, nebo dohoda s provozovatelem).

## Odkazy na parcely (katastr) — aktualizovat při každém běhu

**Historie (přečíst, než se sáhne na cokoli s "katastr" v názvu):**
Do 23. 8. 2026 web prolinkovával zmínky o parcelách přes
`pecky-jednani/katastr-odkazy.json` — globální mapu „číslo parcely →
URL" bez rozlišení katastrálního území, dohledanou přes REST API ČÚZK
(api-kn.cuzk.gov.cz, klíč `.katastr-api-key`), postup popsaný v
`katastr.md`. **Soubor byl smazán**, protože obsahoval prokázanou
chybu: číslo parcely je unikátní jen v rámci jednoho katastru, ale
mapa měla pro každé číslo jen jednu hodnotu. Potvrzený případ: parcela
„254" existuje jak v k.ú. Pečky (362 m², ID 1602232204 — to byla ta
uložená hodnota), tak jako 254/1 a 254/2 v k.ú. Velké Chvalovice (483
a 36 m²) — usnesení UZ-46-4/25/UR-274-30/25/UR-195-21/25 (prodej cca
36 m² ve Velkých Chvalovicích) se tak prolinkovalo na ŠPATNOU (Pečky)
parcelu. `katastr.md` a `katastr-parcely-v-usneseních.md` popisují tenhle
starý, opuštěný postup — ponechány jen jako historická poznámka,
needit se jimi řídit ani do nich nic doplňovat.

**Současný stav:** vše (tabulky Pozemky i obecné prolinkování „parc.
NNNN" v Jednání) generuje jediný skript,
`pecky-jednani/scripts/update-pozemky.py` — viz sekce „Tabulky
Nákup/Prodej na stránce Pozemky" níže pro plný popis. Skript sám
dohledává katastr z kontextu KAŽDÉHO výskytu čísla zvlášť (ne jen
jednou globálně) a čísla, u kterých se katastr napříč výskyty
neshoduje (kolize) nebo se nepodaří určit vůbec, **záměrně vynechá** —
frontend (`jLinkParcely()` v `index.html` i `pecky-jednani/index.html`)
pak takové číslo prostě nepodlinkuje, což je bezpečné chování (žádný
ruční krok navíc není potřeba, nová/změněná jednání se promítnou příštím
spuštěním skriptu).

Výstupy skriptu pro tuhle část:
- `pecky-jednani/parcely-pozemky.json` — katastr-přesná cache
  „katastr|číslo" → RUIAN ID, zdroj pravdy pro obojí níže.
- `pecky-jednani/parcely-odkazy.json` — plochá mapa „číslo" → URL,
  načítá ji frontend pro obecné prolinkování v Jednání (nahrazuje
  smazaný `katastr-odkazy.json`).

## Tabulky Nákup/Prodej na stránce Pozemky — aktualizovat spolu s Jednáním

Panel „Pozemky" v kořenovém `index.html` (subpanely `subpanel-pozemky-nakup`
a `subpanel-pozemky-prodej`) je statický výřez sestavený z usnesení
o prodeji/nákupu pozemku, ne živě dotahovaná data — analogicky k sekci
Smlouvy. **Při každé aktualizaci `pecky-jednani.json` je proto potřeba
spustit i:**

```
python3 pecky-jednani/scripts/update-pozemky.py
```

Skript (spouštět z kořene repa) v jednom běhu:
1. Najde v `pecky-jednani.json` nová/změněná usnesení o prodeji/nákupu
   pozemku (stejná klíčová slova a metodika jako u ruční tabulky
   z 23. 8. 2026 — párování rada→zastupitelstvo, extrakce ceny).
2. Pro nová čísla parcel dohledá RUIAN ID přes vdp.cuzk.gov.cz **vždy
   s konkrétním katastrálním územím** (řádek v tabulce Pozemky katastr
   už zná), takže nemá riziko křížové kolize jako starý globální
   `katastr-odkazy.json`. Cache žije v `parcely-pozemky.json`
   (klíč `"katastr|číslo"`).
3. Přegeneruje obě HTML tabulky a nahradí jimi obsah zmíněných subpanelů
   přímo v `index.html`, ověří balanci HTML tagů.
4. Projde **úplně všechna** usnesení a body programu (ne jen ty
   o pozemcích), pro každou zmínku „parc. NNNN" zjistí katastr z jejího
   vlastního kontextu, sesbírá katastry napříč všemi výskyty daného
   čísla a dohledá/zapíše do `parcely-odkazy.json` jen čísla, kde se
   katastr shoduje; kolidující nebo neurčitelná čísla vynechá (nahlásí
   na stderr, viz sekce výše).

Katastrální území mimo pevný seznam v `KAT_CODES` (aktuálně Pečky,
Velké Chvalovice, Dobřichov, Plaňany, Blinka, Tatce, Radim u Kolína)
je třeba do skriptu doplnit ručně (kód přes vyhledání na
vdp.cuzk.gov.cz/vdp/ruian/parcely — pozor na víceznačné názvy, viz
příklad „Radim" vs „Radim u Kolína" — komentář přímo u `KAT_CODES`
ve skriptu). Číslo, které se nepodaří dohledat automaticky (rozdělená/
sloučená parcela apod.), skript nahlásí a je třeba jej doplnit do
`MANUAL_OVERRIDES` ve skriptu s odůvodněním (výměra/kontext z textu
usnesení).

## Rizika

1. **Cloudflare** — hlavní riziko. Challenge může kdykoli zpřísnit; mitigace:
   persistentní profil, lidské tempo, ruční odklik. Pro plnou automatizaci
   zvážit oficiální cestu: usneseni.cz je komerční systém, město může mít
   export, nebo lze požádat o API.
2. **Změna šablony webu** — parsery jsou striktní; změna struktury skončí
   anomáliemi v reportu, ne tichým poškozením dat. Fixtures v `tests/fixtures/`
   umožní rychlou opravu.
3. **Zpětné úpravy dokumentů** — zápisy lze teoreticky opravit po zveřejnění;
   snímky s časovým razítkem tuto historii zachovají, jen pokud se běh spouští
   pravidelně.
