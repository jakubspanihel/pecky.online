# Monitoring Facebooku

Podrobný archiv příspěvků z facebookových profilů, které web sleduje. Slouží
jako zdroj pro ostatní sekce (Kalendář, Tělocvična, Zakázky, Jednání…) — ne
jako veřejný obsah webu.

## Milníky profilu

Nejstarší událost profilu — **Založení facebooku města, 20. listopadu 2018** (zadal uživatel 3. 10. 2026).
Souhlasí s monitoringem: 20. 11. 2018 jsou nejstarší dostupné příspěvky (9:14–9:19, čtyři „aktualizace stavu“ s nedostupným obsahem),
dřívější se na profilu nenačítají. Milník není příspěvek — v `summary.py` je v konstantě `EVENTS` a na veřejné stránce Monitoring
je jako řádek bez odkazu na konci detailu měsíce 2018-11 (nezapočítává se do počtů příspěvků). Další milníky se přidávají tamtéž.

## Struktura

```
o-webu/facebook-monitoring/
├── README.md                      tento soubor
└── <fb-zdroj-id>/                 jeden adresář na sledovaný profil
    ├── yyyy-mm.json               příspěvky za měsíc (podle data zveřejnění)
    └── media/                     (volitelné) stažené plakáty, jen když je potřeba
```

Zdroje:

| ID zdroje | Profil | Stav |
|---|---|---|
| `facebook-mestopecky` | https://www.facebook.com/mestopecky (Město Pečky), založeno 20. 11. 2018 | ruční běhy, 2018-11 (nejstarší dostupné) až 2026-10 (neúplný, do 9. 10.) |

**Soubory `*.json` a `media/` jsou v `.gitignore`** — jsou jen lokální pracovní
data, do gitu ani na GitHub Pages nejdou. V gitu je jen tento README.

## Formát `yyyy-mm.json`

```json
{
  "source": "facebook-mestopecky",
  "source_url": "https://www.facebook.com/mestopecky",
  "month": "2026-03",
  "collected": "2026-10-02",
  "method": "…",
  "counts_as_of": "2026-10-02",
  "summary": { "posts": 22, "by_type": {…}, "shared_from_other_pages": 2,
               "first_published": "…", "last_published": "…" },
  "posts": [ { … } ]
}
```

`summary` je záměrně malý — slouží ke kontrole úplnosti měsíce, ne ke
statistice. Součty reakcí/komentářů se do něj **nedávají** (zkreslují je
2–4 virální videa, jsou to snímky k `counts_as_of` a odvozená čísla v syrovém
souboru se rozcházejí s daty). Přepočítává ho skript
`python3 o-webu/facebook-monitoring/summary.py` — **spustit po každém zápisu
měsíčního souboru**, ručně se nepíše. Přehled přes všechny měsíce
generuje tentýž skript do `content/fbmonitoring.html` — veřejná stránka
**Monitoring** na `/o-webu/facebook-monitoring/facebook-mestopecky/`
(registrace `EXTRA_PAGES['fbmonitoring']` ve `scripts/build.py`, odkaz z
O webu → Sociální sítě pod položkou „Facebook — Město Pečky (oficiální)“).
Tabulka je statický snímek (zdrojová JSON jsou v `.gitignore`), takže po
každém novém měsíci: `summary.py` → `python3 scripts/build.py` → přepsat
`lastmod` v `EXTRA_PAGES['fbmonitoring']`. Stránka ukazuje měsíc, počet
příspěvků (bez rozsahu dat), sestupně. Od 2. 10. 2026 je řádek měsíce
**klikací**: po rozkliknutí se pod ním ukáže rozpad podle typu (pevné
pořadí text, odkaz, foto, album, video, sdílený příspěvek, událost, změna
úvodní fotky; jen nenulové) a sdílení z cizích profilů, pak tabulka
Datum | Obsah — obsah je **krátký popis příspěvku** (pole `popis`, viz
níže) s odkazem na originál na Facebooku, pod ním
`👍 reakce 💬 komentáře ♺ sdílení`; za datem je chip s typem příspěvku v barvě skupiny z legendy grafu (`TYPE_GROUPS`). Text příspěvku se na web
nepřenáší, takže se tam nedostanou jména ani telefony z původních textů.

