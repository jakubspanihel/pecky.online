# České pevné mezery (NBSP)

Pravidla pro veškerý český text na webu. **Ve zdrojích (`content/*.html`, JSON,
README) psát běžné mezery** — pevné mezery doplní automaticky:

- statický HTML text → `scripts/typografie.py` (volá ho `scripts/build.py`
  na každou stránku; upravuje jen textové uzly v `<body>`, ne značky,
  atributy, `<script>`, `<style>`, `<pre>`, `<code>`, `<textarea>`, `<title>`),
- text vkládaný skriptem za běhu → `peckyNbsp()` + MutationObserver na konci
  `assets/common.js`.

Pravidla držet v obou souborech shodná. Ruční `&nbsp;` jen jako výjimka.

## Pravidla (mezera → NBSP)
1. **Jednopísmenné předložky a spojky** `k s v z o u a i` (i velká): `v Praze`, `a proto`.
2. **Číslo + jednotka/symbol**: `100 km`, `5 kg`, `50 %`, `20 °C`, `1 500 Kč`, `4 500`
   (tisícové oddělovače). `50%` bez mezery se nemění (přídavné jméno: „50% sleva“).
3. **Data a čas**: `24. prosince`, `1. 5. 2026`, `14:00 hod.`
4. **Tituly a oslovení před jménem**: `Bc. Jan Novák`, `prof. MUDr. Jiří Bartoš`, `pan Novák`.
   (Jméno + příjmení se záměrně nespojuje — vznikaly by dlouhé nedělitelné úseky.)
5. **Zkratky + číslo**: `str. 45`, `obr. 3`, `tab. 12`, `čl. 5`, `§ 12`, `č. j. 123/2026`.

## Vícepísmenné předložky a spojky (doporučené / estetické)
Víceslabičné i kratší předložky a spojky by na konci řádku neměly zůstávat,
pokud to škodí čitelnosti nebo estetice (knižní sazba, delší články).
* **Pravidlo:** pevná mezera *za* těmito slovy (malá i velká první písmeno).
* **Dvoupísmenné:** `do`, `na`, `po`, `za`, `od`, `ve`, `ke`, `se`, `ze`, `že`, `či`, `atd.`
* **Tří- a víc písmen:** `pro`, `při`, `nad`, `pod`, `před`, `přes`, `bez`, `což`, `aby`, `když`.
* **Příklady:** `na stole`, `před domem`, `říkal, že přijde`, `aby věděl`.

## Pokyn pro AI
Nově psaný nebo upravovaný český text nemusíš NBSP vkládat ručně — build to
udělá. Po změně pravidel spusť `python3 scripts/build.py` a zkontroluj
falešné zásahy v `git diff`.
