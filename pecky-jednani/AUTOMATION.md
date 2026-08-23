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

Web prolinkovává zmínky o parcelách („č. parc. NNNN(/NNN)“) v textu
usnesení/bodů programu na detail parcely na Nahlížení do KN (VDP).
Mapování číslo → URL žije v `pecky-jednani/katastr-odkazy.json`
(klíč `parcely`), načítá ho JS obou zobrazení (`index.html` i
`pecky-jednani/index.html`) při startu vedle `pecky-jednani.json`.
Postup a metodika dohledávání (přes REST API ČÚZK, api-kn.cuzk.gov.cz)
jsou popsané v `katastr.md`.

**Při každé aktualizaci `pecky-jednani.json` (nová jednání) je třeba:**

1. Projít nová/změněná usnesení a body programu na zmínky „parc.
   NNNN(/NNN)“ (regex `parc\.?\s*(\d{1,5}(?:\/\d{1,3})?)` — stejný,
   jaký web používá k prolinkování na frontendu).
2. Čísla, která ještě nejsou v `katastr-odkazy.json` → `parcely`,
   dohledat přes `GET /api/v1/Parcely/Vyhledani` (klíč v
   `.katastr-api-key`, gitignored). Postup podle `katastr.md`:
   - vyzkoušet všechny 4 kombinace `TypParcely`×`DruhCislovaniParcely`
     (ne jen PKN/pozemková — jednoduché hledání dá falešné negativy),
   - k.ú. odhadnout z kontextu usnesení nebo podle „sourozeneckého"
     čísla (stejné kmenové číslo u jiného už vyřešeného poddělení
     typicky znamená stejné k.ú.), jinak zkusit Pečky, pak Velké
     Chvalovice,
   - **nekaskádovat naslepo přes další obce** bez kontextové opory —
     riziko falešné shody (viz `katastr.md`, případ parcely 531).
3. Nově nalezené dvojice `"NNNN": "https://vdp.cuzk.gov.cz/vdp/ruian/parcely/{id}"`
   přidat do `parcely` v `katastr-odkazy.json`, aktualizovat `count` a
   `generated`.
4. Čísla, která se nedohledala v žádné rozumné kombinaci, do souboru
   nepřidávat — needit vymýšlet, nechat nepodlinkovaná (needit ani
   zpětně dohledávat v `katastr.md`, stačí že v mapě chybí).
5. Žádná změna v HTML/JS není potřeba — prolinkování na frontendu je
   datově řízené (nová položka v JSON se propíše automaticky).

Ověřovací krok: po doplnění spustit stejnou kontrolu úplnosti, jakou
použil první běh (22. 8. 2026) — projít `pecky-jednani.json` regexem
na „parc.“, srovnat proti klíčům v `katastr-odkazy.json` a ověřit, že
nepokryté zůstávají jen vědomé mezery (žádné tiše chybějící číslo).

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
