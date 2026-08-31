# Kontrola nových/doplněných jednání na usneseni.cz (Claude in Chrome)

Lehký, poloautomatický postup pro pravidelnou kontrolu, jestli na
[mesto-pecky.usneseni.cz/verejne/](https://mesto-pecky.usneseni.cz/verejne/)
nepřibylo nové jednání nebo se u existujícího nedoplnil zápis a usnesení
(oproti stavu jen s Pozvánkou). Doplňuje `jednani/pecky-jednani.json`
— lehký soubor, který pohání panel Jednání na webu (`content/jednani.html`,
promítne se do veřejné stránky `/jednani/` přes `scripts/build.py`).
Součástí postupu je i kontrola záznamů
zastupitelstva na YouTube (krok 6) a časových značek jednotlivých bodů
u těch videí (krok 7) — obojí dělat při každém běhu, ne jen jednorázově.

**Vztah k ostatním dokumentům:** dřívější plán počítal s plným scraperem
(Playwright/CDP) běžícím na jiném stroji — popsaný v [SPEC.md](SPEC.md) —
který produkoval velký `archive-YYYY-MM-DD.json` vč. detail-stránek
usnesení (`detail_id`, jmenovitá hlasování). K tomu stroji už není
přístup, takže tohle je teď **jediný aktivní způsob**, jak archiv
doplňovat — přes Claude in Chrome, bez Playwright/CDP, jen ruční
prohlížeč. Spouští se buď ručně, nebo z Routine v appce Claude, která na
tento soubor jen odkazuje. Pro katastr/pozemky viz
[automation-katastr-parcely.md](automation-katastr-parcely.md).

**Stabilní klíče:** jednání = UUID (v URL všech dokumentů); usnesení =
`number_raw` (tvar `UR-XXX-N/RR`, formát ročníku kolísá — `…/26` i
`…/2026`, vždy zapisovat verbatim). Číslo usnesení „detail_id" (numerické
ID z `/verejne/usneseni/<id>`) tímto postupem nezjistíš, viz mezera
u kroku 4.

## Kdy spustit

Kdykoli — na webu nemá smysl kontrolovat víc než jednou denně (rada
zasedá týdně, zastupitelstvo měsíčně). Web zápis obvykle publikuje
s odstupem 1–3 dnů po jednání.

## Postup

### 1. Zjisti aktuální stav archivu

