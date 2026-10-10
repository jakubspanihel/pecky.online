# Archiv jednání města Pečky (usneseni.cz)

Lokální strojově čitelný archiv všech veřejných jednání orgánů města Pečky
z https://mesto-pecky.usneseni.cz/verejne/ — pozvánky, zápisy, jednotlivá
usnesení a hlasování, se zachovanými relacemi. Viz [SPEC.md](SPEC.md) (zadání
a rozhodnutí původního jednorázového exportu),
[automation-kontrola-usneseni-cz.md](automation-kontrola-usneseni-cz.md)
(aktuální postup pro průběžné doplňování nových jednání přes Claude in Chrome)
a [automation-katastr-parcely.md](automation-katastr-parcely.md) (katastr,
tabulky Pozemky).

## Umístění souborů
Všechny soubory týkající se sekce Jednání (index pro fulltextové hledání,
kompletní datový snímek, referenční dokumenty, skripty) patří do
`jednani/`, ne do kořene repa ani do `data/` — i nově vznikající.
Jediná výjimka: zobrazení sekce žije v `content/jednani.html` (od migrace
na vícestránkový web 30. 8. 2026 — viz `ARCHITEKTURA-MIGRACE.md` v kořeni
repa) — needit vygenerovanou veřejnou stránku přímo, jen `content/jednani.html`
a pak spustit `scripts/build.py`. Dřívější samostatná stránka
`jednani/index.html` (kopie bez hlavičky hlavního webu) migrací
zanikla — nahradila ji plnohodnotná veřejná stránka `/jednani/`.

**První kompletní export: 2026-08-04** — 281 jednání (243 Rada, 38
Zastupitelstvo, 2021–2026), 2 731 usnesení vč. detail-stránek, 2 846 hlasování;
číselné řady bez děr, verbatim audit bez odchylek. Viz
`data/report-2026-08-04.md`.

## Výstup

Pozor na cesty: `data/`, `work/` a `logs/` níže jsou složky **scraperu**
na stroji, kde běží (`/Users/sigy/Projects/Pečky`, viz `SPEC.md`), ne
složky tohoto repa — kořenová `data/` v repu neexistuje. Do repa se
z toho přenáší jen snímek archivu, a to rovnou do `jednani/`
(dnes `jednani/archive-2026-08-04.json`).

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

**Není to jednorázová akce.** Zápis a YouTube odkaz se u jednání typicky
doplní v různých bězích kontroly (zápis dřív, video až s odstupem) —
kontrola „má jednání zápis i video, ale chybí mu `video_ts`?" se proto
opakuje při každém běhu, viz
[automation-kontrola-usneseni-cz.md](automation-kontrola-usneseni-cz.md)
→ krok 7.

**Extrakce (přes Claude in Chrome):**
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

**Pozor — účel tohoto pole:** `video_ts`/`video_url` slouží jen k odkazu
„▶ video" na konkrétní místo v záznamu (kde existuje). Zobrazený ČAS
u bodu programu ve výpisu jednání z tohoto pole **nevychází** — původně tak
bylo (chybně) zadáno a implementováno 20.–21. 8. 2026, protože YouTube
kapitoly nejsou totéž co skutečná délka projednávání bodu. Opraveno
21. 8. 2026 — viz `duration_seconds` níže.

**Pro budoucí automatizaci:** při každém novém jednání ZM s YouTube odkazem
zopakovat tento postup (stačí otevřít video a přečíst
`ytInitialPlayerResponse.videoDetails.shortDescription`, žádné klikání není
potřeba). Pokud by šlo získat YouTube Data API klíč, `videos.list` s
`part=snippet` vrátí totéž programově bez prohlížeče — vhodné pro plnou
automatizaci bez GUI Chrome.

## Délka jednání a délka projednávání bodu (`duration_seconds`)

Opraveno 21. 8. 2026 — nahrazuje původní `video_duration_seconds`/`video_ts`
jako zdroj zobrazeného času (to pole popisovalo jen dostupnost/pozici videa,
tedy jen ~30 zasedání Zastupitelstva). Správný zdroj je **skutečná
zaznamenaná délka ze zápisu**, dostupná pro VŠECHNA jednání — radu
i zastupitelstvo, s videem i bez něj.

Zdroj: text zápisu obsahuje u každého jednání přesné časové značky
(`minutes.full_text` a `minutes.agenda_items[].raw_text` ve velkém
`archive-*.json`, případně přímo stránka `/verejne/<uuid>/zapis/`):
- `Jednání zahájeno DD.MM.RRRR v HH:MM:SS` / `Jednání ukončeno DD.MM.RRRR
  v HH:MM:SS` → rozdíl = `meetings[].duration_seconds`. Pozor na tvar „ve"
  místo „v" před některými hodinami (české skloňování, např. „ve 21:04:14").
- U každého bodu programu: `Projednávání bodu bylo zahájeno v HH:MM:SS` /
  `...ukončeno v HH:MM:SS` → rozdíl = `agenda[].duration_seconds`. Párovat
  podle čísla v `(bod číslo N)` z nadpisu bodu, NE podle pořadí v zápisu —
  pořadí projednávání se od pořadí v programu občas liší (stejně jako
  u `video_ts` výše).
