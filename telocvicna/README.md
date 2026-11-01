# Instrukce k sekci: Tělocvična (panel `telocvicna`)

Referenční dokument pro práci na panelu `panel-telocvicna`
(`content/telocvicna.html`) webu pecky.online, generuje se do veřejné
stránky `/telocvicna/` (viz `scripts/build.py`). Doplňuje obecné
instrukce projektu (Project instructions / CLAUDE.md) — tohle je detail
jen pro tuhle jednu sekci.

## Účel sekce

Sledování stavby „Dostavba učeben a tělocvičny ZŠ Pečky“ (205 mil. Kč,
zahájena 3. 6. 2026) a konkrétně problému zjištěného v srpnu 2026:
šest původních pilot podpírajících sousední budovu kuchyně a jídelny,
na které má nová konstrukce navazovat, je kratších, než uvádí dobová
dokumentace — stavba je proto od 26. 8. 2026 částečně zastavená.

Sekce vznikla 2. 9. 2026 na základě osobního podkladu uživatele
(návrh veřejné výzvy) — obsah `content/telocvicna.html` byl před
publikací nezávisle ověřen proti oficiálnímu zápisu ze zasedání
zastupitelstva a proti videozáznamu (viz zdroje níže), a strukturovaný
do obvyklého stylu webu (perex, časová osa, citace důvodové zprávy,
přiznané mezery). Je striktně věcný — žádný osobní názor neobsahuje.

## Pracovní postup: týdenní kontrola

Sekce nemá vlastní snímek dat — hlavním zdrojem jsou **zápisy a usnesení
Rady a Zastupitelstva**, které se stahují v rámci kontroly sekce Jednání
([`jednani/automation-kontrola-usneseni-cz.md`](../jednani/automation-kontrola-usneseni-cz.md),
krok 9). Tenhle postup na něj navazuje a spouští se při každém týdenním
běhu.

1. **Najdi dotčené body.** V jednáních doplněných/zkontrolovaných v tomto
   běhu (i v těch, která mají zatím jen Pozvánku — program bodů je sám
   o sobě informace) projdi `agenda[].t` a `resolutions[].text` a hledej
   nejen slovo „tělocvična“, ale i: „Dostavba učeben“, „ZŠ Pečky“,
   „piloty“, „založení“, „statické zajištění“, „Dodatek č. … k SoD“,
   „změnový list“, „zhotovitel“, „TDI“, „pozastavení stavby“.
2. **Přečti plný text bodu**, ne jen jeho název — důvodová zpráva
   a text usnesení nesou konkrétní čísla a formulace (viz Dodatek č. 1
   níže, kde teprve zápis prozradil částku i větu o odpovědnosti).
3. **Zapiš do `content/telocvicna.html`** (needit vygenerovaný
   `telocvicna/index.html` — přepíše ho příští build). Kam co patří:
   - nový vývoj s datem → nový řádek v tabulce **„Zastavení stavby
     v roce 2026“** (nejnovější nahoře); události před rokem 2026 →
     tabulka **„Historie projektu“**
   - změna ceny, termínu nebo rozsahu → **stat-grid** a perex nahoře
   - citace/postoj radnice → **„Co přesně říká radnice“**
   - co zápis nezodpovídá (dopad na termín, konečná cena, odpovědnost)
     → **„Otevřené otázky“** jako přiznaná mezera
4. **Ověřenost.** Co je doložené zápisem, označ `.stamp` „ověřeno“
   s uvedením jednání a data. Co je tvrzení jedné strany (politik,
   Facebook), drž jako jednostranné tvrzení pod jménem, ne jako závěr.
   Nikdy nedopočítávat čísla, která zdroj neuvádí.
5. **Přegeneruj** — `python3 scripts/build.py`.
6. **Zapiš stopu**: nový blok „## Doplněno <datum>“ na konec `telocvicna/HISTORIE.md`, záznam
   v `HISTORIE.md` v kořeni a přepsaný řádek Tělocvična
   v tabulce „Stav sekcí“ (datum kontroly vždy, datum změny a sloupec
   „Co naposledy“ jen při reálné změně obsahu).
7. **Reportuj.** Ve shrnutí běhu vždy uveď, co se v sekci změnilo —
   jmenovitě soubor a věcnou změnu. Když se nezměnilo nic, napiš přímo
   „Tělocvična: zkontrolováno, beze změny“; tenhle řádek ve shrnutí
   nesmí chybět ani při nulovém nálezu.

