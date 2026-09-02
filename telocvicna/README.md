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

## Doplněno 2. 9. 2026: srpnové zápisy Rady + historie projektu 2008–2022

Na žádost uživatele prohledán celý archiv jednání (`jednani/archive-
2026-08-04.json` pro 2021–07/2026, `jednani/pecky-jednani.json` pro
srpen 2026 mimo záběr archivu) a fulltext Pečeckých novin
(`noviny/pecky-noviny.json`, 2008–2026). Zjištění promítnuta do
`content/telocvicna.html`:

- **Rada věděla dřív než zastupitelstvo.** Zápis RM 28/2026
  (10. 8. 2026) — „řešení nálezové situace (utržené piloty)“ — je
  nejstarší dohledaná zmínka, 16 dní před zápisem ZM 5/2026. RM
  29/2026 (17. 8.) svolává mimořádné ZM právě kvůli tomu. RM 30/2026
  (24. 8.) mluví o „opatřeních vyvolaných pozastavením stavby“ — stavba
  tedy byla zastavená ještě před zápisem ZM. RM 31/2026 (31. 8.) měla
  na programu „Dodatek č. 1 k SoD“, ale zápis/usnesení k 2. 9. 2026
  ještě nejsou zveřejněné (jen pozvánka) — **hlídat, až vyjdou**.
- **Historie projektu jako celku sahá k roku 2008**: zápis RM z
  1. 9. 2008 (starosta Milan Urban) dělí „II. etapu dostavby ZŠ“ na
  vývařovnu a tělocvičnu/aulu, zhotovitel PD Ateliér A11 Hradec
  Králové. Stejná firma znovu 8/2017. Nová smlouva s OV ARCHITEKTI
  s.r.o. 6/2018 (studie od nuly). V 6/2022 (zápis RM 24/2022) je
  zhotovitelem PD už **Atelier A99 s.r.o.** — tedy tři různé
  projekční kanceláře za 14 let. Žádný z prohledaných zdrojů před
  8/2026 nezmiňuje piloty ani problém se základy. **Pozor** — toto NENÍ
  vyvrácení tvrzení „dokumentace z roku 2015“ (viz níže, aktualizace ze
  2. 9. 2026 večer): 2008 je správní rozhodnutí o rozdělení stavby na
  etapy, 2015 je (podle Švejnohové) datum konkrétní kolaudační
  dokumentace kuchyně s vadnými údaji o pilotách — jde o dva různé
  dokumenty, ne o spor o jedno datum.
- Pečecké noviny (offline archiv, ne přes `web_fetch`) nemají u starších
  vydání (2008–2019) přímé URL na pecky.cz — citováno jen číslem
  vydání, ne odkazem (výjimka: 7/2020, ta URL dostupná je).

## Doplněno 2. 9. 2026 (večer): veřejná výzva Aleny Švejnohové na Facebooku

Na žádost uživatele prohledán `facebook.com/svejnohova` — nalezen
čerstvý veřejný příspěvek (v době kontroly ~13 minut starý), permalink:
`https://www.facebook.com/svejnohova/posts/pfbid08z7hPHghV9PkSKSxAXPxHVYhbx8KVh9AfebfjgcHc6sC6bqwox57YFEkzEtTFCJnl`.
Jako předsedkyně Kontrolního výboru v něm tvrdí: vadná dokumentace
(kolaudace kuchyně) je z roku 2015, uváděla piloty 8,5 m, kontrolní
zkoušky po poškození 3 pilot při bourání potvrdily skutečnou délku jen
6,5–6,6 m; tehdejší vedení města: starosta Milan Urban, místostarosta
Milan Paluska (dnešní starosta); popisuje, že jí město dokumenty ke
kontrole nejprve odepřelo („Kontrolní výbor na ně nemá právo“), pak
tvrdilo, že „ještě nejsou dohledané“; vyzývá k trestnímu oznámení pro
podezření z podvodu a zmiňuje možný střet zájmů starosty Palusky.

Toto je **jednostranné tvrzení volené zastupitelky pod jejím jménem**,
ne nezávisle ověřený závěr — na stránce důsledně odlišeno od
ověřených faktů ze zápisů (vlastní `.stamp` „ověřeno, Facebook
A. Švejnohové, 2. 9. 2026“ jen pro fakt, že se takto vyjádřila; obsah
jejích tvrzení zůstává v `.stamp` „přiznaná mezera“). Promítnuto do:
perexu „Co přesně říká radnice“ (přesná čísla pilot), obou calloutů
„Otevřené otázky“, nového řádku 2015 v tabulce „Historie projektu“ a
nového řádku 2. 9. 2026 v tabulce „Zastavení stavby v roce 2026“.

## Co hlídat dál

- Reakce vedení města (Paluska/Urban) na veřejnou výzvu Švejnohové —
  dosud žádná (kontrolováno těsně po zveřejnění příspěvku).
- Jestli případně dojde k trestnímu oznámení, které Švejnohová
  požaduje, a s jakým výsledkem.
- Zápis/usnesení RM 31/2026 (31. 8. 2026, Dodatek č. 1 k SoD) — až
  vyjde, doplnit obsah dodatku do časové osy.
- Jestli/kdy radnice zveřejní vlastní tiskovou zprávu (kontrolováno
  2. 9. 2026 na `pecky.cz/default/default/21395_aktuality` a Facebooku
  Město Pečky — k tomuto datu nic).
- Výsledek diagnostiky, právního posouzení a dopad na harmonogram/
  rozpočet stavby — až se objeví v dalším zápisu ZM/RM nebo na webu
  města, doplnit do časové osy a případně přehodnotit `Režim` v
  kořenové tabulce „Stav sekcí“ (`README.md`) z „hlídat“ na „denně“
  nebo „uzavřené“, podle toho, jak se věc vyvine.
- Které konkrétní firmě/osobě se vadná dokumentace z roku 2015
  přičítá — Švejnohová jmenuje jen tehdejší politické vedení, ne
  zpracovatele dokumentace. Dosud nedohledáno, viz „Historie projektu“.
