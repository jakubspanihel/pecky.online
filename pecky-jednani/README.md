# Archiv jednání města Pečky (usneseni.cz)

Lokální strojově čitelný archiv všech veřejných jednání orgánů města Pečky
z https://mesto-pecky.usneseni.cz/verejne/ — pozvánky, zápisy, jednotlivá
usnesení a hlasování, se zachovanými relacemi. Viz [SPEC.md](SPEC.md) (zadání
a rozhodnutí) a [AUTOMATION.md](AUTOMATION.md) (rozšíření na automatizovaný běh).

**První kompletní export: 2026-08-04** — 281 jednání (243 Rada, 38
Zastupitelstvo, 2021–2026), 2 731 usnesení vč. detail-stránek, 2 846 hlasování;
číselné řady bez děr, verbatim audit bez odchylek. Viz
`data/report-2026-08-04.md`.

## Výstup

- `data/archive-YYYY-MM-DD.json` — kompletní datovaný snímek (jeden soubor)
- `data/report-YYYY-MM-DD.md` — report křížových kontrol a anomálií
- `work/` — surové HTML/PDF každé stažené stránky (auditní ground truth,
  checkpointy pro resume), `work/fetch-log.jsonl` — log každého requestu
- `logs/run-*.jsonl` — strukturované logy běhů

## Struktura archivu (zkráceně)

```jsonc
{
  "export": { "exported_at", "source", "tool_version", "listing_pages", "counts" },
  "meetings": [{
    "uuid",                        // primární klíč jednání (z webu)
    "status": "ok",
    "body_type_raw": "Rada" | "Zastupitelstvo" | …,
    "label_raw": "27/2026 (20. 7. 2026)",   // verbatim z výpisu (vč. NBSP)
    "number": 27, "year": 2026, "date_iso": "2026-07-20",  // normalizace VEDLE originálu
    "links": { "invitation", "minutes", "signed_minutes_pdf", "resolutions", "audio" },
    "link_texts": { … },           // texty odkazů z výpisu

    // Každý dokument nese status + url + fetched_at.
    // status: "ok" | "site_error" (web dokument neumí vydat; error = flash
    // zpráva serveru) | "missing_on_site" (odkaz na webu není)
    "invitation":  { "status", "url", "fetched_at", "pages", "full_text" }, // text z PDF
    "minutes": {                   // zápis
      "status", "url", "fetched_at",
      "title_raw", "date_raw", "date_iso", "time_raw",
      "presence": { "pritomni": {"count","names","raw"}, "omluveni", "nepritomni",
                     "predsedajici", "quorum_raw", "raw_text" },
      "agenda_items": [{           // body programu
        "number", "title_raw", "heading_raw", "predkladatel",
        "votes": [{ "pro": {"count","names","raw"}, "proti", "zdrzel_se", "nehlasoval",
                    "result_raw", "adopted_resolution_number", "raw_text" }],
        "resolution_numbers_mentioned": [],   // vč. odkazů na starší usnesení
        "raw_text"                 // celý bod verbatim
      }],
      "header_raw", "full_text"    // celý zápis verbatim
    },
    "resolutions": { "status", "url", "fetched_at", "items": [{  // jednotlivá usnesení
      "number_raw": "UR-254-27/26",
      "detail_id": 146294,        // stabilní numerické ID z webu
      "detail_url",
      "agenda_item_raw", "text_verbatim", "cell_text_raw",
      "date_raw", "date_iso", "responsible_raw", "deadline_raw",
      "vote": { "pro": {"count","names","raw"}, "proti", "zdrzel_se", "raw_text" },
      "detail": {                  // z detail-stránky usnesení (fáze B)
        "number_raw", "text_verbatim", "typ_raw", "zodpovida_raw",
        "prijato_raw", "prijato_date_iso", "prijato_meeting_label",  // "27/2026"
        "termin_raw", "ukonceno_raw", "ukonceno_date_iso", "fields_raw"
      }
    }]}
  }],
  "validation": { "counts", "series_gaps" },
  "anomalies": []                  // vše, co neodpovídalo očekávané struktuře
}
```

