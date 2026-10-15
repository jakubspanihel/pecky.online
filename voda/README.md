# Instrukce k sekci: Voda (panel `voda`)

Referenční dokument pro práci na panelu `panel-voda` v
`content/voda.html` (generuje se do veřejné stránky `/voda/`, viz
`scripts/build.py`). Doplňuje obecné instrukce projektu (CLAUDE.md) —
tohle je detail jen pro tuhle jednu sekci.

## Účel sekce
Přehled městské vody v Pečkách: ceník vodného a stočného, laboratorní rozbory,
úpravna vody, čistírna odpadních vod, vodovody a vodojem, majetek a provozovatel
(Pečecké služby, fondy obnovy) a dešťová voda. Typ stránky: tematický rozcestník
(více samostatných příběhů), ne jedna časová osa. Pořadí na stránce: perex →
stat-grid → „Kde to teď stojí“ → ceník (graf) → rozbory (graf) → čistírna,
vodovody a vodojem (tabulka projektů + osy) → úpravna (osa) → majetek (tabulky)
→ dešťová voda (osa). Každý blok má vlastní „Co zdroje neříkají“.

## Stav
- Stránka je dostupná na `/voda/`, ale **není zařazená v žádném menu**
  (ani v hlavní navigaci, ani v sekundárním menu v `assets/footer.html`).
  Zařazení do menu je samostatné rozhodnutí.
- Obsah panelu žije v `content/voda.html`; data a obrázky patří do této
  složky (`voda/`). Datové sady: `ceny.json`, `upravna.json`, `rozbory.json`
  (+ `rozbory-sken.json`), `infrastruktura.json`.

## Data: `ceny.json`
Ceník vodného a stočného po letech (Kč/m³, bez DPH a s DPH). Jeden záznam
v `years` na rok, nejnovější nahoře; `celkem` = vodné + stočné.
- 2025: zdroj je tabulka na pecky.as4u.cz (DPH 12 %, stav ověřen
  15. 10. 2026). Starší roky zdrojová stránka neuvádí.
- 2011 a 2014–2022 (15. 10. 2026): z fulltextu Pečeckých novin
  (`noviny/pecky-noviny.json`), u každého roku odkaz na číslo a stranu PDF
  v `source`. Chybí 2012, 2013, 2023 a 2024 — zápisy ZM uvádějí
  u let 2023 a 2024 jen informaci o schválení valnou hromadou Pečeckých
  služeb, bez částek (viz pole `gaps`).
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

## Data: `infrastruktura.json`
Tři bloky, vznikl 15. 10. 2026 průchodem bodů programu a usnesení rady
a zastupitelstva (`jednani/*.json`) a Hlídače státu.
- `projekty[]` — čistírna (`cov`), Bačov (`bacov`), přivaděč Tatce–Pečky
  (`privadec`), vodojem (`vodojem`): `title`, `rok`, `stav` (jedna věta podle
  posledního zápisu), `text`, `gaps`, `events[]` (`date`, `title`, `text`,
  `sources[]` = `{label, url}`; odkazy na `/jednani/#rada-RRRR-MM-DD` nebo
  `#zastupitelstvo-RRRR-MM-DD`).
- `majetek` — `facts`, `text`, `najemne[]` (roční nájemné za vodohospodářský
  majetek bez DPH, 2022–2025), `fondy[]` (kladná částka = vklad, záporná =
  schválené maximum čerpání), `gaps`.
- `destovka` — `text`, `events[]`, `gaps` (program Dešťovka a stavba
  „Hospodaření s dešťovou vodou“, 1. a 2. etapa; dotace SFŽP z Hlídače státu).
- Ověřeno zápisy. Nepoužité/neověřené: částky smluv o dílo a dodatků
  u čistírny a Bačova (1.–2. etapa), termín dokončení Intenzifikace ČOV,
  nájemné za vodohospodářský majetek 2026, pachtovné, zůstatky fondů —
  jsou uvedené jako mezery.
- Hlídač státu: u čistírny, Bačova a dešťové vody hledání podle názvu akce
  vrátilo jen dvě dotační smlouvy SFŽP (dešťová voda); smlouvy o dílo
  v Registru smluv nenalezeny.

## Postup práce
Obecná pravidla (needitovat vygenerovaný `voda/index.html`, upravit
`content/voda.html` a spustit `python3 scripts/build.py`) jsou v
kořenovém `CLAUDE.md`. Postup pro nové téma: skill `pecky-online-nove-tema`.

### Kontrola při týdenním běhu jednání
Klíčová slova v `agenda[].t` a `resolutions[].text`: vodné, stočné,
úpravna vody, Tatce, ČOV, kalolis, Intenzifikace, vodovod, vodovodní řad,
přivaděč, kanalizace, vodojem, Pečecké služby, vodohospodářský majetek,
pachtovní smlouva, Fond obnovy, Dešťovka, Hospodaření s dešťovou vodou, Bačov.
Nález zapsat do `ceny.json` (cena), `upravna.json` / `infrastruktura.json`
(události), případně do `gaps`. Zvlášť hlídat: ZM v prosinci (informace o ceně
na další rok), RM v lednu (nájemné za vodohospodářský majetek), dodatky ke
smlouvě o dílo na Bačov (3. a 4. etapa), nájem vodojemu pro Vantage Towers,
nová poptávka na věžový vodojem. Běh končí řádkem „Voda: zkontrolováno,
beze změny“ nebo výpisem změn.
