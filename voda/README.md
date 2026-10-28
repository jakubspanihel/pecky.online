# Instrukce k sekci: Voda (panel `voda`)

Referenční dokument pro práci na panelu `panel-voda` v
`content/voda.html` (generuje se do veřejné stránky `/voda/`, viz
`scripts/build.py`). Doplňuje obecné instrukce projektu (CLAUDE.md) —
tohle je detail jen pro tuhle jednu sekci.

## Účel sekce
Voda ve městě Pečky. Rozsah obsahu zatím není určen; stránka je založená
jako prázdná kostra.

## Stav
- Stránka je dostupná na `/voda/` a je zařazená v sekundárním menu
  v patičce (`assets/footer.html`, za Pokladnou); do overlay menu „Více...“
  se odkaz doplní automaticky ze stejného seznamu (`assets/common.js`).
- Obsah panelu žije v `content/voda.html`; data (`ceny.json`, `upravna.json`,
  `rozbory.json`) a obrázky patří do této složky (`voda/`).

## Data: `ceny.json`
Ceník vodného a stočného po letech (Kč/m³, bez DPH a s DPH). Jeden záznam
v `years` na rok, nejnovější nahoře; `celkem` = vodné + stočné.
- 2025: zdroj je tabulka na pecky.as4u.cz (DPH 12 %, stav ověřen
  15. 10. 2026). Starší roky zdrojová stránka neuvádí.
- 2011 a 2014–2022 (15. 10. 2026): z fulltextu Pečeckých novin
  (`noviny/pecky-noviny.json`), u každého roku odkaz na číslo a stranu PDF
  v `source`. Chybí 2012, 2013 a 2024 — zápisy ZM uvádějí
  u roku 2024 jen informaci o schválení valnou hromadou Pečeckých
  služeb, bez částek (viz pole `gaps`).
- 2023 (25. 10. 2026): z oznámení Pečeckých služeb „Cena vodného a stočného od 1. 1. 2023“ (archivní kopie web.archive.org z 16. 6. 2024; živá stránka už vrací 404), DPH 10 %.
- 2026: z webu Pečeckých služeb (stránka Pečky, stav 15. 10. 2026). 2017: zdroj uvádí jen ceny bez DPH.
- Stránka as4u.cz se od cca 3/2026 neaktualizuje (viz CLAUDE.md), proto
  ceník na rok 2026 je potřeba dohledat na pecky.cz.

## Data: `upravna.json`
Blok „Úpravna vody“ (Úpravna vody Pečky, zdroj Tatce): tabulka základních
údajů (`summary.facts`), shrnutí (`summary.text`), mezery ve zdrojích
(`summary.gaps`) a časová osa (`events`, řazená při vykreslení od nejnovější;
`date` je `RRRR-MM-DD` nebo `RRRR-MM` u měsíčních zdrojů, `sources` odkazuje
na `/jednani/#<id>`, PDF Pečeckých novin se stránkou, Hlídač státu, úřední
desku nebo Facebook města). Vznikl 15. 10. 2026 průchodem zápisů jednání
(rada, zastupitelstvo 2008–2025) a fulltextu Pečeckých novin.
- Ověřené údaje: cena smlouvy o dílo 47,4 mil. Kč bez DPH (Hlídač státu,
  zakázka z 30. 6. 2022), celkové náklady 48 048 570,53 Kč bez DPH a dotace
  34 313 554,99 Kč (Pečecké noviny 4/2024, s. 5).
- Mezery: výše pachtovného a částky dodatků nejsou v zápisech; Pečecké
  noviny 3/2023 mají u zahájení stavby překlep („září 2023“, správně 2022).

