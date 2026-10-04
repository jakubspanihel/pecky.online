# Na oběd — Denní menu v Pečkách (`/naobed/`)

Stránka s posledním denním menu vybraných pečeckých restaurací. Restaurace
zveřejňují menu na Facebooku jako fotografii jídelního lístku; stránka
zobrazuje poslední stažený snímek u každé z nich.

## Soubory

| Soubor | Účel |
|---|---|
| `content/naobed.html` | tělo stránky (3 horizontální karty, vykreslené JS z JSON níže) |
| `naobed/restaurace.json` | seznam restaurací na stránce: `id` (= `id` v `lide/organizations.json`), název, adresa, telefon, Facebook, web |
| `naobed/menu.json` | poslední stažené menu pro každé `id`: `file` (cesta od `naobed/`), `date` (den, pro který menu platí), `checked` (den kontroly) |
| `naobed/img/<id>/RRRR-MM-DD.jpg` | stažené fotografie menu; datum v názvu = den, který je na lístku (ne den stažení) |

Přidání restaurace: záznam do `lide/organizations.json` (+ zdroj do
`lide/sources.json`), řádek do `naobed/restaurace.json`, pak skill.

## Postup aktualizace

Skill `pecky-online-obedy` (`.claude/skills/pecky-online-obedy/SKILL.md`):
otevře Chrome, na facebookové stránce každé restaurace stáhne fotografii
nejnovějšího menu, uloží ji do `naobed/img/<id>/`, přepíše `naobed/menu.json`
a spustí `python3 scripts/build.py`.

## Poznámky

- Staré fotografie se nemažou (archiv menu); stránka ukazuje jen tu z
  `menu.json`.
- Je-li `date` jiné než dnešní, karta má štítek „menu z <datum>“ místo
  „menu na dnes“.
- Facebooková stránka Asia&Wok, Samer Kebab a Western Saloon denní menu
  nezveřejňují (kontrola 4. 10. 2026), proto nejsou na stránce.
