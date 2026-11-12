# Hledání nových akcí a změn provozu na sociálních sítích (Claude in Chrome)

Samostatná rutina, která projde **všechny** účty ze seznamu Sociální sítě
v [O webu](../o-webu/README.md) (`content/owebu.html`, blok
`#subpanel-owebu-socialni`) a hledá v nich budoucí akce pro Kalendář a
změny běžného provozu. Odděleně od kontroly počtů a dat poslední aktivity
(`o-webu/automation-socialni-site.md`) — ta je rychlá a mechanická, tahle
je pomalá a čtená obsahově, proto každá běží vlastním naplánovaným úkolem
s vlastním časem a kontextem.

Spouští ji skill `DoPecek-nove-akce-check`. Samotný zápis nalezených akcí
řídí `kalendar/automation-plakat-akce.md` (skill `DoPecek-kalendar-plakat`) —
tady je jen sběr kandidátů a evidence průchodu.

## Kdy spustit

Denně, po kontrole počtů sledujících (ta běží v 9:00; Chrome je jen jeden,
oba běhy se nesmí překrývat). Běh není hotový, dokud nejsou projité všechny
účty — viz „Úplnost běhu“ níže. Není-li Chrome (`claude-in-chrome`)
připojené, běh přeskoč, nic neměň a napiš, že je potřeba ho spustit ručně
z lokální relace s Chrome.

## Postup

### 0. Výchozí stav a seznam účtů

1. Nespustil-li tě jiný skill, ulož výchozí stav repa:
   `python3 .claude/skills/DoPecek-commit/snapshot.py save --file <scratchpad>/git-baseline.json`.
2. Přečti `kalendar/automation-plakat-akce.md` (krok „Pořadí zdrojů“ a
   krok 1b) a `kalendar/README.md` → „Kulturní a společenské akce — aktivní“.
3. **Seznam účtů ber vždy z aktuálního `content/owebu.html`** (odkazy
   `a.qlink` v bloku `#subpanel-owebu-socialni`), ne z paměti. Řádek,
   který není sociální sítí (rezervační systém FitPečky), přeskoč a ve
   výpisu uveď. Duplicitní odkazy (stejné URL dvakrát) projdi jednou.
4. **Datum poslední kontroly** = datum nejnovějšího záznamu
   „Nové akce ze sociálních sítí“ v `HISTORIE.md`; nenajdeš-li ho, vezmi
   posledních 6 měsíců. Fotky a příspěvky se čtou jen od tohoto data.
5. **Pokračování po neúplném běhu:** záznam v `HISTORIE.md` z minulého
   běhu uvádí účty, které zůstaly neprojité. Ty projdi jako první.
6. Založ si v scratchpadu kontrolní seznam (`akce-checklist.md`): jeden
   řádek na účet — `[ ] účet | události | příspěvky | fotky`. Políčko
   odškrtni teprve po přečtení dané záložky, ne předem.

### 1. Průchod účtu — Facebook stránka

Čtení dělej dávkou `browser_batch` po 6–8 účtech (navigate + wait 4 s +
`javascript_tool`), jeden účet = jeden blok. Pro každý účet tři zdroje:

**a) Události** — `<profil>/events`, sekce „Nadcházející“ (u profilů
s `profile.php?id=` použij `…&sk=events`). Skript vypíše text od slova
„Události“:

```js
const t=document.body.innerText;const j=t.indexOf('Události');
t.slice(j,j+600).replace(/\n+/g,' | ')
```

Je-li první nadpis „Uplynulé“ (bez „Nadcházející“), žádná budoucí událost
není. Prázdný výstup nebo jen navigace (typicky u Pečeckých služeb, ZŠ
Pečky, AFK) **není „žádná událost“** — zopakuj načtení (delší wait, nebo
`get_page_text`); nepodaří-li se, účet jde do mezer.

**b) Příspěvky od poslední kontroly** — otevři profil a přečti texty
příspěvků novějších než datum poslední kontroly (`get_page_text`, případně
rozkliknout „Zobrazit více“). Hledej konkrétní datum nebo čas v budoucnu,
plakát, pozvánku, výzvu k přihlášení, zmínku „zveme vás“. Čas příspěvku
dává `creation_time` (viz `o-webu/automation-socialni-site.md`, krok 2b).

