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
6. **Zapiš stopu**: nová datovaná podsekce v tomto souboru, záznam
   v changelogu kořenového `README.md` a přepsaný řádek Tělocvična
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

## Doplněno 4. 9. 2026: první oficiální vyjádření vedení města

Na žádost uživatele přečten nový příspěvek na `facebook.com/mestopecky`,
permalink:
`https://www.facebook.com/mestopecky/posts/pfbid0gi67kJjpLYcy3gjuLNim8Co2ggPyUi1REnGAVrhJscmbWtQK12Ty4nMREwWahxkzl`
(zveřejněno pátek 4. 9. 2026 v 0:20, čteno přes claude-in-chrome —
web_fetch na FB nefunguje, viz obecná poznámka v kořenovém `CLAUDE.md`).
Je to **první veřejné vyjádření samotného vedení města** k celé věci
(dosud mlčelo — viz předchozí kontroly Aktualit i Facebooku k
2. 9. 2026 níže). Potvrzuje technické jádro ze zápisu ZM (piloty
nedostatečné délky, zkoušky PIT + kontrolní jádrový vrt), navíc
upřesňuje: sanace pilot pod kuchyní byla plánovaná už od začátku
zakládání stavby, ale bourací práce odhalily pochybnosti o kvalitě/
délce STÁVAJÍCÍCH pilot (ne jen nově budovaných); statik kvůli tomu
zpochybnil délku i dalších pilot, ne jen původně kontrolovaných; město
zvažuje sanaci základů, nebo přeprojektování statiky celé stavby;
dohoda se zhotovitelem o pozastavení prací šetří náklady města; vedení
města a právní zástupce shromažďují dokumentaci a řeší právní otázky.

**Důležité:** vyjádření vůbec nereaguje na konkrétní tvrzení Aleny
Švejnohové z 2. 9. 2026 (rok 2015, jména Urban/Paluska, odepřené
podklady) — nepotvrzuje je ani nevyvrací. Promítnuto do: nového
callloutu a bulletky v „Co přesně říká radnice“, poznámky v obou
calloutech „Otevřené otázky“, nového řádku 4. 9. 2026 v tabulce
„Zastavení stavby“ (nad řádek Švejnohové, protože je novější), a
opraveny/odstraněny pasáže tvrdící, že radnice mlčí (ty byly k
2. 9. 2026 pravdivé, teď ne).

Zároveň na žádost uživatele znovu zkontrolovány Aktuality města na
`pecky.cz/default/default/21395_aktuality` (čteno přes claude-in-chrome
— stránka je jinak bot-chráněná). K 4. 9. 2026 beze změny oproti
kontrole z 2. 9. — nejnovější položka zůstává „Uzavírka ulice
K. Havlíčka Borovského“ (3. 6. 2026, ohlášení startu stavby); žádná
samostatná zpráva o zastavení stavby ani facebookovém vyjádření tam
není, ani po jeho zveřejnění. Bulletka u „Co přesně říká radnice“
aktualizována na datum kontroly a přesnější popis.

## Doplněno 4. 9. 2026 (odpoledne): zápis a usnesení RM 31/2026 (Dodatek č. 1 k SoD)

Na žádost uživatele doplněn obsah zápisu RM 31/2026, který byl v době
předchozí kontroly (2.–4. 9.) dostupný jen jako pozvánka. Zdroj:
`jednani/pecky-jednani.json` (aktualizováno mezitím jiným — pravděpodobně
denním automatizovaným — během), permalink zápisu:
`https://mesto-pecky.usneseni.cz/verejne/a57ac114-a054-11f1-bd57-0242c0a80002/zapis/`.

Klíčová zjištění, promítnutá do stránky:
- **Dodatek č. 1 ke SoD schválen** (usnesení UR-277-31/26, 5 pro –
  0 proti – 1 zdržel se), zahrnuje 13 změnových listů (ZL 01–13),
  mimo jiné „změny související se statickým zajištěním stávajícího
  založení a navazujícími opravami“ — tedy i piloty, ne jen ostatní
  drobné nesoulady PD.