- Body, které byly odloženy („Projednání bodu bylo odloženo.") nebo mají
  prázdný `raw_text`, žádnou časovou značku nemají — bez `duration_seconds`,
  nic se nedopočítává ani nevymýšlí.

Pokrytí k 21. 8. 2026: 283/285 jednání (2 nejnovější — Zastupitelstvo 5/2026,
Rada 30/2026 — mají zatím jen pozvánku, zápis ještě neexistuje), 3998/4046
bodů programu (zbytek odloženo nebo bez zaznamenaného textu). 281/281 jednání
zdrojováno z `archive-2026-08-04.json`; 2 nejnovější tou dobou v archivu
chybějící jednání (Rada 28/2026, 29/2026) doplněna ručně stejným rozborem
přímo ze stránky `/verejne/<uuid>/zapis/`.

**Zobrazení na webu:** formát `NhMMmin` (např. „2h:14min"), pod hodinu jen
`Mmin` (např. „45min") — opraveno 21. 8. 2026 z původního `h:mm`. Čas u bodu
programu je na konci řádku bodu, PŘED odkazem na video (pokud pro daný bod
existuje — `video_url`/`video_ts` beze změny, pořád jen pro odkaz, viz výše).
Délka celého jednání je na konci sbaleného řádku jednání s prefixem „schůze
trvala: …", oddělená znakem „ · " od počtu přítomných členů (`sešlo se N
z/ze M …`) a od případného odkazu na video. Zdrojová funkce:
`jFormatDuration`/`jFormatItemTime` v `content/jednani.html`. Sbalený
řádek se od 21. 8. 2026 už u prvního jednání v seznamu automaticky
nerozbaluje — všechna jednání startují sbalená.

**Pro budoucí automatizaci:** u každého nového jednání dohledat totéž z jeho
`zapis/` stránky stejným rozborem a doplnit `duration_seconds` na úrovni
jednání i jednotlivých bodů do `pecky-jednani.json`.

**Nejdéle projednávaný bod (🔥, od 23. 9. 2026):** bod programu s nejvyšším
`duration_seconds` v rámci jednání dostane u svého času ve výpisu příponu
„ 🔥" (`bod se projednával: 2h:14min 🔥`). Počítá se za běhu z dat, která už
v `pecky-jednani.json` jsou — žádné nové pole, žádný ruční krok při
doplňování jednání. Podmínka: jednání musí mít aspoň dva body s vyplněným
`duration_seconds`, jinak by "nejdelší" u jediného časovaného bodu nic
neříkalo (viz konvence webu o nepřehánění). Při shodě více bodů na stejné
maximální délce dostanou 🔥 všechny. Zdrojová funkce: `jRenderAgendaList`
v `content/jednani.html` (`maxDuration`/`isLongest`).

**Žebříček nejdelších bodů (`/jednani/nejdelsi.html`, od 23. 9. 2026):**
samostatná podstránka se statickou tabulkou TOP 10 bodů programu
**zastupitelstva** (Rada se nesleduje) s nejvyšším `duration_seconds`
v aktuálním volebním období (od ustavujícího zasedání 20. 10. 2022) — na
rozdíl od 🔥 značky výše, která srovnává jen body v rámci jednoho jednání,
jde tady o srovnání napříč všemi jednáními. **Ruční snímek dat, ne živý
`fetch()`** — na rozdíl od `absence.json` (krok 8c) se sama nepřepočítává
a při zapomenutí zestárne beze změny; po každé aktualizaci
`duration_seconds` u nového jednání Zastupitelstva proto zkontrolovat,
jestli by se žebříček změnil, a pokud ano, přepsat tabulku v
`content/nejdelsi.html` ručně (viz krok 8d v
`automation-kontrola-usneseni-cz.md`). Odkázaná z `/jednani/` (odstavec
„Související:" vedle Docházky) přes trvalý hash na konkrétní jednání
(`jSlugForMeeting()`, viz „Permalinky na jednotlivá jednání" níže).

**Žebříček odpracovaných hodin (`/jednani/odpracovano.html`, od 30. 9. 2026):**
statická podstránka se 23 zastupiteli z volebního období 2022–2026
seřazenými podle počtu jednání (rada, ZM, výbory, komise, školská rada),
s odpracovanými hodinami (součet `duration_seconds`, u komisí a výborů
`time`–`time_end`; jednání bez času se do hodin nepočítají, jen se
vykážou) a štítkem „Člen rady"/„Zastupitel". Ruční snímek k 30. 9. 2026,
ne živý `fetch()` — stejně jako `nejdelsi.html`. Sekce „Ti další" je
rozbalovací. Odkázaná z `/jednani/` („Související:").

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

## Jmenovité obsazení (`attendance.present_names`, `attendance.absent_names`)

Doplněno 21. 8. 2026 pro řádek s avatary účastníků nad seznamem bodů
programu v rozbalené položce jednání. Zdroj: `minutes.presence.pritomni.names`
(→ `present_names`) a `minutes.presence.omluveni.names` +
`minutes.presence.nepritomni.names` sloučené dohromady, každé se štítkem
`note` („omluven"/„nepřítomen") (→ `absent_names`, tvar
`[{"name","note"}]`) — web request žádal jen binární Přítomni/Nepřítomni,
proto omluvení a nepřítomní bez omluvy nejsou v UI rozlišeni jinak než
`note` v tooltipu. Pokrytí stejné jako u `duration_seconds` (283/285 —
2 nejnovější jednání ručně, 2 budoucí naplánovaná jednání zápis ještě
nemají). Zobrazení: `.people-avatars`/`.av-init` — stejný vizuální styl
jako sloupec „lidé" u tabulek volebních uskupení (barevný kroužek
s iniciálami, celé jméno v `title`), tady jednotnou barvou (bez vazby na
politické uskupení). Nepřítomní jsou na konci řádku za oddělovací
svislou linkou (`.attendance-sep`) a mají poloviční krytí (`.av-absent`).
Iniciály generuje `jInitials()` — odfiltruje běžné tituly (Ing., Mgr.,
Bc. …) a vezme první písmeno křestního jména a příjmení.

**Pro budoucí automatizaci:** u každého nového jednání doplnit
`present_names`/`absent_names` stejným rozborem prezence jako u
`attendance.present`/`total` výše.

## Průběžná prezence (`attendance.changes`)

Doplněno 9. 9. 2026. Zápis vedle úvodní prezence zaznamenává i každý
příchod, odchod a distanční připojení během jednání („V 15:45:53 přišel
Ing. Petr Dürr, přítomno 7 z 7 radních." + blok „Aktualizovaný stav
prezence"). Do té doby scraper tyhle věty vědomě zahazoval; ukázalo se, že
bez nich vypadá pozdní příchod jako celodenní absence — u Ing. Petra Dürra
100 chybějících úvodních prezencí ze 170 jednání rady, ale u 47 z nich
zápis eviduje pozdější příchod.

Tvar: `[{"time":"15:45:53","event":"přišel","name":"Ing. Petr Dürr",
"present_after":7}]`, seřazeno podle času. `event` je `"přišel"`,
`"odešel"` nebo `"distančně"`. U jednání bez jediné změny se pole
vynechává. Pokrytí: 124 jednání z 286 (218 událostí — 140 příchodů,
77 odchodů, 1 distanční připojení), doplněno zpětně z
`archive-2026-08-04.json` skriptem `scripts/doplnit-prubeznou-prezenci.py`;
pět jednání novějších než snímek archivu ověřeno ručně na `/zapis/`.

Zatím jde o čistě datové pole — **v UI se nezobrazuje**. Řádek s avatary
účastníků pořád ukazuje jen stav ze zahájení, takže kdo dorazil později,
je tam mezi nepřítomnými. Až se bude řešit zobrazení, patří k tomu
i rozhodnutí, jak takového člověka v řádku odlišit.

**Pro budoucí automatizaci:** vytáhnout `changes` z každého nového zápisu
podle `automation-kontrola-usneseni-cz.md`, krok 4.

## Absence na jednáních (`absence.json`, `/jednani/absence.html`)

Doplněno 9. 9. 2026. Kolikrát který zastupitel a radní chyběl — spočítáno
z `attendance` a `attendance.changes` skriptem `scripts/absence.py` do
`jednani/absence.json`, odkud si to stránka natáhne za běhu. Postup,
zdůvodnění a pasti popisuje `INSTRUKCE-absence.md`; skript ho implementuje,
ne naopak — při změně pravidel se mění oba soubory.

`absence.json` drží čtyři bloky (Rada a Zastupitelstvo × dvě volební
období), v každém řádek na osobu s počtem jednání v mandátu, absencí
při zahájení, pozdních příchodů, skutečné nepřítomnosti, dřívějších odchodů
a případnou poznámkou. Blok nese i `kontrola` — součet absencí přes osoby
proti součtu přes jednání; rozdíl smí být nenulový jen tam, kde ho
vysvětluje vadný záznam u zdroje (dnes Rada 24/2024, rozdíl +1).

Od 19. 9. 2026 je odkázaná — odstavec „Kontrola docházky: Jak vás
zastupitelé zastupují" nad nadpisem „Zápisy z jednání" v
`content/jednani.html`. V navigaci vlastní odkaz pořád nemá (žije jen
jako podstránka `/jednani/absence.html`, ne jako plnohodnotná sekce
s vlastním řádkem v „Stav sekcí"). Generuje ji `scripts/build.py`
z `content/absence.html` přes `EXTRA_PAGES` (viz `ARCHITEKTURA-MIGRACE.md`)
— šesté pole u záznamu `absence` je ISO datum, které zároveň sundá
`noindex` a stránku zařadí do `sitemap.xml` s tímhle datem jako
`<lastmod>` (bez vlastního řádku v „Stav sekcí" ho nemá odkud dopočítat
samo — při další obsahové změně stránky datum v `build.py` ručně
posunout).

**Při každém novém jednání** znovu spustit `python3 jednani/scripts/absence.py`
— `absence.json` se nepřepočítává sám. Doplněno 19. 9. 2026 jako vlastní
krok 8c v `automation-kontrola-usneseni-cz.md` (dřív to v týdenním
postupu nebylo, takže se přepočet snadno zapomněl — viz historie
v kořenovém `README.md` → „Stav sekcí"), teď se dělá při každém běhu
automaticky spolu s ostatním.

**Avatar a vizitka osoby u jména (od 19. 9. 2026).** Jméno v prvním sloupci
tabulky je teď u koho jde spárovat s `lide/people.json` (fuzzy přes
`jNameKey`, stejný princip jako u avatarů účastníků v `content/jednani.html`
výše) klikací odkaz s malým kulatým avatarem vedle sebe; klik rozbalí pod
řádek stejnou vizitku (bio, povolání, kontakt, timeline funkcí), jakou
zobrazuje detail osoby v sekci Lidé. U jmen bez záznamu v `people.json`
(v aktuálních datech žádné nejsou, ale mohou přibýt) zůstává jen prostý
text bez avataru a bez odkazu — žádná vymyšlená data. Jen jeden řádek smí
být rozbalený zároveň, ale rozlišuje se podle konkrétního řádku tabulky, ne
podle osoby — `absence.json` drží tutéž osobu klidně ve dvou volebních
obdobích zvlášť (dnes se ale zobrazuje jen jedno, viz níže), a klik na
jeden řádek nesmí otevřít vizitku i v jiném se stejnou osobou.

Vykreslení vizitky (`pcAvatarHtml`/`pcDetailHtml`/`pcBuildTimeline`) je
sdílená komponenta v `assets/helpers.js`, vytažená z detailu osoby
v `content/lide.html` (ten teď na stejné funkce jen deleguje) — viz
`lide/README.md`. Stránka kvůli tomu nově načítá i `lide/people.json`,
`organizations.json` a `affiliations.json` (`EXTRA_PAGES` v
`scripts/build.py` má u `absence` nastavené `helpers.js` na `True`); pokud
se tahle data nenačtou, zůstane tabulka fungovat jako dřív, jen bez avatarů
a bez klikacích jmen.

**Přepracováno na „Docházku" (od 19. 9. 2026), zadal uživatel.** Stránka
dřív ukazovala obě volební období vedle sebe a hlavní číslo bylo „nebyl
vůbec"; teď:

- Titulek je „Jak vás zastupitelé zastupují" (dřív „Kdo chybí na
  jednáních"), perex i `<title>`/meta popisek v `scripts/build.py` přepsané
  na docházkové vyznění.
- Tabulka ukazuje **jen aktuální volební období 2022–2026** — starší
  2018–2022 se v datech dál počítá (`absence.py`/`absence.json` beze
  změny), na webu se ale nevykresluje, protože ho zápisy na usneseni.cz
  pokrývají jen zčásti a srovnání s kompletním obdobím by zkreslilo. Ve
  `vykresli()` (`content/absence.html`) se z bloků daného orgánu bere vždy
  jen nejnovější (`.sort(...).localeCompare...)[0]`), ne všechny — až
  přibude další volební období, přepne se samo.
- Sloupce jsou teď **Jméno, Docházka, Mandát, Poznámka** (dřív Jméno,
  Jednání, Chyběl při zahájení, Dorazil později, Nebyl vůbec, Odešel dřív,
  Poznámka). Docházka (`100 − r.podil`, vždy zobrazená, ne jen při
  mandátu ≥ 10) je teď headline číslo místo „nebyl vůbec". Mandát ukazuje
  tvar „X / Y" (jednání v mandátu / jednání v celém období) místo dřívějšího
  jednoho čísla s podmíněným rozpadem. Chyběl při zahájení, dorazil později
  a odešel dřív se nezobrazují jako vlastní sloupce, ale jako bodový seznam
  v Poznámce (spolu s případným textovým vysvětlením typu „náhradník, slib
  …") — vynechá se, kde je hodnota 0.
- Vysvětlující `.callout` (co čísla znamenají, odchody, tabulka nehodnotí)
  se přesunul z hlavního těla stránky do záložky „Jak se to počítá", kde
  teď žije hned pod „Odkud data jsou"; text přepsaný na Docházku
  („sloupec Docházka…", „docházka 41 % místo 69 %" — stejný podkladový
  příklad jako dřív, jen z druhé strany).
- Datový model (`jednani/absence.json`, `jednani/scripts/absence.py`,
  `INSTRUKCE-absence.md`) se **neměnil** — jde čistě o přepočet/přeuspořádání
  existujících polí (`podil`, `mandat`, `chybel`, `omluven`, `nepritomen`,
  `dorazil`, `odesel`, `poznamka`) na frontendu v `content/absence.html`.

**Pořadí záložek a řazení tabulky (týž den, dodatečná úprava zadaná
uživatelem).** Záložka Rada je teď první a výchozí (dřív Zastupitelstvo);
pořadí se prohodilo jak u tlačítek `.subtablink`, tak u odpovídajících
`.subpanel` divů a v poli `for (const organ of [...])` ve `vykresli()`.
Tabulka se řadí **od nejmenší docházky** (`blok.radky.slice().sort((a,b)
=> b.podil - a.podil)`, sestupně podle `podil` = vzestupně podle
docházky) místo dřívějšího řazení od nejkratšího mandátu ze zdrojových
dat — `absence.json` samo dál drží pořadí podle mandátu (viz
`INSTRUKCE-absence.md` → „Řazení a poznámky"), přeřazuje se až na
frontendu. Meta-poznámka pod nadpisem bloku i vysvětlení v „Jak se to
počítá" přepsané na novou logiku řazení.

**Zjednodušení perexu a nadpisu bloku (týž den, další úprava zadaná
uživatelem).** Perex zkrácen na jednu větu s odkazem: „Docházka
zastupitelů a radních na jednání. Zdrojem dat jsou zápisy z
[jednání](/jednani/)." — druhý odstavec (dřívější vysvětlení opravy
o pozdní příchody) zahozen, přesun informace o volebním období do
nadpisu bloku (viz níže) ho udělal nadbytečným. Popisný řádek nad
tabulkou („31. 10. 2022 – 7. 9. 2026. Řazeno od nejmenší docházky…")
zrušen u obou orgánů. `<h3>{období} — N jednání</h3>` nahrazen odstavcem
ve tvaru „Rada města se ve volebním období 2022–2026 sešla 175 krát."
(`sešla`/`sešlo` podle rodu orgánu — `Rada` žensky, `Zastupitelstvo`
středně, viz `tabulka()` v `content/absence.html`).

**Položka „Přítomen" v poznámce (týž den, zadal uživatel).** Bodový seznam
v Poznámce má teď vždy první položku „Přítomen: N" — reálný počet jednání,
na kterých osoba byla (`r.mandat - r.nebyl`), protějšek sloupce Docházka
v absolutním čísle místo procenta. Na rozdíl od „chyběl při zahájení"/
„dorazil později"/„odešel dřív" se zobrazuje vždy, i při nulové absenci
(`poznamkaHtml()` v `content/absence.html`).

**Skloňování „přítomen/přítomna" vyřešeno (19. 9. 2026, týž den).**
`people.json` má nově u každé osoby pole `gender`; `poznamkaHtml(r, p)`
volá sdílenou `pcGendered(p, 'Přítomen', 'Přítomna')` z
`assets/helpers.js`, takže „Ivana Trčková … Přítomna: 166" je teď
gramaticky správně. Podrobnosti (odvození `gender` ze jmen, validace,
obecný mechanismus pro celý web) viz `lide/README.md` → „České skloňování
osob (gender)".

**Sloupec Mandát ukazuje tři čísla (29. 9. 2026, zadal uživatel.)**
Tvar „X / Y / Z" — X je `mandat − nebyl` (přítomen), Y je `mandat`
(jednání v době, kdy osoba v orgánu zasedala), Z je `blok.jednani`
(jednání v celém období) — dřív jen „Y / Z". X duplikuje číslo, které
poznámka pod řádkem uvádí jako „Přítomen: N", ale v Mandátu je vidět bez
rozbalení řádku. `tabulka()`/`poznamkaHtml()` v `content/absence.html`
teď počítají `pritomen` jednou a sdílí ho.

**Finanční a Kontrolní výbor přidány (29. 9. 2026, zadal uživatel.)**
Stejná Docházka/Mandát/Poznámka tabulka jako u Rady a Zastupitelstva, teď
i pro oba výbory ZM — dvě nové podzáložky za Zastupitelstvem (pořadí
podle `content/jednani.html`). Zdroj je
`jednani/vybory.json` (viz „Jednání výborů ZM" výše), ne
`pecky-jednani.json` — `jednani/scripts/absence.py` teď čte oba soubory
a slučuje je do jednoho seznamu jednání ještě před výpočtem
(`nacti_vybory()`). Tři úpravy skriptu byly potřeba, ne jen přičtení dat:

- `vybory.json` skloňuje `absent_names[].note` podle rodu
  (`"omluven"`/`"omluvena"`, `"neomluven"`/`"neomluvena"`,
  `"nepřítomen/nepřítomna, zápis důvod neuvádí"`, `"zápis účast
  neuvádí"`) — `pecky-jednani.json` má jen `"omluven"`/`"nepřítomen"`.
  Test na přesnou shodu `x['note'] == 'omluven'` by `"omluvena"` (8×
  v datech) špatně započítal jako neomluvenou absenci; opraveno na
  `.startswith('omluven')` (stejné řešení jako `lAttachVyborAttendance`
  v `content/lide.html` už používá pro totéž).
- `vybory.json` nemá jedno pole `attendance.changes`, ale zvlášť
  `arrived_late[{name,time}]`/`left_early[{name,time}]` — `nacti_vybory()`
  je při načtení sloučí do stejného tvaru `{event, name}`
  (`'přišel'`/`'odešel'`) jako Rada/ZM čekávají.
- `OBDOBI` má nové položky `'Finanční výbor'`/`'Kontrolní výbor'`, stejná
  hranice volebních období jako Zastupitelstvo (výbory volí ZM).

Obě volební období se počítají (`absence.json` teď má 8 bloků místo 4),
na webu se stejně jako u Rady/ZM zobrazuje jen 2022–2026 — období
2018–2022 má u výborů vlastní mezery (zápis `financni-vybor-2018-11-22`
bez zaznamenané účasti, dva zápisy kontrolního výboru z roku 2021 vůbec
nezmiňují Lenku Krúpovou → `kontrola().rozdil = -2`, zdokumentováno jako
vadný záznam stejně jako starší Rada 27/2021 a Rada 24/2024). Čtyři
řádky aktuálního období mají poznámku o nástupu/konci členství ve výboru
(`POZNAMKY` v `absence.py`, zdroj `lide/README.md` → „Finanční a
kontrolní výbor ZM") — pozor, jde o jinou vazbu než stejná osoba má
u typu Zastupitelstvo, takže i jiné datum (např. Lenka Třísková: mandát
zastupitelky skončil 19. 6. 2024, mandát ve výboru až 11. 9. 2024).

Vzorek je malý (12 jednání FV, 11 KV za 2022–2026 — necelá desetina
Rady), doplněna vlastní věta v „Co do čísel nespadá" upozorňující, že tu
procento kolísá výrazně víc. Perex a meta popisek (`scripts/build.py`)
přepsané z „zastupitelů a radních" na „zastupitelů, radních a členů
výborů zastupitelstva".

**Tabulka zúžena na dva sloupce (týž den, zadal uživatel.)** Mandát
(dřív vlastní sloupec „X / Y / Z") a Poznámka zmizely jako samostatné
sloupce — zůstávají Jméno a Docházka:

- Docházka teď pod procentem nese menším písmem „přítomen X z Y"
  (`X = mandat − nebyl`, `Y = mandat`) — `Z` (celkový počet jednání
  v období) zůstává jen ve větě nad tabulkou, teď navíc tučně
  (`<strong>${blok.jednani}</strong>`).
  Dřívější řádek se z Mandátu nikam nekopíroval, jen se přesunul.
- Poznámka (chyběl při zahájení/dorazil později/odešel dřív + volný
  text) se přesunula do buňky se jménem, pod avatar a odkaz — `tabulka()`
  ji teď připojuje rovnou za `personCellHtml()` do stejné `<td>`.
- Položka „Přítomen: N" v poznámce zmizela — duplikovala nové „X z Y"
  u Docházky. `poznamkaHtml(r)` ztratila parametr `pritomen`, číslo se
  teď počítá jen jednou v `tabulka()` a jde přímo do řádku Docházky.
- `colspan` rozbaleného řádku vizitky změněn ze 4 na 2.
- CSS (`assets/styles.css`): `td:last-child` pravidlo (mělo cílit na
  Poznámku, po přesunu by sedělo na Docházku) nahrazeno stylem přímo na
  `.absence-poznamka-text`/`.absence-poznamka-list`; nové
  `.absence-mandat` pro řádek „X z Y" pod procentem; zrušen
  `white-space:nowrap` na prvním sloupci (teď nese víceřádkovou
  poznámku, ne jen krátké jméno).
- Metodika („Jak se to počítá") a poznámka o malém vzorku u výborů
  přepsané na novou podobu sloupců.

**Aktuální podoba stránky (29. 9. 2026, konec dne)** — starší odstavce
výše jsou chronologický záznam úprav, tohle je stav, který platí:

- Podzáložky: Rada, Zastupitelstvo, Finanční výbor, Kontrolní výbor.
  Záložka „Jak se to počítá" zrušena; metodika (Odkud data jsou, Co čísla
  znamenají, Jmenovatel je mandát, Co do čísel nespadá) je jeden
  sdílený blok pod tabulkami (`#absence-metodika`), sbalený za tlačítkem
  `.toggle-details` („Více informací (rozbalit)" — popisek nastavuje
  `assets/common.js`).
- Tabulka má dva sloupce v pořadí **Docházka, Jméno**: Docházka =
  procento + „Přítomen X z Y" (`X = mandat − nebyl`, `Y = mandat`, rod
  přes `pcGendered`), Jméno = avatar + odkaz na vizitku + poznámka
  (chyběl při zahájení/dorazil později/odešel dřív + volný text z
  `POZNAMKY`). Řazeno od nejmenší docházky. Celkový počet jednání v
  období je jen ve větě nad tabulkou, tučně.

## Pořadí v poli `meetings` (opraveno 28. 9. 2026)

`pecky-jednani.json` → `meetings` musí být seřazené sestupně podle `date`
(nejnovější/nejbližší budoucí první) — `content/jednani.html` pole za
běhu nijak nepřetřiďuje, zobrazuje ho přesně v pořadí ze souboru (žádné
`.sort()` na `data.meetings` nikde v kódu). Nový záznam patří na místo
odpovídající jeho datu, ne na konec pole.

**Zjištěno 28. 9. 2026:** Zastupitelstvo 7/2026 (7. 10. 2026) — rada mu
usnesením RM 34/2026 (bod 16) určila termín, program a místo konání, ještě
předtím, než web usneseni.cz cokoli o tomto jednání zveřejnil (žádná
Pozvánka, žádné UUID — proto `"uuid": null` a prázdné `links`). Záznam byl
i tak správně přidán do `pecky-jednani.json`, ale `.append()`-em na konec
pole, tedy za nejstarší jednání z roku 2021 — na webu se tak fakticky
ztratil (musel by se scrollovat úplně dolů pod celý archiv, aby ho někdo
našel), přestože podle `jIsFutureMeeting()` měl být nahoře se štítkem
„plánováno". Souběžně nesouhlasil i `meta.meetings_count` (290 místo
skutečných 291 záznamů v poli) — uživatel si všiml až toho, že jednání
v tabulce vůbec nevidí, a dotázal se. Oprava: záznam přesunut na index 0,
`meta.meetings_count` opraveno na 291. Do
[automation-kontrola-usneseni-cz.md](automation-kontrola-usneseni-cz.md)
→ krok 5 doplněno pravidlo pro vkládání nových záznamů i pro
synchronizaci `meta` počtů, ať se stejná chyba neopakuje.

## Zvýraznění budoucích jednání (`jIsFutureMeeting()`)

Doplněno 21. 8. 2026 — jednání s datem po dnešním dni (naplánovaná, zatím
bez zápisu) dostanou ve výpisu štítek „plánováno" a jemně zvýrazněné
pozadí sbaleného řádku (`.meeting-row--future`). Porovnání je čistě podle
`m.date` vs. aktuální datum v prohlížeči (`jIsFutureMeeting()`), žádné
zvláštní pole v datech není potřeba.

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

## Permalinky na jednotlivá jednání (`jSlugForMeeting()`)

Doplněno 31. 8. 2026 — každý řádek v tabulce má trvalý odkaz tvaru
`#rada-YYYY-MM-DD` / `#zastupitelstvo-YYYY-MM-DD`; obecné `#rada` /
`#zastupitelstvo` filtrují celou tabulku jen na daný typ jednání. Slug se
počítá za běhu z `type` + `date` (`content/jednani.html`, funkce
`jSlugForMeeting()`) — **není to pole uložené v JSON ani krok, který by bylo
potřeba dělat ručně.** Jakmile přibude nové jednání do `pecky-jednani.json`
(viz `automation-kontrola-usneseni-cz.md`, krok 5) a web se přegeneruje
(`python3 scripts/build.py`), permalink pro něj funguje sám od sebe — u
kolizí data (dvě jednání týž den) je typ součástí slugu, takže nekoliduje.

Odkazem je přímo název jednání (datum + „Jednání rady/zastupitelstva č. N")
v hlavičce řádku — žádný zvláštní „#" vedle textu. Rozkliknutí řádku
(kliknutím na název i kdekoli jinde v hlavičce) vždy nastaví URL na
permalink daného jednání přes `history.replaceState`, jako by uživatel
proklikl přímo tento odkaz, včetně scrollu na řádek — ale bez těžšího
resetu filtrů, protože řádek je už viditelný na místě (`jToggleRow()`).
Ctrl/Cmd/Shift/prostřední klik na název se nechává prohlížeči beze změny
(otevření v nové kartě). Teprve příchod zvenčí (přímý odkaz, historie
zpět/vpřed) spustí těžší `jGotoMeetingBySlug()` — reset filtrů, dohledání
řádku a scroll.

**V seznamu smí být rozbalený vždy jen jeden řádek** — `jToggleRow()` před
rozbalením nového řádku sbalí všechny ostatní (`jCollapseRow()`). Netýká se
`jGotoMeetingBySlug()`: ten pracuje na čerstvě vykresleném seznamu
(`jRunSearch()` znovu sestaví celé HTML), kde je jinak rozbalených řádků
vždy nula.

## Fotky u avatarů účastníků (od 31. 8. 2026)

Řádek s avatary účastníků (viz „Jmenovité obsazení" výše) teď u lidí, kde
existuje fotka, zobrazuje ji místo barevného kroužku s iniciálami — stejný
princip jako u tabulek volebních uskupení a v sekci Lidé. Zdroj fotek je
`lide/people.json` (`photos[0].url`, nejnovější fotka dané osoby, viz
`lide/SPEC.md` §3.7) — `content/jednani.html` si ho při načtení natáhne
navíc k `pecky-jednani.json`. Spárování jména z prezence jednání
(`attendance.present_names`/`absent_names`, prostý text z usneseni.cz) se
záznamem v `people.json` je fuzzy: `jNameKey()` (assets/helpers.js) odstraní
tituly a diakritiku a porovná jen normalizované „jméno příjmení" — jména
napříč zdroji totiž titul za jménem zapisují nekonzistentně (s/bez čárky).
U koho se fotka nedohledá (typicky zastupitelé z volebního období
2018–2022, které `people.json` nepokrývá — viz jeho `meta.note`), zůstává
beze změny barevný iniciálový avatar.

## Rozbalovací body programu (od 31. 8. 2026)

Každý bod programu, který má co ukázat navíc (důvodovou zprávu nebo text
usnesení), je teď rozbalovací stejným způsobem jako celý řádek jednání —
klik kdekoli v hlavičce bodu (ne jen na text jako dřív), `+`/`−` indikátor
vpravo (`.agenda-toggle`, stejný vizuální jazyk jako `.meeting-toggle` u
řádku jednání). Rozbaluje se jen obsah samotné důvodové zprávy a plný text
usnesení — čísla usnesení s výsledkem (přijato/zamítnuto apod.) zůstávají
vidět vždy, bez rozbalení, stejně jako dřív. Na rozdíl od řádků jednání
(kde je vždy rozbalený nejvýš jeden) se body programu rozbalují nezávisle
na sobě — u jednání s víc body je běžné chtít porovnat text dvou z nich
najednou. Zdrojová funkce: `jRenderAgendaList`/click handler v
`content/jednani.html`.

## Zamítnuté návrhy usnesení (`agenda[].rejected_vote`, od 25. 9. 2026)

`m.resolutions` (a z něj `content/jednani.html` odvozený `a._res`) obsahuje
jen **přijatá** usnesení, tak jak je vede stránka `/usnesení/` na
usneseni.cz — návrh, který hlasování neprošlo, tam vůbec nevznikne (nemá
`UR-`/`UZ-` číslo, žádnou vlastní URL). Zápis (`/zapis/`) ale hlasování
o takovém návrhu pořád zaznamenává, vč. počtu hlasů — bez zvláštního pole
by proto bod, o kterém se **reálně hlasovalo a byl zamítnut**, vypadal
na webu stejně jako čistě informativní bod bez hlasování (např. „Aktuální
informace vedení města").

Pole `agenda[].rejected_vote` (`{"text", "pro", "proti", "zdrzel"}`) tohle
rozlišuje: `text` je verbatim navržené znění usnesení z zápisu (ne
vymyšlené - proto ne "usnesení", ale "návrh usnesení", protože k přijetí
nedošlo), `pro`/`proti`/`zdrzel` je výsledek hlasování. Zobrazí se jako
badge „Zamítnuto" (stejná vizuální třída `res-outcome zamitnuto` jako
u zamítnutých/neschválených přijatých usnesení) + hlasování na sbaleném
řádku bodu, s rozbalovacím "i" tlačítkem na plný navržený text — stejný
vzor jako `jResInfoIcon`/`jResInfoText` u běžných usnesení, jen bez čísla
a odkazu (žádné neexistuje). Zdrojová funkce: `jRenderRejectedVote`
v `content/jednani.html`.

**Zatím jen u jednoho bodu** — bod 14 „Souhlas s krátkodobým užitím části
pozemku parc. č. 1018 (Park pod vodojemem)" u Rady 34/2026 (21. 9. 2026,
zamítnuto 1 pro : 4 proti : 2 zdržel se). Historický přepočet zbytku
archivu (ve velkém `archive-2026-08-04.json` je zamítnutých hlasování
napříč 2021–2026 evidováno 81, žádné z nich zatím v `pecky-jednani.json`
není) je vědomě odložený na později — viz úkol níže.

**Pro budoucí automatizaci:** u nového jednání sledovat v zápisu i výsledek
„Návrh nebyl přijat" (ne jen přijatá usnesení ze stránky `/usnesení/`) a
takový bod doplnit stejně jako výše — `text` (navržené znění), `pro`,
`proti`, `zdrzel`. Bod bez hlasování vůbec (čistě informativní, „bere na
vědomí" bez explicitního usnesení) `rejected_vote` nedostává — jen bod,
o kterém se reálně hlasovalo a neprošel.

**Otevřený úkol:** promítnout `rejected_vote` zpětně i do starších jednání
z velkého `archive-2026-08-04.json` (81 nalezených případů) — vědomě
odložené, viz zadání uživatele 25. 9. 2026.

## Upozornění na chybějící zápis (od 4. 9. 2026)

Sbalený řádek jednání, které už proběhlo (datum v minulosti, ne dnes),
ale zatím k němu není zápis (`links.minutes` chybí — typicky pár
nejnovějších jednání, viz „Jednání jen s Pozvánkou" výše), zobrazí na
pravé straně řádku „Proběhlo před N dny, zápis zatím není k dispozici"
místo prázdného místa (+ odkaz na video, pokud existuje). Původně to
platilo jen pro Zastupitelstvo (`pastNoMinutes` v `jRenderMeetingList`,
`content/jednani.html`) — od 4. 9. 2026 obecně pro libovolný typ
jednání, protože avatary/počet přítomných u Rady jsou odvozené ze
stejného zápisu a bez něj jsou taky prázdné.

Od 18. 9. 2026 je text „zápis zatím není k dispozici" barevně zvýrazněný
(`.no-minutes-warning`, `var(--burgundy)`) — zbytek řádku („Proběhlo před
N dny…", odkaz na video) zůstává neutrální.

## Pozvánka PDF jen u nadcházejících jednání (od 18. 9. 2026)

Odkaz „Pozvánka PDF ↗" v rozbaleném řádku jednání (`m.links.invitation`)
se od 18. 9. 2026 zobrazuje jen u jednání, které ještě neproběhlo
(naplánované nebo dnešní — `future || isToday` v `jRenderMeetingList`,
`content/jednani.html`). U proběhlého jednání ztrácí Pozvánka smysl (zápis
a usnesení ji nahradí) a odkaz mizí, i když v datech `links.invitation`
zůstává (nemaže se, jen se nevykresluje).

## Živé vysílání budoucího jednání zastupitelstva (`links.livestream`, od 18. 9. 2026)

Rada nemá video vůbec (viz „Nesoulad číslování videí" níže), ale
Zastupitelstvo bývá na kanálu @mestopecky přenášeno živě. Pro **naplánované**
jednání zastupitelstva (`jIsFutureMeeting()` = true) je potřeba při každém
běhu kontroly zjistit, jestli už na playlistu „Zasedání ZM"
(`https://www.youtube.com/playlist?list=PL1KVT2dbyIKSTFRv7tfDqrfk5gkTSnoyu`)
existuje záznam pro nadcházející/plánovaný přenos (YouTube ho typicky
zobrazí jako „Premiéra"/naplánované video ještě před začátkem).

- **Pokud odkaz existuje**, doplnit ho do `pecky-jednani.json` jako
  `links.livestream` (stejný tvar URL jako `links.youtube`). Frontend pak
  na sbaleném řádku zobrazí „📺 Živé vysílání od HH:MM" (čas je z pole
  `time`, doplněného už dřív z Pozvánky — viz automation-kontrola-usneseni-cz.md
  krok 4) jako odkaz, a v rozbaleném řádku funguje tlačítko „Video ↗"
  stejně jako u proběhlého jednání s `links.youtube`.
- **Pokud odkaz zatím neexistuje**, nic nevymýšlet a nic nezobrazovat —
  žádný generický text typu „přenos bude na Youtube" (vymyšlené tvrzení
  bez ověření, viz konvence webu o zákazu vymyšlených dat). Zkusit znovu
  při příštím běhu.
- Po jednání se `links.livestream` stává zbytečným — stejné video pak
  najde a do `links.youtube` doplní běžný krok 6 kontroly (spárování podle
  data v popisku). `links.livestream` u proběhlého jednání se dá smazat,
  ale není to nutné. Od 8. 10. 2026 frontend `links.livestream` po jednání
  používá jako záložní odkaz na video (když chybí `links.youtube`), takže
  video je vidět i před doplněním záznamu a před zveřejněním zápisu.
- Zdrojová logika: `livestreamHtml`/`videoUrl` v `jRenderMeetingList`,
  `content/jednani.html`.

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

### Zápisy výborů ZM (`Data/{datum}-financni-vybor/`, `…-kontrolni-vybor/`)

Finanční a kontrolní výbor nejsou na `usneseni.cz` — zápisy z jejich
jednání zveřejňuje jen pecky.cz (Zastupitelstvo → [Výbory ZM](https://pecky.cz/default/default/21133_vybory-zm)
→ Finanční / Kontrolní výbor → Zápisy {rok}). Staženo jednorázově
29. 9. 2026: `Data/{datum}-financni-vybor/zapis.pdf` (31 zápisů,
11/2018–6/2026) a `Data/{datum}-kontrolni-vybor/zapis.pdf` (14 zápisů,
3/2020–6/2026; stránka „Zápisy 2022" KV je na webu prázdná). Přípona
složky je vždy, i bez kolize data — jde o jiný orgán než Rada/ZM.

- Soubor se jmenuje `zapis.pdf`, ne `podepsany-zapis.pdf` — web ho tak
  neoznačuje a podpis nebyl ověřován.
- Datum složky je datum jednání. Většinou odpovídá názvu souboru na webu
  (formáty se liší: `FV_10.5.2022`, `KV-18.2.2026`, `17_6_2026`), ale dva
  soubory jsou na pecky.cz pojmenované chybně a složky jsou přejmenované
  podle data v zápisu: `KV_23.09.2023` → `2023-09-20-kontrolni-vybor`,
  `KV_16.11.2024` → `2024-11-06-kontrolni-vybor` (obojí ověřeno proti skenu).
- 31 PDF má textovou vrstvu (`pdftotext`), 14 jsou skeny bez textu — čtou
  se přes OCR: `pdftoppm -r 300 -png` + `tesseract -l ces`. OCR plete
  hlavně diakritiku ve jménech (Důrr, Kůúty) a odrážky — jména se vždy
  normalizují podle Lidí, sporná místa (hlasování) ověřit proti obrázku.
- Na rozdíl od `usneseni.cz` pecky.cz Cloudflare neblokuje — stačí přímý
  `curl` na `/files/pecky/gallery/…`. Všech 45 souborů má různý MD5.
- Tři zápisy, které na pecky.cz chybí, stažené 29. 9. 2026 ze starého webu
  (pecky.as4u.cz → Výbory a komise → Zápisy finančního/kontrolního výboru):
  `2023-11-23-financni-vybor`, `2025-05-21-kontrolni-vybor`,
  `2025-11-19-kontrolni-vybor`. Starý web má zbylé zápisy taky (se správným
  datem v popisku odkazu), ale od jara 2026 se neaktualizuje.
- Obsah je vytěžený do `vybory.json` (všech 48 zápisů), viz
  „Jednání výborů ZM (`vybory.json`)“ níže.

### Jednání výborů ZM (`vybory.json`)

Samostatný soubor vedle `pecky-jednani.json` — ten se přírůstkově plní
z usneseni.cz a výbory by se v něm míchaly se scraperem. `content/jednani.html`
načte oba a spojí je do jednoho chronologického seznamu; filtr
„Finanční výbor“ / „Kontrolní výbor“, trvalé odkazy `#financni-vybor-{datum}`
a `#kontrolni-vybor-{datum}`. Stav 29. 9. 2026: 48 jednání (32 FV, 16 KV)
a 75 usnesení — všechny zápisy zveřejněné na pecky.cz (FV od 11/2018,
KV od 3/2020) a tři, které má jen starý web pecky.as4u.cz (FV 23. 11. 2023,
KV 21. 5. 2025, KV 19. 11. 2025; `links.minutes` u nich míří na as4u). Složení výborů 2018–2022 je v Lidech (viz `lide/README.md`
→ „Finanční a kontrolní výbor ZM“), aby šly vykreslit avatary přítomných.

Záznam má stejná pole jako jednání Rady/ZM, s těmito rozdíly:

- `id` (`financni-vybor-2025-11-11`) místo `uuid` (to je `null`),
  `number: null` — výbory jednání nečíslují.
- `time`/`time_end` a z nich `duration_seconds`, jen když zápis uvádí obojí.
  `venue` jen když ho uvádí zápis (nedopočítávat z pozvánek v jiných zápisech).
- `links.minutes` = PDF na pecky.cz (lokální `Data/` je v `.gitignore`),
  `links.source_page` = stránka „Zápisy {rok}“.
- `attendance.present_names` / `absent_names[{name, note}]` s plnými jmény
  a tituly podle Lidí, i když zápis píše jen příjmení nebo iniciálu.
  `note`: `omluven(a)`, `neomluven(a)`, nebo `nepřítomen/nepřítomna, zápis
  důvod neuvádí`, když zápis chybějícího člena vůbec nezmiňuje.
  `total` = počet členů výboru v tu chvíli (KV 6. 11. 2024 měl 6).
  Navíc `arrived_late[{name, time}]`, `left_early[{name, time}]` (na
  stránce viditelně v detailu, bez důvodu — ten je v PDF) a
  `guests[{name, note}]` (funkce hosta).
- `agenda[{n, t}]` doslovně z programu zápisu, bez délek. Zápis bez
  programu → `[]` („Zápis neuvádí program jednání“).
- `resolutions[{n, text, pro, proti, zdrzel, adopted, vote_names?, note?}]`
  — text doslovně, `n` jen když ho zápis dává (`1`, `KV-1/2026`).
  **Patří sem i neschválené návrhy** (`adopted: false`, štítek
  „Neschváleno“), protože výbor o nich formálně hlasoval. `vote_names`
  jen když zápis jména uvádí; rozpory v zápisu jdou do `note`, neopravují se.
- `chair`, `recorded_by`, `attachments[]` (přílohy podle zápisu),
  `extraction{method: pdftotext|ocr, checked, note}` — poznámka ke
  čtení zápisu (překlepy, nejasnosti, odkazy na nezveřejněná jednání).

Zápisy odkazují na jednání, jejichž zápis není zveřejněný ani na pecky.cz,
ani na starém webu: FV 12. jednání (12/2019–2/2020), ohlášené FV 18. 3. 2020,
KV před 5. 3. 2020 a ohlášené KV 23. 3. 2020, ohlášené KV 6. 10. 2021
a KV 5. 9. 2023 — přiznáno v calloutu na stránce (příklady). FV 23. 11. 2023
a KV 19. 11. 2025 se našly na starém webu (doplněno 29. 9. 2026).

**Zvláštnosti zápisů 2018–2022** (FV za předsedy Vodičky, KV za předsedy
Palusky): FV v zápisech číslovalo jednání („3. jednání“ … „20. jednání“,
číslo je jen v `extraction.note`, `number` zůstává `null`), chodilo
kontrolovat jednotlivé příspěvkové organizace a o dílčích doporučeních
hlasovalo průběžně — každé hlasované doporučení je samostatný záznam
v `resolutions`. Většina usnesení ale výsledek hlasování neuvádí →
`pro/proti/zdrzel: null`, `adopted: null` (štítek jen podle slovesa,
u hlasování „hlasování zápis neuvádí“). Čas a místo často chybí a jsou
doplněné z ohlášení v předchozím zápisu („Příští zasedání: …“) — vždy
s poznámkou v `extraction.note`. Zápis 22. 11. 2018 neuvádí účast
(`present: null`), 28. 11. 2018 jen hlasující. Zápisy KV 2021 Lenku
Krúpovou vůbec nezmiňují — není jisté, jestli byla ještě členkou, proto
v nich není ani mezi nepřítomnými (přítomní + nepřítomní tu dávají 6 ze 7).

**Pravidlo pro účast:** jinak zápis v datech vždy vede všechny členy
výboru — přítomné i chybějící (s poznámkou „zápis důvod neuvádí“, když
chybějícího nezmiňuje). Na tom stojí počty účasti u osob v Lidech
(`content/lide.html` → `lAttachVyborAttendance`): kdo u jednání není
uveden vůbec, tehdy ve výboru nebyl a jednání se mu nezapočítá.

### Kontrola nových zápisů výborů (týdně, skill `pecky-online-vybory-check`)

Výbory nejsou na usneseni.cz, takže je kontrola Jednání (scraper, Chrome)
nepokrývá — běží zvlášť, ve stejném týdenním běhu. Zdroj je pecky.cz,
funguje i přímý `curl`, žádný prohlížeč netřeba.

1. `python3 jednani/scripts/vybory-check.py` — vypíše složení obou výborů
   podle webu a každý zápis, jehož URL ještě není v `vybory.json`
   (`links.minutes`; u starého webu pecky.as4u.cz podle výboru + data
   z popisku odkazu), stáhne do `Data/{datum}-{financni|kontrolni}-vybor/zapis.pdf`.
   Datum je jen z názvu souboru — **vždy ověřit proti textu zápisu**
   (dvakrát už byl chybný), případně složku přejmenovat.
2. **Složení:** liší-li se výpis od Lidí (aktuální vazby „člen/předseda
   finančního|kontrolního výboru“), dohledat usnesení ZM o volbě/odvolání
   a upravit `lide/affiliations.json` podle `lide/README.md` → „Finanční
   a kontrolní výbor ZM“. Samotný výpis na webu stačí jen jako potvrzení,
   datum změny se bere z usnesení. Web píše „Metalák“ — to je známý
   překlep, ne změna.
3. **Vytěžení** nového zápisu do `vybory.json` podle struktury v „Jednání
   výborů ZM (`vybory.json`)“ výše: text přes `pdftotext -layout`, sken
   přes `pdftoppm -r 300 -png` + `tesseract -l ces`, sporná místa (jména,
   hlasování) proti obrázku stránky. Všichni členové výboru musí být
   v `present_names` nebo `absent_names` (kontrola: `present +
   len(absent_names) == total`) — na tom stojí počty účasti v Lidech.
   Přepočítat `meta.meetings_count` / `resolutions_count`.
4. **Promítnutí:** týká-li se zápis tělocvičny (financování, úvěr —
   `UZ-24-4/26` ukládá FV podávat zprávu o úvěru aspoň jednou ročně),
   nový řádek v Tělocvičně → „Financování a finanční výbor“; týká-li se
   konkrétní parcely z tabulek Pozemků, callout „Kontrolní výbor
   k pozemkům“ v `content/pozemky.html` (mimo generované tabulky).
5. `python3 kalendar/scripts/update-kalendar.py` a `python3 scripts/build.py`.
6. Do shrnutí běhu vlastní řádek „Jednání — výbory“ (i „zkontrolováno,
   beze změny“); při změně přepsat řádek Jednání v `README.md` → „Stav
   sekcí“.

### Zápisy komisí RM (`Data/{datum}-sportovni-komise/`, `…-kulturni-komise/`, `…-stavebni-komise/`, `…-pracovni-skupina/`)

Komise rady města zveřejňuje jen pecky.cz (Rada města → [Komise RM](https://pecky.cz/default/default/21179_komise-rm)
→ komise → „2018-2022“ / „2022-2026“); stejně jako u výborů stačí přímý `curl`.
Rozsah: **obě volební období** (zápisy před 2018 web nemá). Staženo
30. 9. 2026 (49 jednání): 2022–2026 — sportovní komise 7 (4/2023–2/2026), kulturní
komise + pracovní skupina pro oslavy 100 let povýšení Peček 9, stavebně-dopravní
komise 4 (1/2024–9/2025); 2018–2022 — sportovní komise 8 (12/2018–6/2022), kulturní
komise 10 (12/2018–8/2022), stavební komise 10 (12/2018–3/2022), Sbor pro občanské
záležitosti 1 (13. 12. 2018).

- **Sociální komise zápisy nezveřejňuje.** Web výslovně uvádí, že
  anonymizované zápisy kvůli ochraně osobních údajů zveřejňovány nebudou
  a neanonymizované jsou k nahlédnutí na úřadě. **Sbor pro občanské
  záležitosti** má zveřejněný jediný zápis (13. 12. 2018, stránka komise
  ho drží přímo, bez podstránky po letech). Na stránce Jednání je to
  přiznané v calloutu; skript hlídá obojí (kdyby zápis přibyl, ohlásí ho).
- **Volební období 2018–2022:** komise ve zcela jiném složení; společná
  jednání sportovní a stavební komise (23. 5. a 27. 6. 2019) mají na
  pecky.cz zápis u každého orgánu zvlášť (různá čísla jednání, téměř totožný
  obsah) — v datech jsou jednou pod typem „Sportovní komise“ s `bodies`
  obou orgánů a druhý zápis je v `links.minutes_more`. Zápis stavební komise
  z 27. 11. 2019 je na webu vystavený dvakrát (stejný soubor). Původní „školská
  a kulturní komise“ (13. 12. 2018) byla po prvním jednání rozdělena a je
  vedená jako Kulturní komise. Soubor „informace-kulturni-komise-1.pdf“ není
  zápis (vyjádření předsedkyně z doby covidu) a vytěžen není. U 4 kulturních
  zápisů z let 2019–2020 je zveřejněn jen program jednání (přiznáno v
  `extraction.note` a na stránce).
- **Společná jednání kulturní komise a pracovní skupiny jsou na pecky.cz
  dvakrát** — pět zápisů (9. 1., 20. 3., 22. 5., 28. 5. 2024, 2. 9. 2025) je
  vystavených jako dva různé soubory (jiný MD5, stejný obsah) na stránce
  kulturní komise a pracovní skupiny. V datech jsou jednou; složka se jmenuje
  podle `type` (`kulturni-komise`). Zápisy 19. 9. 2024 a 30. 1. 2025 jsou
  jen u pracovní skupiny (19. 9. 2024 je ale ve skutečnosti „schůzka kulturní
  komise a komise pro oslavy“, proto má typ Kulturní komise a `bodies`
  obou orgánů; 30. 1. 2025 je čistě pracovní skupina).
- 2022–2026: zápisy z 18. 1. 2023 a 20. 3. 2024 jsou skeny (OCR: `pdftoppm -r 300 -png`
  + `tesseract -l ces`), zbylých 18 má textovou vrstvu. 2018–2022: 10 zápisů je
  skenů (kulturní 7, sportovní 3, stavební žádný), sportovní zápisy
  z let 2018–2019 mají vadnou textovou vrstvu z OCR (rozházená písmena). OCR plete
  diakritiku ve jménech (Můller) — jména se normalizují podle Lidí.

### Jednání komisí RM (`komise.json`)

Samostatný soubor vedle `vybory.json`, načítaný stejně (`content/jednani.html`
soubory spojí do jednoho chronologického seznamu; filtr **Komise** ukazuje
všech pět typů, konkrétní jednání mají trvalý odkaz
`#sportovni-komise-2024-02-06`, `#kulturni-komise-…`, `#stavebni-komise-…`,
`#pracovni-skupina-…`, `#sbor-…`). Stav 30. 9. 2026: 49 jednání, 102 usnesení.

Záznam má stejná pole jako ve `vybory.json` (viz výše) a navíc:

- `group: "komise"` — podle něj `jIsKomise()` odliší komise od výborů
  (`jIsVybor()` platí pro obojí, protože jednání mají shodné vykreslení).
- `type` — `Sportovní komise`, `Kulturní komise`, `Stavebně-dopravní komise`
  (do 2022 „stavební komise“), `Pracovní skupina pro oslavy 100 let`,
  `Sbor pro občanské záležitosti`.
- `bodies` — orgány, kterých se jednání týká (společné jednání má dva:
  `["Kulturní komise", "Pracovní skupina pro oslavy 100 let"]`); podle toho
  Lidé párují docházku s vazbou člena. `links.minutes_more[]` = další zápis
  téhož jednání (`{label, url}`), když ho druhý orgán vede zvlášť.
- `summary[]` — krátké věcné shrnutí z textu zápisu (komise často nehlasují,
  bez shrnutí by u jednání bez usnesení nebylo vidět nic než program).
  Jen to, co v zápisu stojí, žádné vlastní závěry.
- `number` je vždy `null`: sportovní komise sice zápisy číslují („5. jednání“),
  ale po ročních řadách (2024: 1., 2., …, 5.), takže číslo nejde spojit se
  zápisy dalších let; zůstává jen v `extraction.note`.

**Rozdíly proti výborům:**

- **Účast:** `present_names` + `absent_names` jsou jen lidé, které zápis
  jmenuje. Výjimka: zápis sportovní komise uvádí „Celkem 12 členů komise“
  — člen, kterého zápis nezmiňuje (Šestáková 10. 2. 2026), je mezi
  nepřítomnými s poznámkou „zápis důvod neuvádí“. U stavebně-dopravní a kulturní
  komise se celkový počet členů v zápisech nepíše a `total` = jmenovitě
  uvedení. V Lidech proto u komisí stojí „jen ta, kde je zápis jmenuje“
  (`L_ATTENDANCE_ROLES` v `content/lide.html`).
- **Usnesení:** komise většinou nehlasují o číslovaných usneseních.
  Do `resolutions` patří to, co zápis označuje jako „Usnesení“ nebo
  „Komise doporučuje“, a hlasované doporučení (u sportovní komise každá
  dotace oddílu zvlášť; text sestavený z tabulky a hlasování — poznamenáno
  v `extraction.note`). Závěrečná formule „všechny body navrženého
  programu byly projednány a schváleny“ **není** usnesení a nezapisuje se.
  „Všichni pro“ = počet přítomných (poznámka v `extraction.note`); doporučení
  bez hlasování mají `pro/proti/zdrzel: null`, `adopted: null`.
- U dotací oddílům jde o **doporučení pro RM** — schvaluje je až rada.
- Sportovní komise 24. 10. 2024 uvádí 9 přítomných, ale jmenuje 8
  (Krejčí chybí mezi přítomnými i omluvenými) — počet 9 je ze zápisu,
  jméno se nedopočítává.

**Rozpory se složením v Lidech (zjištěno 30. 9. 2026, neopraveno):**

- Stavebně-dopravní komise: Lubomír Metelák je na pecky.cz mezi členy, ale
  v žádném zápisu 2024–2025 se nevyskytuje; Tomáš Vodička je v Lidech člen,
  na pecky.cz už není a v zápisech taky ne (odchod nedatován). Jiří
  Katrnoška je v Lidech členem od 14. 11. 2022, v zápisech je poprvé
  5. 6. 2024 (17. 1. 2024 ani omluven není).
- Sportovní komise: web uvádí 11 členů, bez Ladislavy Šátkové ml.; zápisy
  2023–2026 ji ale vedou jako členku a Lidé také.

### Kontrola nových zápisů komisí (týdně, skill `pecky-online-komise-check`)

Běží ve stejném týdenním běhu jako kontrola výborů; zdroj pecky.cz, stačí `curl`.

1. `python3 jednani/scripts/komise-check.py` — vypíše složení všech pěti komisí
   podle webu a každý zápis (2018–2026), který ještě není v `komise.json`
   (porovnává komisi + datum z názvu souboru, ne URL — kvůli dvojím
   souborům u společných jednání); stáhne do
   `Data/{datum}-{sportovni-komise|kulturni-komise|stavebni-komise}/zapis.pdf`.
   Datum je jen z názvu souboru — **vždy ověřit proti textu zápisu**.
   Zápis pracovní skupiny přejmenovat složku na `…-pracovni-skupina`.
2. **Složení:** liší-li se výpis od Lidí (vazby `role_type: "komise"`),
   dohledat usnesení RM o jmenování/odvolání (viz `lide/README.md` →
   „Komise RM“) a upravit `lide/affiliations.json`. Rozpory výše jsou známé.
3. **Vytěžení** do `komise.json` podle struktury výše: text přes
   `pdftotext -layout`, sken přes `pdftoppm -r 300 -png` + `tesseract -l ces`.
   Jména normalizovat podle `lide/people.json`, hosty nechat tak, jak je zápis
   uvádí. Přepočítat `meta.meetings_count` / `resolutions_count`.
   Ověřit `present ≤ len(present_names) + len(absent_names)`.
4. **Promítnutí:** týká-li se zápis tělocvičny (starosta či předseda komise
   informuje o dostavbě ZŠ), nový řádek v Tělocvičně → „Tělocvična v komisích
   rady města“ (`content/telocvicna.html`); týká-li se konkrétní parcely,
   sekce Pozemky (viz `automation-katastr-parcely.md`).
5. **Kalendář:** `python3 kalendar/scripts/update-kalendar.py` — nová jednání komisí (i pracovní skupiny
   a Sboru) přidá jako události kategorie `vybor` a hned je synchronizuje do Google Kalendáře (generátor
   sync spouští sám, viz `kalendar/README.md`). Pak `python3 scripts/build.py`. Domů (`_dash_jednani`)
   komise zatím nezahrnuje.
6. Do shrnutí běhu vlastní řádek „Jednání — komise“ (i „zkontrolováno,
   beze změny“); při změně přepsat řádek Jednání v `README.md` → „Stav sekcí“.

### Školská rada ZŠ Pečky (`skolska-rada.json`, `Data/{datum}-skolska-rada/`)

Školská rada je orgán školy (zřizovatel město), ne komise rady města, ale v datech
i na stránce se vede s komisemi (`group: "komise"`, filtr **Komise**, `type:
"Školská rada"`, trvalé odkazy `#skolska-rada-{datum}`). Zdroj je web školy —
[Zápisy a dokumenty ŠR](https://www.zspecky.cz/skola/skolska-rada/zapisy-a-dokumenty-sr/),
ne pecky.cz. Stav 30. 9. 2026: **34 jednání** (7. 9. 2009 – 28. 8. 2026), 61 usnesení.
Soubory jsou stažené do `Data/{datum}-skolska-rada/` (zapis.pdf nebo zapis-N.jpg + `zdroj.txt`
s odkazem na stránku školy; `Data/` je v `.gitignore`).

- **Struktura webu školy:** každé jednání je vlastní podstránka s přílohou (většinou
  PDF, u starších zápisů obrázky JPG); dva záznamy drží víc jednání v jednom souboru —
  „Zápis 2009-10“ (PDF se zápisy 7. 9. a 13. 10. 2009; soubor je kvůli tomu ve dvou složkách)
  a „Zápisy 2011-12“ (6. 10. 2011 a 24. 4. 2012). Stránka „zápis z jednání školské rady“
  (17. 9. 2013) nemá přílohu a „zápis z jednání rady školy“ (10. 10. 2013) je jen titulní
  strana téhož zápisu jako „Zápis z jednání ŠR ze dne 10. 10. 2013“ (jeden záznam,
  druhá stránka v `links.minutes_more`). Nejsou tu volební řád, výroční zprávy ani výsledky
  voleb — jen zápisy z jednání.
- **Kvalita zdroje:** téměř všechny zápisy před 2023 jsou skeny (OCR, u 2009–2016 nízké
  rozlišení ~500×770 px, ověřováno proti obrázku); od 2023 mají textovou vrstvu.
  Zápis z 31. 8. 2023 je na hlavičkovém papíru Města Pečky („VÝBORY – KOMISE“).
- **Jména členů:** zápisy do 2014 a 2019–2022 uvádějí členy jen příjmením („p. Katrnoška, pí. Krúpová“,
  „paní Astrová, pan Korouš“). V datech jsou celými jmény podle Lidí tam, kde jde osobu spolehlivě určit
  z jiného zdroje: výsledky voleb rodičů a doplňovacích voleb na webu školy (Procházka, Hovorka, Literová,
  Chárová, Charousová, Minaříková), jmenování rady města v Pečeckých novinách (Katrnoška, Jedlička, Krúpová,
  Homan, Horynová), výčet členů v zápisu 15. 6. 2015 a zápisy od 2023. **Iveta Minaříková (zápisy 2015–2019) je
  dnešní Bc. Iveta Dvořáková** (`dvorakovai`, dřívější příjmení v `former_last_names`), v datech vedená jejím
  dnešním jménem. Neurčeni (zůstávají příjmením): Astrová, Taxová, Korouš (rodiče 2019–2022), Hájková (2014),
  Charouzová/Charousová jako přepis téhož příjmení a „p. Zajíc“ (ředitel) v zápisech do 2022. Kozáková, Píšová
  a Vinohradníková jsou vedeny celým jménem po celou dobu (pedagožky se shodným příjmením v zápisech 2009–2026).
- **Účast a hlasování:** `total` je počet členů rady (9), zápis ho ale zpravidla nepíše.
  U hlasování per rollam (3. 9. 2020, 20. 11. 2020, 24. 11. 2021, 22. 6. 2022) zápis nejmenuje
  přítomné; datum jednání je datum zápisu. Zápis „ze 3. 9. 2020“ jmenuje 7 hlasujících ze 9.
- **Ochrana osobních údajů:** zápis z 7. 11. 2024 obsahuje diskuzi o personální záležitosti
  konkrétního zaměstnance školy (nepravomocně rozhodnutá věc). V datech ani ve shrnutí
  není jméno ani obsah přepsán (`extraction.note`); zůstává jen v původním zápisu, na který
  jednání odkazuje.
- **Lidé:** členové rady mají u vazeb `školské rady ZŠ Pečky` (organizace `zs-pecky`) počítanou
  docházku (`L_ATTENDANCE_ROLES` v `content/lide.html`), a to jen tam, kde se jméno v zápisu shoduje.
  Členství a začátky mandátů (jmenování RM, volby, ustavení rady) jsou popsané v `lide/README.md` →
  „Školská rada ZŠ Pečky — členové 2009–2026“ (30. 9. 2026).
- **Další dokumenty ze stránky ŠR** jsou v `Data/skolska-rada-dokumenty/{stránka}/` (volební řád 2025, doplňovací
  volby 2009, výsledky voleb 2011 a 2014, výroční zprávy 2016/17 a 2017/18, hlasování o VZ 2015/16, volební lístek 2011;
  u každého `zdroj.txt` a `stranka.txt` s textem stránky). Z nich jsou vytěžené jen údaje o volbách a schvalování
  (klíče `election_rules`, `elections`, `other_decisions` v `skolska-rada.json`; stránka je nezobrazuje). U volebních
  výsledků se jmenují jen zvolení členové — kandidáti, kteří zvoleni nebyli, jsou soukromé osoby a jména se
  nepřepisují. Výroční zprávy školy nevytěženy (jde o dokumenty školy, ne rady).

**Kontrola nových zápisů (týdně):** `python3 jednani/scripts/skolska-rada-check.py` —
porovná záznamy se zápisy na webu školy s `skolska-rada.json` (podle data v názvu záznamu),
stáhne nové do `Data/{datum}-skolska-rada/`; vytěžení do `skolska-rada.json` je ruční krok
(struktura jako `komise.json`, viz „Jednání komisí RM“ výše; počty přepočítat v `meta`).
Promítnutí: týká-li se zápis tělocvičny, řádek v Tělocvičně → „Tělocvična v komisích rady
města a ve školské radě“. **Kalendář:** nové jednání školské rady se zapisuje jako událost stejně jako komise
(`python3 kalendar/scripts/update-kalendar.py`, sync do Google se spouští sám). Skript hlídá jen zápisy jednání; ostatní dokumenty ŠR
(výroční zprávy, volební řád) ne.

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

## Jednání jen z bodu programu Rady, ještě bez vlastní Pozvánky (od 28. 9. 2026)

Ještě o krok dřív než „Jednání jen s Pozvánkou" níže: Rada na svém
jednání běžně schvaluje **termín a program příštího zasedání ZM** jako
vlastní bod programu (i s usnesením) — a to o dost dřív, než ZM samo
dostane na `usneseni.cz` vlastní UUID/Pozvánku (ta se zveřejňuje jen
pár dní předem). První případ: **Zastupitelstvo 7/2026 (7. 10. 2026)**,
zapsáno na žádost uživatele 28. 9. 2026 z bodu 16 zápisu **Rady
34/2026 (21. 9. 2026)**, usnesení `UR-309-34/26`: „Rada města schvaluje
termín a program zasedání ZM dne 7.10.2026 od 16.30 hodin v Kulturním
domě, Tř. Jana Švermy čp. 255, Pečky."

Záznam má na rozdíl od „Jednání jen s Pozvánkou" **`uuid: null`**
(žádné zatím neexistuje) a **`links` úplně `null`** včetně
`invitation` (žádná Pozvánka na ZM samotné ještě nevyšla). `venue`
a `time` ale znát jde — jsou přímo v textu usnesení Rady. `agenda: []`
a `resolutions: []` zůstávají prázdné, protože vlastní program/usnesení
ZM se z bodu Rady nedají vyčíst (Rada schvaluje jen termín, ne
jednotlivé body) — nevymýšlet je. Na webu se to zobrazí korektně samo:
`content/jednani.html` u budoucího jednání bez `links.minutes` ukáže
štítek „PLÁNOVÁNO" a text „Program ani usnesení k tomuto jednání
nejsou zveřejněné", stejnou logikou jako u běžného „jen Pozvánka"
záznamu níže — není potřeba žádná zvláštní podmínka v kódu.
`kalendar/scripts/update-kalendar.py` zvládá `uuid: null` bez úprav
(`source_ref` má fallback na stabilní `id`, viz `sync-google.py`).

**Důležité pro příští běh kontroly:** až `usneseni.cz` zveřejní
skutečnou Pozvánku/UUID pro Zastupitelstvo 7/2026, **tenhle záznam
aktualizovat na místě** (doplnit `uuid`, `links`, `agenda` ze skutečné
Pozvánky) — **nezakládat nový, duplicitní záznam**. Poznat ho jde podle
kombinace `type`+`date` (Zastupitelstvo, 2026-10-07) při `uuid: null`.
Stejné pravidlo platí pro jakékoli další jednání zapsané tímhle
postupem v budoucnu.

## Jednání jen s Pozvánkou (od 21. 8. 2026)

Od 21. 8. 2026 platí, že se do `pecky-jednani.json` zaznamenává i jednání,
které má na webu zatím jen Pozvánku — bez zápisu
a usnesení (dřív se takové jednání při kontrole přeskakovalo). Záznam má
prázdné `resolutions: []`, `links.minutes`/`links.pdf`/`links.resolutions`
`null`, `agenda` vyplněnou z textu Pozvánky. Až web zveřejní zápis
a usnesení, jednání se doplní stejně jako běžný přírůstek.

**Zdroj `agenda` u takového záznamu:** Pozvánka je na `usneseni.cz` jen PDF
za Cloudflare — přímý `fetch()`/`curl` dostane 403. Funkční postup v Claude
in Chrome session bez přístupu k reálné složce Stažené soubory (tedy mimo
plný scraper výše): v kontextu stránky `fetch(url, {credentials:'include'})`
načte PDF jako `ArrayBuffer` (cf_clearance cookie prohlížeče projde), pak
`pdf.js` (`cdnjs.cloudflare.com/ajax/libs/pdf.js/…/pdf.min.js`, dynamicky
vložený `<script>`) z něj v prohlížeči vytáhne čistý text (`getTextContent()`
po stránkách) — ten už jde vrátit ven jako běžný string. Syrové PDF bajty
(base64) ven vrátit nejde — nástroj pro spouštění JS v prohlížeči takový
výstup blokuje jako bezpečnostní opatření proti exfiltraci binárek — takže
`Data/{datum}/pozvanka.pdf` u těchto dvou jednání (Zastupitelstvo 5/2026,
Rada 30/2026) zatím **chybí**; doplnit při příštím běhu plného scraperu
(sekce „Stahování pozvánek a podepsaných zápisů" výše, který běží s reálným
přístupem ke stažením).

## Nesoulad číslování videí na YouTube (zjištěno 21. 8. 2026)

Kanál @mestopecky čísluje videa zasedání ZM ve svých vlastních titulcích
odděleně od oficiálního číslování usneseni.cz — od jara 2026 se rozešly.
Jednání **3/2026 (25. 5. 2026)** nemá na kanálu žádný záznam (mezera
v playlistu „Zasedání ZM" mezi videi z 22. 4. a 24. 6. 2026). Video
s titulkem **„ZM Pečky č. 3/2026, 24. 6. 2026"** patří ve skutečnosti
oficiálnímu jednání **4/2026** (ověřeno obsahem: bod „Plnění rozpočtu
k 31.5.2026" nedává smysl pro jednání z 25. 5.) — je proto v archivu
napárované na `d4c6e9ea-649c-11f1-95ba-0242c0a80003` (4/2026), ne na
`88ca441d-4dca-11f1-b28e-0242c0a80003` (3/2026). Obě jednání mají pole
`video_note` s vysvětlením, zobrazuje se i v panelu Jednání na webu.
Při doplňování `links.youtube`/`video_ts` u budoucích jednání vždy ověřit
shodu podle **obsahu** videa (program, zmíněná data), ne jen podle čísla
v titulku na YouTube.

## Cloudflare

Web je za agresivní bot-ochranou. Scraper proto:
- spouští **systémové Chrome bez automatizačních příznaků** (jen `--remote-debugging-port`)
  a připojuje se přes CDP → ruční odklik Turnstile funguje,
- naviguje lidským tempem (3–8 s, konfigurovatelné v `config.json`),
- drží persistentní profil (`work/chrome-profile`) kvůli `cf_clearance` cookie,
- při detekci challenge čeká, až ho v okně odklikneš, a pokračuje sám.

Playwright headless/vlastní HTTP klienti (curl, `page.request`) dostávají 403.

**Předchozí období u výborů (30. 9. 2026, zadal uživatel).** Pod tabulkou
Finančního i Kontrolního výboru na `/jednani/absence.html` je rozbalovací
blok „Předchozí volební období 2018–2022" (tatáž `tabulka()` + vlastní
výhrada o mezerách v zápisech; `content/absence.html`, `VYHRADA_PREDCHOZI`).
Rada a Zastupitelstvo dál ukazují jen 2022–2026. Datový model se neměnil.

## Starší jednání z úřední desky (od 6. 10. 2026)

Archiv z usneseni.cz začíná v dubnu 2021 (Rada 12. 4., ZM 16. 6. 2021). Starší jednání, která byla vyvěšena
na úřední desce města, jsou **mimo `pecky-jednani.json`** (ten je přesný export a živí docházku, žebříčky
i PečkyBota) v samostatném souboru `jednani/starsi-jednani.json` — tvar záznamu jako `komise.json`
(`group: "starsi"`), navíc `doc_kind` (`zápis` / `usnesení`), `doc_title`, `posted`, `file`, `ocr`, `text`
(úroveň A: bez parsování hlasování a přítomných).
- **Obsah (74):** zápisy Rady 6/2015–12/2016 (38) + usnesení ZM 7/2015–4/2021 (36; ZM od 6/2021 už je v archivu).
- **Generuje** `python3 jednani/scripts/starsi-jednani.py` z dat Monitoringu úřední desky
  (`o-webu/uredni-deska-monitoring/<rok>.txt`, `Data/`, `Text/`). Ke každému jednání zkopíruje **jediný** soubor do
  `jednani/Data/<datum>-<rada|zastupitelstvo>/zapis.*` resp. `usneseni.*` (`Data/` je v `.gitignore`).
- **Stránka:** záznamy jsou **zamíchané do hlavního výpisu** (`content/jednani.html`, `jRenderStarsiRow`): řádek
  = datum + název dokumentu, vpravo štítek „z úřední desky“ místo seznamu osob, po rozkliknutí text usnesení /
  zápisu (`.starsi-text`) a odkaz na dokument. Načtou se jako `m._starsi` s prázdným `agenda`/`resolutions`;
  filtry Vše / Rada / Zastupitelstvo je zahrnují, fulltext hledá v jejich textu (`m._textNorm`, karta `hit-card`
  s úryvkem), hash `#rada-2015-06-08` / `#zastupitelstvo-2016-03-02` funguje jako u ostatních. Vazba výborů na
  „předchozí jednání“ (`jLinkVyborItems`) je záměrně ignoruje. Pod výpisem je vysvětlující callout s mezerami
  (hardcodovaný text — po změně dat přepsat).
- **Mezery:** ZM č. 1/2015 a 2/2015 (před začátkem desky), 3/2017, 1/2018, 4/2020 na desce nejsou; ZM 6/2018 a 7/2019
  mají na desce jen záznam bez souboru; Rada 2017–3/2021 na desce není vůbec. Duplicitní záznam ZM 2/2019 je uveden jednou.
- **Případné rozšíření (úroveň B):** z textu zápisů RM vytáhnout přítomné a hlasování po jménech, z usnesení ZM seznam
  usnesení (I.–IV.); u OCR skenů (5 dokumentů) jména ručně zkontrolovat.

## Jednání z Pečeckých novin (od 10. 10. 2026)

Zápisy Rady a usnesení Zastupitelstva, která vyšla v Pečeckých novinách **před** zápisy na úřední desce (první je RM
8. 6. 2015), jsou v samostatném souboru `jednani/noviny-jednani.json` (tvar jako `starsi-jednani.json`, `group: "noviny"`).
- **Obsah (195):** 165 zápisů Rady a 30 usnesení ZM z 6/2001, 2005–2006 a 11/2007–7/2015 (nejstarší RM 4. 6. 2001,
  nejmladší ZM 3. 6. 2015). Čísla 6/2015 a 7/2015 jsou zahrnuta jen u jednání před 8. 6. 2015 (RM 27. 4., 13. 5., 25. 5.,
  ZM 2/2015 3. 6.). Po 8. 6. 2015 platí úřední deska.
- **Generuje** `python3 jednani/scripts/noviny-jednani.py` z `noviny/Data/PN RRRR/*.pdf` (textová vrstva `pdftotext`, 2001–2011;
  u 2001 a 2008–2011 s opravami níže) a z OCR textu v `noviny/pecky-noviny.json` (skeny 2012–2015). Pro rychlejší ladění
  `NOVINY_CACHE=/cesta/k/cache`; `--review` vypíše začátek/konec každého jednání, `--tail N id…` posledních N řádků.
- **Postup:** nadpis „Rada města Pečky / konaná dne …“ resp. „Usnesení č. … z veřejného zasedání Zastupitelstva“ určí začátek
  a datum, konec určí (1) další nadpis, (2) OCR značka konce článku (■ čtené jako `m`, `=`, `B`, `L`), (3) první odstavec,
  který už není zápis (nadpis, VERZÁLKY, po prázdném řádku), u ZM podpisy ověřovatelů. Zalomené řádky se slepí (`reflow`).
- **Ruční opravy v skriptu** (vždy ověřeno v PDF): `TEXT_FIXES` (poškozená data nadpisů, např. „1%. dubna 201%“ → 14. 4. 2014),
  `DATE_OVERRIDE` (RM v 4/2014 má v nadpisu chybně „3. února“, z textu vyplývá 3. 3. 2014), `CUT` (konec, kde za zápisem
  následuje jiný článek), `DROP`/`TRIM` (vsunuté rámečky a řádky), `PARTIAL` (poznámka u zkráceného přepisu).
  Překlep v novinách: RM 15. 6. 2009 má v nadpisu „2008“ (uživatel potvrdil, že jde o 2009).
- **Stránka:** záznamy se načítají v `content/jednani.html` stejně jako starší jednání z úřední desky (`m._starsi`, navíc
  `m._noviny`): štítek „z novin“, po rozkliknutí text + odkaz na stranu PDF novin (`#page=N`), fulltext, hash
  (`#rada-2010-08-23`), filtry. Pod výpisem je vysvětlující callout (hardcodovaný text a počty — po změně dat přepsat).
- **Mezery a spolehlivost:** archiv novin nemá 2002–2004 a 2007, z 2001/2005–2006 jen několik čísel, z 2008–2015 chybí např. 2/2011,
  3/2011. Text je strojový přepis; u skenů mohou být vsuvky z okolních článků a chyby OCR, u několika jednání je přepis zkrácený
  (`text_note`). Ustavující zasedání 2010, 2006 a 2002 se ve `volebni-obdobi.json` nehledala (výpis nemá dělicí čáru).

**Hranice volebních období (`volebni-obdobi.json`, doplněno 6. 10. 2026):** kromě ustavujícího zasedání 20. 10. 2022
jsou zapsaná i **14. 11. 2018** (PN 11/2018 a 12/2018, s. 3; zasedání se posunulo kvůli návrhu na neplatnost
voleb) a **5. 11. 2014** (PN 12/2014, s. 2–3, usnesení ustavujícího zasedání). Zdroje jsou odkazy na PDF novin
s `#page=N`. Díky tomu se i mezi staršími jednáními z úřední desky zobrazí dělicí čára „Ustavující zasedání 2018“
a „… 2014“. Ustavující zasedání 2010 a starší se nehledala (výpis nesahá před červen 2015).
