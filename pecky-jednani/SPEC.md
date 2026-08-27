# SPEC: Lokální JSON archiv jednání města Pečky

> Zdroj: https://mesto-pecky.usneseni.cz/verejne/
> Zadání: „Lokální JSON timestamp všech dostupných jednání (pozvánky, zápisy, hlasování a jednotlivá usnesení). Hlavním cílem je mít lokálně dostupné všechny informace pro další strojovou analýzu. Zachovávej relace mezi jednáními, hlasováními a usneseními. Hlavní priorita je nekompromisní přesnost.“
> Datum interview: 2026-08-04

## Problem Statement

Veřejná data o jednáních orgánů města Pečky (zastupitelstvo, rada, výbory) existují jen na webu usneseni.cz za Cloudflare bot-protection, po stránkách, bez strojově čitelného exportu. Cílem je jednorázový, auditovatelný export **všeho dostupného obsahu** do jednoho datovaného JSON snímku, se zachovanými relacemi jednání ↔ usnesení ↔ hlasování, jako podklad pro libovolnou budoucí strojovou analýzu (fulltext, hlasování, sledování témat — účel zatím neurčen, proto maximální granularita).

**Kritérium úspěchu:** JSON obsahuje 100 % jednání viditelných na webu, každé s kompletně zparsovaným obsahem všech dostupných dokumentů, texty verbatim, žádná tichá vynechávka; závěrečný report křížových kontrol bez nevysvětlených anomálií.

## Zjištěná fakta o zdroji (průzkum 2026-08-04)

- Výpis: ~19 stránek (`/verejne/?page=N`), řádově **~280 jednání**; filtr typů: Zastupitelstvo, Rada, Finanční výbor, Kontrolní výbor.
- Jednání identifikováno UUID. Odkazy per jednání:
  - Pozvánka: `/verejne/?uuid=<UUID>&do=printPublicInvitation` (HTML print view)
  - Zápis: `/verejne/<UUID>/zapis/` (HTML)
  - Podepsaný zápis: `?meetingReportControl-uuid=<UUID>&do=meetingReportControl-getSignedReportPdf` (PDF)
  - Přijatá usnesení: `/verejne/<UUID>/usneseni/` (HTML)
  - Zvukový záznam: jen u některých zasedání zastupitelstva
- **Cloudflare:** curl dostává 403 challenge; automatizovaný Chrome prošel na první load, ale po několika rychlých navigacích dostal neřešitelný challenge-loop. ⇒ pomalé lidské tempo + možnost ručního odkliknutí je nutnost.
- Přesná struktura stránek zápisu/usnesení (a forma hlasování) zatím neověřena — CF zablokoval hlubší průzkum. Schéma se finalizuje po prvním úspěšném stažení vzorku.

## Requirements

### Must
- Všechny 4 orgány, všechna jednání z výpisu (bez filtru, všechny stránky).
- Per jednání zparsovat: metadata z výpisu (typ, číslo `N/RRRR`, datum), pozvánku (program verbatim), zápis (plný text), jednotlivá usnesení (číslo, plný text verbatim, výsledek hlasování v maximální granularitě, jakou web uvádí — jmenovitě, pokud jmenovitě zobrazuje).
- Relace: usnesení a hlasování nesou UUID jednání; vše v jednom souboru propojené přes UUID.
- Binárka (podepsaný PDF zápis, audio) **nestahovat** — uložit jen absolutní URL.
- Výstup: **jeden JSON snímek** `archive-YYYY-MM-DD.json`; uvnitř čas exportu a `fetched_at` u každé stažené stránky.
- **Verbatim zásada:** žádné čištění/normalizace textů; normalizovaná pole (ISO datum, číslo jednání) vždy *vedle* originálu, nikdy místo něj.
- Chybějící/nestáhnutelný dokument ⇒ explicitní status (`missing_on_site` / `fetch_failed` + důvod), běh pokračuje, anomálie v závěrečném reportu. Nikdy tiché vynechání.
- Checkpoint + resume: průběžné ukládání do work-dir, po přerušení běh pokračuje, finální JSON se složí až z kompletních dat.
- Křížové kontroly úplnosti (viz Verification Plan) jako součást běhu.