- **Poprvé známé konkrétní číslo:** navýšení ceny díla o 6 150 969 Kč
  bez DPH, nová cena 174 765 820 Kč bez DPH / 211 466 642 Kč vč. DPH
  (původně cca 205 mil. Kč vč. DPH). **Pozor** — dodatek sám avizuje, že
  jde o vyúčtování zatím uzavřených změn, ne o odhad celkových nákladů
  na vyřešení pilot — nepsat to jako „konečnou cenu“.
- Dopad na **harmonogram** dodatek výslovně neřeší („v současné době
  není spolehlivě vyhodnocen“).
- Radnice v textu dodatku výslovně uvádí, že jeho uzavřením „není
  dotčeno případné následné posouzení příčin vzniku jednotlivých změn
  ani odpovědnosti zhotovitele, projektanta či jiné osoby“ — silná
  citace pro „Otevřené otázky“, potvrzuje, že otázka odpovědnosti je
  formálně otevřená i podle samotného města, ne jen podle nás.
- Vedlejší detail z bodu 3 (Aktuální informace vedení města): zázemí
  školní jídelny bylo mezitím předáno k zahájení provozu — část
  komplexu tedy funguje navzdory zastavení tělocvičny.

Promítnuto do: intra + stat-grid (211,5 mil. místo 205 mil.), plně
přepsaný řádek 31. 8. 2026 v tabulce „Zastavení stavby“, nový třetí
callout v „Otevřené otázky“ (rozpočet/harmonogram/odpovědnost).

## Doplněno 10. 9. 2026: zápis RM 32/2026 + program ZM 6/2026

Automatická kontrola usneseni.cz (krok 9). Zdroj: zápis RM 32/2026
(7. 9. 2026),
`https://mesto-pecky.usneseni.cz/verejne/9b05ec54-a5f5-11f1-a3cf-0242c0a80003/zapis/`,
a pozvánka ZM 6/2026 (16. 9. 2026).

- **Externí odborník na sanace.** Bod 3 (Aktuální informace vedení
  města): „porada externího pracovníka na sanace budov ve věci dalšího
  pokračování stavby, příprava vyjádření právní kanceláře o dalším
  postupu“. Je to první doklad, že město k věci přizvalo externího
  specialistu na sanace — dosud se mluvilo jen o generálním projektantovi,
  autorském dozoru, statikovi a TDI. Jméno ani firmu zápis neuvádí.
- **10 mil. Kč do letošního rozpočtu — ale ne vícenáklady.** Bod 9
  (Rozpočtová opatření č. 9/2026): „§ 3113 Dostavba učeben a tělocvičny
  v ZŠ Pečky č. 2026, zvýšení o 10 000 000 Kč, jedná se o předpoklad
  plateb v letošním roce“. **Nepsat to jako zdražení stavby** — je to
  úprava letošního cash flow, ne nově vyčíslený vícenáklad; celková cena
  díla zůstává na 211,5 mil. Kč vč. DPH po Dodatku č. 1. Rada doporučila
  ZM ke schválení (UR-288-32/26, 4 pro – 0 proti – 1 zdržel se).
- **Rozhodne zastupitelstvo 16. 9. 2026.** Pozvánka ZM 6/2026 má na
  programu samostatný bod 6 „Informace o stavební akci ‚Dostavba učeben
  a tělocvičny v ZŠ Pečky‘“ a bod 8 s rozpočtovými opatřeními č. 9/2026.
  Obsah informace ani stanovisko právní kanceláře pozvánka neuvádí —
  doplnit ze zápisu, až vyjde.

Promítnuto do `content/telocvicna.html`: nový řádek 7. 9. 2026 v tabulce
„Zastavení stavby v roce 2026“ (nad 4. 9.), nový čtvrtý callout
v „Otevřené otázky“ k jednání ZM 16. 9., `lastmod` na 10. 9. 2026.
Stat-grid ani perex se neměnily — cena díla se nezměnila.

## Doplněno 14. 9. 2026: dávka Pečeckých novin 2012–2015 (uživatel)

