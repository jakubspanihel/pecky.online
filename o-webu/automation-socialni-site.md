# Kontrola sociálních sítí (Claude in Chrome)

Denní, poloautomatický postup. U všech odkazů v sekci [O webu](README.md) →
„Sociální sítě“ (`content/owebu.html`, druhý blok `div.quicklinks`)
aktualizuje dva údaje:

- **počet sledujících / členů / odběratelů**,
- **datum posledního příspěvku / videa** — datum skutečné aktivity účtu,
  **nikdy datum kontroly**.

Navíc obnoví stránku zhlédnutí záznamů zastupitelstva (krok 4).
Nemá vlastní datový soubor, údaje se zapisují přímo do HTML. Sociální sítě
uskupení z [Voleb 2026](../volby/2026/README.md) se tady neaktualizují.

**Co se tady nedělá:** hledání akcí a změn provozu pro Kalendář. Má ho
samostatný skill `DoPecek-nove-akce-check` (`kalendar/automation-nove-akce.md`)
a vlastní naplánovaný úkol. Narazí-li kontrola mimochodem na akci, zapíše ji
podle `kalendar/automation-plakat-akce.md`, ale nehledá ji.

Podrobnosti dřívějších běhů a změn metod jsou v `HISTORIE.md`.

## Prostředí

Facebook, Instagram i YouTube vyžadují `mcp__claude-in-chrome__*` (skutečné
přihlášené Chrome). `WebFetch`, curl ani izolovaný `mcp__Claude_Browser__*`
nefungují (přihlašovací stěna, cookie-consent u YouTube). Není-li rozšíření
připojené, kontrolu přeskočit, nic neměnit a napsat, že je potřeba ji spustit
ručně z lokální relace s Chrome.

Číslo nebo datum, které se nepodaří přečíst, nechat beze změny a nahlásit
jako mezeru. Nic nedopočítávat.

## Postup

### 1. Seznam účtů

V `content/owebu.html` je `div.quicklinks` s jedním `<a class="qlink">` na
účet. Projít **všechny, které tam právě jsou** (seznam roste, počet si
nepamatovat). Přehled účtů s dosavadním počtem a datem (jen čte):

```bash
python3 o-webu/socialni-site-prehled.py
```

Účtu bez řádku `url-meta` (datum) doplnit datum stejně jako ostatním.
Skript vynechává interní odkazy (`/o-webu/…`). Odkazy na weby jsou v jiném
bloku (mimo „Sociální sítě“) a netýkají se ho.

### 2. Přečíst údaje (Chrome)

Číst dávkou `browser_batch`: navigate → wait 4 s → `javascript_tool`.
Po navigaci nechat stránku načíst aspoň 4 s, jinak jsou skripty prázdné.

| Zdroj | Počet | Datum poslední aktivity |
|---|---|---|
| Facebook stránka | text „sledující (N)“ | `creation_time` (viz níže) |
| Facebook skupina | „N členů“ (jiná metrika, jednotka „členů“) | `creation_time` |
| Instagram | „Sledující (N)“ | `<time datetime>` na detailu příspěvku |
| YouTube kanál `@handle` | „N odběratelů“ | playlist „Zasedání ZM“ |

**Zaokrouhlení:** Facebook od cca 1 000 ukazuje „1 tis.“, „4,5 tis.“. Zapsat
ve stejném tvaru, nedopočítávat přesné číslo.

#### Facebook — počet a datum jedním skriptem

Datum posledního příspěvku je ve `<script>` datech stránky. Bere se
**nejvyšší** hodnota, takže připíchnuté i sdílené starší příspěvky vypadnou
samy:

```js
const s=[...document.querySelectorAll('script')].map(x=>x.textContent).join(' ');
const m=[...s.matchAll(/(?:creation_time|publish_time)\\?"?:\s*(\d{9,13})/g)]
  .map(x=>+x[1]).filter(v=>v>1600000000&&v<1900000000);
({f:(document.body.innerText.match(/[^\n]*(sledující|členů|členové)[^\n]*/g)||[]).slice(0,2),
  t:[...new Set(m)].sort((a,b)=>b-a).slice(0,2).map(v=>new Date(v*1000).toISOString().slice(0,16))})
```

Čas je v UTC (v listopadu +1 h do českého; kolem půlnoci dávat pozor na
posun dne). Vrátí-li pole `t` prázdné (zatím Wok Pečky), datum nechat beze
změny a nahlásit jako mezeru. Záloha: absolutní datum v textu prvního
příspěvku („31. srpna v 18:45“) je přesnější než relativní „4 d“; relativní
čas se snadno splete o den. Při sdíleném příspěvku (dvě jména a dvě data)
platí datum **vlastního** sdílení.

#### Instagram — datum

Mřížka profilu **není chronologická**: 1–3 příspěvky jsou připíchnuté
(i vícedílný příspěvek může zabrat tři dlaždice, pin může být třeba jen na
dlaždici 2) a pin ikona na screenshotu není spolehlivá. Proto **otevřít
aspoň první 4–5 dlaždic a zapsat nejnovější nalezené datum**, ne datum první
dlaždice.

Spolehlivě funguje otevření dlaždice skriptem (čtení `href` je blokované
jako „Base64 encoded data“, samotné `.click()` projde) a čtení prvního
`<time>`:

```js
document.querySelectorAll('main a[href*="/p/"], main a[href*="/reel/"]')[0].click();1
```