**Relace:** usnesení jsou vnořena pod jednání (uuid). Hlasování v zápisu nese
`adopted_resolution_number` → číslo usnesení. `resolution_numbers_mentioned`
zachycuje odkazy i na usnesení jiných jednání (revokace apod.).
`names` u hlasování: jmenovitě u zastupitelstva, `null` u rady (web uvádí jen počty).

## Časové značky videa (`agenda[].video_ts`, `video_url`)

Od jednání ZM 2/2025 (2. 4. 2025) přikládá Město Pečky k YouTube záznamu
zasedání **kapitoly** — timestampy jednotlivých bodů programu v popisku
videa. Doplněno 20. 8. 2026 do lehkého souboru `pecky-jednani.json`
(ne do velkého `archive-*.json`), jen pro Zastupitelstvo — Rada video
nemá.

**Extrakce (jednorázově, ručně přes Claude in Chrome):**
1. Pro jednání s `links.youtube` otevřít video, z `window.ytInitialPlayerResponse
   .videoDetails.shortDescription` vytáhnout řádky ve tvaru `H:MM:SS Text`
   (regex `^(\d{1,2}:\d{2}(?::\d{2})?)\s+(.*)$`).
2. Z textu kapitoly vyparsovat číslo bodu programu — obvykle na začátku
   (`N. Text`), někdy s prefixem `Úvod, N. …`, někdy dva body na jednu
   kapitolu (`N., M. Text` nebo `N. Text + M. Text`) — pak stejný čas patří
   oběma bodům. Číslo kapitoly v popisku **neodpovídá vždy chronologickému
   pořadí** ani číslu předchozí kapitoly (rada/zastupitelstvo body občas
   probírá v jiném pořadí, než jsou v programu) — parsovat vždy podle
   extrahovaného čísla, ne podle pořadí řádků.
3. Spárovat podle čísla bodu (`agenda[].n`) s jednáním v `pecky-jednani.json`,
   doplnit `video_ts` (sekundy) a `video_url` (`https://youtu.be/<id>?t=<sekundy>`).
   Ne všechny body mají vlastní kapitolu (výjimečně YouTube kapitolu
   nedostanou — necháno bez `video_ts`).
4. Jednání před 2/2025 (celé 2022–2024 a ZM 1/2025) kapitoly v popisku
   nemají vůbec — `shortDescription` obsahuje jen jednořádkový název.

**Pro budoucí automatizaci:** při každém novém jednání ZM s YouTube odkazem
zopakovat tento postup (stačí otevřít video a přečíst
`ytInitialPlayerResponse.videoDetails.shortDescription`, žádné klikání není
potřeba). Pokud by šlo získat YouTube Data API klíč, `videos.list` s
`part=snippet` vrátí totéž programově bez prohlížeče — vhodné pro plnou
automatizaci bez GUI Chrome.

## Délka videa (`video_duration_seconds`)

U každého jednání s `links.youtube` (nejen ZM s kapitolami — **všech 30**
k 20. 8. 2026) je v `pecky-jednani.json` na úrovni jednání i celková délka
záznamu v sekundách, doplněná 20. 8. 2026 pro zobrazení "▶ Video, h:mm" ve
sbaleném řádku výpisu jednání. Zdroj: `ytInitialPlayerResponse.videoDetails
.lengthSeconds` (jedno číslo, žádné parsování popisku není potřeba). **Při
každé aktualizaci archivu o nové jednání s YouTube odkazem doplnit i tuto
hodnotu** stejným způsobem.

## Účast na jednání (`attendance.present`, `attendance.total`)

