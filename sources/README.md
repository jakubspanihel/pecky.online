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