Zároveň hledej **zrušení a změny** už zapsaných akcí (*zrušeno, ruší se,
odloženo, přesunuto, změna termínu/času/místa, nekoná se, z důvodu nemoci*)
a porovnej je s akcemi v `kalendar/akce.json` — zapisuje se podle kroku 5a.

**c) Fotky** — `<profil>/photos` (u skupin `groups/<id>/media`). Plakáty a
pozvánky bývají jen obrázek bez textu. Čtou se fotky přidané od data
poslední kontroly, nejnovější první; **plakát se čte vizuálně**
(`screenshot` + `zoom`), ne z textu. Na plakátu hledej i **nápis o zrušení či změně**
(„ZRUŠENO“, „odloženo“, přeškrtnutý termín) — oznámení bývá jen obrázek
bez textu, a to i u příspěvků. Dlaždice bez změny od poslední kontroly
nečti znovu. Při prvním průchodu účtu nebo po vynechané kontrole delší než
týden čti archiv fotek od nejnovější do data poslední kontroly (u nového
účtu aspoň 6 měsíců).

### 2. Průchod účtu — Facebook skupina

Skupiny nemají Události ve stejném tvaru: projdi příspěvky od poslední
kontroly (`get_page_text`) a `groups/<id>/media`. Události skupiny najdeš
na `groups/<id>/events`.

### 3. Průchod účtu — Instagram

Příspěvky otevři jako při zjišťování data (krok 2b v
`o-webu/automation-socialni-site.md`) — skriptem, který klikne na první
5–6 dlaždic a přečte `<time datetime>`. **Rozšiř skript o čtení obsahu**:
vedle `datetime` vrať i popisek (`h1`, případně `div[role=dialog] span`
s textem) a u příspěvků novějších než datum poslední kontroly otevři
plakát vizuálně. Mřížka není chronologická (připíchnuté příspěvky), proto
rozhoduje datum, ne pozice dlaždice.

### 4. Co je akce a co ne

Do Kalendáře patří budoucí akce s konkrétním dnem (nebo obdobím) a místem
v Pečkách či okolí, na které se může přijít. Vynech: prodejní nabídky,
jídelní lístky, výsledky zápasů, vzpomínky na proběhlé akce, obecné
„zvu vás“ bez data. Co přesně a jak se zapisuje, určuje
`kalendar/automation-plakat-akce.md`. Před zápisem vždy ověř, že akce už
v `kalendar/akce.json` není (shoda podle dne + času + místa/pořadatele —
viz `CLAUDE.md` → „Konvence“ → „Jedna akce = jeden záznam“); existující
akci jen doplň o doklad (`evidence`).

### 5. Změny provozu

U **každého** účtu hledej i příspěvky, které mění běžný provoz zdrojů
generovaných Kalendářem z pravidel: *zavřeno, uzavřen, mimořádná nebo
změněná otevírací doba, posunutý/náhradní/zrušený svoz, odložená zkouška
sirén, výpadek, uzavírka*. Bývají kolem státních svátků a prázdnin. Zvlášť
pozorně projdi **Pečecké služby** (`facebook.com/pececkesluzby`) a **Město
Pečky**. Zápis:

- sběrný dvůr, zkouška sirén, další provozní doby → `exceptions[]`
  v `kalendar/sberny-dvur.json` / `zkouska-siren.json` (termín zůstane,
  název dostane „[zavřeno]“; schéma viz `kalendar/README.md` → „Provozní
  doba: Sběrný dvůr“), doklad = odkaz na příspěvek v `url`;
- svoz odpadu → `exceptions[]` u typu svozu v `kalendar/svoz-odpadu.json`
  (název „[zrušeno!]“); mimořádný/náhradní svoz jako samostatná akce podle
  `kalendar/README.md`;
- pak `python3 kalendar/scripts/update-kalendar.py` (Google sync dělá sám).

### 5a. Zrušené a změněné akce

U **každého** účtu hledej i příspěvky, které **zrušují nebo mění akci**,
jež už je v `kalendar/akce.json` (*zrušeno, ruší se, odloženo, přesunuto,
změna termínu/místa*). Akci najdi podle dne + pořadatele/místa (stejně jako
při duplicitách). Příspěvek musí akci výslovně zrušit — zrušení se
z nepřítomnosti na plakátu odvodit nedá.