Doplněno 21. 8. 2026 pro zobrazení "sešlo se N z/ze M radních/zastupitelů"
ve sbaleném řádku výpisu. Zdroj: `minutes.presence.pritomni.count` a
`minutes.presence.quorum_raw` (věta „Přítomno je N (z M) členů…") ve velkém
`archive-2026-08-04.json` — pro 281/283 tehdy existujících jednání. Pozor:
`quorum_raw` uvádí `z M` jen když je M jiné než celý sbor; jinak jen počet
přítomných — celkový počet (`total`) proto dopočítat z pevné velikosti
orgánu (Rada = 7, Zastupitelstvo = 21; ověřeno konstantní napříč celým
obdobím 2021–2026 ve všech 281 záznamech, kde byl výslovně uveden). Dvě
nejnovější jednání (Rada 28/2026, 29/2026), která v datovaném archivu ještě
nebyla, doplněna ručně z jejich `zapis/` stránky.

**Pro budoucí automatizaci:** u každého nového jednání dohledat totéž z jeho
zápisu (`minutes.presence` v přírůstkovém přeparsování, nebo věta „Přítomno
je…" na stránce `/verejne/<uuid>/zapis/`) a doplnit `attendance` do
`pecky-jednani.json`.

**Technická poznámka k velkému `archive-*.json`:** přímé čtení tohoto
souboru z připojené složky (`open()`/`head`/`cat` na cestě přes mount)
občas skončí `OSError: [Errno 35] Resource deadlock avoided` (viz i
poznámka v kořenovém `CLAUDE.md`). Spolehlivé obejití: nejdřív soubor
zkopírovat (`cp archive-*.json /tmp/…`) a pracovat s kopií — `cp` samo
selhání nemělo, ačkoli přímé čtení stejné cesty ano.

**Verbatim zásada:** texty se nikdy nečistí (vč. nezlomitelných mezer a
anonymizačních bloků █). Normalizovaná pole (`date_iso`, `number`) jsou vždy
vedle `*_raw` originálu. Assemble fáze programově ověřuje, že každý text
usnesení je (modulo whitespace) obsažen v surovém HTML.

## Známá omezení zdroje (ověřeno 2026-08-04)

1. **Pozvánky**: web je generuje jen pro jednání od ~června 2026 (8 z 281);
   u starších vrací serverovou chybu („Neočekávaná chyba. Náš tým byl
   informován.") — v archivu `status: "site_error"` s flash zprávou.
2. **Zápisy rady z 2021** (4×) nemají skupinu „Nepřítomni" — starší šablona;
   `presence.nepritomni = null` + anomálie.
3. **Detail endpoint `/verejne/usneseni/<id>` je globální** napříč všemi městy
   na platformě usneseni.cz (nekontroluje tenant). Parser proto ověřuje shodu
   čísla usnesení; nesouhlas = anomálie `detail_number_mismatch`, detail se
   zahodí.
4. Formát ročníku v číslech usnesení kolísá (`…/26` vs `…/2026`) — čísla jsou
   vždy verbatim; pro spolehlivé párování používej `detail_id`.

## Lokální PDF archiv (`Data/`)

Vedle `archive-YYYY-MM-DD.json` (extrahovaný text) udržujeme i syrové PDF
soubory, jeden pár na jednání:

- `Data/{datum}/podepsany-zapis.pdf` — podepsaný zápis (283/283 jednání,
  2021–2026, kompletní)
- `Data/{datum}/pozvanka.pdf` — pozvánka (jen 10/283 — dostupná pouze pro
  jednání od 1. 6. 2026, viz „Známá omezení zdroje" výše; starší trvale
  vrací serverovou chybu, ověřeno opakovaně napříč lety 2021–2025)

Kolize data (víc jednání týž den — zatím jediný případ 25. 5. 2026: Rada
20/2026 + Zastupitelstvo 3/2026) se řeší příponou složky
`-rada`/`-zastupitelstvo`.

### Stahování pozvánek a podepsaných zápisů (pro budoucí doplnění)

Cloudflare blokuje jakýkoli non-browser přístup (curl, přímé HTTP) —
jediná cesta je opravdový prohlížeč (Claude in Chrome). Postup:

1. **Jednorázové nastavení Chrome** (klíčové!): otevři
   `chrome://settings/content/pdfDocuments` a zapni „Download PDFs instead
   of automatically opening them in Chrome". Bez toho se PDF otevře
   v interním PDF.js prohlížeči a pozvánka (na rozdíl od zápisu) vyžaduje
   ruční klik na stahovací tlačítko + potvrzení nativního OS dialogu „Kam
   uložit" — ten automatizace nevidí ani nemůže odkliknout. Se zapnutým
   nastavením se OBA typy dokumentů stahují stejně: přímou navigací na URL,
   automaticky, bez klikání.
2. `python3 _pending_chunk.py <zapis|pozvanka> <N>` — vypíše dalších N
   dosud chybějících jednání jako JSON (`date`/`number`/`year`/`type`/`url`).
3. Přes `browser_batch` navigovat postupně na `url` každého jednání
   (navigate + wait ~2 s), v dávkách ~15–20 (víc zvyšuje riziko serverové
   503 i záměny dokumentů, viz past níže).
4. Než spustíš organize, počkej ~10–15 s a ověř (`ls ~/Downloads/*.pdf | wc -l`
   dvakrát po sobě), že se počet PDF v `~/Downloads` ustálil — stahování
   velkých souborů má zpoždění za navigací. Organize spuštěný předčasně nic
   nerozbije, jen nechá ještě-nedokončené soubory na příště.
5. `python3 _organize_downloads.py <zapis|pozvanka> <chunk.json>` — spáruje
   stažené soubory s jednáními v chunku a přesune do `Data/{datum}/`.
6. Opakovat, dokud `_pending_chunk.py` nehlásí 0 zbývajících. U pozvánek to
   validně skončí na ~10 (starší jednání trvale nedostupná — nemá smysl
   zkoušet dál, ověřeno vzorkem napříč všemi lety).

**Kritická past — záměna dokumentů mezi jednáními.** Rada i Zastupitelstvo
číslují jednání odděleně od 1 každý rok, takže „č. 4/2023" v názvu
staženého souboru může patřit dvěma různým jednáním. Horší: web občas (při
rychlých po sobě jdoucích requestech; přesná příčina neznámá) **vrátí pro
jedno UUID obsah jiného jednání se stejným číslem** — zjištěno opakovaně
u obou typů dokumentů. `_organize_downloads.py` proto po každém běhu
porovná MD5 hash všech souborů daného typu napříč `Data/` a nahlásí
`DATA INTEGRITY WARNING`, pokud jsou dva různé dny bit-identické. Postup
při nálezu: smazat oba soubory a stáhnout znovu každý zvlášť, jednotlivou
navigací (ne v dávce), s ověřením hashe před finálním uložením.

## Spuštění

```bash
.venv/bin/python -m scraper.cli discover       # stáhne stránky výpisu (~3 min)
.venv/bin/python -m scraper.cli index          # postaví work/meetings-index.json
.venv/bin/python -m scraper.cli fetch          # dokumenty všech jednání (~1,5 h)
.venv/bin/python -m scraper.cli parse          # offline: HTML/PDF → parsed.json
.venv/bin/python -m scraper.cli fetch-details  # detail-stránky usnesení (~2,5 h)
.venv/bin/python -m scraper.cli parse          # doplní data z detailů
.venv/bin/python -m scraper.cli assemble       # archiv + validace + report
```

(Časy z běhu 2026-08-04 při plném rozsahu; `fetch --uuids <uuid>…` omezí běh
na vybraná jednání.)

Všechny fáze mají resume — přerušený běh po restartu pokračuje (checkpointy
ve `work/`). Parsing je čistě offline nad `work/`, lze ho opakovat bez sítě.

## Cloudflare

Web je za agresivní bot-ochranou. Scraper proto:
- spouští **systémové Chrome bez automatizačních příznaků** (jen `--remote-debugging-port`)
  a připojuje se přes CDP → ruční odklik Turnstile funguje,
- naviguje lidským tempem (3–8 s, konfigurovatelné v `config.json`),
- drží persistentní profil (`work/chrome-profile`) kvůli `cf_clearance` cookie,
- při detekci challenge čeká, až ho v okně odklikneš, a pokračuje sám.

Playwright headless/vlastní HTTP klienti (curl, `page.request`) dostávají 403.

## Testy

```bash
.venv/bin/python -m pytest tests/
```

33 testů proti reálným fixtures v `tests/fixtures/` (staženo 2026-08-04).
Fixtures pokrývají 4 varianty layoutu textu usnesení, které se na webu
v letech 2021–2026 vyskytují: `<p>`, `<div>`, holý text za labelem a vnořené
tabulky/seznamy (dotace, školské obvody).
