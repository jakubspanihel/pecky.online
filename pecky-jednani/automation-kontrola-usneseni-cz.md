# Kontrola nových/doplněných jednání na usneseni.cz (Claude in Chrome)

Lehký, poloautomatický postup pro pravidelnou kontrolu, jestli na
[mesto-pecky.usneseni.cz/verejne/](https://mesto-pecky.usneseni.cz/verejne/)
nepřibylo nové jednání nebo se u existujícího nedoplnil zápis a usnesení
(oproti stavu jen s Pozvánkou). Doplňuje `pecky-jednani/pecky-jednani.json`
— lehký soubor, který pohání panel Jednání na webu (root `index.html` i
`pecky-jednani/index.html`).

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

Přečti `pecky-jednani/pecky-jednani.json`, seřaď `meetings` podle `date`
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
  — frontend to zvládá (`r.url ? … : ''` v `index.html`). Dřív šlo doplnění
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

Ověřit: `python3 -c "import json; json.load(open('pecky-jednani/pecky-jednani.json'))"`.

### 6. Pozemky (pokud relevantní)

Pokud nové usnesení řeší prodej/nákup pozemku, spustit i
`python3 pecky-jednani/scripts/update-pozemky.py` — viz
[automation-katastr-parcely.md](automation-katastr-parcely.md) pro plný
popis.

### 7. Ověř na webu

Spustit lokální server (`.claude/launch.json`, config
`pecky-online-main`, port 8934), otevřít `#jednani`, rozkliknout dotčené
jednání, zkontrolovat: počet usnesení v perexu nahoře odpovídá (`Archiv
obsahuje … usnesení` — počítá se dynamicky, žádné jinde neupravovat),
agenda seřazená 1..N, časy bodů dávají smysl, badge SCHVÁLENO/DOPORUČENO/
NEDOPORUČENO u usnesení.

Tahle vizuální kontrola není formalita — extrakce v kroku 4 je založená na
konkrétních textových vzorech (`bod číslo N`, „Jednání zahájeno…",
„Přítomno je…"). Bez automatizovaných testů/fixtures se změna šablony webu
pozná jen tak, že očekávaný text v `get_page_text` chybí nebo nedává
smysl — proto se výsledek nesmí slepě důvěřovat, vždy zkontrolovat.

### 8. Nahlaš uživateli

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