Přečti `jednani/pecky-jednani.json`, seřaď `meetings` podle `date`
sestupně, podívej se na několik posledních záznamů. Zvlášť si všimni těch,
kde `links.minutes` je `null` (zaznamenané jen z Pozvánky, viz README.md
sekce „Jednání jen s Pozvánkou") — u těch je potřeba web zkontrolovat jako
první.

### 2. Otevři výpis na webu (Claude in Chrome)

Naviguj na `https://mesto-pecky.usneseni.cz/verejne/` a přečti `get_page_text`
první stránky (nová jednání přibývají nahoře, stačí první stránka —
stránkování `?page=N` navíc není stabilní adresa, posouvá se s každým
novým jednáním). U každého řádku web ukazuje, co už je k dispozici:
`Pozvánka`, `zápis`, `podepsaný zápis`, `přijatá usnesení`. Jde i filtrovat
podle orgánu (`?type=zastupitelstvo|rada|financni-vybor|kontrolni-vybor`),
ale pro běžnou kontrolu to není potřeba — nefiltrovaný výpis stačí.

Porovnej se stavem z kroku 1:
- **Úplně nové jednání** (číslo/datum, které v archivu vůbec není) →
  přidat nový záznam, minimálně s `agenda` z Pozvánky (pokud je Pozvánka
  dostupná — jinak počkat na příště, web pro starší jednání pozvánky
  negeneruje, viz „Známá omezení zdroje" v README.md).
- **Existující záznam s `links.minutes: null`, ale web teď ukazuje
  `zápis`/`usnesení`** → doplnit plný obsah (hlavní případ, viz níže).
- Nic nového → nahlásit uživateli beze změny, nic nevymýšlet.

### 3. Stáhni zápis a usnesení

Pro každé jednání k doplnění zjisti UUID (z `href` odkazu `zápis` na
výpisu, tvar `/verejne/<uuid>/zapis/`) a naviguj postupně na:
- `https://mesto-pecky.usneseni.cz/verejne/<uuid>/zapis/` — `get_page_text`
- `https://mesto-pecky.usneseni.cz/verejne/<uuid>/usneseni/` — `get_page_text`

Cloudflare tento web chrání, ale běžná navigace v Claude in Chrome
(ne curl/fetch) zatím vždy prošla bez challenge.

### 4. Vytáhni strukturovaná data ze zápisu

Ze `zápis` textu:
- **Agenda**: pro každý bod nadpis obsahuje `(bod číslo N)` — párovat podle
  tohoto čísla, NE podle pořadí v zápisu (rada/zastupitelstvo body občas
  probírá v jiném pořadí, než jsou v programu; nový bod přidaný až během
  jednání usnesením o schválení programu má číslo za posledním původním
  bodem, viz příklad Rada 30/2026 níže).
- **Délka bodu** (`duration_seconds`): `Projednávání bodu bylo zahájeno
  v HH:MM:SS` / `...ukončeno v HH:MM:SS`, rozdíl v sekundách. Bod bez
  časové značky (odložen/prázdný text) — bez `duration_seconds`, nic
  nedopočítávat.
- **`predkladatel`**: řádek „Předkladatel: …" u bodu.
- **`duvodova_zprava`**: text pod „Důvodová zpráva:" — jen pokud bod nějakou
  má, jinak pole vynechat.
- **Délka celého jednání** (`duration_seconds` na úrovni jednání):
  `Jednání zahájeno DD.MM.RRRR v HH:MM:SS` / `Jednání ukončeno … v HH:MM:SS`.
- **`attendance`**: z „Úvodní prezence" (na začátku zápisu, NE z pozdějších
  „Aktualizovaný stav prezence" po příchodu/odchodu člena v průběhu —
  archiv drží stav ze zahájení, konzistentně s ostatními záznamy).
  `present`/`total` z věty „Přítomno je N (z M) členů"; `present_names` ze
  jmen v „Přítomni"; `absent_names` = „Omluveni" + „Nepřítomni" sloučené,
  každé se `note: "omluven"` / `"nepřítomen"`.
- Po doplnění `links.minutes`/`resolutions`/`agenda`/`duration_seconds`
  smazat pole `time` (scheduled čas z Pozvánky) — ostatní kompletní
  záznamy ho nemají, nahrazuje ho skutečný `duration_seconds`.

Ze stránky `usnesení`:
- Pro každé usnesení: `n` (číslo, tvar `UR-XXX-N/RR`), `item` (bod
  programu), `text` (plné znění), `date`, `pro`/`proti`/`zdrzel` z
  hlasování.
- **Trvalá mezera**: odkazy na jednotlivá usnesení na této stránce mají
  `href="#"` (žádná skutečná URL, jen JS placeholder bez network requestu
  za klikem) — pole `url` (odkaz na detail usnesení s `detail_id`) proto
  u takto doplněných usnesení NELZE touto cestou získat. Nechat vynechané
  — frontend to zvládá (`r.url ? … : ''` v `content/jednani.html`). Dřív šlo doplnění
  nechat na plný scraper na jiném stroji, který k detailu přistupoval jinak
  (`in-page fetch`, ne klikání) — k tomu stroji už není přístup, takže jde
  o trvalou mezeru, ne dočasný stav do dalšího běhu.

### 5. Zapiš do `pecky-jednani.json`

Načíst přes `json.load`, najít záznam podle `uuid`, doplnit pole podle
schématu výše (viz existující kompletní záznam, např. jakékoliv jednání
s `resolutions` neprázdným, jako referenční tvar), zapsat zpět
`json.dumps(data, ensure_ascii=False, indent=2) + "\n"` — stejný formát
jako zbytek souboru, jinak diff zasáhne celý soubor místo jen dotčeného
záznamu.

Ověřit: `python3 -c "import json; json.load(open('jednani/pecky-jednani.json'))"`.

**Permalink vzniká automaticky, nic dalšího tu není potřeba dopisovat.**
Trvalý odkaz tvaru `#rada-YYYY-MM-DD` / `#zastupitelstvo-YYYY-MM-DD` se
u každého jednání v tabulce generuje za běhu z `type` + `date`
(`content/jednani.html`, funkce `jSlugForMeeting()`) — není to pole
uložené v JSON. Jakmile je nový záznam v `pecky-jednani.json` a web se
přegeneruje (`python3 scripts/build.py`), permalink pro něj funguje sám
od sebe.

### 6. Kontrola YouTube u zastupitelstva (dělat při KAŽDÉM běhu)

Rada nikdy nemá záznam na YouTube (ověřeno 27. 8. 2026: 0/246 jednání
rady má `links.youtube`) — tenhle krok se týká jen Zastupitelstva.
Provádět při každém běhu kontroly, ne jen když přibylo nové jednání —
video se objevuje na kanálu s odstupem (u jednání 26. 8. 2026 vyšlo
cca 22 hodin po jednání), takže jednání kontrolované „bez videa" dnes
může mít video zítra.

1. Najdi v archivu všechna jednání `type: "Zastupitelstvo"` s `date`
   v minulosti a chybějícím/`null` `links.youtube`.
2. Pro každé otevři playlist „Zasedání ZM" na kanálu Město Pečky
   (`https://www.youtube.com/playlist?list=PL1KVT2dbyIKSTFRv7tfDqrfk5gkTSnoyu`)
   — přes Claude in Chrome (`navigate` + `find`/`get_page_text`).
   **WebFetch na YouTube nefunguje** — narazí na cookie-consent redirect
   (`consent.youtube.com`), vrátí prázdno.
3. Najdi video, jehož **datum** v titulku (`ZM Pečky č. N/RRRR, D. M.
   RRRR, HH:MM`) sedí s `date` jednání. **Nespoléhat na číslo N v
   titulku** — město ho čísluje nezávisle na usneseni.cz a historicky
   se rozešlo (viz `video_note` u jednání 4/2026: video označené
   „č. 3/2026" patří ve skutečnosti jednání 4/2026 z 24. 6. 2026).
   Datum je jediný spolehlivý klíč pro spárování.
4. Otevři nalezené video a ověř v popisku (obvykle „Záznam zasedání
   zastupitelstva města Pečky č. N/RRRR, …") i v prvním kapitolovém
   bodu, že souhlasí datum, číslo a případně první bod `agenda[0].t`.
5. Doplň `links.youtube` (poslední klíč v objektu `links`), formát
   `https://www.youtube.com/watch?v=<ID>&list=PL1KVT2dbyIKSTFRv7tfDqrfk5gkTSnoyu`
   (bez dalších trackovacích parametrů z URL, jen `list`). Pokud číslo
   v titulku videa nesedí s číslem jednání, doplň i `video_note`
   vysvětlující nesoulad (vzor viz jednání 4/2026 výše v tomto
   dokumentu).
6. Jednání, ke kterým video na kanálu vůbec není (mezera v playlistu —
   potvrzený případ jednání 3/2026, video k němu chybí úplně), nechat
   bez `links.youtube` a nevymýšlet. Může se objevit až při některém
   příštím běhu, nebo nikdy — v obou případech nic nepředstírat.

Frontend (`content/jednani.html`, `jRenderMeetingList`)
je na `links.youtube` datově řízený — žádná úprava kódu není potřeba,
nový odkaz se automaticky promítne i do textů „K dispozici je video" (u
proběhlého jednání bez zápisu) a tlačítka Video v rozbaleném řádku.

### 7. Časové značky videa u zastupitelstva (dělat při KAŽDÉM běhu)

**Pravidlo:** má-li jednání zastupitelstva zároveň zápis (`links.minutes`)
i video (`links.youtube`), musí mít i `video_ts`/`video_url` u
jednotlivých bodů agendy — jinak zůstane nedotažené napůl (video
existuje, ale bez přímého odkazu na konkrétní bod). Kontrolovat při
každém běhu, ne jen u nově doplněných jednání — obě podmínky se typicky
splní v různých bězích (zápis se doplní tento týden, video až příští),
takže mezera vzniká i u starších záznamů.

1. Najdi v archivu jednání `type: "Zastupitelstvo"` s vyplněným
   `links.minutes` i `links.youtube`, kde aspoň jeden bod `agenda[]`
   nemá `video_ts`.
2. Pro každé otevři video (`links.youtube`) přes Claude in Chrome a v
   konzoli přečti `window.ytInitialPlayerResponse.videoDetails.shortDescription`
   — od jednání ZM 2/2025 (2. 4. 2025) obsahuje kapitoly ve tvaru
   `H:MM:SS Text bodu`. Starší jednání (2022–2024, ZM 1/2025) kapitoly
   nemají vůbec — nechat bez `video_ts`, nevymýšlet.
3. Spáruj kapitoly s `agenda[].n` podle **čísla bodu v textu kapitoly**
   (obvykle na začátku, `N. Text`), ne podle pořadí řádků — číslování
   v popisku se nemusí krýt s pořadím v zápisu. Plný popis rizik a edge
   cases (dvě čísla v jedné kapitole, prefix „Úvod, N. …") je v
   [README.md](README.md) → „Časové značky videa".
4. Doplň `agenda[].video_ts` (sekundy od začátku) a `agenda[].video_url`
   (`https://youtu.be/<ID>?t=<sekundy>`). Bod bez vlastní kapitoly
   nechat bez těchto polí.

Stejně jako krok 6 je i tohle datově řízené — žádná úprava kódu, nové
`video_ts` se promítnou do tlačítka „▶ video ↗" u bodu agendy
automaticky.

### 8. Pozemky (pokud relevantní)

Pokud nové usnesení řeší prodej/nákup pozemku, spustit i
`python3 jednani/scripts/update-pozemky.py` — viz
[automation-katastr-parcely.md](automation-katastr-parcely.md) pro plný
popis.

### 9. Ověř na webu

Nejdřív spustit `python3 scripts/build.py` (promítne `content/jednani.html`
do `jednani/index.html`), pak spustit lokální server (`.claude/launch.json`,
config `pecky-online-main` — port se přiděluje automaticky, `autoPort: true`),
otevřít `/jednani/`, rozkliknout dotčené
jednání, zkontrolovat: počet usnesení v perexu nahoře odpovídá (`Archiv
obsahuje … usnesení` — počítá se dynamicky, žádné jinde neupravovat),
agenda seřazená 1..N, časy bodů dávají smysl, badge SCHVÁLENO/DOPORUČENO/
NEDOPORUČENO u usnesení.

Tahle vizuální kontrola není formalita — extrakce v kroku 4 je založená na
konkrétních textových vzorech (`bod číslo N`, „Jednání zahájeno…",
„Přítomno je…"). Bez automatizovaných testů/fixtures se změna šablony webu
pozná jen tak, že očekávaný text v `get_page_text` chybí nebo nedává
smysl — proto se výsledek nesmí slepě důvěřovat, vždy zkontrolovat.

### 10. Nahlaš uživateli

Stručně: co bylo nové/doplněné, co zůstává čekat na publikaci webem. Nic
nevymýšlet — pokud web nic nového neukazuje, říct to přímo.

## Příklad (Rada 30/2026, 24. 8. 2026 → doplněno 27. 8. 2026)

Bod 11 „Pečky – oprava místní komunikace…" byl přidán až usnesením
o schválení programu (UR-270), takže se v zápisu objevuje mimo pořadí
(hned po bodu 7), ale patří na konec agendy podle `(bod číslo 11)`
v nadpisu. Přítomnost na začátku 5/7 (Ing. Petr Dürr dorazil až v půlce
jednání) — do `attendance` šel počáteční stav 5/7, ne pozdější 6/7.

## Další rizika

- **Cloudflare** — web je za bot-ochranou, curl/přímý HTTP dostává 403.
  Funguje jen skutečná navigace v prohlížeči — Claude in Chrome zatím
  vždy prošlo bez challenge (krok 3).
- **Zpětné úpravy dokumentů** — zápisy lze teoreticky opravit i po
  zveřejnění. Starý plný scraper držel časově razítkované snímky
  (`archive-YYYY-MM-DD.json`), takže by taková zpětná změna šla dohledat
  diffem. Tenhle lehký postup přepisuje `pecky-jednani.json` na místě,
  bez historie verzí mimo git — zpětnou opravu zápisu odhalí jen git
  historie souboru nebo ruční opětovná kontrola konkrétního jednání.
- **YouTube** (krok 6) — `WebFetch` na YouTube nefunguje (cookie-consent
  redirect přes `consent.youtube.com`), jen Claude in Chrome. Číslo
  jednání v titulku videa se nesmí považovat za spolehlivé — město ho
  historicky očíslovalo jinak než usneseni.cz (viz `video_note` u
  jednání 4/2026) — spárovat vždy podle data, ne podle čísla.
- **Časové značky videa** (krok 7) — jednání před ZM 2/2025 (2. 4. 2025)
  kapitoly v popisku vůbec nemají (`shortDescription` je jednořádkový
  název bez timestampů) — u nich `video_ts` trvale chybí, nezkoušet
  dohledávat jinak.
