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
  ale není to nutné (`future` podmínka ve frontendu ho stejně přestane
  používat, jakmile datum jednání mine).
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