### Should
- Work-dir se surovým HTML každé stažené stránky ponechat po běhu jako auditní ground truth (deliverable je ale jen JSON — dle volby uživatele).
- `AUTOMATION.md`: spec pro budoucí rozšíření na automatizovaný/inkrementální export (jak detekovat nová jednání, co je stabilní klíč, kde jsou rizika). *(pozn. 27. 8. 2026: soubor zrušen — stroj, pro který popisoval provoz, už není dostupný; zbylá fakta přesunuta do [automation-kontrola-usneseni-cz.md](automation-kontrola-usneseni-cz.md) a [automation-katastr-parcely.md](automation-katastr-parcely.md).)*
- README/AGENTS.md s dokumentací zdroje a struktury dat (dle globálních pravidel pro data extraction).
- Strukturované JSON logy běhu do `logs/`.

### Could
- Testy parserů na uložených HTML fixtures.
- Porovnávací report vzorku jednání (web vs. JSON) pro ruční kontrolu.

### Won't (vědomé neřešení)
- Stahování PDF a audia (jen URL) — úspora místa, HTML obsah je pro strojovou analýzu primární.
- Inkrementální aktualizace — jen popsaná v AUTOMATION.md *(zrušen 27. 8. 2026, viz poznámka výše — inkrementální doplňování teď řeší [automation-kontrola-usneseni-cz.md](automation-kontrola-usneseni-cz.md))*.
- OCR/parsing podepsaných PDF, přepis audia.
- Neveřejné sekce webu.

## Technical Approach

- **Stack:** Python 3.11+, Playwright (Chromium, persistentní profil), parsing lxml/BeautifulSoup nad uloženým HTML (parsing offline z work-dir ⇒ opakovatelný bez sítě).
- **Anti-CF režim:** viditelný (headed) Chrome, náhodné prodlevy 3–8 s mezi requesty, navigace v jednom tabu, persistentní profil kvůli cf_clearance. Detekce challenge stránky (`Okamžik…`/`Just a moment`) ⇒ pauza a výzva uživateli k ručnímu odkliknutí, pak pokračování. Konfigurace (tempo, cesty, base URL) v config souboru, ne hardcoded.
- **Fáze běhu:**
  1. *Discovery:* projít všechny stránky výpisu ⇒ seznam jednání (UUID, typ, číslo, datum, dostupné odkazy) ⇒ checkpoint `meetings-index.json`.
  2. *Fetch:* pro každé jednání stáhnout pozvánku, zápis, usnesení ⇒ raw HTML do `work/<uuid>/*.html` + `fetch-log.jsonl` (URL, čas, HTTP výsledek). Resume = přeskočit už stažené.
  3. *Parse:* offline z raw HTML ⇒ strukturovaná data. Parser je striktní: neočekávaná struktura ⇒ anomálie do reportu, ne tichý fallback.
  4. *Assemble + validate:* křížové kontroly ⇒ `archive-YYYY-MM-DD.json` + `report-YYYY-MM-DD.md`.
- **Schéma (návrh, finalizace po vzorku):**
  ```
  { export: {exported_at, source, tool_version, counts},
    meetings: [{ uuid, body_type, number_raw, number, year, date_raw, date_iso,
                 links: {invitation, minutes, signed_minutes_pdf, resolutions, audio},
                 invitation: {fetched_at, status, program_items[], raw_text},
                 minutes: {fetched_at, status, raw_text, ...},
                 resolutions: [{ id, number_raw, text_verbatim, vote: {...max granularita z webu...},
                                 meeting_uuid }] }],
    anomalies: [...] }
  ```
- Umístění: kód `scraper/`, data `data/`, work-dir `work/`, logy `logs/` v `/Users/sigy/Projects/Pečky`.

## Edge Cases & Error Handling