Hned za perexem je statický SVG skládaný sloupcový graf počtu příspěvků po měsících (sloupec je rozdělený podle typu příspěvku do pěti skupin `TYPE_GROUPS` v `summary.py`: foto a alba, texty a odkazy, video, sdílené příspěvky, události a změny úvodní fotky; legenda nad grafem, rozpad v tooltipu) (osa x čas, osa y počet; `render_chart` v `summary.py`,
bez externích knihoven, barvy z proměnných webu, maximum zvýrazněno). Nad grafem vpravo (na řádku s nadpisem „Počet příspěvků na Facebooku města“) je segmentový přepínač rozsahu „Od začátku“ (měsíce) / „Volební období“ (sloupec = období od ustavujícího zasedání z `jednani/volebni-obdobi.json`) / „Posledních 30 dní“ (dny do posledního zachyceného příspěvku, ne do dneška); všechny tři SVG jsou předrenderované, přepínač jen ukazuje/skrývá. Sloupec grafu je odkaz (kotva): měsíc → řádek měsíce `#fb-yyyy-mm`, období → první měsíc období `#fb-yyyy-mm`, den → první příspěvek dne `#fb-d-yyyy-mm-dd` (dny bez příspěvku vedou na měsíc). Skript stránky rozbalí příslušný měsíc, zvýrazní cíl a posune ho pod sticky nadpisy; kotvy fungují i z adresy (`…/#fb-2020-03`). Zvolený rozsah grafu se ukládá do adresy parametrem `?graf=obdobi` / `?graf=30dni` (výchozí „Od začátku“ bez parametru), takže jde poslat odkaz rovnou na „Volební období“; parametr jde zkombinovat s kotvou (`?graf=obdobi#fb-2022-10`).

**Analýza obsahu.** Na konci stránky je tlačítko „Analýza: Co město na Facebooku publikuje“, které rozbalí skrytou sekci `#fb-analyza`
(období dělená komunálními volbami 1. 10. 2022 — po nich se změnil správce profilu: četnost v bodech, tabulka témat se shrnutím, srovnání).
Generuje ji `analyza.py` (volá `summary.py`): každý příspěvek jde podle klíčových slov v poli `popis` do jedné skupiny (pravidla `R`,
pořadí = přednost; zařazení orientační, ≈ 85 % správně). Při změně pravidel nebo po novém měsíci stačí pustit `summary.py` a `scripts/build.py`;
bodová shrnutí používají počty spočtené z dat, jen vyprávěcí věty jsou psané ručně a je třeba je po novém měsíci zkontrolovat.

**Rozložení stránky.** Od šířky 768 px jsou pod grafem dva sloupce: vlevo strom roků a měsíců (`nav#fb-tree`, rozbalený je nejnovější rok), vpravo příspěvky vybraného měsíce (`#fb-pane`, výchozí je nejnovější měsíc). Obsah měsíce se z mobilní tabulky do pravého sloupce **přesouvá** (nekopíruje), takže id kotev zůstávají jedinečná; při zúžení pod 768 px se vrací zpět. Do 767 px zůstává původní akordeon roků a měsíců. Kotvy `#fb-yyyy-mm`, `#fb-d-…` i `#fb-y-yyyy` (rok → jeho nejnovější měsíc) vyberou měsíc; ruční výběr měsíce zapíše `#fb-yyyy-mm` do adresy.


Od 3. 10. 2026 je tabulka rozdělená po letech: každý rok má vlastní sticky `h3` „2026 (189 příspěvků)“ a vlastní tabulku měsíců,
navíc pod tabulkami je řádek „Celkem“ (viz `render_page` v `summary.py`).

Příspěvek (řazeno od nejnovějšího):

| Pole | Význam |
|---|---|
| `id` | `post_id` z Facebooku, klíč pro slučování při opakovaném běhu |
| `url` | trvalý odkaz (bez parametrů) |
| `published` | místní čas (Europe/Prague), ISO bez zóny |
| `type` | `text`, `odkaz`, `foto`, `album`, `video`, `sdílený příspěvek`, `změna úvodní fotky` |
| `text` | plné znění, rozbalené, tak jak je (včetně emoji); `null` u čistých sdílení |
| `popis` | krátký **ručně psaný** popis příspěvku pro veřejnou stránku Monitoring (jedna věta, bez jmen soukromých osob a telefonů; u příspěvků bez textu „Foto (bez textu)“, „Sdílený příspěvek profilu …“). Píše se při sběru měsíce; chybí-li, `summary.py` použije neutrální popis podle typu |
| `shared_from` | u sdílení: `url`, `page`, a pokud je původní příspěvek v datech, i `post_id`/`published` (text hledat u něj) |
| `attachments` | u odkazů: `title` + `url` přílohy |
| `media_count` | počet fotek v albu |
| `reactions`, `comments`, `shares` | počty ke dni `counts_as_of` (mění se, při opakovaném běhu se přepíší) |

