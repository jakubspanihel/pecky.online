# Instrukce k sekci: Prostory (`/prostory/`)

Referenční dokument pro práci na sekci Prostory (`content/prostory.html`).
Doplňuje obecné instrukce projektu (`CLAUDE.md`) — tohle je detail jen pro
tuhle jednu sekci.

## Účel sekce
Přehled **nebytových prostor**, které město Pečky pronajímá nebo půjčuje
(ordinace ve zdravotním středisku, Dům služeb, prodejny, ochoz vodárenské
věže, kanceláře). U každého prostoru: záměr pronájmu → smlouva → dodatek →
ukončení, vždy s odkazem na usnesení rady v `/jednani/`.

Mimo rozsah: byty, pozemky (sekce Pozemky), místa v garážích, jednorázové
půjčení sálů a Parkhaly.

## Datový tok
- `prostory/prostory.json` — **ručně vedený** seznam prostorů. Každá událost
  je odkaz na usnesení (`n`, např. `UR-304-34/26`) a/nebo na dokument úřední
  desky (`deska`: číslo dokumentu z `o-webu/uredni-deska-monitoring/<rok>.txt`,
  např. `382845`, nebo `as4u:<id>` pro starý web) + ručně přepsaná poznámka
  `pozn` s ověřenými čísly (nájemné, doba, plocha). Datum a odkaz na jednání
  se dopočítají z `jednani/pecky-jednani.json`, datum vyvěšení a sejmutí a
  odkaz na detail z `<rok>.txt`. Záměr schválený radou a vyvěšený na desce je
  jedna událost s `n` i `deska`; starší záměr bez usnesení má jen `deska`.
  Generátor selže, pokud `n` nebo `deska` neexistuje, a vypíše POZOR, když se
  datum vyvěšení liší od usnesení o víc než 21 dní.
- Fulltext příloh desky (`o-webu/uredni-deska-monitoring/Text/`) je jen lokální
  (v `.gitignore`) — z něj se čísla přepisují ručně, generátor ho nečte.
- `prostory/update-prostory.py` — přegeneruje část `content/prostory.html`
  mezi `<!-- PROSTORY:START -->` a `<!-- PROSTORY:END -->` (banner právě
  vyhlášeného záměru, souhrn, přehledová tabulka, historie po prostorech).
  Selže, pokud usnesení `n` v datech jednání neexistuje.
- Poté vždy `python3 scripts/build.py`.

```
python3 prostory/update-prostory.py
python3 scripts/build.py
```

## Pravidla
- **Jména fyzických osob se neuvádějí** (v usneseních jsou začerněná, i když
  se občas objeví v názvu bodu nebo textu). Uvádět jen firmy, spolky,
  organizace; u fyzické osoby jen roli („lékař“, „fyzická osoba“).
- Stav prostoru (`stav`) se určuje z **posledního usnesení** — `zamer`
  (nabídky se ještě přijímají; vyplnit `uzaverka`, případně `uzaverka_cas`
  a `nabidka`), `pronajato`, `vypujceno`, `volne` (záměr bez smlouvy),
  `ukonceno`, `neznamy` (záměr z desky bez navazujícího usnesení či smlouvy). Nejasnosti (např. usnesení neuvádí, o jaký prostor jde)
  patří do `poznamka_stav`, ne do domněnky.
- Banner se po termínu `uzaverka` nevykreslí až při dalším běhu generátoru;
  po týdenní kontrole Jednání proto skript pouštět vždy.

## Postup při nové kontrole
1. Po aktualizaci Jednání projít nová usnesení rady hledáním: „prostor
   sloužící podnikání“, „nebytov“, „výpůjčk“, „ochoz vodárenské věže“,
   „záměr na pronájem“ (ne pozemky ani byty).
2. Nová událost → přidat do `events` stávajícího prostoru, nový prostor →
   nový záznam; přehodit `stav` / `stav_text` / `podminky`.
3. Spustit generátor a build, zapsat řádek do `README.md` → „Stav sekcí“.

## Úřední deska
Od 6. 10. 2026 jsou v přehledu záměry z úřední desky 2015–2026
(`vyhlašované záměry města`, výběr podle názvu). Vynecháno: pronájem budovy
ZUŠ čp. 700 (celá škola, 2015 a 2017), pozemky, byty, prodej majetku.
Hraniční objekty (hasičská zbrojnice ve Velkých Chvalovicích, chata u
Benešáku) jsou zařazeny. Při týdenní kontrole se nový záměr hledá v
`<rok>.txt` podle názvu („záměr“ + pronájem/výpůjčka) a připojí k usnesení
rady.