Na žádost uživatele prohledána dávka nově doplněných výtisků
(`noviny/pecky-noviny.json`, roky 2012–2015, 44 vydání) na klíčová
slova `tělocvičn`, `kolaudac`, `pilot`, `základ`, `kuchyň`, `vývařovn`,
`statik`. Většina zásahů byla falešný poplach (např. „pilotní projekt“
soutěže, kolaudace ulice Palackého, statika mostu po povodni) — ale
osm výtisků z let 2014–2016 vyplnilo skutečnou mezeru mezi řádky
1. 9. 2008 a červen 2016 v tabulce „Historie projektu“:

- **Nezávislé potvrzení tvrzení Švejnohové o roce 2015.** Zápis RM
  citovaný v Pečeckých novinách 4/2015: „dokončení aktualizace
  projektové dokumentace projekční kanceláří A11 Hradec Králové —
  vývařovna ZŠ Pečky“. Je to první dobový (ne dodatečný, ne od
  Švejnohové) zdroj, který potvrzuje **rok i zpracovatele** z jejího
  facebookového tvrzení ze 2. 9. 2026 — **ale ne** konkrétní údaj
  o délce pilot (8,5 m) ani to, že šlo o „kolaudační“ dokumentaci
  (tenhle zápis mluví o aktualizaci projektové dokumentace, ne o
  kolaudaci samotné stavby). Rozdíl je důležitý, nepřepisovat na
  „potvrzeno“ bez výhrady.
- **Chronologie 2014–2016 dřív chyběla úplně.** PN 9/2014 (titulní
  článek „Dostavba vývařovny obědů základní školy“): tehdy ještě
  žádná projektová dokumentace pro stavební povolení neexistovala,
  II. etapa (vývařovna + tělocvična + aula) čekala 8 let na dotaci,
  odhad rozpočtu jen 78 mil. Kč (dnešní cena za samotnou tělocvičnu/
  učebny: 211,5 mil. Kč — desetinásobek za menší rozsah, stojí za
  zmínku při psaní o nákladech). Podepsal tehdejší místostarosta
  Ing. Karel Krištoufek — dnes stále radní, možný zdroj k oslovení,
  kdyby měl uživatel zájem. PN 10/2014 a 11/2014: Rada ještě na
  podzim 2014 teprve vybírala zpracovatele PD a jednala s A11 o
  cenových návrzích — potvrzuje, že proces se táhl roky, ne že
  „dokumentace z 2015“ vznikla odnikud. PN 11/2015: spolek rodičů
  ZŠ pořád „podporuje výstavbu vývařovny“ — stavba tedy ještě
  neskončila. PN 8/2016 („Vývařovna finišuje“): stavba byla
  v dokončovací fázi ještě v srpnu 2016, dva měsíce po předchozí
  poznámce webu „červen 2016 — kuchyň se dokončuje“.
- **Nenalezeno:** žádná zmínka o kolaudaci konkrétně kuchyně/vývařovny
  (jen nesouvisející kolaudace ulice), žádná zmínka o pilotách
  v technickém smyslu, žádné jméno zhotovitele stavby (na rozdíl od
  zpracovatele PD, kterým byl A11). Zůstává mezerou.

Promítnuto do `content/telocvicna.html`: šest nových řádků v tabulce
„Historie projektu“ (září/říjen/listopad 2014, duben/listopad 2015,
srpen 2016), upravený úvodní odstavec nad tabulkou, upravený
gap-callout pod tabulkou, upravený první callout v „Otevřené otázky“
(rok a zpracovatel teď „nezávisle podepřené“ místo „jen jejím
tvrzením“), `lastmod` na 14. 9. 2026.

## Doplněno 21. 9. 2026: zápis ZM 6/2026 a RM 33/2026

Automatická kontrola usneseni.cz (krok 9). Zdroje: zápis ZM 6/2026
(16. 9. 2026),
`https://mesto-pecky.usneseni.cz/verejne/1e69bf60-aa81-11f1-b174-0242c0a80002/zapis/`,
a zápis RM 33/2026 (14. 9. 2026),
`https://mesto-pecky.usneseni.cz/verejne/fe58c641-ab82-11f1-8b0b-0242c0a80002/zapis/`.