Kromě zápisů zůstávají doplňkovými zdroji Facebook města a A. Švejnohové
a Aktuality na pecky.cz (obojí čitelné jen přes claude-in-chrome) —
kontrolují se, když na ně narazí kontrola sociálních sítí v sekci O webu,
nebo když si o to uživatel řekne.

## Ověřené jádro (zápis ZM 5/2026, 26. 8. 2026)

Bod č. 4 programu „Dostavba učeben a tělocvičny v ZŠ Pečky — aktuální
stav realizace“, předkladatel Milan Paluska. Důvodová zpráva doslovně:
obnaženo 6 pilot (č. 1, 10, 15, 21, 27, 37) určených ke zkrácení a
napojení na nové základové pasy, u 3 z nich při demolici „k oddělení
cca ve 2 m délky (hloubky)“; zkoušky PIT „nepotvrdila délka pilot dle
zhotovovacích protokolů“; na základě stanoviska generálního projektanta
a autorského dozoru dočasně zastaveny práce ovlivňující nosné
konstrukce/založení; dopad na harmonogram a náklady zatím nelze
predikovat. Zastupitelstvo vzalo informaci na vědomí bez hlasování o
dalším postupu. K bodu se vyjádřili Milan Paluska, Michael Havránek
(TDI), Milan Urban, Lubomír Metelák, Ondřej Schulz, Ing. Hana Kuprová,
Mgr. Tibor Flašík, Ivana Trčková; v bodě 5 (diskuze s občany) i
JUDr. Jiří Švejnoha.

Zdroj čten přes claude-in-chrome — usneseni.cz blokuje `web_fetch`
(403), viz obecná poznámka v kořenovém `CLAUDE.md`.

## Co hlídat dál

- Jestli a jak vedení města zareaguje konkrétně na tvrzení Švejnohové
  (rok 2015, jména, odepřené podklady) — vyjádření z 4. 9. 2026 na ně
  nereagovalo vůbec.
- Trestní oznámení město podalo 6. 10. 2026 (na neznámého pachatele,
  viz níže) — sledovat jeho výsledek a jestli se objeví v zápisech.
- Stanovisko právní kanceláře k dalšímu postupu — k 21. 9. 2026 (zápisy
  RM 33/2026 i ZM 6/2026) se na něj pořád jen čeká, žádný z dosud
  dohledaných zápisů ho neobsahuje. Sledovat další zápisy RM/ZM.
- Obsah „návrhu dalšího postupu“, kterým byly podle zápisu ZM 6/2026
  doplněny materiály k bodu 6 po kontrolním dni na stavbě 10. 9. 2026
  — zápis konstatuje, že existuje, ale necituje ho.
- Které řešení si město nakonec vybere — sanaci základů, nebo
  přeprojektování statiky celé stavby (obě možnosti otevřené podle
  vyjádření 4. 9. 2026) — a jestli přinesou další dodatky/vícenáklady
  nad rámec Dodatku č. 1.
- Výsledný dopad na harmonogram dokončení stavby — Dodatek č. 1 ho
  výslovně neřeší.
- Výsledek diagnostiky, právního posouzení a případné budoucí posouzení
  odpovědnosti zhotovitele/projektanta — až se objeví v dalším zápisu
  ZM/RM, doplnit do časové osy. (Režim sekce v kořenové tabulce „Stav
  sekcí“ se 8. 9. 2026 změnil z „hlídat“ na „týdně“ — viz „Pracovní
  postup: týdenní kontrola“ výše. Až věc doběhne, přehodnotit na
  „uzavřené“.)
- Kdo konkrétně (v rámci Ateliéru A11) odpovídá za vadné údaje o délce
  pilot — zápis RM 4/2015 potvrdil aspoň firmu a rok, ale ne
  konkrétní osobu ani to, že šlo o „kolaudační“ dokumentaci, jak tvrdí
  Švejnohová. Dosud nedohledáno, viz „Historie projektu“.
- Zhotovitel stavby vývařovny: **DMC CZ, s.r.o., Brno** (viz [`HISTORIE.md`](HISTORIE.md),
  „Doplněno 6. 10. 2026“). Nedohledáno zůstává, kdo z firmy/subdodavatelů prováděl
  základy a piloty — ověřit např. na Hlídači státu (smlouva 2015) nebo
  ve stavebním archivu.
- Jestli/kdy proběhla formální kolaudace vývařovny — v novinách ani
  v zápisech Rady 2015–2016 nedohledána (rada předává dílo k 31. 8. 2016,
  kolaudace se nezmiňuje), a hodila by se pro přesné porovnání s tvrzením
  Švejnohové o „kolaudační dokumentaci z roku 2015“.
