# Postup: zápis akcí z plakátu do kalendáře

Referenční postup pro skill `pecky-online-kalendar-plakat`. Vstupem je
plakát nebo pozvánka kteréhokoli pořadatele akcí v Pečkách (kulturní
středisko, knihovna, spolek, škola, město) — obrázek přiložený v chatu,
soubor v repu, nebo odkaz na příspěvek na sociální síti či web. Výstupem jsou nové
nebo aktualizované záznamy v `kalendar/akce.json`, promítnuté do mřížky
i pohledu Seznam na `/kalendar/` (přepínač „Zobrazit jako: Kalendář /
Seznam", od 24. 9. 2026 bez samostatné podstránky `/kalendar/akce/`).

Datový model a pravidla zdroje popisuje `kalendar/README.md` → „Kulturní
a společenské akce — aktivní". Tenhle soubor je jen postup, ne druhý
zdroj pravdy o schématu.

## 1. Získat obrázek — a nejdřív zkontrolovat sociální sítě podle `sources.json`

- **Před ručním zpracováním jednoho plakátu: projít všechny facebookové
  a instagramové zdroje ze `sources.json` podle pravidla v
  `kalendar/README.md` → „Kulturní a společenské akce — aktivní"** (seznam
  se vytahuje ze `sources.json` znovu při každé kontrole, ne z pevného
  výčtu tady). U facebookových zdrojů vždy nejdřív `facebook.com/<profil>/events`
  (u skupin `facebook.com/groups/<id>/events`), ne fotky — kde organizátor
  Události zakládá, je datum/čas/místo hned jako strukturovaný text
  (`get_page_text`), bez čtení plakátu okem. Záložka „Nadcházející" je ta,
  co zajímá — existuje jen u organizátorů, co Události aktivně používají
  (u KD a TJ Sokol k 22. 9. 2026 nic, u knihovny ano). Zkontrolovat i proti
  už zapsaným akcím v `akce.json`, ne jen hledat nové — Události umí
  ukázat změnu termínu, kterou plakát/`evidence[0]` mlčky nezachytí (viz
  „S knížkou do života" u knihovny, `kalendar/README.md`). U instagramových
  zdrojů (nemají obdobu Událostí) projít mřížku posledních příspěvků okem.
- **Příloha v chatu nebo soubor v repu** — čti rovnou nástrojem `Read`.
- **Odkaz na příspěvek nebo webovou stránku** — otevři ho přes `claude-in-chrome`
  (`navigate` + `computer screenshot`). Plakát je obrázek bez textové
  vrstvy, `WebFetch` z něj nic nevytáhne.
- **Celý profil** (`https://www.facebook.com/kspecky/photos`) — `read_page`
  s filtrem `interactive` vypíše odkazy `photo.php?fbid=…` na jednotlivé
  fotky v pořadí od nejnovější; projdi je `navigate` + `screenshot`.

Program kulturního domu vychází ve dvou plakátech (září+říjen
a listopad+prosinec jako dva příspěvky téhož dne) — po zpracování prvního
vždy zkontroluj, jestli existuje pokračování, jinak polovina programu tiše
vypadne.

## 2. Přepsat text z plakátu

Plakát je hustá sazba drobným písmem. Celostránkový screenshot stačí na
rozvržení, ne na spolehlivý přepis — **na vlastní text použij `computer`
s akcí `zoom` po svislých pruzích** (jeden sloupec plakátu, výška zhruba
600 px na jeden výřez). Bez toho se pletou číslice v datech a časech.

Přepisuje se **doslova**, včetně překlepů a useknutých názvů pořadatele
(program 9–12/2026 má „ČKA – přednáška: Pohádky a jejich léčivá" bez
konce věty a „Česko zpívá koledy 2025" v prosinci 2026). Chybu
neopravuj — přepiš ji, jak je, a důvod napiš do pole `note`. Web stojí
na tom, že fakt je buď doložený zdrojem, nebo přiznaný jako mezera;
domyšlený název není ani jedno.

Nedohledatelný údaj zůstává prázdný:

- **čas** — „promítání po setmění" bez hodiny znamená `"time": null`
  (v kalendáři z toho bude celodenní akce). Upřesnil-li pořadatel čas
  v textu příspěvku nebo v komentářích, zapiš ho a do `note` uveď, že
  plakát sám uvádí jen „po setmění".
- **místo** — vypiš celé, jak ho plakát uvádí („Velký sál Kulturního
  domu Pečky", ne „velký sál").

## 3. Roztřídit na `akce` a `kurz`

- `kurz` — taneční kurzy a všechno, co na ně navazuje: „Kurzy
  společenského tance", „Prodloužená hodina" (odpolední i večerní),
  „věneček".
- `akce` — všechno ostatní: přednášky (ČKA, Pečecký okrašlovací spolek),
  divadlo, kino, koncerty, slavnosti, turnaje, adventní setkání, schůze
  spolků.

Kurzů bývá na plakátu skoro třetina; oddělená kategorie je proto, aby
šly v mřížce schovat filtrem.

## 3b. Určit pořadatele — a nezaměnit ho se zdrojem

Tohle jsou dvě různé věci a `akce.json` je drží zvlášť:

- **`organizer`** — kdo akci pořádá. Id v `lide/organizations.json`,
  rejstříku organizací celého webu (`kulturni-stredisko-pecky`,
  `mestska-knihovna-pecky`, `tj-sokol-pecky`,
  `pececky-okraslovaci-spolek`, `mesto-pecky`, `zs-pecky`…).
- **`evidence[].source`** — od koho o akci víme. Id v kořenovém
  `sources.json` (`facebook-kspecky`, `facebook-mestopecky`,
  `web-knihovna-pecky`, `facebook-tj-sokol-pecky`, `pecky-cz`…).

Sokolský turnaj ohlášený na facebooku města má `organizer: tj-sokol-pecky`
a `source: facebook-mestopecky`. Zaměnit je znamená tvrdit, že akci pořádá
někdo jiný, než ji pořádá.

Pořadatele ber z toho, co plakát říká, ne z toho, kde se akce koná: sál
kulturního domu si pronajme i cizí pořadatel. Neuvádí-li plakát pořadatele
vůbec a jde o položku v programu jednoho pořadatele, je jím ten pořadatel.
Odvodil-li ses pořadatele z názvu akce (program KD uvádí „Pečecký
okrašlovací spolek – přednáška"), napiš to do `note` — čtenář má poznat,
co je na plakátu a co dopočet.

**Pořadatel mimo rejstřík:** stálého pořadatele (spolek, škola, knihovna)
nejdřív založ v `lide/organizations.json` podle `lide/SPEC.md` — identifikaci
ověř v rejstříku (Hlídač státu podle názvu vrátí IČO) — a teprve pak se
odkazuj na jeho id. Jednorázového pořadatele (hostující divadelní soubor)
nezakládej: `organizer: null` a `organizer_name: "…"` textem.

## 4. Co vynechat

- **Jednání rady a zastupitelstva**, i když je program uvádí — kalendář
  je má z `jednani/pecky-jednani.json` a zápisem sem by na tentýž den
  vznikly dva odznaky. (Program 9–12/2026 takhle uvádí zastupitelstvo
  16. 9. 2026.)
- Akce bez data (celoroční nabídka, otevírací doba, kontakty).

## 4b. Plakát bez konkrétního data — pravidelná akce nebo kurz

Plakát, který neuvádí jedno konkrétní datum, ale pravidelný rytmus („každé
úterý a pátek od 15 hodin", „každou středu od 19:00"), se **nezahazuje**.
Pokus o zápis pravidelné akce se dělá vždy, když na plakátu není žádná
jednorázová akce s datem:

- `category: kurz` (pravidelné tréninky, kroužky, kurzy, hospodské kvízy).
- **Rytmus a čas přepsat doslova** (dny, hodina, místo, cílová skupina);
  do `description` jen to, co plakát říká (např. „Primárně pro děti
  1. až 3. tříd."). Kontakty do záznamu nepatří.
- **Začátek série:** uvádí-li plakát první termín, použít ho. Neuvádí-li,
  vzít první výskyt dne po datu přijetí e-mailu a do `note` napsat, že
  plakát začátek neuvádí a termín je dopočtený. Neznámé datum zveřejnění
  plakátu nevymýšlet.
- **Konec série:** výchozí horizont podle `kalendar/README.md` → „Kategorie"
  (konec školního roku 30. 6. 2027, prázdniny vynechat podle MŠMT); u
  plakátu bez vazby na školní rok a bez uvedeného konce platí variantu
  „Negarantováno" z téhož README (8 týdnů dopředu, každý záznam s poznámkou
  „Negarantováno").
- **Pořadatel** jako v kroku 3b (z plakátu, odvozený z názvu nebo loga
  vysvětlit v `note`). Chybí-li v `lide/organizations.json`, navrhnout jeho
  založení, ale nezakládat ho bez schválení.
- **Duplicity:** porovnat podle pořadatele, dne v týdnu, času a názvu s už
  zapsanými `kurz` záznamy (např. rozvrh TJ Sokol z Pečeckých novin). Shoda
  → nový záznam nevzniká, jen se navrhne doplnit `evidence`.
- V návrhu pro schválení uvést řádek „pravidelná akce": rytmus, první a poslední
  termín, počet vygenerovaných záznamů, jistota (čitelné / nejisté / dopočtené).
  Zápis jen po schválení stejně jako u jednorázových akcí.
- Nedá-li se z plakátu určit ani den, ani čas, zapsat nic nenavrhovat a výslovně
  napsat proč.

## 5. Porovnat s tím, co už v `akce.json` je

Shoda se hledá podle dvojice `date` + název:

- **Stejné datum i název** → záznam už existuje, nový nepřidávej. Je-li
  doklad z jiného zdroje, **přidej ho do `evidence`** téhož záznamu —
  dvě ohlášení nejsou dvě akce. Liší-li se čas nebo místo, přepiš je podle
  silnějšího dokladu (pořadí níže) a poražený údaj popiš v `note`.
- **Stejná akce, jiný název** (souhrnný program uvádí „Svatováclavský
  vinný košt" od 13:00, samostatný plakát „Slavnosti svatého Václava"
  od 15:00) → jeden záznam podle samostatného plakátu, rozpor do `note`,
  oba doklady do `evidence`. Dva záznamy na tutéž akci nezakládej.

**Pořadí zdrojů při rozporu:** vlastní kanál pořadatele → oficiální web
města → zpravodaj nebo tisk → přepis třetí strany. Mezi doklady téže
úrovně vyhrává novější podle `published`. První položka `evidence` je vždy
ta, podle které jsou zapsané údaje.
- **Termín z plakátu zmizel** → záznam v `akce.json` nech být a zmiň to
  ve výpisu změn. Zrušení akce se z nepřítomnosti na novějším plakátu
  spolehlivě odvodit nedá.

## 6. Zapsat

Do `kalendar/akce.json`:

1. **Doklad** do pole `evidence` u akce: `source` (id v kořenovém
   `sources.json` — **není-li tam zdroj ještě zapsaný, založ ho tam
   nejdřív**, viz krok 7), `kind` (`plakat` · `prispevek` · `web` ·
   `zpravodaj` · `tisk` · `ustni`), `url` (odkaz na konkrétní příspěvek
   nebo stránku, ne na profil), `label` (název konkrétního plakátu —
   u vícedílného programu i s částí), `published`, `retrieved` (dnešek).
2. **Akce** do pole `events`, pole podle `kalendar/README.md`. `id` má
   tvar `akce-RRRR-MM-DD-<slug názvu, první čtyři slova>`, při kolizi
   `-2`, `-3`. **Jednou zapsané `id` se už nemění** — drží `UID`
   v `kalendar.ics`, takže přejmenování by v kalendářích odběratelů
   založilo duplicitní událost.
3. `events` nech seřazené podle `date`, pak `time`.
4. `meta.updated` na dnešní datum.

Pak spusť:

```
python3 kalendar/scripts/update-kalendar.py
python3 scripts/build.py
```

První přegeneruje `udalosti.json` a `kalendar.ics` a sám je hned promítne
do veřejného Google kalendáře „Co se děje v Pečkách" (od 29. 9. 2026
automaticky, samostatný `sync-google.py` už nespouštět), druhý promítne
změnu do stránek (a zvaliduje HTML/JS). Popis synchronizace je
v `kalendar/README.md` → „Odebírání kalendáře".

**Chybí-li klíč, generátor synchronizaci sám vynechá (hláška „SYNCHRONIZACE PŘESKOČENA“) — nahlas to ve shrnutí.** `sync-google.py` čte
`.google-calendar-api-key.json` v kořeni repa; ten soubor je
v `.gitignore`, takže cloudový checkout ho nemá a skript by na něm spadl.
Neexistuje-li, do závěrečného výpisu (krok 8)
přidej řádek „Google kalendář čeká na synchronizaci — spustit
`python3 kalendar/scripts/sync-google.py` lokálně". Celý běh kvůli tomu
neukončuj, zbytek kroků na Googlu nezávisí.

## 7. Dopsat kontext

- `sources.json` — je-li zdrojem nový profil nebo web, přidej záznam
  a odkaz do quicklinks v sekci O webu. Facebook kulturního střediska
  (`facebook-kspecky`) tam je od 20. 9. 2026, u něj stačí případně
  upravit `note`. Zdroje pro akce, které už v rejstříku jsou:
  `facebook-kspecky`, `facebook-mestopecky`, `web-knihovna-pecky`,
  `facebook-knihovna-pecky`, `web-sokolpecky-cz`,
  `facebook-tj-sokol-pecky`, `pecky-cz`.
- `lide/organizations.json` — přibyl-li stálý pořadatel, ověř jeho
  identifikaci a založ ho (viz krok 3b); zmiň to i v `lide/README.md`.
- `README.md` → „Stav sekcí" — řádek Kalendář: datum kontroly vždy,
  datum změny a sloupec „Co naposledy" jen při reálné změně obsahu, pak
  řádek přesunout na správné místo v řazení.

## 8. Vypsat změny

Na závěr vypiš, co se změnilo: kolik akcí přibylo, kolik se
aktualizovalo, ke kterým akcím přibyl jen další doklad, které záznamy mají
`note` kvůli rozporu mezi zdroji, jestli přibyl pořadatel nebo zdroj do
rejstříků a co se do kalendáře vědomě nezapsalo (jednání, akce bez data).
Nenašel-li plakát nic nového, řekni to výslovně — „zkontrolováno, beze
změny".