- **Kontrolní den na stavbě 10. 9. 2026.** Bod 6 ZM 6/2026 (Informace
  o stavební akci): písemné materiály k bodu dostali zastupitelé
  dodatečně, protože je zpracovatelé doplnili „na základě výsledků
  kontrolního dne, následných konzultací a případného právního
  posouzení dalšího postupu“ o „aktuální informace a návrh dalšího
  postupu“. Je to první doklad, že na stavbě proběhla fyzická kontrola
  po zastavení prací — samotný obsah návrhu dalšího postupu ale zápis
  necituje, jen konstatuje, že existuje. Zastupitelstvo vzalo informaci
  na vědomí bez hlasování.
- **10 mil. Kč schváleno, ne jen doporučeno — a poprvé číslo za
  dosavadní náklady.** Bod 8 (Rozpočtová opatření č. 9/2026),
  usnesení **UZ-35-6/26**: navýšení § 3113 o 10 mil. Kč schváleno
  (s nesouvisející úpravou o odchytu nutrií). Důvodová zpráva k tomu
  poprvé uvádí souhrnné číslo za **už vynaložené** náklady na
  zrealizovanou část („dle smlouvy a dodatku, vč. dozorů, výběr.
  řízení, úpravy projektu“): **26 mil. Kč** — a že do konce roku se
  čekají další výdaje na zastavení/konzervaci stavby, stavební práce
  v kuchyni (zateplení), úpravu projektu a právní služby, bez
  konkrétní částky. **Nepřepisovat 26 mil. na „cenu vyřešení pilot“**
  — zahrnuje i běžné náklady realizované části stavby před zastavením.
- **RM 33/2026 (14. 9., před ZM): stav beze změny.** Bod 3 (Aktuální
  informace vedení města), místostarosta Zdeněk Fejfar: stavba
  „pozastavena“ a „zakonzervována“, řeší se „pochybnosti týkající se
  délky nosných pilot“, čeká se na vyjádření právní kanceláře. Stejná
  formulace jako v předchozích týdnech — žádný nový fakt, jen potvrzení
  že se stav k tomuto datu nezměnil.
- **Právní kancelář k 16. 9. 2026 pořád nevydala stanovisko** — ani
  jeden ze dvou zápisů (RM 33/2026, ZM 6/2026) ho neobsahuje, oba jen
  zmiňují, že se na něj čeká. Otázka odpovědnosti a technického řešení
  zůstává otevřená i po zasedání ZM, na které se čekalo od 10. 9. 2026
  (viz „Doplněno 10. 9. 2026“ výše).

Promítnuto do `content/telocvicna.html`: dva nové řádky v tabulce
„Zastavení stavby v roce 2026“ (16. 9. a 14. 9., nad 7. 9.), rozšířený
čtvrtý callout v „Otevřené otázky“ (dopad na rozpočet — nová čísla
26 mil. + 10 mil.), přepsaný pátý callout tamtéž (dřív anticipoval, co
ZM řekne — teď referuje, co zápis skutečně obsahuje a co pořád chybí).
Stat-grid ani perex se neměnily — cena díla podle smlouvy/dodatku se
nezměnila, 26/10 mil. jsou náklady/rozpočet, ne cena díla.

## Co hlídat dál

- Jestli a jak vedení města zareaguje konkrétně na tvrzení Švejnohové
  (rok 2015, jména, odepřené podklady) — vyjádření z 4. 9. 2026 na ně
  nereagovalo vůbec.
- Jestli případně dojde k trestnímu oznámení, které Švejnohová
  požaduje, a s jakým výsledkem.
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
- Zhotovitel/dodavatel samotné stavby vývařovny (2015–2016, ne
  zpracovatel PD) — jméno se v prohledaných Pečeckých novinách
  nenašlo. Pokud přibudou další ročníky novin, hledat i tohle.
- Jestli/kdy proběhla formální kolaudace vývařovny — v novinách 2015–
  2016 nedohledána (jen „finišuje“ v 8/2016), a hodila by se pro
  přesné porovnání s tvrzením Švejnohové o „kolaudační dokumentaci
  z roku 2015“.