- **Zrušení** → před `title` přidej prefix **`[ZRUŠENO!] `** (přesně takto,
  jednotně u všech akcí), do `note` stručně, co pořadatel oznámil
  a proč (datum příspěvku, důvod, bez „my“) a nový doklad
  (`kind: "prispevek"`, `url` přímo na příspěvek, `published`, `retrieved`)
  přidej na **konec** `evidence` (`evidence[0]` zůstává původní).
  Akce se nemaže. Je-li zrušená akce z řady (kurz, týdenní konání),
  zrušit jen dotčený termín, ne celou řadu.
- **Změna času/místa/termínu** → uprav údaje v záznamu, starý údaj zmiň
  v `note`, doklad přidej do `evidence` (pravidlo „aktuální údaje z novějšího
  zdroje“ viz `CLAUDE.md` → „Konvence“).
- Zápis, `update-kalendar.py` (Google sync dělá sám) a `build.py` jako
  v kroku 6. Změny **provádět rovnou**, neptat se; vyjmenovat je až
  ve výpisu na konci běhu (u každé akce: co, kdy, odkaz na příspěvek).
- **Příspěvek bez data akce** („dnešní představení se ruší“): akci urči
  podle pořadatele a dne příspěvku — kandidát je jediná akce téhož
  pořadatele v nejbližších dnech (u „dnes“/„zítra“ v ten den). Je-li
  kandidátů víc nebo žádný, nezapisuj a nahlas.
- Nejasné případy (příspěvek nejde přiřadit k jedné akci, rozpor mezi
  zdroji) nezapisovat, nahlásit ve výpisu.

### 6. Zápis, build a kontrola

1. Nalezené akce zapiš podle `kalendar/automation-plakat-akce.md`
   (`akce.json` upravuj nástrojem Edit, ne skriptem), pak
   `python3 kalendar/scripts/update-kalendar.py` a `python3 scripts/build.py`.
2. Řádek Kalendář ve „Stav sekcí“ (`README.md`) přepiš jen při reálné
   změně obsahu (datum kontroly vždy); záznam „Nové akce ze sociálních
   sítí“ přidej nahoru `HISTORIE.md` **vždy**, i když nic nového nebylo
   (je to zároveň evidence data poslední kontroly pro příští běh).
3. Commit jen vlastních změn (`DoPecek-commit`) a push podle `CLAUDE.md`
   → „Git / GitHub“. Nezměnilo-li se nic v repu, necommituj; záznam do
   `HISTORIE.md` ale změnou je, takže se commituje.

## Úplnost běhu (povinné)

Běh smí hlásit „projito N z N“ jen tehdy, když jsou v kontrolním seznamu
odškrtnuté **všechny tři zdroje** (události, příspěvky, fotky; u
Instagramu a skupin ty, které se na dané síti dají otevřít) u každého
účtu. Jinak:

- ve výpisu i v záznamu `HISTORIE.md` napiš **„NEÚPLNÉ“**, kolik účtů
  z kolika je projito, a jmenovitě které účty nebo záložky zůstaly
  (příští běh začne od nich);
- nikdy nepiš „nové akce: žádné nalezeny“ bez dodatku „(projito N z M)“;
- účet, jehož záložku se nepodařilo načíst, je mezera, ne „nic nenalezeno“.

## Výpis na konci běhu

Podle `CLAUDE.md` → „Konvence“: u každého dotčeného souboru jednou větou,
co a proč se změnilo; „zkontrolováno, beze změny“ tam, kde se nic nenašlo.
Dále:

1. **Projito N z M účtů** (a které chybí), z toho s projitými Událostmi /
   příspěvky / fotkami.
2. **Nové akce pro Kalendář:** název, datum, pořadatel a co se s nimi stalo
   (nová / doplněný doklad k existující / vynechána a proč) — nebo
   výslovně „žádné nalezeny (projito N z M)“.
3. **Změny provozu:** např. „sběrný dvůr zavřen 28. 10.“ — nebo výslovně
   „žádné nalezeny“.
4. Mezery: účty a záložky, které se nepodařilo přečíst.