Záměrně se **neukládají komentáře** (osobní údaje občanů) ani odkazy na
obrázky/videa z CDN Facebooku (do pár dnů vyprší). Případný plakát se stáhne do
`media/`.

Syrová data zůstávají oddělená od našeho zařazení. Až bude potřeba označit
příspěvky tématy sekcí (kalendář, tělocvična…), přidává se samostatné pole
`topics`/`note`, nikdy se nepřepisuje `text`.

## Postup běhu (Chrome, Claude in Chrome)

0. **Na začátku běhu upozornit uživatele, že musí mít záložku Chrome se
   skupinou Claude v popředí.** Skrytá záložka (`document.visibilityState ===
   "hidden"`) nenačítá další příspěvky a feed zůstane na šedých kostrách.
1. Otevřít `https://www.facebook.com/mestopecky`, počkat na načtení.
2. **Hned potom nainstalovat zachytávání odpovědí** (patch `window.fetch` a
   `XMLHttpRequest.prototype.open`, uložit odpovědi na `/api/graphql/` do
   `window.__G`). Musí to být před nastavením filtru — Facebook si dotazy
   cachuje, stejný dotaz podruhé na síť nejde.
3. Tlačítko **Filtry** u Příspěvků → Rok → Měsíc → Hotovo (měsíc březen je
   v nabídce popsán jako „3."). Filtr jen skočí na konec měsíce, feed pokračuje
   do minulosti.
4. Scrollovat, dokud nejstarší `creation_time` nepadne před 1. dne měsíce
   (cca 3,5 s čekání mezi kroky; nepouštět JS smyčku delší než ~40 s, nástroj
   vyprší a smyčka pak běží dál na pozadí).
5. Z odpovědí vybrat objekty `__typename: "Story"` s `post_id` a
   `creation_time` (duplicity sloučit podle `post_id`, ponechat úplnější),
   převést čas do Europe/Prague a vyfiltrovat jen příspěvky daného měsíce.
6. U každého příspěvku doplnit pole `popis` (viz tabulka polí). Zapsat `yyyy-mm.json`. Při opakovaném běhu stejného měsíce slučovat podle
   `id` a přepisovat jen počty a případně změněný `text`. Pak spustit
   `summary.py`.
7. **Kandidáti do jiných sekcí webu** (např. stavba tělocvičny → Tělocvična,
   plakát na akci → Kalendář, pozemky, zakázky): nic nepromítat samovolně.
   Na konci běhu je vypsat a **zeptat se uživatele, co s nimi dál.**
   Zprávy typu odstávka vody se nezpracovávají vůbec (historická, už
   nerelevantní data — rozhodnutí uživatele z 2. 10. 2026); nenabízet je ani
   jako kandidáty.

### Proč GraphQL a ne DOM

Desktopový Facebook záměrně rozbíjí datum příspěvku (v DOMu zbydou jen prázdné
uzly a desítky „Facebook" návnad) a mimo viewport příspěvky odstraňuje z DOMu.
Odpovědi GraphQL obsahují přesný čas, plný text a počty bez těchto překážek.
Facebook strukturu občas mění — při výpadku zkontrolovat klíče
(`creation_time`, `post_id`, `comet_sections…message.text`,
`feedback.reaction_count`, `comment_rendering_instance.comments.total_count`,
`share_count`).

## Poznámky

- Čtení probíhá pod přihlášením uživatele v jeho Chrome, v nízkém objemu a jen
  u veřejné stránky.
- Postup běhu je převedený do skillu `.claude/skills/pecky-online-facebook-monitoring/`
  (+ `capture.js` s pomocným kódem pro Chrome). Pravidelnost: měsíční rutina
  `pecky-online-facebook-monitoring-mesicne` (1. v měsíci v 10:00) stáhne chybějící
  uzavřené měsíce a přegeneruje stránku; vyžaduje Chrome s Facebookem a záložku v popředí.