## Data: `rozbory.json`
Laboratorní protokoly o zkoušce pitné vody (Vodohospodářská společnost
Vrchlice – Maleč, objednatel Pečecké služby) — 32 protokolů, únor 2016 –
červen 2025. PDF jsou v `voda/rozbory/<id>.pdf` (originály z
pecky.as4u.cz/filemanager/files/<id>.pdf, popisy v
`_WORKING/voda-rozbory/index.json`). `python3 voda/update-rozbory.py`
přečte text PDF (`pdftotext -layout`) a vygeneruje `rozbory.json`
(`samples[]`: `date`, `misto` (sjednocený název místa pro filtr),
`misto_orig`, `protokol`, `pdf`, `params{název: {v, u, op, limit, ok}}`).
- 7 protokolů je naskenovaných bez textové vrstvy; jejich hodnoty jsou
  ručně přepsané z obrázků do `rozbory-sken.json` (u 2017–2019 jen první
  strana s ukazateli do boru; organické látky a těžké kovy z další strany
  nejsou přepsané — jsou v PDF).
- Protokoly 291732 (5/2017), 365019 (12/2017), 378524 (3/2018) a 429401
  (2/2019) nemají na zveřejněné straně datum odběru; `date` je měsíc
  z názvu dokumentu (`date_approx`), v grafu 15. den měsíce.
- Sjednocení míst: „Pečky, VDJ upravená“ = „Pečky VDJ“ = „Pečky VD“
  (vodojem). „OU“ je ponecháno beze zkratky rozvádění (význam v protokolu
  není uveden).
- Nové protokoly: stáhnout PDF do `voda/rozbory/`, doplnit řádek do
  `_WORKING/voda-rozbory/index.json`, spustit generátor a build.

## Data: `vodojem.json`
Stejná struktura jako `upravna.json` pro záložku „Vodojem“ (`summary.facts`,
`summary.text`, `summary.gaps`, `events` s datem `RRRR-MM-DD` nebo `RRRR-MM`).
Sestaveno 16. 10. 2026 z Pečeckých novin (historie, rozměry, projektant,
památková ochrana), zápisů rady a zastupitelstva 2016–2026 a úřední desky.
Ověřeno v novinách: projektant Dr. Ing. František Uher, schválení projektu
25. 7. 1930, provoz od 1. 7. 1932, kulturní památka od 9. 9. 2011 (č. ÚSKP
104468), parametry (325 m³, 39,02 m). Mezery: cena opravy, výsledek žádosti
o dotaci z 2021, jména firem u části nájmů.

Stránka `/voda/` má pod ceníkem a rozbory dvě záložky (`.subtabs`, hash
`#upravna` a `#vodojem`), obě se vykreslují stejnou funkcí `blok()` v
`content/voda.html`.

## Data: `havarie-odstavky-vody.json`
Havárie, odstávky a omezení dodávky pitné vody z Facebooku města a od
23. 10. 2026 i z aktualit Pečeckých služeb (od 1. 12. 2018 do 27. 10. 2026,
58 událostí, 68 zdrojů). Z tohoto souboru se kreslí sloupce počtu událostí
za rok v grafu na `/voda/` — po zápisu nové události spustit build. Struktura je v
`meta.pole` souboru. Soubor zatím nemá vykreslení na stránce `/voda/`.
Doplňuje se při týdenní kontrole aktualit Pečeckých služeb (typy Havárie a Oznámení, postup v
`.claude/skills/DoPecek-update/SKILL.md`, bod „Aktuality Pečeckých služeb“) a při měsíčním
monitoringu Facebooku (krok 7 v
`o-webu/facebook-monitoring/README.md`) — nové události se zapisují bez
dotazu, opakovaná oznámení se slučují. Pokrytí starších let (2018–2024) je
řidší než 2025–2026; úřední deska odstávky vody neobsahuje (jen elektřiny).

## Postup práce
Obecná pravidla (needitovat vygenerovaný `voda/index.html`, upravit
`content/voda.html` a spustit `python3 scripts/build.py`) jsou v
kořenovém `CLAUDE.md`. Zdroje a zvláštní pravidla doplnit sem, až vzniknou.