- Stará jednání bez zápisu/usnesení ⇒ `missing_on_site` (odkaz na webu chybí) vs. `fetch_failed` (odkaz je, stažení selhalo — uložit důvod a HTTP kód).
- Cloudflare challenge kdykoli ⇒ detekce, pauza, ruční odkliknutí, retry téže stránky; po N neúspěších checkpoint a čistý exit s instrukcí.
- Nové jednání přibude během běhu ⇒ discovery seznam je fixní snapshot; nesoulad zachytí závěrečná kontrola počtů.
- Duplicitní UUID / jednání na dvou stránkách výpisu (posun stránkování) ⇒ dedupe podle UUID, zaznamenat.
- Neparsovatelné datum/číslo ⇒ normalizované pole `null`, raw hodnota zůstává, anomálie do reportu.
- Hlasování bez jmen (jen součty) ⇒ uložit přesně to, co web uvádí; nedopočítávat.
- Přerušení běhu ⇒ resume z checkpointů; finální JSON nikdy z částečných dat.

## Open Questions — uzavřeno při implementaci (2026-08-04)

1. ~~Struktura stránek zápisu a usnesení~~ → ověřeno na vzorku i plném běhu;
   finální schéma v README.md. Layout textu usnesení má 4 varianty
   (p / div / holý text / vnořené tabulky) — všechny pokryté testy.
2. ~~Jmenovité hlasování?~~ → **ano u zastupitelstva** (pro/proti/zdržel se/
   nehlasoval se jmény, v zápisech i u usnesení), u rady jen souhrnné počty.
3. ~~Formát pozvánky~~ → **pouze PDF** (ne HTML). Rozhodnuto stahovat PDF
   (~67 KB/ks) a extrahovat text — odchylka od „binárka jen URL" schválená
   v průběhu. Navíc: web pozvánky generuje jen pro jednání od ~06/2026,
   starší vrací trvalou serverovou chybu → `site_error`.
4. ~~Work-dir ponechat?~~ → ponechán (auditní ground truth + resume).

## Dodatečná rozhodnutí v průběhu

- Detail-stránky usnesení (`/verejne/usneseni/<id>`): **stahovat vše**
  (volba uživatele; +2 731 stránek, ~2,5 h). Detail endpoint je globální pro
  celou platformu → implementován identity guard na číslo usnesení.
- Cloudflare: Playwright launch neprošel ani s ručním odklikem; funguje
  systémové Chrome bez automatizačních příznaků + `connect_over_cdp`
  + in-page `fetch()` pro binárka/detaily.

## Výsledek prvního běhu (2026-08-04)

281/281 jednání, 2 731 usnesení (vše s detaily), 2 846 hlasování, číselné řady
bez děr, verbatim audit bez odchylek, 0 CF challenge. Viz
`data/report-2026-08-04.md`.

**Stav k 27. 8. 2026:** ke stroji, na kterém tento scraper běžel
(`/Users/sigy/Projects/Pečky`), už není přístup — jde o uzavřenou
kapitolu, žádný další běh se neplánuje. Archiv se od té doby doplňuje
lehkou cestou přes Claude in Chrome, viz
[automation-kontrola-usneseni-cz.md](automation-kontrola-usneseni-cz.md).
Důsledek: `detail_id` a jmenovitá hlasování u jednání doplněných tímto
novým postupem chybí a nemají náhradní zdroj — trvalá mezera oproti
původnímu rozsahu.

## Verification Plan

1. **Úplnost výpisu:** počet jednání nalezených v discovery = počet záznamů v archivu; počet stránek výpisu projitých = počet dle paginace.
2. **Číselné řady:** per orgán a rok kontrola děr v číslech jednání (1/2026…N/2026); díra = anomálie v reportu (může být legitimní, ale musí být vidět).
3. **Relace:** každé usnesení má existující `meeting_uuid`; každé jednání se statusem OK má neprázdný parsovaný obsah.
4. **Verbatim audit:** parsované texty jsou substring/ekvivalent raw HTML textu (žádná ztráta ani úprava); namátkově ověřitelné proti work-dir.
5. **Round-trip normalizace:** `date_iso`/`number` zpětně zformátované odpovídají `*_raw`.
6. **Vzorková kontrola:** před hromadným během ruční odsouhlasení parsovaného vzorku (viz Open Q1); po běhu report anomálií — hotovo teprve, když jsou všechny anomálie vysvětlené.
7. Souhrnný `report-YYYY-MM-DD.md`: počty per orgán/rok, seznam chybějících dokumentů, seznam anomálií.
