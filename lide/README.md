# Instrukce k sekci: Lidé (panel `lide`)

Referenční dokument pro práci na panelu `panel-lide` v
`content/lide.html` (generuje se do veřejné stránky `/lide/`, viz
`scripts/build.py`). Doplňuje obecné instrukce projektu (Project instructions /
CLAUDE.md) — tohle je detail jen pro tuhle jednu sekci.

## Účel sekce
Kartičky členů zastupitelstva (21) a rady města (7) — kdo v nich sedí,
za jaké uskupení, případně fotka. Zdroj: jmenný seznam ZM/RM z pecky.cz,
doplňkově web ODS Pečky (viz kořenový `README.md` → „Zdroje dat").

Každé politické uskupení má na celém webu jednu pevně přiřazenou barvu
(CSS třídy `.person-card.party-*`) — používá se konzistentně napříč
sekcemi Lidé, Plán, Volby 2018/2022/2026. Tabulka barev je v
[`volby/README.md`](../volby/README.md) → „Barevná paleta
uskupení"; při přidávání nového uskupení nebo člena vždy použít
existující barvu z té tabulky, ne vymýšlet novou.

Známá mezera: kompletní seznam 21 zastupitelů se nedaří ověřit napřímo
(pecky.cz blokuje bot přístup) — viz kořenový `CLAUDE.md`.

## Lidé = aktuální stav, Volby = stav při ustavení
Tenhle panel ukazuje, kdo v zastupitelstvu a radě sedí **teď**. Jmenný
seznam zvolených po volbách je v subpanelu „Výsledky voleb" příslušného
ročníku — viz [`volby/README.md`](../volby/README.md) →
„Zvolení zástupci". **Oba seznamy jsou samostatné a už se rozcházejí:**
od ustavujícího zasedání 20. 10. 2022 se složení dvakrát změnilo —
Jaroslava Vosecká nastoupila za Lenku Třískovou (slib 11. 9. 2024) a
Ondřej Schulz za Bc. Ivetu Dvořákovou (slib 26. 2. 2025). Při další
rezignaci, kooptaci náhradníka nebo změně ve vedení se opraví **jen
tenhle panel**; historický seznam u Voleb 2022 zůstává, jaký byl.

## Fotky
Portréty na kartičkách (`img.avatar`) nejsou ve složce této sekce —
leží u volebního ročníku, ke kterému se váží: `volby/2022/zastupitele/
{prijmeni}.jpg` (42 souborů, příjmení bez diakritiky malými písmeny;
u shody příjmení i s křestním, např. `hruska-ivan.jpg`), od 30. 8. 2026
i `volby/2026/zastupitele/{prijmeni}.webp` (15 souborů, kandidátka ODS
z ods.cz — kandidátka nejde stáhnout jako jpg, formát ponechán webp).
Jeden člověk tak může mít fotky ve víc ročnících najednou — proto
`people.json` drží `photos` jako pole, ne jednu hodnotu, viz SPEC.md
§3.7. Po dalších volbách zakládat novou sadu ve složce nového ročníku,
staré nepřepisovat. Detaily viz [`volby/README.md`](../volby/README.md).

Výjimkou jsou portréty, které nepocházejí z voleb — ty leží v
`lide/foto/{prijmeni}.jpg`. Zatím jde o jediný případ: 2. místostarosta
Ing. Martin Jedlička, jehož fotka je z Rady města na oficiálním webu
(pecky.as4u.cz). Do složky volebního ročníku nepatří, protože ta je
popsaná jako portréty zvolených kandidátů z volebních materiálů — fotka
z webu radnice by tam o svém původu lhala.

## Datová sada

Ve složce leží strojově čitelný adresář osob, organizací a vazeb mezi
nimi. Návrh a rozhodnutí, proč je model takový, jsou v [`SPEC.md`](SPEC.md);
tahle kapitola je provozní — jak s daty pracovat.

```
foto/                portréty z jiných zdrojů než z voleb (viz níž)
people.json          381 osob (21 aktuálních zastupitelů + 2 bývalí s plným
                      profilem, 206 dalších kandidátů ze všech kandidátek
                      2018/2022/2026 s minimálním záznamem (SPEC.md §3.6),
                      13 vedení úřadu/příspěvkovek/firem (fáze 5b, §7),
                      8 jen kvůli členství v komisi RM/školské radě,
                      21 pedagogů ZUŠ Pečky, 48 pedagogů ZŠ Pečky,
                      22 lidí z MŠ MAŠINKA Pečky, 2 noví z výboru
                      Pečeckého okrašlovacího spolku, 16 nových z AFK Pečky — viz níž)
organizations.json   24 organizací (Město Pečky + 8 volebních uskupení +
                      7 příspěvkovek + 2 firmy + 6 spolků — poslední
                      4 spolky/firmy založeny jinou souběžnou session
                      pro sekci Kalendář; vazby na osoby mají
                      Pečecký okrašlovací spolek, SŽM Pečky, Minigolfclub
                      Dráčata a AFK Pečky)
affiliations.json   615 vazeb osoba–organizace
validate.mjs         validátor
```

**Pečecký okrašlovací spolek — výbor** (doplněno 24. 9. 2026): 5členný
výbor dohledaný v obchodním rejstříku
([rejstrik.penize.cz](https://rejstrik.penize.cz/21001634-pececky-okraslovaci-spolek),
zdroj justice.cz) — organizace samotná byla v `organizations.json` už
od 20. 9. 2026 (přidala jiná souběžná session pro Kalendář), ale bez
vazeb na osoby, což si i sama poznamenala v `note`. Tři z pěti členů
výboru šlo spárovat s existujícími záznamy podle jména a titulu přesně
(`houdkoval`, `vodickat`, `vodickal`) — malé město, stejní lidé se
potkávají v komisích, kandidátkách i spolcích. Nový `role_type` se
nezaváděl: použit už existující, dosud nepoužitý `"clen"` z číselníku,
na pokyn autora webu — je to obdoba `"komise"`, jen u nezávislého
spolku místo orgánu města, takže se stejně jako komise počítá do
`_komise`/`_office` v `content/lide.html` (jinak by dva zcela noví lidé,
kteří nikde jinde nefigurují, v adresáři vůbec nenaskočili). Skupina
„Komise rady města a školská rada" byla proto přejmenována na „Komise,
spolky a školská rada" a čip „Spolky" přibyl vedle „Výbory a komise".
Datum vzniku funkce (`from`) je datum vzniku spolku (11. 12. 2023) — to
jediné rejstřík uvádí, žádná pozdější změna ve výboru není zapsaná.

**AFK Pečky — vedení a realizační týmy** (doplněno 24. 9. 2026): 21 lidí
z webu klubu — výkonný výbor ze stránky
[afkpecky.cz/vedeni-klubu](https://www.afkpecky.cz/vedeni-klubu/) (předseda,
jednatel, hospodář → `vedeni-organizace`, stejně jako výbor SŽM Pečky)
a trenéři, asistenti trenéra a vedoucí mužstev ze stránek
`/<tým>/realizacni-tym/` všech 7 týmů → vlastní `role_type: "trener"`
(zaveden týž den na pokyn autora webu, s přístupem jako u `ucitel`:
vlastní čip „Trenéři" ve filtru, ale skupina „Městské organizace" spolu
s vedením klubu, `_organizace` v `content/lide.html`). Vedoucí mužstva
nemá samostatný typ — je součástí realizačního týmu, rozlišuje ho jen
text v `role` (stejně jako „vedoucí vychovatelka" u vychovatelek).
Původně (týž den) zapsáni jako `clen` ve skupině „Komise, spolky a školská
rada" — autorovi webu se to nelíbilo. Kontakty ani fotky web neuvádí.
**Soupisky hráčů se nepřebírají** — nejsou to funkce ve spolku a u mládeže
jde o děti. Realizační týmy web vede jen pro sezónu 2025/2026 (jiná
v nabídce není), vazby proto mají `from: "2025"` a přiznanou poznámku,
že složení pro 2026/2027 nemusí sedět.
Předseda Jaroslav Lukáš je jako jediný zapsaný i ve spolkovém rejstříku
(statutární orgán, předsedou od 27. 1. 2014) — datum narození z ARES
odpovídá věku 65 let na kandidátní listině ODS 2026, spojení s existujícím
záznamem `lukasj` je tedy ověřené. Čtyři další přesné shody jména
(`konupekj`, `drizhalj`, `vilimj` — týž učitel ZŠ?, `spikm`) jsou
spárované jen podle jména a vazba to v `note` přiznává. Jaroslav Vorlíček
(jednatel) **není** Jiří Vorlíček z kandidátky 2026 — nový záznam
`vorlicekj2`. Zdeněk Buřič má dvě vazby (hospodář + trenér mladších
žáků), Vojtěch Buřič je samostatná osoba.

**Pečecké služby, s.r.o. — zaměstnanci** (doplněno 29. 9. 2026): zdroj
[pececkesluzby.cz/office](https://pececkesluzby.cz/office/) uvádí kromě
jednatele ještě 5 lidí (asistentka vedení/personalistka, objednávky/
pokladna/fakturace, ekonomka, 2 provozní techniky) — zadal uživatel
dotazem, jestli jsou v adresáři. Simona Vrbová (ekonomka) tam mezitím
souběžně doplnila jiná session (vč. jejího krátkého jednatelství
27. 1.–2. 3. 2026 mezi Brantem a Högerovou). Ze zbylých 4: Pavel
Sedláček je na pokyn autora webu **stejná osoba** jako stávající
zastupitel `sedlacekp` (SNK Pečky Pečákům) — dostal jen novou vazbu.
Luboš Hanzelín je naopak na pokyn autora webu **jiná osoba** než
stávající `hanzelinl` Lukáš Hanzelín (ředitel Kulturního střediska) —
nezaměňovat přes podobné jméno, nový záznam `hanzelinl2`. Aneta
Bernardová a Libuše Černá jsou nové bez podobnosti k nikomu
existujícímu. Všichni čtyři `role_type: "zamestnanec"` — firma (`type:
"firma"`) není úřad, takže spadají pod `_organizace` ve `content/lide.html`
stejnou větví, jaká už existovala pro zaměstnance organizací mimo úřad
(žádná úprava kódu nebyla potřeba, na rozdíl od ZUŠ/ZŠ/MŠ výš).

**MŠ MAŠINKA Pečky** (doplněno 22. 9. 2026): 13 učitelek + zástupkyně
ředitelky + 4 asistentky pedagoga + 4 uklízečky, dohledáno na
stránkách jednotlivých tříd — zdroj
[msmasinkapecky.cz/nase-tridy](https://www.msmasinkapecky.cz/nase-tridy/)
(7 tříd, každá má vlastní podstránku s bios učitelek a závěrečnou větou
jmenující úklid a asistentku pedagoga). Ředitelka `bubenickovak` beze
změny — jen potvrzeno, že vedle vedení školy učí i ve třídě Domeček
(do jejího záznamu se to nedopisovalo, stejný princip jako u ředitelky
ZUŠ). **Nový nález:** Petra Tvrdá je
zástupkyně ředitelky (dosud v datech nebyla vůbec) — zapsaná jednou
vazbou `role_type: "vedeni-organizace"`, která kombinuje funkci vedení
i to, že učí třídu Kytička (stejný vzor jako zástupkyně ředitelky ZUŠ).
Dva nové typy v číselníku, na pokyn autora webu:
`role_type: "asistent-pedagoga"` (pomáhá konkrétnímu dítěti/třídě, nemá
kvalifikaci učitele — jiná profese než učitel i vychovatel) a
`role_type: "provozni"` (nepedagogický personál — úklid; dvě uklízečky
uklízí po dvou třídách, zapsané jednou vazbou s oběma třídami v `role`,
ne dvakrát). Všechny čtyři nové typy (`ucitel`, `vychovatel`,
`asistent-pedagoga`, `provozni`) — a od 24. 9. 2026 i `trener` (AFK
Pečky, viz níž) — počítají do stejné skupiny „Městské
organizace" (`_organizace` v `content/lide.html`), každý s vlastním
filtrovacím čipem. Žádná z těchto osob nemá e-mail/telefon — třídní
stránky uvádí jen kontakt na třídu jako celek, ne na jednotlivé lidi.

**Pedagogický sbor ZŠ Pečky** (doplněno 22. 9. 2026): 46 učitelů 1. a
2. stupně a 7 vychovatelek školní družiny — zdroje
[zspecky.cz/1-stupen/ucitele](https://www.zspecky.cz/1-stupen/ucitele/),
[.../2-stupen/ucitele](https://www.zspecky.cz/2-stupen/ucitele/) (jmenné
seznamy konzultačních hodin, bez e-mailu/telefonu — proto ho u učitelů
nemá nikdo) a jednotlivé podstránky `družina/školní-družina/{i–vii}-oddeleni/`
(u vychovatelek e-mail i telefon má každá). Pět z nich šlo spárovat
s existujícími záznamy podle jména a tituly se přesně shodovaly
(`kozakovab`, `pisovam`, `vinohradnikovah` už byly ze školské rady;
`kristoufkoval`, `kuprp` z kandidátek/komisí — u Kupra navíc sedí i jeho
vlastní údaj „učitel, trenér" v `occupations`) — dostali jen novou vazbu,
ne duplicitní osobu. `role_type: "ucitel"` u učitelů (stejný typ jako
u ZUŠ, role text rozlišuje „učitel/učitelka 1. stupně" vs „2. stupně");
vychovatelky mají vlastní `role_type: "vychovatel"` — jiná profese než
učitel, i když jde taky o pedagogického pracovníka školy, na pokyn autora
webu zadaný jako vlastní typ, aby se dala filtrovat samostatně
(`content/lide.html` počítá oba do skupiny „Městské organizace", stejně
jako komise/vedeni-organizace, viz odstavec u ZUŠ výš). Bc. Hana
Vinohradníková je „vedoucí vychovatelka" II. oddělení — rozlišeno
v `role`, `role_type` zůstává stejný jako u ostatních vychovatelek.

Jana Bartáková je na 1. stupni i na 2. stupni se skoro identickým
záznamem (stejná místnost, čas se liší jen o 5 minut) — nejde vyloučit,
že je to duplicita ze šablony webu školy, ale na pokyn autora webu jsou
zapsané obě vazby, tak jak to zdroj uvádí.

**Přiznaná mezera:** školní klub (`/druzina/skolni-klub/`) uvádí jen dva
e-maily bez celého jména (`hatasova@zspecky.cz`, `kasparkova@zspecky.cz`)
— bez křestního jména nejde založit záznam s `id` podle konvence, takže
tihle dva lidé v adresáři chybí, dokud se jméno nedohledá jinde.

**Pedagogický sbor ZUŠ Pečky** (doplněno 22. 9. 2026): ředitelka (dřív
`vorlickovap`), zástupkyně ředitelky a 20 učitelů ze 4 oborů (hudební,
výtvarný a multimediální, taneční, literárně-dramatický) — zdroj
[zuspecky.cz/kontakty](https://zuspecky.cz/kontakty/), který u každého
uvádí jméno, obor/nástroj a pracovní e-mail. Zástupkyně ředitelky
(`role_type: "vedeni-organizace"`, stejně jako ředitelka) je zapsaná
jednou vazbou, která v `role` kombinuje funkci i to, co učí — dělat pro
tutéž osobu na stejné organizaci dvě vazby (vedení + výuka) by jen
duplikovalo kartičku. Zbylých 20 má vlastní `role_type: "ucitel"`
(doplněno 22. 9. 2026, na pokyn autora webu) — **ne** `"zamestnanec"`,
aby šli učitelé filtrovat zvlášť od úřednického personálu; do budoucna
se stejný typ použije i pro učitele ZŠ Pečky. `content/lide.html`
i tak počítá `ucitel` do stejné skupiny „Městské organizace" jako
`vedeni-organizace`/`zamestnanec` u ostatních organizací (`_organizace`
v `lJoin`) — jen řádek s filtry navíc nabízí čip „Učitelé", který
`role_type` „zamestnanec" nechává čistě pro úřad. Zavedení tohoto typu
poprvé opouští dosavadní pravidlo „jen zaměstnanci úřadu" (viz „Kdo do
adresáře patří" níž) — škola samotná zveřejňuje jmenný seznam učitelů
s e-maily, takže platí stejná logika transparentnosti jako u úřadu.
Datum nástupu web školy neuvádí u nikoho, proto `from: null` napříč.

**Komise RM a školská rada** (doplněno 19. 9. 2026): pět iniciativních a
poradních komisí rady města (sportovní, kulturní, Sbor pro občanské
záležitosti, stavebně-dopravní a ŽP, sociální/zdravotní/bytová) plus
školská rada ZŠ Pečky. Modelováno jako vazby s `role_type: "komise"` —
stejný typ, jaký už měl předsednictví kontrolního výboru zastupitelstva —
ne jako nové organizace: komise nejsou samostatné právnické osoby, jde
o orgány zřízené radou (viz `Jednaci_rad_komisi.pdf` na pecky.cz), takže
vazby míří na existující `mesto-pecky` (pět komisí RM) nebo `zs-pecky`
(školská rada, protože jde o orgán školy, ne úřadu). Zdroj: podstránky
pecky.cz → Rada města → Komise RM; přesné datum jmenování tam není
uvedené, jen aktuální složení — vazby proto mají `from: null` a `note`
s vysvětlením. Členství v komisi teď počítá do `_office` stejně jako
`vedeni-urad`/`vedeni-organizace`/`zamestnanec` (viz `content/lide.html`
→ `lJoin`), jinak by přes 20 lidí, kteří v komisi sedí, ale nikdy
nekandidovali ani nepracují na úřadu, v adresáři vůbec nenaskočilo —
stejná past, jaké se předešlo u `vedeni-urad`/`vedeni-organizace`
(fáze 5b, viz odstavec výš). Panel proto má šestou skupinu „Komise rady
města a školská rada"; kdo má vedle komise i mandát, úřad nebo vedení
organizace, zůstává ve své dosavadní skupině — komise je pak vidět jen
v jeho detailu/timeline, ne jako duplicitní kartička.

**Komise RM, doplnění a data jmenování** (29. 9. 2026, po porovnání se
starým webem `pecky.as4u.cz` → Komise rady města 2022–2026, stav
18. 2. 2025, a s usneseními rady). Zdroj dat jmenování: usnesení RM
`UR-436` až `UR-442-45/22` z jednání rady **14. 11. 2022** (první složení
všech komisí ve volebním období 2022–2026) a pozdější změny —
`UR-2-1/23` (9. 1. 2023, doplněna Sladká, Šestáková a Šátková ml. do
sportovní komise), `UR-163-15/24` (22. 4. 2024, Horkel), `UR-362-37/24`
a `UR-363-37/24` (21. 10. 2024, ukončení členství Velké a Růžičkové,
úmrtí Třískové), `UR-232-25/25` (30. 6. 2025, Svatoňková). Všem
stávajícím členům komisí, které v těch usneseních jsou, bylo doplněno
`from` a přesný odkaz na usnesení. Nově:
- **Fond rozvoje bydlení** — komise rady, která doporučuje půjčky
  z fondu (`role`: „předseda/člen komise Fondu rozvoje bydlení RM“):
  Jedlička (předseda), Krištoufek, Janoušková, dřívější člen Vlastimil
  Kmoch (`kmochv`, v 2/2025 už není). Aktuální pecky.cz složení neuvádí,
  vazby jsou vedené jako aktuální na základě starého webu a toho, že rada
  komisi využívá i v září 2026 (`UR-283-32/26`).
- **Pracovní skupina pro oslavy 100 let povýšení Peček na město** — šest
  uzavřených vazeb (14. 11. 2022 – 12. 1. 2026, zrušena `UR-22-2/26`),
  nová osoba Jan Karbus.
- **Školská rada:** Mgr. Michaela Fejfarová (`fejfarovam`, zástupkyně
  zřizovatele 5. 12. 2022 – 10. 11. 2025, kdy rada jmenovala místo ní
  JUDr. Michaelu Trčkovou); Kuprová a Nepovímová mají `from: 2022-12-05`.
- **Komise, které dnes už nemají původní členy:** uzavřené vazby Velké
  (`velkas`) a Růžičkové (`ruzickovav`) v sociální komisi, Třískové ve
  stavební, Vodičky ve stavební (odchod nedatován), Šátkové ml.
  (`satkoval2`, sportovní; na webu „Šestáková ml.“ je překlep), a nová
  členka sociální komise Blanka Svatoňková (`svatonkovab`, jen
  z usnesení rady, ve výpisu komise není).

**Školská rada ZŠ Pečky — členové 2009–2026** (doplněno 30. 9. 2026 na žádost
uživatele po vytěžení zápisů školské rady, viz `jednani/README.md` → „Školská rada“).
Vazby `role_type: "komise"` na organizaci `zs-pecky`, role „člen(ka) školské rady ZŠ Pečky
(zástupce zřizovatele / pedagogických pracovníků / zákonných zástupců žáků)“ a „předseda/předsedkyně
školské rady ZŠ Pečky“. Vazba = jedno funkční období nebo jeho doložený úsek, proto mají
dlouholetí členové víc vazeb. **Začátek mandátu** je vždy nejlepší doložený:
- **zástupci zřizovatele:** datum usnesení rady města — 29. 11. 2010 (Krúpová) a 13. 12. 2010
  (Katrnoška, Jedlička; Pečecké noviny 1/2011), 24. 11. 2014 (Homan, Horynová, Jedlička; Pečecké noviny 1/2015 —
  datum je z OCR „2?. listopadu 2014“ a cyklu zasedání rady), 5. 12. 2022 (Kuprová, Fejfarová, Nepovímová;
  UR-484-48/22) a 10. 11. 2025 (Kuprová, Trčková, Nepovímová; UR-364-42/25). Konec: odvolání 24. 11. 2014, resp.
  nahrazení dalším složením; u členů 2014–2022 nejsou dostupná případná jmenování v letech 2017 a 2020.
- **volení zástupci rodičů:** datum voleb, kde ho škola zveřejnila — 14. 9. 2009 (Procházka, Hovorka), 11. 3. 2011
  (Literová), 23. 10. 2014 (Minaříková/Dvořáková, Chárová, Charousová). Rodiče 2019–2022 (Astrová, Taxová, Korouš)
  a 2023–2025 (Břečka, Kubinová, Bitrmanová) mají jen první doložené jednání (17. 1. 2023 u posledních tří).
- **volení zástupci pedagogů:** web školy data voleb pedagogů nezveřejňuje — `from` je první doložené jednání
  (Vinohradníková 7. 9. 2009, Kozáková 23. 9. 2010, Píšová 15. 6. 2015), dřívější mandát je vedený jako jedno
  souvislé období do 5. 1. 2026.
- **současná rada:** funkční období všech devíti členů začalo **5. 1. 2026**, kdy rada města (RM 1/2026, bod 15)
  vzala na vědomí složení školské rady v plném obsazení — podle volebního řádu (UR-365-42/25) je tím stanoven počátek
  tříletého funkčního období; zřizovatelé mají navíc datum jmenování 10. 11. 2025. Předsedkyní byla 5. 2. 2026 zvolena
  Michaela Trčková (dříve od 17. 1. 2023 Hana Kuprová, předsedou byl Martin Jedlička 2011–2014 a 2015–2023).
Nové osoby (`tags: ["skolska-rada"]`, zdroj zápisy/výsledky voleb): Klára Literová, Lucie Charousová, Pavel Břečka,
Romana Kubinová, Lenka Bitrmanová, Vlastimil Procházka, Petr Hovorka, Ludmila Podlešáková. **Iveta Minaříková
z ŠR 2014–2019 je Bc. Iveta Dvořáková (`dvorakovai`)** — alias `minarikovai` je už v datech, proto je její vazba
na ní. Ostatní členové už v Lidech byli (Homan a Chárová jen jako kandidáti, Němcová jako učitelka). Neurčeni a proto
v Lidech chybí: Astrová, Taxová, Korouš, Hájková (jen příjmení v zápisech). Jaroslav Hovorka
(`hovorkaj`) v Lidech **není** Petr Hovorka ze školské rady — nesměšovat.

**Komise RM 2018–2022 — členové ze zveřejněných zápisů** (doplněno 30. 9. 2026 na žádost uživatele;
zdroj `jednani/komise.json`, volební období 2018–2022). Vazby `role_type: "komise"` na `mesto-pecky`
u Komise sportovní, Komise stavebně-dopravní (od 2020 se scházela společně s komisí pro životní prostředí),
Komise pro kulturu a vzdělávání (dnešní Kulturní komise) a Sboru pro občanské záležitosti: 52 členských vazeb
a 5 předsedů (Katrnoška — sportovní, Vodička — stavební, Kozáková — kulturní do 2021, Janáčková — kulturní od
4. 11. 2021, Turynová — SPOZ), 10 nových osob (`tags: ["komise"]`): Jana Vaníčková, Vojtěch Malina, Radek Čížek,
Kateřina Čiháková, Hana Pokorná, Miroslava Zumrová, Romana Růžičková, Eva Jíchová, Miloslava Turynová,
Svatava Jindřichová. **Začátek mandátu:** členové počátečního složení komisí (Pečecké noviny 12/2018, s. 3) mají
`from: 2018-11-19` — rada města komise jmenovala na prvním zasedání po ustavení zastupitelstva; přesné datum
19. 11. 2018 je doloženo u SPOZ (zápis SPOZ z 13. 12. 2018 cituje jmenování „dne 19. 11. 2018“), u ostatních
komisí Noviny uvádějí jen listopadové zasedání rady. Kdo v počátečním seznamu není (Zindrová, Vlk, Krulišová
jako zástupkyně knihovny, Čížek, Čiháková, Šestáková, Šátková, Fejfar, Janáčková v kulturní komisi…), má `from`
= první doložené jednání a v `note` „datum jmenování nedohledáno“. `to: 2022-11-14` = nové komise jmenované
usnesením RM UR-436 až UR-442-45/22; poslední doložená účast je v `note`. Ze zápisů jsou **vynecháni** hosté a ti,
kdo v žádném zápisu nefigurují (např. Hála, Janovský, Douděra, Kynclová z jmenovacích seznamů), a městský architekt
Jan Drška (v zápisech jako prezentující). Sociální, bytová a další komise bez zveřejněných zápisů se nedoplňovaly.
Docházka u vazeb se počítá z `komise.json` (role „Komise pro kulturu a vzdělávání“ a „Komise pro životní
prostředí“ jsou v `L_ATTENDANCE_ROLES` napojené na kulturní, resp. stavební komisi). `jNameKey()` v
`assets/helpers.js` teď umí i „Petra Vorlíčková, DiS.“ (čárka před titulem se lepila k příjmení a nespárovala
docházku) a tituly `arch.`, `M.Sc.`, `MBA`, `MPA`, `PaedDr.`.

**Komise bytová a sociální — členové 2010–2019** (doplněno 30. 9. 2026 na žádost uživatele; zdroj Pečecké
noviny, ne zápisy — tyto komise zápisy nezveřejňují, členství je proto doložené jen jmenovacími seznamy rady města).
**Komise bytová:** 2010–2014 (RM 29. 11. 2010 — Horynová předsedkyně, Janoušková, V. Růžičková, Vinohradník, Semerád),
2014–2018 (předsedkyně jmenována RM 24. 11. 2014, „konečné obsazení“ 8. 12. 2014 — navíc Mgr. Petra Šetková, nová
osoba `setkovap`) a 2018–2019 (RM listopad 2018 — Horynová, Heroldová, Vinohradník, Čermáková, V. Růžičková,
Janoušková). **Komise pro sociální oblast a zdravotnictví** 2018–2019 (předsedkyně Iveta Minaříková, dnes
Dvořáková; Horynová, Schürzová, Kynclová, Vinohradník, Velká, Čermáková). Obě komise zrušila rada města v létě 2019
(Pečecké noviny 9/2019, s. 2, „prázdninová jednání“; datum usnesení nedohledáno, `to: 2019`) a zřídila
Komisi pro otázky sociální, zdravotní a bytové — **její členy z let 2019–2022 zdroje neuvádějí** (mezera; od
14. 11. 2022 jsou členové v Lidech podle UR-436-45/22). Zapisovatelka Dana Pečenková (úřednice) a členové, kteří
nejsou ve zdrojích jmenovitě (např. „zástupce knihovny“), se nedoplňovali. Před rokem 2010 Noviny seznamy komisí
neuvádějí; sociální komise 2010–2018 v Novinách nefiguruje (mohla neexistovat). Datum 8. 12. 2014 vychází z toho,
že Noviny 1/2015 uvádějí „bude doplněno na příští RM 8. 12. 2014“ a následně „jmenuje konečné obsazení“.

**Vedení úřadu, příspěvkových organizací a městských firem** (`role_type:
"vedeni-urad"` a `"vedeni-organizace"`, doplněno 5. 9. 2026, fáze 5b
SPEC.md §7): tajemnice úřadu, 4
vedoucí odborů a velitel Městské policie (všichni jako vazba na
`mesto-pecky` — úřad je součástí téže právnické osoby jako obec, ne
samostatná organizace), plus ředitel/ka u každé ze 7 nově založených
organizací (MŠ MAŠINKA, ZŠ, ZUŠ, Kulturní středisko, Městská knihovna,
Pečovatelská služba, Pečecké služby s.r.o.). Zdroj: kontaktní stránky
pecky.cz, cross-ověřeno v Hlídači státu; u Pečeckých služeb (s.r.o.)
jednatelka dohledána přímo v obchodním rejstříku (justice.cz), protože
firemní web k datu ověření uváděl už neplatné jméno — viz `note` u
organizace `pececke-sluzby`. Aby se tihle lidé (bez mandátu v ZM/RM)
zobrazili i ve výchozím rozsahu „Jen aktuální“, `lInScope()` v
`content/lide.html` teď kromě `_mandate`/`_exec` počítá i s `_vedeni`.

**Panel `panel-lide` se z těchhle souborů generuje.** Kartičky v
`index.html` už nejsou — vytváří je `loadLide()` v posledním `<script>`
bloku. Personální změna se tedy dělá **jen v JSON**, do HTML nesahat.

Ručně psaný v panelu zůstává jen nadpis a úvodní odstavec; řádek se
statistikou nad kartičkami (`#lide-status`) se dopočítává z dat.

Souhrnný callout „O fotografiích" **na stránce už není** (odstraněn
5. 9. 2026). Původ každé fotky nese `photo_source` u příslušné položky
v `photos` a vypisuje se v detailu osoby s rokem. Cenou za to je, že
web už nikde nevysvětluje, **proč** u části lidí fotka chybí —
zdůvodnění (tři z pěti uskupení mají jen Facebook, kde nejdou fotky
spolehlivě spárovat se jmény) zůstalo jen v historii gitu a v
[`volby/2026/README.md`](../volby/2026/README.md).

Protože se data načítají `fetch`em, panel **nefunguje z `file://`** —
stejně jako Jednání a Pečecké noviny. Lokálně `python3 -m http.server`.

### Odkazovatelné adresy

Panel má vlastní routing v hashi, takže na konkrétního člověka i uskupení
jde poslat odkaz:

```
#lide/osoba/paluskam               detail starosty
#lide/uskupeni/nasepecky           uskupení a jeho lidé
#lide?org=ods&role=rada            radní za ODS
#lide?q=svejnohova&scope=all       hledání včetně bývalých členů
```

Adresy stojí na `id` z JSON — proto se `id` po zveřejnění nemění.

### Vizitka osoby je sdílená komponenta (od 19. 9. 2026)

Vykreslení detailu osoby (`lPersonDetail` v `content/lide.html`) i avatar
kartičky delegují na `pcDetailHtml`/`pcAvatarHtml`/`pcBuildTimeline`
v `assets/helpers.js` — čistě formátovací a vykreslovací funkce bez závislosti
na routingu nebo filtrech téhle sekce. Vznikly proto, aby stejnou vizitku šlo
znovu použít i mimo Lidé: první uplatnění je jméno v tabulce Jednání →
Absence (`/jednani/absence.html`, viz `jednani/README.md` →
„Avatar a vizitka osoby u jména"), kde se klikem na jméno rozbalí přesně
tahle karta. `content/lide.html` si drží krátké aliasy (`lFullName`,
`lRoleLabel` apod.) na `pc*` funkce, ať se nemusí přepisovat zbytek souboru —
při úpravě formátování (datum, telefon, timeline) měnit vždy `pc*` verzi
v `assets/helpers.js`, ne kopírovat logiku zpátky sem.

### Tři entity, ne jedna kartička

Dnešní kartička slepuje tři různé věci dohromady. V datech jsou oddělené,
protože každá má vlastní začátek, konec a zdroj:

| Vazba | `role_type` | Od kdy | Zdroj |
|---|---|---|---|
| mandát v zastupitelstvu | `zastupitel` | složení slibu | zápis ustavujícího zasedání |
| funkce v radě | `starosta`, `mistostarosta`, `rada` | volba na ustavujícím zasedání | usnesení `UZ-90-7/22`…`UZ-96-7/22` |
| kandidátka, za kterou byl zvolen | `kandidatka` | den voleb | výsledky ČSÚ |

Proto má každý zastupitel nejméně dvě vazby a člen rady tři. Že je
někdo zároveň radní i zastupitel, **není duplicita**.

Náhradník má vazbu na kandidátku od voleb 2022, ale mandát až od složení
slibu — Ondřej Schulz od 26. 2. 2025, Jaroslava Vosecká od 11. 9. 2024.
Ten rozdíl je správně a je vidět v timeline.

### Co panel vypisuje a co ne

Šest skupin v tomhle pořadí: **Rada města**, **Ostatní členové
zastupitelstva**, **Úřad města** (`vedeni-urad`), **Městské organizace**
(`vedeni-organizace`), **Výbory, komise, spolky a školská rada** (`komise`
a `clen`, doplněno 19., resp. 24. 9. 2026; výbory ZM 29. 9. 2026) a — až po přepnutí rozsahu
na „Včetně historie" —
**Dřívější vedení a bývalí zastupitelé**. Volení lidé nahoře, jmenovaní
pod nimi, historie nakonec.

Poslední skupina není jen o lidech, kteří odešli uprostřed období. Patří
do ní každý s doloženou ukončenou funkcí a bez aktuální — tedy i starostové,
místostarostové a radní minulých volebních období.

**Se zapnutým filtrem podle role se skupiny pojmenují podle něj** —
„Starosta — nyní" a „Starosta — dříve" — a výchozí pětice se nevykreslí.
Důvod: seskupení podle *dnešního* postavení přestává dávat smysl ve chvíli,
kdy filtr matchuje i minulé funkce. Hledání starostů s historií vracelo
Milana Urbana a Alenu Švejnohovou pod nadpisem „Ostatní členové
zastupitelstva" s popiskem „Bez funkce v radě" — pravdivé o jejich dnešním
postavení, ale mlčící o tom, proč se v seznamu octli. Kartička dál ukazuje
současné postavení, celý průběh je v detailu.

Filtr rolí míří na `role_type`, ne na členství v radě jako orgánu.
Místostarosta je člen rady, ale má vlastní `role_type`, takže pod „Radní"
nespadá — Zdeněk Fejfar se proto objeví v „Radní — dříve" (radním byl
2014–2018, dnes je místostarosta). Je to důsledek modelu, ne chyba.

Nad kartičkami je jediný řádek filtrů, **podle role**. Čipy podle uskupení
tam byly a jsou pryč — řádek s pěti stranami nad jednadvaceti lidmi zabíral
víc místa, než přinášel. **Filtrování podle uskupení ale nezmizelo**, jen
nemá vlastní tlačítka: pořád funguje přes URL (`#lide?org=ods`), přes klik
na uskupení na kartičce a přes pohled `#lide/uskupeni/{id}`. Kdo by chtěl
čipy zpátky, vrátí je v `lBuildChips()` — `L_STATE.orgs` i větev v
`lMatches()` zůstaly na místě.

Kdo nespadá ani do jedné, se **nevypisuje a nezapočítává** do statistiky nad
kartičkami. V praxi jde o lidi, o kterých z dat víme jen to, že byli na nějaké
kandidátní listině (`role_type: "kandidatka"` a nic dalšího) — dnes přes dvě
stovky záznamů z ročníků 2018/2022/2026. V `people.json` zůstávají a používají
je sekce Volby, panel Lidé je ale nezobrazuje.

Dřív je sbírala skupina „Kandidáti bez mandátu". Ten nadpis byl zavádějící:
padali do něj i vedoucí odborů a ředitelé městských organizací, kteří do
zastupitelstva nikdy nekandidovali. Proto mají teď vlastní skupinu a nadpis,
který o nich mluví pravdivě.

**Když někoho přidáš a on se neobjeví**, chybí mu vazba mimo kandidátku —
mandát (`zastupitel`), funkce v radě, `vedeni` nebo `zamestnanec`.

### Finanční a kontrolní výbor ZM (doplněno 29. 9. 2026)

Oba výbory mají sedm členů (UZ-97-7/22). Složení je z usnesení ustavujícího
zasedání 20. 10. 2022 (`UZ-98`…`UZ-111`) a pozdějších doplňovacích voleb
(`UZ-47-5/24`, `UZ-2-1/25`, `UZ-3-1/25`). Křížově ověřeno proti aktuálnímu
výpisu na pecky.cz (Zastupitelstvo → Výbory ZM) 29. 9. 2026 — sedí na
jméno. `role_type: "komise"`, stejně jako předsednictví kontrolního výboru,
které už v datech bylo. U každé vazby je v `note` číslo usnesení a poměr
hlasů, ve `sources` přímý odkaz na usnesení (a u aktuálních členů i na
výpis na pecky.cz).

- **Finanční výbor:** předseda Ing. Karel Krištoufek; členové Ing. Šárka
  Jedličková, Pavel Sedláček, Milan Urban, Tomáš Vodička, Jaroslav Železný,
  Lubomír Metelák — beze změny od roku 2022. Web města píše „Metalák",
  usnesení i kandidátka „Metelák".
- **Kontrolní výbor:** předsedkyně Bc. Iveta Dvořáková (do 26. 2. 2025, kdy
  jí skončil i mandát), pak Mgr. Alena Švejnohová (do té doby řadová členka,
  proto má dvě vazby za sebou). Členové Milan Pečenka, Ivana Trčková,
  Václav Drška, Ing. Petr Dürr; Lenka Třísková do roku 2024 (viz Přiznané
  mezery), po ní Jaroslava Vosecká (od 13. 11. 2024) a na místo Dvořákové
  Jiří Katrnoška (od 26. 2. 2025).
- **Období 2018–2022** (doplněno týž den, podklad pro zápisy výborů na
  stránce Jednání): složení z Pečeckých novin 12/2018, str. 3 (ustavující
  zasedání 14. 11. 2018), křížově ověřeno seznamy přítomných ve všech
  zápisech FV 2018–2022 a KV 2020–2021 na pecky.cz. Usnesení ZM od 4/2021
  žádnou další volbu do výborů neobsahují.
  - FV: předseda Tomáš Vodička; členové Ing. Petr Dürr, Ing. František
    Pospíšil (spárován s prvním polistopadovým starostou), Ing. Jana Sladká,
    Ing. Martin Jedlička, Jaroslav Semerád a od února 2019 jako sedmý
    Ing. Ladislav Zindr (nová osoba `zindrl`, Pečecké noviny 3/2019 —
    přesné datum zasedání neuvedeno, vazba má `from: "2019"`).
  - KV: předseda Milan Paluska; členové Mgr. Bc. Lenka Krúpová,
    Mgr. Jaroslava Heroldová, Ing. Jan Korouš, Jaroslav Železný, Zdeněk
    Fejfar, Jaroslav Martinec.
- Členství předsedů se jako zvláštní vazba „člen" nezapisuje — předseda
  je členem výboru automaticky.
- **Účast na jednáních výborů** (od 29. 9. 2026): u každé vazby na výbor
  ukazuje detail osoby, na kolika zveřejněných jednáních výboru v období
  vazby byl člověk přítomen / omluven / jinak nepřítomen. Počítá se za
  běhu z `jednani/vybory.json` (`lAttachVyborAttendance` v
  `content/lide.html`), do `affiliations.json` se nic nezapisuje. Vazba
  si výsledek nese v `_extraHtml`, který sdílená vizitka (`pcDetailHtml`
  v `assets/helpers.js`) vykreslí pod poznámku.
- Všichni kromě Šárky Jedličkové jsou (nebo byli) zastupitelé, takže
  párování je jednoznačné. Jedličková spárována podle jména a titulu Ing.
  (kandidátka 2026 uvádí povolání „vedoucí finančního odboru"). Jako jediná
  nezastupitelka se na stránce objeví ve skupině „Výbory, komise, spolky
  a školská rada".

### Validace

Z kořene repa, před každým commitem datové změny:

```bash
node lide/validate.mjs
```

Exit 0 = čisté, 1 = chyby. Kromě obecné integrity hlídá i pravidla
Peček: 21 zastupitelů, 7 radních, právě jeden starosta, každý zastupitel
má kandidátku, dvě uskupení nemají tutéž barvu, a soubor, na který
ukazuje `url` každé položky `photos`, existuje.

### Historie vedení města

| Období | Starosta/ka | Místostarostové | Zdroj |
|---|---|---|---|
| 1990–2002 | Ing. František Pospíšil | — | kandidátní listina 2026 · Příběhy našich sousedů · Pečecké noviny 12/2019 |
| 2006–2018 | Milan Urban (Sdružení ODS a NK) | — | Kolínský deník 29. 9. 2018 |
| 2014–2018 | Milan Urban | Milan Paluska | Kolínský deník 29. 9. 2018 |
| 2018–2022 | Mgr. Alena Švejnohová | Bc. Iveta Minaříková, Mgr. Blanka Kozáková | Pečecké noviny 12/2018, str. 3 |
| 2022–dosud | Milan Paluska | Zdeněk Fejfar, Ing. Martin Jedlička | usnesení ZM 7/2022 |

**František Pospíšil** byl prvním polistopadovým starostou Peček, rovněž tři
období po sobě (1990, 1994, 1998). Do vedení města nastoupil už 1989 jako
tajemník a poté předseda městského národního výboru — to je ale jen z jednoho
zdroje (životopis Příběhů našich sousedů), proto je ta část jen v `note`, ne
jako samostatná vazba. Samotné starostování 1990–2002 potvrzují tři nezávislé
zdroje, z toho jeden úřední: kandidátní listina 2026 u jeho jména uvádí
„starosta města 1990-2002".

**Mezera 2002–2006 zůstává.** Jaroslav Tvrz je v Pečeckých novinách doložený
jako starosta v roce 2005 a začátkem 2006, ale kdy nastoupil, doložené není —
v adresáři proto zatím není.

Milan Urban byl starostou **tři volební období po sobě (2006, 2010, 2014)**,
dvanáct let. Ve volbách 2018 už nekandidoval a v zastupitelstvu 2018–2022
není; vrátil se až mandátem z voleb 2022. Přesné datum nástupu v roce 2006
se nepodařilo doložit (archiv Pečeckých novin má mezeru mezi dubnem 2006
a prosincem 2007), proto je `from` uložené jen jako rok.

Rada 2014–2018: Ing. Petr Zedník, Martin Homan, Ing. arch. Pavel Švanda
M.Sc. (KDU-ČSL), Šárka Horynová (KDU-ČSL), Zdeněk Fejfar.
Rada 2018–2022: Šárka Horynová, Tomáš Vodička, Jiří Katrnoška,
Jaroslav Železný (+ starostka a obě místostarostky).

**Ještě nedoplněno:** řadoví zastupitelé období 2014–2018 a 2018–2022.
Oba jmenné seznamy jsou doložené (Kolínský deník má u roku 2014 i uskupení
u každého jména; soupis „Naši zastupitelé" v Pečeckých novinách 12/2018 má
sloupce v PDF promíchané, takže přiřazení uskupení k jménům z něj **nelze
brát jako ověřené**). Většina těch lidí už v `people.json` je — jako
kandidáti — takže jde o doplnění vazeb, ne osob.

### Když se ukáže, že dva záznamy jsou jedna osoba

Stává se to hlavně při změně příjmení. Postup (poprvé použit 8. 9. 2026 na
Ivetě Minaříkové → Dvořákové):

1. Ponechat záznam s **dnešním** příjmením, druhý smazat.
2. Do ponechaného doplnit `former_last_names` (dřívější příjmení; jde i do
   fulltextu, takže se člověk najde pod oběma) a `aliases` se **starým `id`**.
3. Vazby zrušeného záznamu přepojit na `person_id` ponechaného a přečíslovat
   jejich `id` podle konvence `{person_id}--{organization_id}--{pořadí}`.
4. Sloučit `sources`, `tags`, případně `photos`; přepsat `bio`, aby popisovalo
   celou dráhu.

Podruhé použit 29. 9. 2026: `sladkaj2` (jednatelka TJ Sokol, založená
zvlášť kvůli nepotvrzené shodě jména) sloučena do `sladkaj` (Komise
sportovní RM) na pokyn autora webu, že jde o jednu osobu — zároveň i ta
„Ing. Jana Sladká“ z finančního výboru 2018–2022. Příjmení se neměnilo,
takže bez `former_last_names`, jen `aliases: ["sladkaj2"]`.

Alias je tam proto, že SPEC §3.1 označuje `id` za neměnné — starý odkaz
`#lide/osoba/minarikovai` se nesmí rozbít. Router ho tiše přesměruje na
platné `id` a přepíše URL na kanonickou. Validátor hlídá, že se alias nekryje
s existujícím `id` (to by znamenalo nedotažené sloučení) ani s jiným aliasem.

### Jak přidat osobu

1. **`people.json`** — `id` je příjmení + iniciála křestního bez
   diakritiky (`paluskam`, `svejnohovaa`).
2. **`organizations.json`** — jen pokud uskupení nebo organizace ještě
   chybí. U uskupení povinně `color`, `color_bg` a `css_class` **z palety** v
   [`volby/README.md`](../volby/README.md), ne nová barva. Barvy se
   do CSS dostanou přes build (`assets/org-colors.css`), nikde je nepsat ručně.
3. **`affiliations.json`** — mandát, případná funkce v radě, kandidátka.
   `id` ve tvaru `{person_id}--{organization_id}--{pořadí}`.
4. Zvýšit `meta.count` a `meta.updated` ve všech změněných souborech.
5. Spustit validátor.

**`id` se po zveřejnění nikdy nemění** — bude na něj odkazovat URL
(`#lide/osoba/paluskam`) i všechny vazby.

### Jak ukončit funkci

Vazbu **nemazat.** Nastavit `to` na datum konce a `current` na `false`.
Právě proto sekce existuje — z ručních kartiček historie mizí, z vazeb ne.
Bc. Iveta Dvořáková a Lenka Třísková jsou v datech přesně z tohohle
důvodu: ve výchozím zobrazení nejsou vidět, po přepnutí rozsahu na
„Včetně historie" se objeví ve třetí skupině se štítkem, do kdy mandát
trval.

### Kdo do adresáře patří

Volení funkcionáři (zastupitelé, rada), jmenované vedení (úřad, městské
organizace), **i řadoví zaměstnanci úřadu** — referentky, účetní, matrikářka
— a od 19. 9. 2026 i **členové komisí rady města a školské rady ZŠ Pečky**
(`role_type: "komise"`, viz „Datová sada" výš). U zaměstnanců se ale vede
**jen to, co organizace sama zveřejňuje jako služební spojení**: jméno,
funkce, pracovní e-mail a telefon. Nic dalšího se k nim nedohledává. Podrobně
a s odůvodněním v SPEC.md §6, bod 4.

Do 8. 9. 2026 platilo pravidlo opačné („ne řadoví zaměstnanci") a změnilo se
na pokyn autora webu při doplňování kontaktů z organizační struktury na
pecky.cz. Od 22. 9. 2026 platí stejné pravidlo i mimo úřad — první případ
je celý pedagogický sbor ZUŠ Pečky (21 lidí, zdroj zuspecky.cz/kontakty),
protože škola sama zveřejňuje jmenný seznam učitelů s e-maily; u jiných
příspěvkovek se to samé doplní, až se najde srovnatelně veřejný zdroj.

Kandidáti bez mandátu jsou v datech, ale panel je nevypisuje — to je jiná věc,
viz „Co panel vypisuje a co ne".

**Organizace bez vazeb na osoby.** Od 20. 9. 2026 jsou v
`organizations.json` i dva spolky — `tj-sokol-pecky` a
`pececky-okraslovaci-spolek` (`type: "spolek"`, identifikace a IČO z Hlídače
státu). Žádné vazby v `affiliations.json` nemají a v adresáři Lidí se
nezobrazují: rejstřík organizací slouží celému webu, ne jen téhle sekci, a
sekce Kalendář se na jejich id odkazuje jako na pořadatele akcí
(`kalendar/akce.json` → `organizer`, viz `kalendar/README.md`). Vazby na
konkrétní lidi se k nim doplní, až pro ně bude doložený zdroj.

Od 22. 9. 2026 přibylo `vzdelavaci-centrum-pecky` (`type: "prispevkova"`,
stejné IČO jako `kulturni-stredisko-pecky` — jde o tutéž právnickou osobu,
jen jiný provoz/budova) — samostatné id, aby se v Kalendáři jeho ~1400
týdenních kroužků neslila ve filtru s vlastním programem Kulturního domu
pod jedno pořadatelské jméno. Přesný vzor jako u obou spolků výše, jen
s odlišným důvodem pro oddělení (kapacita filtru, ne odlišná právnická
osoba).

Od 23. 9. 2026 přibylo `maminky-sobe` (`type: "spolek"`, IČO 27033431) —
spolek realizující Komunitní centrum Pramínek v **sousední obci
Dobřichov**, ne v Pečkách. Na žádost uživatele („akce z Dobřichova budeme
také evidovat") je přesto v rejstříku jako pořadatel akcí v Kalendáři —
vazba na Pečky je přes spolupráci s Farností Pečky, viz `kalendar/README.md`.
První případ pořadatele mimo katastr města.

### Povolání

`occupations` je pole seřazené od nejnovějšího ročníku, každá položka nese
`year`, `value` a `source`. Text si **vyplňuje kandidát sám** ve volebních
podkladech — není ověřený a mezi volbami se mění (Paluska 2022 „podnikatel",
2026 „starosta města"). Detail proto vypisuje všechny ročníky s rokem.
Podrobnosti v SPEC.md §3.6c.

Pokrytí: 111 osob, z toho 15 má oba ročníky. Zdroje — `volby/2026/data-export.csv`
(105 kandidátů 2026) a Poradna pro obce (21 zvolených 2022).

### Fotky a jejich původ

`photos` je pole, ne jedna hodnota — jeden člověk může kandidovat víckrát
a fotka na kandidátce se mezi lety mění (viz SPEC.md §3.7). Každá položka:
`year` (ročník kandidátky nebo volební období), `url` (cesta od kořene
repa — `volby/{rok}/zastupitele/…` u fotek z voleb, `lide/foto/…`
u ostatních), `photo_source` (původ — kandidátka ods.cz, inzerát
v Pečeckých novinách, web města…). Karta osoby ukazuje vždy nejnovější
(`photos[0]`, pole je řazené sestupně), detail osoby všechny. Kdo fotku
nemá, má `photos: []` a v UI dostane iniciálový avatar na barvě
uskupení — viz kapitola „Fotky" výš.

Při nálezu nové fotky za další ročník se **stará položka neodstraňuje**,
jen přibude nová — stejně jako u vazeb historie nemizí.

### České skloňování osob (gender)

Doplněno 19. 9. 2026, zadal uživatel — vzniklo z textu „Přítomen: N"
v poznámce `jednani/absence.html` (mužský tvar u žen gramaticky špatně,
např. „Ivana Trčková … Přítomen" místo „Přítomna"). Řešení je obecné pro
celý web: kdekoli se generuje text o konkrétní osobě z přídavného jména/
příčestí (přítomen/přítomna, zvolen/zvolena, jmenován/jmenována…),
používá stejný mechanismus.

`people.json` nese u každé osoby povinné pole `gender` (`"m"` / `"f"`,
SPEC.md §3.2). U všech 258 záznamů odvozeno ze **jména** (ne příjmení —
česká křestní jména jsou téměř bezvýhradně rodově jednoznačná, na rozdíl
od příjmení, kde selhávají cizí/nesklonná tvary jako „Middleditch" nebo
„Vaz Santos"): 105 unikátních jmen ručně roztříděno a zkřížově ověřeno
proti příponě příjmení (`-ová`/`-á`) — 5 shod nesedělo kvůli právě
takovým nesklonným příjmením, ne kvůli špatně určenému rodu. `validate.mjs`
kontroluje, že `gender` je u každé osoby `"m"` nebo `"f"`.

Vykreslení: `pcGendered(p, masc, fem)` v `assets/helpers.js` — vrátí `fem`
jen když `p.gender === 'f'`, jinak `masc` (i když `p` chybí, tedy osobu
se nepodařilo spárovat — bezpečný výchozí mužský tvar). Použití v
`jednani/absence.html` → `poznamkaHtml(r, p)`: `pcGendered(p, 'Přítomen',
'Přítomna')`. Při dalším místě na webu, kde bude potřeba skloňovat text
o konkrétní osobě, použít stejnou funkci, ne psát tvary napevno.

### Přiznané mezery v datech

- **Kontakty má 33 z 243 osob** (21 zastupitelů, 6 vedení úřadu, 6 vedení
  městských organizací). Zdroje: [Zastupitelstvo
  města](https://pecky.as4u.cz/cs/mesto/zastupitelstvo-mesta/) (e-maily
  všech 21, tvar `jmeno.prijmeni@pecky.cz` bez diakritiky),
  [Telefonní seznam](https://pecky.as4u.cz/cs/mestsky-urad/telefonni-seznam-5.html)
  a stránky odborů. Telefon má jen ten, komu web uvádí **vlastní linku** —
  ústředna `+420 321 785 051` se jako osobní kontakt nezapisuje, fax taky ne.
  Kdo má kancelář i služební mobil, má obě čísla v jednom poli oddělená
  `" · "` (SPEC.md §3.6b); v detailu osoby z každého vede odkaz `tel:`.
  Kandidáti bez funkce kontakt nemají a mít nebudou: nejsou veřejní
  funkcionáři a město jejich spojení nezveřejňuje.
- **Čtyři lidé z ekonomicko-správního odboru sdílejí linku `+420 721 183 560`
  a tři z investic `+420 606 753 278`** — je to číslo odboru, ne osobní.
  Zapsané je (lepší než nic), ale každá taková vazba to má v `note`.
- **Při rozporu mezi zdroji platí pecky.cz, ne pecky.as4u.cz.** Starý web se
  od jara 2026 neaktualizuje. Konkrétně: Jiří Moravec má na pecky.cz
  `+420 724 125 367`, na as4u.cz `+420 724 885 367` — platí to první.
  „Nina Husová" je na as4u.cz vedená jako „Nina Vlčková"; vypadá to na změnu
  příjmení, ale doložené to není, takže je v datech jen pod aktuálním jménem.
- ~~Uskupení Bc. Ivety Dvořákové a Lenky Třískové je dopočítané~~ —
  uzavřeno 8. 9. 2026. Výsledky voleb 2022 na Poradně pro obce uvádějí
  kandidátku přímo u jména, obě vazby jsou teď doložené.
- ~~Výbory jsou zatím jen dva záznamy~~ — uzavřeno 29. 9. 2026, viz
  „Finanční a kontrolní výbor ZM" níže.
- **Lenka Krúpová nemá doložený konec členství v kontrolním výboru
  2018–2022** (`to: null`, `current: false` — validátor to hlásí jako
  varování, je to záměr). V zápisu KV 5. 3. 2020 je neomluvená, v zápisech
  z roku 2021 už chybí úplně, ani mezi omluvenými; odvolání ani rezignace
  nejsou nikde zapsané.
- **Lenka Třísková nemá přesné datum odchodu z kontrolního výboru.**
  Vazba má `to: "2024"`: mandát jí skončil 11. 9. 2024 a její místo ve
  výboru zastupitelstvo obsadilo 13. 11. 2024 (Jaroslava Vosecká, UZ-47-5/24),
  ale samotný odchod (spolu s mandátem, nebo dřív) usnesení nezachycují.
- ~~Komise RM a školská rada nemají doložené datum jmenování~~ — doplněno
  29. 9. 2026 z usnesení RM, viz „Komise RM, doplnění a data jmenování“.
  Zůstávají mezery: **Kuprová jako předsedkyně školské rady** je doložená
  jen starým webem k 2/2025 (jen v `note`, `role` zůstala „členka“);
  **odchod Vlastimila Kmocha z komise Fondu rozvoje bydlení, Tomáše
  Vodičky ze stavební komise a Ladislavy Šátkové ml. ze sportovní**
  není v žádném dohledaném usnesení (`to: null`, `current: false`);
  komise FRB a složení komisí před 14. 11. 2022 (2018–2022) v datech
  chybí; **Ladislava Šátková ml.** je vedená jako samostatná osoba,
  shoda s Ing. Ladislavou Šátkovou (`satkoval`) není potvrzená.
- **Z ustavujícího zasedání po volbách 2018 je v datech jen vedení**
  (starostka, obě místostarostky a rada), ne všech 21 zastupitelů.
  Zasedání je starší než archiv usneseni.cz (začíná dubnem 2021), viz
  [`volby/2018/README.md`](../volby/2018/README.md), takže zdrojem jsou
  Pečecké noviny 12/2018 — a **poměry hlasů při volbě starostky se
  dohledat nedaří**. Jmenný soupis „Naši zastupitelé" v témž článku má
  v PDF promíchané sloupce, takže přiřazení uskupení k jménům z něj nelze
  brát jako ověřené; proto zatím nedoplněno.
- **Kandidatury mají v datech `current: true` a `to: null`**, přestože jde
  o jednorázovou událost. Panel to obchází zobrazením — `lActive()` je za
  aktivní nepovažuje a v timeline je vypisuje jako „volby 5. 10. 2018",
  jinak by dávno skončená kandidatura přebila skutečné funkce. Správně by
  to měla řešit data; změna se dotkne přes 350 vazeb, proto zatím čeká.
- **206 kandidátů (fáze 5a, SPEC.md §3.6) má zatím jen minimální
  záznam** — jméno, příjmení, vazba na kandidátku. Bez `bio`, fotky,
  kontaktů a `sources` na osobě (zdroj je jen na vazbě). Doplnění je
  fáze 5b, postupně a jen tam, kde se najde veřejný zdroj.
- **Fotky za 2026 ověřeny 31. 8. 2026, dohledatelné jen u 2 z 5
  uskupení.** ODS a nezávislí kandidáti (ods.cz) a NAŠE PEČKY A PEČKY
  NEXT (nasepecky.cz) si pro tyhle volby udělaly vlastní web s portréty
  kandidátů — viz §3.7 SPEC.md. Sdružení nezávislých kandidátů PEČKY
  PEČÁKŮM, Lidé pro Pečky a Velké Chvalovice s podporou SPD a Pečky
  srdcem mají jen Facebook (stránku/skupinu) — bez přihlášení jde
  projít jen omezeně a fotky v příspěvcích nejsou jmenovitě popsané,
  takže je nejde spolehlivě spárovat s konkrétním kandidátem. Nejde
  o nedostatek hledání, ale o to, že takový zdroj u těchhle uskupení
  reálně neexistuje — needit to zkoušet znovu, dokud web/inzerce
  nevznikne.

Textový obsah panelu jinak žije v `content/lide.html`. Další zvláštní
pravidla doplnit sem, až nějaká vzniknou.