Po 2 s čekání:

```js
[...document.querySelectorAll('time')].map(t=>t.getAttribute('datetime')).slice(0,1)
```

Mezi dlaždicemi navigovat znovu na URL profilu (ne `back`, ten se pletl).
Počet: `document.body.innerText.match(/Sledující[^\n]*/)` na profilu.
Údaj `<time>` číst jen z **prvního** elementu. Další mohou patřit jinému
příspěvku (u streetpeopleofpecky druhý `<time>` ukazoval nesouvisející datum).
Je-li relace odhlášená a objeví se přihlašovací stěna, ověřit přihlášení
Chrome, než se použije jiná metoda.

#### YouTube — datum

Záložka „Videa“ neodpovídá skutečné aktivitě (zasedání ZM se nahrávají jako
neveřejná). Datum posledního videa brát z playlistu „Zasedání ZM“
(`https://www.youtube.com/playlist?list=PL1KVT2dbyIKSTFRv7tfDqrfk5gkTSnoyu`):
je seřazený od nejstaršího, nejnovější je poslední položka („Vysíláno před N
dny“), tedy po scrollu na konec stránky. Relativní údaj je přibližný, proto
se zapisuje datum zastupitelstva z Jednání, pokud sedí.

### 3. Zapsat do `content/owebu.html`

Každý `<a class="qlink">` má dva řádky v `span.url`:

```html
<span class="url"><span class="follower-count">N sledujících</span><span class="url-meta">poslední příspěvek <span data-date="RRRR-MM-DD">D. M. RRRR</span></span></span>
```

- `follower-count`: jen číslo s jednotkou (bez handle, URL a šipky ↗).
  U YouTube „odběratelů“ a „poslední video“, u FB skupiny „členů“.
- `data-date` a viditelné datum: absolutní datum poslední aktivity. Text
  „dnes / včera / před X dny“ dopočítá `relDatum()` v `assets/common.js`.
  Ručně ho nepsat.
- Seznam je seřazený sestupně podle počtu sledujících. Změní-li se pořadí,
  přesunout řádek `<a class="qlink">` (ne po každé kontrole, jen při skutečné
  změně).
- Vyjde-li u mnoha účtů najednou totéž (typicky dnešní) datum, je to
  varovný signál chyby čtení. Ověřit.
- Účty propojených stránek (NAŠE PEČKY, Pečky NEXT, Alena Švejnohová) občas
  zveřejní identický příspěvek najednou. Datum přesto ověřit zvlášť u každého
  účtu a nekopírovat mezi nimi.
- Nový nebo zaniklý účet: doplnit nebo odebrat řádek podle aktuálního stavu
  `content/owebu.html`.

### 4. Zhlédnutí záznamů zastupitelstva (YouTube)

Stránka `/jednani/youtube.html` je statický snímek. Při každé kontrole:

1. `python3 jednani/update-youtube.py` přečte zhlédnutí všech záznamů ZM
   s YouTube odkazem v `jednani/pecky-jednani.json` a přepíše
   `content/youtube.html` (bez Chrome, jen HTTP). Hlásí-li
   `CHYBA: nelze přečíst zhlédnutí`, ten záznam v grafu chybí → nahlásit jako
   mezeru.
2. Přibylo-li nové jednání ZM s videem, skript ho zařadí sám. Není-li video
   v `pecky-jednani.json`, nejdřív doplnit tam (skill `DoPecek-jednani-check`).
3. Změnila-li se čísla, přepsat `lastmod` záznamu `youtube` v `EXTRA_PAGES`
   ve `scripts/build.py` na dnešní datum a řádek Jednání ve „Stav sekcí“
   (`README.md`). Beze změny čísel se nic nezapisuje.
4. Do hlášení: nový součet, o kolik se změnil, nové záznamy, největší nárůst
   u konkrétního videa.

### 5. Přegenerovat a ověřit

`python3 scripts/build.py`, pak zkontrolovat `/o-webu/`: u každého odkazu
musí být nové číslo a datum (přesné datum v tooltipu).

### 6. Záznam a hlášení

- `README.md` → „Stav sekcí“: přepsat řádek O webu (datum kontroly vždy,
  datum změny a „Co naposledy“ jen při reálné změně).
- `HISTORIE.md`: odstavec nahoru.
- Hlášení: u kterých účtů se změnil počet (o kolik), kde je nová aktivita,
  které účty jsou dlouhodobě neaktivní, které údaje se nepodařilo přečíst.
  „Beze změny“ je platný výsledek, nemlčet.

## Bezobslužný běh bez potvrzování

Při naplánovaném běhu nikdo neodklikává povolení. Příkaz, který se nevejde do
povolených tvarů, běh zastaví na dotazu, proto:

- Jeden jednoduchý příkaz na volání Bash: bez předpony `PROMENNA=…;`, bez
  řetězení `;`/`&&`, bez rour do `xargs`/`awk`/`sed`. Cestu do scratchpadu
  psát celou přímo do argumentu.
- Soubory měnit nástrojem Edit/Write, ne skriptem ani heredocem.
- Přidání do indexu: `snapshot.py stage --file <baseline> <soubor> …` se
  seznamem souborů výslovně (seznam z `snapshot.py report` jedním samostatným
  voláním, pak ručně opsat do `stage`).
- Zbloudilé soubory typu `… 2.json` (Finder) nepřesouvat: build je ignoruje
  a do commitu nepatří.
