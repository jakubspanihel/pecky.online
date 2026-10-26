# Na oběd — Denní menu v Pečkách (`/naobed/`)

Stránka s posledním denním menu vybraných pečeckých restaurací. Restaurace
zveřejňují menu na Facebooku jako fotografii jídelního lístku; stránka
zobrazuje poslední stažený snímek u každé z nich.

## Soubory

| Soubor | Účel |
|---|---|
| `content/naobed.html` | tělo stránky (horizontálně posuvné karty stejné výšky, vykreslené JS z JSON níže) |
| `naobed/restaurace.json` | seznam restaurací na stránce: `id` (= `id` v `lide/organizations.json`), název, adresa, telefon, Facebook, web |
| `naobed/menu.json` | index: pro každé `id` poslední menu (`file` a `date`, cesta od `naobed/`), `checked` (den kontroly), případně `notice` |
| `naobed/data/<id>/RRRR-MM.json` | archiv přepisů jednoho měsíce: `schema`, `restaurace`, pole `dny` se záznamy dnů (viz níže) |
| `naobed/img/<id>/RRRR-MM-DD.jpg` | stažené fotografie menu; datum v názvu = den, který je na lístku (ne den stažení) |
| `naobed/scripts/zapis-menu.py` | zapíše záznam dne do `data/` a aktualizuje `menu.json` (volá ho skill) |

Přidání restaurace: záznam do `lide/organizations.json` (+ zdroj do
`lide/sources.json`), řádek do `naobed/restaurace.json`, pak skill.

## Záznam dne

Jeden den v `dny` (a soubor pro `zapis-menu.py`):

```json
{
  "date": "2026-10-23",
  "photo": "img/sinorita-pecky/2026-10-23.jpg",
  "checked": "2026-10-26",
  "polevky": [{"nazev": "Česnečka", "objem": "0,33 l", "cena": 39}],
  "menu": {"nazev": "Plněné bramborové knedlíky uzeným masem, zelí", "cena": 139},
  "jidla": [{"nazev": "Smažený vepřový řízek, bramborový salát", "gramaz": "150 g", "cena": 139}],
  "ostatni": [{"nazev": "Okurkový salát", "gramaz": "150 g", "cena": 45}],
  "poznamka": "Na pondělí: Segedínský guláš, houskové knedlíky."
}
```

- `date` a `photo` jsou povinné; `photo` je cesta od `naobed/`. `menu` (paušální
  menu s polévkou), `polevky`, `ostatni` (přílohy, saláty, pití, omáčky) jsou
  volitelné. Pole `polevky`, `jidla` a `ostatni` jsou seznamy položek
  `{nazev, gramaz?, objem?, cena}`.
- `cena` je celé číslo v Kč, `gramaz` a `objem` jsou text (`"150 g"`, `"0,33 l"`).
- `checked` se doplní jen u posledního zachyceného dne (den kontroly). Starší záznamy ho nemají.
- Přepis je odečtený z fotografie, ne z oficiálního zdroje. Nečitelné položky se vynechají a uvedou v `poznamka`.

Zápis: `python3 naobed/scripts/zapis-menu.py <id> záznam.json` (nebo
`--checked` pro restauraci bez nového menu). Skript den přepíše, pokud už v
měsíčním souboru je, a `menu.json` nastaví na nejnovější den.

## Otevírací doba

Týdenní otevírací doba je u organizace v `lide/organizations.json`
(`opening_hours`, popis polí v `lide/SPEC.md`); stránka z ní ukazuje řádek
„Dnes otevřeno …“ / „Dnes zavřeno“, celý týden je v tooltipu. Zdroje:
web podniku (Western Saloon, Pizza Maximo) nebo Mapy.com (U Marka, Siňorita,
Samer Kebab; na Facebooku je jen „teď je zavřeno“). Hostinec U Stříkačky: Facebook (dialog „Otevřeno“ v levém sloupci profilu),
údaj starý asi 3 roky. U Asia&Wok je doba jen v poznámce (stránka je
zastaralá, podnik se přestěhoval) a u Hospůdky Velké Chvalovice se nenašla —
řádek se nezobrazuje.

## Postup aktualizace

Skill `DoPecek-obedy` (`.claude/skills/DoPecek-obedy/SKILL.md`):
otevře Chrome, na facebookové stránce každé restaurace stáhne fotografii
nejnovějšího menu, uloží ji do `naobed/img/<id>/`, přepíše lístek do záznamu
dne a zapíše ho přes `naobed/scripts/zapis-menu.py` do `naobed/data/` a
`menu.json`, pak spustí `python3 scripts/build.py`.

## Poznámky

- Školní jídelna (`skolni-jidelna-pecky`, v `restaurace.json` s `jidelnicek: true`) nemá fotografii: karta vypisuje
  dnešní (jinak nejbližší další) den z `naobed/jidelna.json`, který se přepisuje z textu na
  https://www.zspecky.cz/jidelna/jidelnicek/ (polévka, 2 hlavní jídla, alergeny v závorce)
  skriptem `python3 naobed/scripts/update-jidelna.py` (`--check` jen ověří, jestli soubor
  má dnešek; dny starší 7 dní zahodí). Spouští ho ranní rutina spolu se skillem.
- Oznámení restaurace (zavřeno, nevaří, změna): položka `notice` u restaurace v `menu.json`
  (`date` = den platnosti, `chip` = krátká informace, `text` = text příspěvku, případně zkrácený,
  `url` = odkaz na příspěvek). Karta ji ukazuje jen v den `date`: chip v záhlaví a blok s textem
  a odkazem nad fotografií. Skill při neúspěšném hledání menu projde poslední příspěvky a takové
  oznámení zapíše.
- Staré fotografie se nemažou (archiv menu); stránka ukazuje jen tu z
  `menu.json`.
- Je-li `date` jiné než dnešní, karta má štítek „menu z <datum>“ místo
  „menu na dnes“.
- Facebooková stránka Asia&Wok, Samer Kebab a Western Saloon denní menu
  nezveřejňují (kontrola 4. 10. 2026), proto nejsou na stránce.
