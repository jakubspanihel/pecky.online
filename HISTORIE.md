# Historie změn webu

Chronologický deník běhů a úprav, nejnovější nahoře. Přesunuto z
kořenového `README.md` (sekce „Poslední aktualizace“). Aktuální stav sekcí
je v tabulce „Stav sekcí“ v `README.md`; sem patří podrobnosti běhu.

4. listopadu 2026 (jmenovité hlasování zastupitelstva). Do `jednani/pecky-jednani.json` doplněno pole `vote_names` (pro / proti / zdrželi se / nehlasovali) u všech 433 usnesení Zastupitelstva 2021–2026: 415 skriptem `jednani/scripts/doplnit-jmenovite-hlasovani.py` z archivu, 18 usnesení ZM 5/2026, 6/2026 a 7/2026 ručně ze zápisů na usneseni.cz. Web je ukazuje v rozbaleném bodu jako „Jak hlasovali“ (`content/jednani.html`, `assets/styles.css`); Rada jména nemá (zdroj uvádí jen počty). Postup pro nová jednání: krok 8g v `automation-kontrola-usneseni-cz.md`, popis v `jednani/README.md`.

4. listopadu 2026 (úpravy po kontrole, na pokyn uživatele). **Smlouvy:** souhrn skupiny přepsán podle Hlídače státu na 156 smluv / 97 027 982 Kč (dřív 185 / 104 558 592 Kč); úřad beze změny. **Kalendář:** zapsán florbal TJ Sokol Pečky (inzerce v Pečeckých novinách 11/2026, s. 14): čtvrtky 16:00 (mladší) a 17:00 (starší), Sokolovna, od 5. 11. do 17. 12. 2026 (14 termínů), všechny s poznámkou „Negarantováno“ — inzerce neuvádí začátek ani konec; u starší skupiny poznámka o překryvu s badmintonem dospělých z rozvrhu Sokolovny.

4. listopadu 2026 (týdenní kontrola /DoPecek-update, doplnění po kontrole Jednání). **Pečecké noviny:** doplněno vydání 11/2026 (Listopad 2026, 16 stran, vyšlo 2. 11. 2026): `noviny/Data/PN 2026/2026-11.pdf`, fulltext a záznam v `noviny/pecky-noviny.json` (208 vydání, 3 192 stran), obálka `noviny/img/2026-11.jpg`, náhledy stran `noviny/pages/2026-11/`, karta „Poslední číslo“ v `content/zpravodaj.html` (Říjen přesunut do roku 2026); tiráž (redakce Alena Brantová, rada Zavřel, Kusá, Hartman) beze změny. Plakáty z novin: str. 12 Adventní setkání v Pečkách (29. 11.) a str. 15 Rozsvícení stromu ve Velkých Chvalovicích (28. 11.) — obě akce už v kalendáři, v `kalendar/akce.json` doplněn doklad z novin a poznámka s programem; str. 14 inzerce Sokol Pečky, oddíl florbalu (čtvrtek 16–17 a 17–18, Sokolovna) — pravidelný trénink bez data začátku, nezapsáno. **Úřední deska:** 1 nový dokument (498396, rozhodnutí o povolení stavby v k. ú. Pečky, vyvěšeno 3. 11. 2026) do `2026.txt` a příloh (`prilohy-2026.txt`, stažení a extrakce), stránka Monitoringu přegenerována (1 929 dokumentů); do jiných sekcí nic nepatří. **Kalendář:** z Aktualit města přibyla akce Koncert k poctě sv. Cecílii (19. 11. 2026 17:30, sál ZUŠ Pečky), synchronizováno do Google Kalendáře; ostatní položky Aktualit (Falklandy, jarmark MŠ Mašinka, Rong string, jóga v knihovně, Pouť do Říma, Okřídlená svatba) už v kalendáři jsou. **Tělocvična:** nový řádek z Pečeckých novin 11/2026, s. 3 (jednání se soudním znalcem v první polovině října, termín obnovení prací nelze stanovit); v Aktualitách města zmínka o zastavení stavby není. **Monitoring Facebooku města:** doplněn listopad 2026 (3 příspěvky, stav k 4. 11.). **Smlouvy:** žádná nová smlouva (nejnovější z 27. 10. už v tabulce), úřad 49 smluv / 33 899 163 Kč beze změny; skupina podle Hlídače státu hlásí 156 smluv / 97,0 mil. Kč proti 185 / 104,6 mil. Kč v tabulce — úbytek, čísla ponechána beze změny a nahlášena. **Zakázky:** beze změny (193 výsledků, 13 ID ve snímku). **Výbory, komise, školská rada:** beze změny. **Aktuality Pečeckých služeb:** Havárie, Oznámení, Odpady a vodoměry bez novinek (Voda i Kalendář aktuální).

4. listopadu 2026 (týdenní kontrola Jednání). Na usneseni.cz přibyl zápis a usnesení RM 39/2026 (2. 11. 2026): `jednani/pecky-jednani.json` doplněn o 2 usnesení (UR-338 a UR-339-39/26), délky bodů, docházku (6 ze 7), důvodové zprávy a zamítnutý návrh prodeje/zápůjčky sochy Klementa Gottwalda (0–6–0); čas `time` smazán. ZM 8/2026 (4. 11. 2026) zůstává jen s Pozvánkou, živý přenos je doplněný a sedí s úřední deskou pecky.cz. Nové shrnutí `jednani/shrnuti/2026-11-02-rada.md` (banner „Z poslední Rady města“ na Domů). Přegenerováno: Pozemky/parcely (`update-pozemky.py`), Kalendář (`update-kalendar.py`), docházka (`absence.py`). Tělocvična: nový řádek 2. 11. 2026 (schůzka se znalcem 9. 11., diagnostika piloty) v `content/telocvicna.html` + `telocvicna/HISTORIE.md`. Prostory: zkontrolováno, beze změny.

4. listopadu 2026 (denní kontrola sociálních sítí, 49 účtů). Počet sledujících: Pravoslavná obec (FB skupina) 325 → 328 členů, Alena Švejnohová 971 → 972, Pečecké služby 815 → 818, NAŠE PEČKY – komunita (FB skupina) 538 → 540 členů, Instagram AFK Pečky 361 → 362, ZŠ Pečky při ZŠ Kolín 141 → 142, ostatní beze změny. Nová aktivita: 4. 11. (PEČKY město v Polabí, U Marka, Siňorita, NAŠE PEČKY – komunita), 3. 11. (Máme rádi Pečky, Město Pečky, Školní jídelna, Pramínek FB, U Stříkačky, ZUŠ). Datum posledního příspěvku na Instagramu se četlo z kódů příspěvků (nejnovější z prvních 12 dlaždic). YouTube Město Pečky 100 odběratelů beze změny; `jednani/update-youtube.py` obnovil `content/youtube.html` (33 záznamů, 9 172 zhlédnutí, +8). Fotky ani Události nebyly tento běh procházeny, hledání akcí a změn provozu pro Kalendář se neprovedlo.

4. listopadu 2026 (denní běh Na oběd). Doplněno menu U Marka a Siňority z 4. 11. 2026 (přepis z fotografie do `naobed/data/<id>/2026-11.json` a `menu.json`). U Stříkačky bez nového menu (poslední příspěvek je lístek z 3. 11.), označeno jako zkontrolováno. Školní jídelna už měla jídelníček na dnešek; skript nepřidal žádný nový den.

3. listopadu 2026 (opakovaný běh Na oběd). U Stříkačky doplněno menu z 3. 11. 2026 (přepis z fotografie do `naobed/data/hostinec-u-strikacky-pecky/2026-11.json` a `menu.json`). U Marka, Siňorita a školní jídelna už měly dnešní menu (přeskočeno).

3. listopadu 2026 (denní kontrola sociálních sítí, 49 účtů). Počet sledujících: Pečky NEXT (Facebook) 327 → 328, ostatní beze změny. Nová aktivita 3. 11. 2026: U Marka, Pečecké služby, Alena Švejnohová, Instagram Pramínek. YouTube Město Pečky 100 odběratelů beze změny; `jednani/update-youtube.py` obnovil `content/youtube.html` (33 záznamů, 9 164 zhlédnutí). Fotky ani Události nebyly tento běh procházeny, hledání akcí pro Kalendář se neprovedlo.

3. listopadu 2026 (otevírací doba Hospůdky na hřišti ve Velkých Chvalovicích). Z plakátu „Zimní otevírací doba od 1. 11.“ (příspěvek ve Facebook skupině, 2. 11. 2026) doplněno `opening_hours` v `lide/organizations.json` (st–čt 17:00–23:00, pá–so 17:00–24:00, ne–út zavřeno), nový zdroj v `lide/sources.json`; `naobed/README.md` upraven, že doba už je známá. Build bez chyb.

3. listopadu 2026 (denní běh Na oběd). U Marka a Siňorita doplněno menu z 3. 11. 2026, U Stříkačky lístek z 2. 11. 2026 (nejnovější příspěvek; přepis z fotografií, zapsáno do `naobed/data/<id>/2026-11.json` a `menu.json`). Školní jídelna už měla dnešní jídelníček (přeskočeno). Dodatečně doplněn lístek Siňority z 2. 11. 2026 (dohledán v sekci Fotky na Facebooku).

3. listopadu 2026 (oprava času přednášek okrašlovacího spolku). Začátek přednášek 3., 10. a 24. 11. 2026 vrácen na 18:30 (platí podle aktualit města a plakátu spolku); program KD Pečky (18:00) je jen přehled, takže pravidlo „novější zdroj“ se na něj nevztahuje — upřesněno v `CLAUDE.md`, poznámky u akcí opraveny.

3. listopadu 2026 (sloučení dalších duplicit v Kalendáři). `kalendar/akce.json`: přednášky Pečeckého okrašlovacího spolku 10. 11. (Hradiště z doby bronzové) a 24. 11. 2026 (Pouť do Říma) sloučeny s obecnými záznamy z programu KD Pečky (doklad přesunut do `evidence`, druhý záznam smazán). Podle nového pravidla „aktuální údaje z novějšího zdroje“ se u všech tří přednášek včetně té ze 3. 11. (Falklandy) mění začátek z 18:30 na 18:00 (program KD z 24. 9. 2026 je novější než aktuality města z 30. 7.–1. 9. 2026); rozpor v poznámce. Pravidlo doplněno do `CLAUDE.md`. Google Kalendář synchronizován.

3. listopadu 2026 (kontrola duplicit v Kalendáři). `kalendar/scripts/update-kalendar.py`: nová funkce `najdi_podezrele_duplicity()` a výpis `POZOR možná duplicita` při každém běhu — dvojice akcí téhož pořadatele ve stejný den do 60 minut od sebe se shodným slovem v místě; kurzy a řady se společným začátkem názvu se přeskakují. Popsáno v `kalendar/README.md`.

3. listopadu 2026 (sloučení duplicity v Kalendáři). `kalendar/akce.json`: dne 3. 11. 2026 byla přednáška Pečeckého okrašlovacího spolku v Kulturním domě vedena dvakrát — „Pečecký okrašlovací spolek – přednáška“ (18:00, jen doklad z programu KD Pečky) a „Falklandy, ostrovy vzdorující času“ (18:30, doklad z pecky.cz). Podle pravidla „jedna akce = jeden záznam“ zůstal záznam s dokladem z pecky.cz (18:30), doklad z programu KD se přesunul do jeho `evidence`, do poznámky přibyla zmínka o rozdílu 18:00/18:30 a druhý záznam se smazal. Google Kalendář přes `update-kalendar.py` synchronizován (1 událost smazána).

3. listopadu 2026 (úprava Voleb 2026 a postupu kontroly sociálních sítí). V tabulce „Volební uskupení“ na Volbách 2026 (`content/volby2026.html`) odstraněny odkazy na Facebook a Instagram uskupení i počty sledujících s daty posledních příspěvků; u každého uskupení zůstal odkaz na kandidátní listinu na volby.gov.cz. Z `assets/styles.css` smazána pravidla `.socials-cell .social-meta` a šířky posledního sloupce na 50 %. V `volby/2026/README.md` zrušeny bloky „Kde se volí“, „Perex“, „Podzáložky“ a „Sociální sítě uskupení“. V `o-webu/automation-socialni-site.md` zrušen krok 4 (promítnutí na Volby 2026), upraveny `o-webu/README.md` a skilly `DoPecek-socialni-site-check` a `DoPecek-update`: kontrola sociálních sítí se týká už jen O webu.

2. listopadu 2026 (týdenní kontrola zdrojů, bez změny obsahu). Smlouvy: Hlídač státu stále 185 smluv / 104,6 mil. Kč (úřad 49 / 33,9 mil. Kč), nejnovější podpis 27. 10. 2026 už v tabulce. Zakázky: 193 výsledků jako dřív, 13 ID z první strany výpisu je ve snímku; úplná rekonciliace pole `ids` se nedělala (stránkování Hlídače vrací UUID bez ID `P##V########`). Aktuality města (3 strany): všechny akce už v Kalendáři, bez zmínky o zastavení stavby tělocvičny. Úřední deska: poslední položky z 28. 10. 2026 už v `2026.txt`. Monitoring Facebooku: říjen 2026 uzavřen 1. 11., nic nechybí. Noviny: nové vydání nevyšlo. Jednání, výbory, komise a sociální sítě zkontrolovány dříve téhož dne (viz tabulka Stav sekcí). Aktuality Pečeckých služeb (Havárie, Oznámení, Odpady, Zapisování stavů vodoměrů, včetně archivu): vše už je ve Vodě a v Kalendáři (nejnovější havárie 30. 10., oznámení 21. 10., odpady 6. 1., vodoměry 19.–30. 9. 2026). Do tabulky Stav sekcí přepsáno jen datum kontroly u Kalendáře, Tělocvičny, Smluv, Novin a Zakázek.

2. listopadu 2026 (zkrácení sloupce „Co naposledy“ ve „Stavu sekcí“). Dlouhé buňky v `README.md` zkráceny na 1–2 věty; původní plné znění zde: **O webu:** sociální sítě (druhá kontrola 2. 11. 2026, 55 odkazů): počty Pravoslavná obec 319 → 325 členů, NAŠE PEČKY – komunita 536 → 538, U Stříkačky 524 → 526, Siňorita 616 → 617, AFK FB 656 → 657, Pramínek FB 919 → 921, hasiči 949 → 950, ZŠ 214 → 215; nová aktivita u 6 účtů (Okrašlovací spolek, Pravoslavná obec, Siňorita, U Stříkačky, skupina 302811704063917, Knihovna); zhlédnutí záznamů ZM na YouTube 9 163 **Volby 2026:** promítnuty účty (kontrola 31. 10. 2026): Pečky NEXT FB 328 → 327, Pečky Pečákům 255 → 256, ODS 265 → 266, Pečky srdcem 126 → 128 (poslední příspěvek 27. → 28. 10.), skupina SPD 56 → 57 členů, ostatní beze změny (NAŠE PEČKY FB i IG, Pečky NEXT IG) **Kalendář:** Pramínek Dobřichov (plakát Listopad 2026 a Události na Facebooku): 30 nových termínů (kavárna, Švadlenka, Tvořivý listopad, Jóga, Filatelistický kroužek, Krabice od bot, Průvod podzimníčků aj.), Zálesák od 3. 11. posunut na 17:15 **Voda:** dvě nové události: havárie vodovodu na Masarykově náměstí (30. 10. 2026) a plánovaná odstávka 2. 11. 2026 (J. A. Komenského, Chvalovická, V Kaštánkách, Nymburská, areál TONA, U Měnírny, Velké Chvalovice; Aktuality města a Pečeckých služeb), 60 událostí / 72 zdrojů **Dotace od města:** nová stránka `/dotace/` (sekundární menu za Pokladnou): skládaný sloupcový graf dotací po letech 2016–2026 a příjemcích (77 smluv, 13 dodatků, 17,94 mil. Kč), blok Investiční akce Sokola 2019 (3,6 mil. Kč, smlouva č. 30/2019) a tabulka dodatků ke smlouvám (2 navýšení: AFK 2018 +20 000 Kč, Sokol 2025 +110 000 Kč) **Obchvat:** nová stránka `/obchvat/` (hlavní menu před Tělocvičnou): blok „Obchvat města“ přesunut ze stránky Plán, přidán perex a situační mapa; oddíl „Co o obchvatu říká územní plán“ (2 km, 1,71 ha, S9,5/70, napojení, limity, doprava 2010 podle výroku ÚP po změně č. 2, 04/2024), dva řádky časové osy (2010, 04/2024), oddíl „Zástavba, která s obchvatem počítá“ (lokality Z08, Z09, Z11), upřesněná věta o koridoru v územním plánu a nový zdroj; z archivu jednání (2001–2026) a Pečeckých novin (2005–2026) doplněno 10 nových řádků časové osy a rozšířeno dalších 6 (2008, 10/2008 článek o 2,13 km a 85 mil. Kč, 2014 korespondence s krajem, 2016, 2017, 2019, 9. 2021, 2022–2024, 12/2025), oprava RM 10. 1. 2022 (usnesení ukládá doprojektování protihlukové stěny, ne schválení strategie výkupu), hlasování ZM 20. 10. 2021 (12:0:6), nové oddíly „Obchvat ve volebních programech“ a „Stará silnice II/329 a přechod u hřbitova“, odkazy na jednání a noviny **Plán:** projity všechny dokumenty ze sekce „Strategický plán“ na pecky.cz (Souhrn, plné znění, Excel aktualizace 2020, 3 dodatky, Akční plán 2024–2026, Adaptační strategie, Zásady pro investory): nový výklad plnění plánu (Excel s aktualizací 2020: 197 z 339 úkolů 2016–2020 splněno, od 2021 stav chybí; původní Souhrn: 13 splněno), čísla 697 úkolů / 558,5 mil. Kč po aktualizaci 2020 vedle původních 718 / 360,8 mil. Kč, callouty Aktualizace plánu (dodatky 6/2020, 12/2020, 9/2021) a Jak se verze liší; řádky tabulky Sociální pracovník, Stacionář, Tělocvična (178 mil. Kč v Akčním plánu), Obchvat, Mlýnský náhon (2. etapa splněna 2018, 15 mil. Kč v Akčním plánu) a Veřejné WC doplněny; nová tabulka Další položky Akčního plánu 2024–2026 včetně srovnání částek původního plánu a Akčního plánu (tělocvična 140 → 178 mil. Kč, náhon 5,4 → 15 mil. Kč, kabiny 6 → 9,7 mil. Kč, městská policie, workout, cyklostezky, Benešák, WC, obchvat, vodojem); nahrazen odkaz na Adaptační strategii a Zásady pro investory shrnutím **Pozemky:** nové fulltextové vyhledávání v tabulkách Nákup/Prodej (hledaný výraz v URL `?q=`, tlačítko Kopírovat odkaz); do tabulek doplněno 133 bodů ze starších jednání 2013–3/2021 (82 jednání z úřední desky a archivu města; po sloučení rady a zastupitelstva nákup 95 a prodej 44 unikátních obchodů; odebrány součty cen pod tabulkami; katastr z textu bodu nebo kontextu zápisu; nový `extract_rows_starsi()` v `update-pozemky.py`) **Prostory:** ordinace logopedie (čp. 292): po usnesení UR-323-36/26 stav „pronajato od 30. 10. 2026“ (5 100 Kč/měsíc, při využití 2 dny v týdnu 1 020 Kč, + služby 2 000 Kč, na dobu neurčitou), banner „Na programu“ odstraněn; vinotéka v Domě služeb (čp. 184): UR-325-36/26 — smlouva ukončena dohodou k 31. 12. 2026 **Volby 2014:** nová stránka `/volby/2014/`: výsledky pěti uskupení, tabulka 21 zvolených podle osobních hlasů s funkcemi (ČSÚ, Pečecké noviny 11/2014 a 12/2014), tlačítko ročníku 2014 v rozcestníku; nadpis „Výsledky voleb“ nad kartami uskupení (2014, 2018, 2022), z rozcestníku odebrán popisek „Volby:“ **Volby 2022:** nový blok „Kolik kdo dostal hlasů od voličů?“: tabulka 21 zvolených zastupitelů podle osobních hlasů (zápis o výsledku voleb) s pořadím na kandidátce, funkcemi a legendou uskupení; zkrácený perex a texty kolem karet; chipy koalice/opozice v rohu karty, `party-body` v pravé polovině karty na velkých obrazovkách; odstraněn blok „Kdo byl zvolen“ **Pečecké noviny:** vydání 10/2026 (Říjen 2026, 16 stran) doplněno do archivu (207. vydání celkem, 3176 stran) — PDF z pecky.cz, nahráno 26. 10. 2026; předchozí číslo 9/2026 přesunuto do roku 2026 v gridu, počet vydání v poznámce pod archivem 70; tiráž (redakce Alena Brantová, rada Zavřel, Kusá, Hartman) beze změny **PečkyBot:** index doplněn o 72 starších jednání z úřední desky (zápisy rady 2015–2016, usnesení ZM 2015–2021; ≈ 900 úryvků) a podstránky Kdo vede Pečecké noviny, Zhlédnutí záznamů, Odpracované hodiny, Nejdelší body jednání; rejstřík 1,6 → 2,0 MB (6 020 úryvků)

2. listopadu 2026 (Kalendář: Pramínek Dobřichov z Facebooku). Na žádost uživatele projit účet Komunitní centrum Pramínek (Události, záložka Fotky, plakát „Listopad v komunitním centru Pramínek“, plakáty Švadlenka, Komunitní kavárna a Průvod podzimníčků). `kalendar/akce.json`: 30 nových záznamů (Komunitní kavárna 8. a 15. 11., Švadlenka 10. 11., Tvořivý listopad 13./18./20. 11., Ukulele 5. a 26. 11., Zpívání 19. 11., Bandování 2. a 30. 11., Hravé muzicírování pro děti 5./19./26. 11., Průvod podzimníčků 6. 11. (MŠ Sluníčko Dobřichov), Tvoření s Jitkou 9. a 23. 11. bez času, Jóga st+ne a Filatelistický kroužek út v listopadu jako kurz, Krabice od bot 23. 11.–7. 12. jako kurz); u 33 termínů Zálesáku od 3. 11. čas 17:00 → 17:15 podle novějšího plakátu. Jóga a filatelie zapsány jen na listopad, plakát jiné měsíce neuvádí. `update-kalendar.py` včetně synchronizace Google proběhl (30 založeno, 33 upraveno).

2. listopadu 2026 (druhá kontrola sociálních sítí téhož dne, bez Událostí a Fotek). `content/owebu.html`: znovu přečteny počty a data u všech 55 odkazů (Facebook z `creation_time`, skupina Máme rádi Pečky z řazení „nové příspěvky“, Instagram z `<time>` prvních 5–6 příspěvků, YouTube z playlistu Zasedání ZM); změněny počty u 9 účtů a data u 6 účtů (viz řádek ve „Stav sekcí“). `content/volby2026.html`: osm překrývajících se odkazů beze změny. `content/youtube.html` obnoven (33 záznamů, 9 163 zhlédnutí, nejvíc ZM 6/2026 – 960). Hledání nových akcí a změn provozu v Událostech a záložce Fotky v tomto běhu neproběhlo.

2. listopadu 2026 (kontrola sociálních sítí). `content/owebu.html`: u 48 Facebook/Instagram/YouTube účtů přečten počet sledujících a datum posledního příspěvku (Facebook z `creation_time`, Instagram z `<time>` prvních příspěvků); změněny počty u 10 účtů (PEČKY město v Polabí 1,6 tis., Pravoslavná obec 319 členů, Pečecké služby 815, AFK FB 656, AFK IG 361, NAŠE PEČKY – komunita 536, U Stříkačky 524, Nejen kavárna u Radu 518, streetpeopleofpecky 1 195, YouTube 100) a data u Města Pečky, Máme rádi Pečky, U Marka, Pramínku FB a IG, AFK, Pravoslavné obce a dalších. U Instagramu streetpeopleofpecky, Nejen kavárna u Radu a Western Saloon se datum posledního příspěvku nepodařilo přečíst, zůstalo beze změny. `content/volby2026.html`: osm překrývajících se odkazů beze změny. `content/youtube.html` obnoven (33 záznamů, 9 160 zhlédnutí). Hledání akcí v Událostech a Fotkách u jednotlivých účtů neproběhlo (jen čtení počtů a dat).

2. listopadu 2026 (denní kontrola Na oběd). U Marka: zapsáno denní menu z 2. 11. 2026 (polévka, 12 jídel, přílohy) přepsané z fotografie na Facebooku (`naobed/data/u-marka-pecky/2026-11.json`, `naobed/menu.json`). Siňorita (poslední menu 29. 10.) a U Stříkačky (30. 10.) bez nového menu, označeny jako zkontrolované. Školní jídelna už měla dnešní jídelníček.

1. listopadu 2026 (úprava stránky Usnesení, zatím bez odkazu). Přidány nepřijaté návrhy (81 z archivu usneseni.cz do `usneseni/neprijata.json` + 2 z `rejected_vote` v `jednani/pecky-jednani.json`) s filtrem Výsledek a štítkem „Nepřijato“; karty jsou sbalené (datum | nadpis, „+“). Změněno: `content/usneseni.html`, `usneseni/update-hlasovani.py`, `usneseni/README.md`.

1. listopadu 2026 (úprava Domů). Widget „Dnes“: když dnes nezbývá žádná akce, ukáže se nejbližší další den s chipem (zítra / pozítří / za N dní) a jeho událostmi (`assets/common.js`, popis v `domu/README.md`).

1. listopadu 2026 (Usnesení, rozpočtová opatření). Na `/usneseni/` přibyl u usnesení k rozpočtovým opatřením sbalovací blok s důvodovou zprávou a ručně sestaveným shrnutím změny rozpočtu v titulku (`usneseni/rozpocet-shrnuti.json`, 30 usnesení s úplnými částkami); dále jména hlasujících u usnesení zastupitelstva (`usneseni/hlasovani.json`, `hlasovani-rucne.json`, generátor `update-hlasovani.py`).

1. listopadu 2026 (nová stránka Usnesení, zatím bez odkazu). Založena `/usneseni/` (`content/usneseni.html`, `usneseni/README.md`, záznam v `EXTRA_PAGES` v `scripts/build.py` s `noindex`, mimo navigaci a sitemapu): seznam všech 2 828 usnesení rady a zastupitelstva od 4/2021 z `jednani/pecky-jednani.json` s fulltextem, filtrem orgánu a roku, štítkem výsledku a odkazem na jednání. Klasifikace výsledku usnesení přesunuta z `content/jednani.html` do `assets/helpers.js`, aby ji sdílely obě stránky.

1. listopadu 2026 (Lidé, fotky z Pečeckých novin 9/2018). Ze str. 8 (kandidáti NAŠE PEČKY 2018) vyříznuto 10 portrétů do `volby/2018/zastupitele/` (Janáčková, Schürzová, T. Drška, J. Drška, B. Kozáková, Vlk, Jiroudková, Kynclová, Crkalová, Vaz Santos) a doplněno do `lide/people.json` jako `photos` s ročníkem 2018 a zdrojem; těmto lidem dosud žádná fotka v adresáři nechyběla jinak. Doplněno ještě 9 portrétů kandidátů ODS ze str. 10 (Homan, Strnad, Kusý, Lazar, Vaníček, Šíma, K. Holub, Hof, Š. Růžička) a u Janáčkové, Schürzové a Vlka připojeny dosud nepropojené fotky z 2022; do `lide/sources.json` přidán zdroj FB skupiny Pravoslavné obce. Dále připojeno 25 dosud nepropojených portrétů z `volby/2022/zastupitele/` (15 ODS ze str. 9, 10 NAŠE PEČKY ze str. 11 Pečeckých novin 9/2022).

1. listopadu 2026 (Monitoring Facebooku města, měsíční běh). Říjen 2026 dokončen: 35 příspěvků (5 nových z 27.–30. 10. s popisy, počty reakcí u ostatních obnoveny); archiv má 96 měsíců a 2 103 příspěvků. Změněno: `content/fbmonitoring.html` a stránka Monitoring (generováno `summary.py`), `lastmod` v `scripts/build.py`, rozsah zdroje v `o-webu/facebook-monitoring/README.md`, řádek O webu ve „Stav sekcí“.

1. listopadu 2026 (úprava Domů, témata bannerů). Zvýraznění částek zahrnuje i „/m²“ (celé „52 Kč/m²“). Zmínky „parc. č. N“ v tématech bannerů „Z rady města“ / „Ze zastupitelstva“ jsou odkazy do katastru (`_odkaz_parcely()` v `scripts/build.py`, mapa `jednani/parcely-odkazy.json`); popsáno v `jednani/automation-katastr-parcely.md`.

1. listopadu 2026 (úprava Domů, vzhled bannerů). Štítky (`.tag`) na bannerech s barevným pozadím jsou globálně bílé s barvou banneru (dřív žlutý chip na slate banneru a nízký kontrast „ZÍTRA“ na bordó). Témata v bannerech „Z rady města“ / „Ze zastupitelstva“: build (`_zvyrazni()` v `scripts/build.py`) zvýrazní částky v Kč a procenta žlutým `<mark>` (`.banner mark` v `assets/styles.css`); ručně `==text==`, popsáno v `jednani/INSTRUKCE-shrnuti-schuzky.md`.

1. listopadu 2026 (úprava Domů). Banner příštího zasedání zastupitelstva: jednořádková poznámka nahrazena odrážkami (jednání je veřejné, živý přenos a záznam, dotazy přes chat na YouTube nebo telefonicky). Telefon se bere z `lide/people.json` (tajemnice, `nepovimovap`) přes `_zm_poznamky()` v `scripts/build.py`; styl `.banner-points` v `assets/styles.css`.

1. listopadu 2026 (úprava Lidé). `lide/people.json`: u tajemnice Bc. Pavlíny Nepovímové doplněno `bio` — její mobil +420 607 025 406 je v příloze „odkaz na YouTube“ k pozvánkám na zasedání zastupitelstva uveden jako telefonní kontakt v době zasedání (ověřeno u 26 příloh od ZM 9. 2. 2022 po ZM 7. 10. 2026). `lide/sources.json`: nový zdroj `uredni-deska-youtube-zm-7-10-2026`. `README.md`: řádek Lidé ve „Stavu sekcí“.

25. října 2026 (týdenní kontrola `DoPecek-update`). Jednání: do `jednani/pecky-jednani.json` přidána Rada 38/2026 (26. 10. 2026) jen s pozvánkou (14 bodů, bez zápisu, `time` 15:00); ZM 3/2026 bez videa na YouTube (ověřeno hledáním v playlistu), ZM 2/2026 má časové značky u 14 z 16 bodů (body 8 a 9 v popisku videa kapitolu nemají). Pozemky, Kalendář (+1 událost Rada 38/2026, synchronizováno do Google), absence a Prostory přegenerovány, Prostory beze změny. Výbory a komise: nový zápis nebyl, složení sedí s Lidmi. Smlouvy: skupina 184 smluv / 104 408 592 Kč, úřad 48 / 33 749 163 Kč; přidána smlouva o plavecké výuce ZŠ (7. 10. 2026, 352 473 Kč), přepsána tabulka Největší smlouvy; nárůst o 30 záznamů oproti 154 na webu je k ověření. Zakázky: 193 výsledků beze změny (ověřena první stránka). Pečecké noviny: archiv končí 9/2026, 10/2026 nenalezeno. Dokončeno 25. 10. 2026 (druhý běh): sociální sítě (O webu, 50 účtů; Volby 2026 bez změny), Úřední deska (shoduje se s monitoringem), Monitoring Facebooku (říjen do 23. 10., beze změny), Aktuality města (přidáno 5 přednášek a 1 akce do Kalendáře). Aktuality Pečeckých služeb přečteny i s archivem u typů Havárie, Odpady, Oznámení a Zapisování stavů vodoměrů (havárie a odstávky odpovídají Voda, svozy a zapisování stavů jsou v Kalendáři). Ověřeno znovu: Facebook (AFK, Vinotéka, Máme rádi Pečky, PEČKY Polabí, DC Glow) — data z dnešního dne potvrzena; Švejnohová 24. 10. potvrzena; YouTube 99 odběratelů, poslední ZM video 7. 10. 2026. Místa a pořadatelé přednášek a tvoření doplněny z plakátů; jen přednáška Pouť do Říma má místo odvozené od série spolku. Nepotvrzeno zůstává: datum posledního příspěvku u ZUŠ, Tenis Spartak, Hasičů a několika dalších stránek bez čitelného data.

20. října 2026, noc (týdenní kontrola `DoPecek-update`). Jednání: usneseni.cz beze změny (Rada 37/2026 z 19. 10. jen s Pozvánkou, nové jednání ani zápis nepřibyly); výbory, komise i školská rada beze změny; YouTube playlist ZM bez nového videa (ZM 3/2026 z 25. 5. dál chybí v playlistu), žádné nadcházející ZM. Tělocvična: zkontrolováno, beze změny (Aktuality města žádnou zprávu o zastavení stavby neobsahují). Smlouvy: nová smlouva 19. 10. 2026 (SZIF, 275 275 Kč) přidána do tabulky; počet smluv skupiny klesl 182 → 154 (úřad 47 → 48); souhrnná čísla přepsána na 154 smluv · 96 525 509 Kč (skupina) a 48 smluv · 33 749 163 Kč (úřad) na pokyn autora. Zakázky: beze změny (193 výsledků, 13 P##V ID ve snímku). Pečecké noviny: nejnovější je 9/2026, 10/2026 zatím nevyšlo. Úřední deska: 3 nové dokumenty (`493257`, `493185`, `491821`), přílohy staženy, Monitoring přegenerován; nic pro Prostory, Pozemky ani Tělocvičnu. Aktuality města: všechny akce už v Kalendáři; odstávky elektřiny 21. 10. a nález kola jen zmíněny. Kalendář: zápasy AFK Pečky znovu staženy (14 nových výsledků, nový venkovní zápas B týmu 21. 11.), generátor přeskakuje záznam bez soupeřů (prázdný řádek mladší přípravky 11. 10.), Google kalendář synchronizován. Sociální sítě: pokrývá denní naplánovaný úkol (poslední běh 20. 10.).

16. října 2026 (týdenní kontrola `DoPecek-update`, Zakázky). Hlídač veřejných zakázek hlásí beze změny 193 výsledků, všech 13 ID viditelných ve výpisu je v `zakazky/pecky-zakazky-ids.json`; do snímku doplněn jen údaj `snapshot_date` a `note`, web beze změny.

15. října 2026 (kontrola Jednání). Doplněn zápis RM 36/2026 (12. 10.; UR-322 až UR-326, docházka 6 ze 7, délky bodů) do `jednani/pecky-jednani.json`; ZM 7/2026 dostalo časové značky videa u všech 8 bodů. Kalendář (Google synchronizován) a `absence.json` přepočítány. Prostory: logopedie v čp. 292 pronajata od 30. 10. (UR-323), nájem vinotéky v Domě služeb ukončen k 31. 12. (UR-325). Tělocvična: nový řádek 12. 10. 2026 (bod 3 RM 36/2026, bez usnesení). Pozemky, nejdelší jednání: beze změny.

6. října 2026, večer (Tělocvična, starší zápisy Rady 2015–2016; na žádost uživatele). V `jednani/starsi-jednani.json` dohledán zhotovitel stavby kuchyně DMC CZ, s.r.o. (RM 25. 9. 2015), technický dozor, úvěr 18 mil. Kč, dodatky z 8/2016 (vč. PD skutečného provedení od A11) a ZM 5/2016. `content/telocvicna.html`: sedm nových řádků v „Historii projektu“, úvod, gap-callout a první callout „Otevřené otázky“; `telocvicna/README.md`: nová podsekce a upravené „Co hlídat dál“. Zápisy nezmiňují piloty ani kolaudaci kuchyně.

5. října 2026 (týdenní kontrola `DoPecek-update`). Jednání: usneseni.cz beze změny (Rada 35/2026 z 5. 10. a ZM 7/2026 ze 7. 10. zatím jen s Pozvánkou; živý přenos ZM 7/2026 už v datech je), výbory, komise i školská rada beze změny. Tělocvična: program RM 35/2026 (body 10, 14, 15) i ZM 7/2026 (bod 3) už v sekci je, beze změny. Kalendář: nová akce Vítací koncert v ZUŠ Pečky (20. 10.) z Aktualit města, 7 nových výsledků zápasů AFK; Google kalendář synchronizován. O webu a Volby 2026: počty sledujících a data aktivity u 26 účtů, Western Saloon Pečky (IG) má nově datum posledního příspěvku. Pečecké noviny (nejnovější 9/2026), Zakázky (193 výsledků, všech 13 viditelných ID ve snímku) beze změny. Smlouvy: žádná nová smlouva (nejnovější 7. 9.), ale dotaz na skupinu nyní vrací 152 smluv / 95 486 534 Kč místo 182 na webu — čísla ponechána, k rozhodnutí.

3. října 2026 (Kalendář, plakát Pramínku; na žádost uživatele). Z plakátu „Říjen v komunitním centru Pramínek“ (Facebook Komunitní centrum Dobřichov Pramínek, příspěvek z cca 30. 9. 2026) přepsáno do `kalendar/akce.json` 11 nových záznamů (pořadatel `maminky-sobe`) a doklad přidán k Hrátkám s batolátky (1., 8., 15., 22. 10.), Kaštanové masti, Kožedělné dílně a kavárně 4. 10. Plakát neuvádí čas u Mozkového joggingu, Tvoření s Jitkou a kavárny 17. 10. (`time: null`); Drakiáda je „na Píchoře“. Google kalendář synchronizován.

2. října 2026, večer (Tělocvična, příprava stavby 2025; na žádost uživatele). Z Facebooku města 2025 promítnuty do
`content/telocvicna.html` tři příspěvky (31. 10., 11. 11., 21. 11. 2025) jako nová tabulka „Příprava stavby na podzim 2025“:
zeď u ZŠ jako podmínka zahájení, zadávací řízení (nabídky do 15. 12. 2025), plánovaná žádost o dotaci NSA až 30 mil. Kč.
K ověření příště: zda a s jakým výsledkem byla dotace NSA podána.

3. října 2026, noc (Monitoring Facebooku, rok 2019). Staženy a popsány měsíce 2019-01 až 2019-12 (309 příspěvků, pole `popis`
u každého); stránka Monitoring má teď 93 měsíců (2019-01 až 2026-09), 2 035 příspěvků. Přenos dat opět jedním staženým souborem
(smazán po běhu).

3. října 2026, noc (Monitoring Facebooku, rozsah grafu v adrese; na žádost uživatele). Zvolený rozsah se ukládá do URL: `?graf=roky`, `?graf=30dni`
(výchozí „Od začátku“ bez parametru); lze kombinovat s kotvou (`?graf=roky#fb-y-2022`).

3. října 2026, noc (Monitoring Facebooku, kotvy v grafu; na žádost uživatele). Sloupec grafu je odkaz na měsíc (`#fb-yyyy-mm`), rok (`#fb-y-yyyy`)
nebo den (`#fb-d-yyyy-mm-dd`): skript rozbalí měsíc, zvýrazní cíl a posune ho pod sticky nadpisy; fungují i kotvy v adrese.

3. října 2026, noc (Monitoring Facebooku, přepínač grafu; na žádost uživatele). Pod grafem segmentový přepínač rozsahu: Od začátku (měsíce) /
Po letech / Posledních 30 dní (dny do posledního zachyceného příspěvku, 30. 9. 2026). Osa y má dílky podle rozsahu dat (`bar_svg` v `summary.py`).

3. října 2026, noc (Monitoring Facebooku, graf; na žádost uživatele). Na stránce Monitoring hned za perexem statický SVG graf počtu příspěvků
po měsících (osa x čas, osa y počet, maximum březen 2020 zvýrazněno; `render_chart` v `summary.py`, bez externích knihoven).

3. října 2026, noc (Monitoring Facebooku, úprava stránky; na žádost uživatele). Tabulka měsíců na stránce Monitoring rozdělena po letech:
každý rok má sticky `h3` „2026 (189 příspěvků)“ a vlastní tabulku (`render_page` v `summary.py`); „Celkem“ je pod tabulkami jako řádek textu.

3. října 2026, noc (Monitoring Facebooku, milník; na žádost uživatele). Do `o-webu/facebook-monitoring/README.md` (sekce Milníky profilu)
a na stránku Monitoring (řádek na konci detailu měsíce 2018-11, konstanta `EVENTS` v `summary.py`) zapsána událost „Založení facebooku
města“ — 20. 11. 2018. Do počtů příspěvků se nezapočítává.

3. října 2026, noc (Lidé, z monitoringu Facebooku 2018; na žádost uživatele). U Aleny Švejnohové doplněna funkce předsedkyně Dobrovolného
svazku obcí Pečeckého regionu (zpráva starostky z 27. 11. 2018); nová organizace `dso-pececkeho-regionu`, vazba bez data volby a bez
příznaku „aktuální“ (zdroj neříká, zda funkci vykonává dosud), nový zdroj ve `sources.json`.

3. října 2026, noc (Monitoring Facebooku, rok 2018). Facebookový profil města má nejstarší dostupné příspěvky z 20. 11. 2018 —
feed se při scrollování zastavil, dřívější příspěvky se nenačítají. Staženy a popsány měsíce 2018-11 a 2018-12 (33 příspěvků);
stránka Monitoring má teď 95 měsíců (2018-11 až 2026-09), 2 068 příspěvků. Starší roky nemá smysl stahovat.

3. října 2026, noc (Pečecké noviny, na žádost uživatele). Ve výpisu archivu nový oddělovač „Noviny zdarma do schránek“ mezi čísly
červenec–srpen 2021 a září 2021 (roznos do všech schránek od 9/2021) a na konci stránky callout s odkazy na tři příspěvky Města Pečky
na Facebooku (10. 4. 2020, 11. 6. 2021, 10. 9. 2021).

3. října 2026, noc (Tělocvična + Lidé, z monitoringu Facebooku 2020; na žádost uživatele). Tělocvična: dva řádky v „Historii projektu“
(1. 7. 2020 schválená studie na webu města, 23. 11. 2020 Česká cena za architekturu pro autory studie); opraveno řazení tabulky
(červen 2022 zpět nahoře). Lidé: u Jaroslava Kučery doplněna Cena starostky města Pečky z 27. 1. 2020 za správu radničních hodin.

3. října 2026, noc (Monitoring Facebooku, rok 2020). Staženy a popsány měsíce 2020-01 až 2020-12 (324 příspěvků, pole `popis`
u každého); stránka Monitoring má teď 81 měsíců (2020-01 až 2026-09), 1 726 příspěvků. Přenos dat opět jedním staženým souborem
(smazán po běhu). Stahování selhalo napoprvé kvůli jinému rozměru okna — kliknutí na filtr se musí kontrolovat screenshotem.

3. října 2026 (Lidé, na žádost uživatele). Doplněn Jaroslav Kučera (†27. 7. 2023, správce věžních hodin města, zaměstnanec Pečeckých služeb)
s poznámkou o úmrtí; zdroj příspěvek města na Facebooku (přímý odkaz doplněn 3. 10. 2026). Uživatel psal „Jan“,
oznámení města uvádí křestní jméno Jaroslav. Celkem 441 osob.

3. října 2026 (Tělocvična + Lidé, z monitoringu Facebooku 2021; na žádost uživatele). Tělocvična: dva řádky 2021 v „Historii projektu“
(22. 2. výběr dodavatele PD, 17. 9. veřejná prezentace PD); příspěvek z 30. 3. 2021 s tělocvičnou nesouvisí. Lidé: nový záznam
Vladimír Hoza (†27. 1. 2021) s poznámkou o úmrtí. Úmrtí osob bez veřejné funkce (J. Kučera 2023, Z. Kašparová 2023) do Lidí nezapsána.

3. října 2026 (Monitoring Facebooku, rok 2021). Staženy a popsány měsíce 2021-01 až 2021-12 (251 příspěvků, pole `popis`
u každého); stránka Monitoring má teď 69 měsíců (2021-01 až 2026-09), 1 402 příspěvků. Přenos dat opět jedním staženým souborem
(smazán po běhu).

2. října 2026, večer (Monitoring Facebooku, roky 2023 a 2022). Staženy a popsány měsíce 2022-01 až 2023-12 (519 příspěvků, pole `popis`
u každého); stránka Monitoring má teď 57 měsíců (2022-01 až 2026-09), 1 151 příspěvků. Data z prohlížeče se přenesla jedním
souborem staženým z karty Facebooku (výstup nástroje má limit ~1 500 znaků) — soubor po běhu smazán.

2. října 2026, večer (Monitoring Facebooku, rok 2025). Staženy a popsány měsíce 2025-01 až 2025-12 (271 příspěvků, pole `popis`
u každého); stránka Monitoring má teď 21 měsíců (2025-01 až 2026-09), 460 příspěvků. Menu: žádné (rozhodnutí uživatele).

2. října 2026, noc (Monitoring Facebooku, rok 2024). Staženy a popsány měsíce 2024-01 až 2024-12 (172 příspěvků, pole `popis`
u každého); stránka Monitoring má teď 33 měsíců (2024-01 až 2026-09), 632 příspěvků.

2. října 2026, večer (Monitoring Facebooku, úprava obsahu stránky). Místo výňatků z textu je v tabulce příspěvků krátký ruční
popis (nové pole `popis` v JSON, doplněno u všech 189 příspěvků), takže se na web nedostanou jména ani telefony z původních
textů; zrušeno zvýraznění rozbaleného řádku při najetí myší. Pole `popis` se píše při sběru každého nového měsíce.

2. října 2026, večer (O webu → Monitoring Facebooku, úprava stránky). Tabulka zjednodušena na Měsíc | Příspěvků; řádek měsíce je
klikací (rozbalí rozpad podle typu v pevném pořadí + tabulku Datum | Obsah s výňatkem a odkazem na FB, pod ním
👍 💬 ♺ a typ). Generuje `summary.py` do `content/fbmonitoring.html` (inline CSS + malý JS v obsahu stránky).

2. října 2026, večer (O webu → Monitoring Facebooku, na žádost uživatele). Doplněny měsíce 2026-01 (19 příspěvků) a 2026-02
(12); stránka Monitoring má teď 9 měsíců, 189 příspěvků (`summary.py` → `content/fbmonitoring.html` → build).

2. října 2026, večer (O webu → Sociální sítě + nová stránka Monitoring, na žádost uživatele). Pod položku „Facebook — Město
Pečky (oficiální)“ přidán podřádek s odkazem na novou stránku `/o-webu/facebook-monitoring/facebook-mestopecky/`
(`content/owebu.html`, ne vnořený `<a>`, ať nerozbije počítání `class="qlink"` v kontrole sociálních sítí). Stránka
(`content/fbmonitoring.html`, registrace `EXTRA_PAGES['fbmonitoring']` ve `scripts/build.py`) vypisuje sestupně
tabulku měsíců „2026 Březen“…: počet příspěvků, typy, sdílení z cizích profilů, celkem 158. Tabulku generuje
`summary.py`; po každém novém měsíci spustit `summary.py`, `build.py` a přepsat `lastmod` v EXTRA_PAGES.

2. října 2026, večer (Tělocvična, z Facebooku květen–září; na žádost uživatele). Staženy měsíce 2026-05 až 2026-09
(114 příspěvků, `o-webu/facebook-monitoring/facebook-mestopecky/`). Do `content/telocvicna.html` promítnuty čtyři
příspěvky: 1. 6. (uzavírka ulice K. Havlíčka Borovského), 4. 6. (zahájení stavby), 30. 7. (návštěva náměstka
hejtmanky Skopečka) a 23. 9. (reakce vedení města — právní stanovisko, dokumentace). Prověřeno v Chrome: vyjádření vedení
města k pozastavení stavby bylo zveřejněno 3. 9. 2026 v 16:50, ne 4. 9. v 0:20 — opraveno na stránce i v
`telocvicna/README.md`. Ostatní FB kandidáty (Volby, Plán/Zakázky, Jednání, Kalendář) zatím nezpracovány.

2. října 2026, odpoledne (Tělocvična + nový monitoring Facebooku, na žádost uživatele). Založen
`o-webu/facebook-monitoring/` (README + `facebook-mestopecky/2026-03.json`, 22 příspěvků; JSON a `media/` v
`.gitignore`, jen lokálně). Z března promítnuto do Tělocvičny video „Nová tělocvična schválena!" (5. 3. 2026)
spolu se zápisem ZM 1/2026 (UZ-2-1/26) — v `content/telocvicna.html` nový řádek „4.–5. 3. 2026“. Zprávy typu
odstávka vody se nezpracovávají (rozhodnutí uživatele). Při příštím běhu monitoringu se na konci ptát, co s nalezenými
kandidáty do jiných sekcí.

2. října 2026 (kontrola sociálních sítí na žádost uživatele, skill
`DoPecek-socialni-site-check`). **O webu + Volby 2026:** 36 účtů,
počty se změnily u 7 (např. Švejnohová 961, skupina NAŠE PEČKY - komunita
520, Pečky NEXT FB 315), nová aktivita u 7 (2. 10.) a 2 (1. 10.);
Instagram čten přes `<time datetime>` dlaždic 1–5; YouTube 95 odběratelů,
beze změny. **Kalendář:** nové akce nenalezeny (všechny nalezené už v
`kalendar/akce.json`).

1. října 2026 (týdenní kontrola všech zdrojů, skill `DoPecek-update`).
**Jednání:** na usneseni.cz nová Rada 35/2026 (5. 10., 15:00, obřadní síň)
s Pozvánkou — 18 bodů, mj. bod 10 Dodatek č. 2 k SoD (informace), 14 TDS
a 15 KBOZP (dodatky č. 1 k příkazním smlouvám); zapsáno do
`pecky-jednani.json` (292 jednání). ZM 7/2026 (7. 10.) beze změny, živý
přenos je na kanálu. Video k ZM 6/2026 a značky videa jsou kompletní.
**Výbory:** nový zápis Kontrolního výboru z 28. 8. 2026 (sken, OCR ověřený
proti obrázku; 5 z 7 přítomno, bez usnesení; podklady ke stavbě —
protokol TDI o jádrovém vrtání piloty č. 102, výzva Atelier 99, e-maily
A99/Elsa consulting a Iora) — `vybory.json` má 49 jednání. **Komise a
školská rada:** beze změny. **Tělocvična:** dva nové řádky v tabulce
„Zastavení stavby v roce 2026" (28. 8. zápis KV a 5. 10. pozvánka RM 35)
+ podsekce v `telocvicna/README.md`. **Kalendář:** Rada 35/2026 a
Kontrolní výbor 28. 8. přidány (Google synchronizován), AFK zápasy 5 nových
výsledků, aktuality AFK bez změny; žádná nová akce s budoucím datem na
Facebooku/Instagramu (Události i čerstvé příspěvky pořadatelů). **O webu +
Volby 2026:** 36 účtů, počty změněny u 7, nová aktivita u 15, Instagram
načítán pomalu (počty z meta popisu, data z `<time datetime>`).
**Pečecké noviny:** archiv končí 9/2026, vydání 10/2026 zatím není.
**Smlouvy:** žádná nová smlouva; skupina ukazuje 181 smluv (web 182) —
pokles o 1, čísla na webu nepřepsána, k rozhodnutí uživatele; hodnota
skupiny 103 017 144 Kč (web 102 416 276), úřad 47 smluv, 33 473 888 Kč
(web 33 132 977) — počet beze změny, hodnota vyšší. **Zakázky:** žádné
nové P##V ID, ale Hlídač hlásí 188 výsledků (dřív 214), P##V ID jsou ve
výpisu jen u 13 nejnovějších záznamů, detail zakázky vyžaduje registraci
a „poslední změna" je u zakázky Dostavba (MARHOLD, 168 614 851 Kč)
19. 9. 2026 a u dvou dalších (ZEPRIS 23 213 64x Kč, CE-DA stezka
15 425 714 Kč) 16. 9. — web ukazuje starší data, k ověření ručně.
`python3 scripts/build.py` bez chyby.

30. září 2026, večer (O webu — nový zdroj, na žádost uživatele). Do Sociální sítě
přidána FB skupina Hospůdka na hřišti Velké Chvalovice (624 členů, poslední příspěvek
26. 9. 2026) — `content/owebu.html` (řádek řazen podle počtu členů), `sources.json`
(`facebook-group-hospudka-na-hristi`). Seznam má nově 36 účtů a skupina je tím součástí
týdenní kontroly (ta bere seznam z `content/owebu.html`). Zkontrolována na akce pro
Kalendář: záložka Události bez nadcházejících, poslední pozvánka (Rozloučení s létem
27. 9.) už proběhla — nové akce pro Kalendář: žádné nalezeny (poznámka v
`kalendar/README.md`). Do Volby 2026 se nepromítá (není volební uskupení).

30. září 2026, večer (Jednání + Tělocvična — pozvánka ZM 7/2026). Pozvánka na Zastupitelstvo 7. 10. 2026 je PDF
(čte se přes `fetch` z usneseni.cz a rozbalení streamů); z ní doplněn program 7 bodů do `pecky-jednani.json`
(+ UUID, odkaz na pozvánku, `links.livestream`). Bod 3 „Dodatek č. 2 k SoD“ promítnut do Tělocvičny (nový řádek
„7. 10. 2026 — plánováno“); obsah a cena dodatku z pozvánky nevyplývají. Kalendář i absence přegenerovány.

30. září 2026, večer (Lidé — sociální a bytová komise, na žádost uživatele). Doplněny vazby členů
**Komise bytové 2010–2019** a **Komise pro sociální oblast a zdravotnictví 2018–2019** z jmenovacích seznamů rady
města v Pečeckých novinách (RM 29. 11. 2010, 24. 11. a 8. 12. 2014, listopad 2018): 24 vazeb a 1 nová osoba
(Mgr. Petra Šetková); ostatní členové už v Lidech byli (celkem 427 osob, 801 vazeb; `node lide/validate.mjs`
bez chyb). Komise zápisy nezveřejňují, členství je doloženo jen jmenováním; obě zrušila rada města v létě 2019
a členy nové Komise pro otázky sociální, zdravotní a bytové z let 2019–2022 zdroje neuvádějí (mezera).
Popis v `lide/README.md`.

30. září 2026, večer (Lidé — členové komisí 2018–2022, na žádost uživatele). Ze zápisů komisí
(`jednani/komise.json`) doplněno do Lidí 10 nových osob a 57 vazeb (52 členských, 5 předsedů) u Komise sportovní,
Komise stavebně-dopravní (+ životního prostředí), Komise pro kulturu a vzdělávání a Sboru pro občanské záležitosti
za volební období 2018–2022 (celkem 426 osob, 777 vazeb; `node lide/validate.mjs` bez chyb). Mandát počíná
19. 11. 2018 (RM, komise jmenované po ustavení ZM; datum doloženo u SPOZ), pozdější členové mají první doložené
jednání; konec 14. 11. 2022 (nové komise UR-436 až UR-442-45/22). U vazeb se počítá docházka. Oprava
`jNameKey()` v `assets/helpers.js` (jména s „, DiS.“ a tituly arch./M.Sc./MBA/MPA se nepárovaly) — týká se i
docházky u výborů a stávajících komisí. Popis v `lide/README.md`.

30. září 2026, večer (Kalendář — komise a školská rada, na žádost uživatele). Do Kalendáře
přibylo 83 jednání: komise rady města, pracovní skupina pro oslavy 100 let, Sbor pro občanské záležitosti
(`jednani/komise.json`, 49) a školská rada ZŠ Pečky (`jednani/skolska-rada.json`, 34, pořadatel `zs-pecky`);
výbory (48) už v kalendáři byly. Kategorie `vybor`, titulek je název orgánu (u společného jednání dvou
orgánů oba názvy), odkaz vede na trvalý odkaz jednání. `build_vybory_events()` v
`kalendar/scripts/update-kalendar.py` čte všechny tři soubory; celkem 131 událostí orgánů, 4338 událostí
v kalendáři. Google Kalendář: dry-run ukázal 83 k založení, 0 změn a 0 mazání; ostrá synchronizace
spuštěna hned. **Do budoucna:** nová jednání komisí a školské rady se po vytěžení přidávají jako události
(poslední krok `DoPecek-komise-check`, `jednani/README.md` → „Kontrola nových zápisů komisí“ a „Školská
rada“, `kalendar/README.md`). `content/kalendar.html`: doplněný výčet zdrojů.

30. září 2026, večer (Lidé + Jednání — školská rada, na žádost uživatele). Do sekce
Lidé doplněny osoby a **začátky mandátů členů školské rady ZŠ Pečky** (2008–2026): 8 nových
osob (Klára Literová, Lucie Charousová, Pavel Břečka, Romana Kubinová, Lenka Bitrmanová,
Vlastimil Procházka, Petr Hovorka, Ludmila Podlešáková) a 32 nových či upravených vazeb
`zs-pecky` (celkem 720 vazeb, 416 osob; `node lide/validate.mjs` bez chyb). Začátek mandátu
zástupců zřizovatele je datum usnesení rady města (29. 11. a 13. 12. 2010, 24. 11. 2014,
5. 12. 2022, 10. 11. 2025 — starší z Pečeckých novin), volených rodičů datum voleb
(14. 9. 2009, 11. 3. 2011, 23. 10. 2014), u pedagogů první doložené jednání. **Funkční období
současné rady začalo 5. 1. 2026** (RM 1/2026, bod 15 „Složení školské rady“ — podle volebního
řádu tím rada města stanoví počátek tříletého mandátu); předsedkyně Michaela Trčková od
5. 2. 2026, předtím Hana Kuprová (od 17. 1. 2023) a Martin Jedlička (2011–2014, 2015–2023).
Iveta Minaříková z rady 2014–2019 je Bc. Iveta Dvořáková (`dvorakovai`, dřívější příjmení).
`jednani/skolska-rada.json`: příjmení členů z let 2009–2014 nahrazena celými jmény (podle
voleb a jmenování), přibyly klíče `election_rules`, `elections` (volby 2009, 2011, 2014,
2019, ustavení 2026) a `other_decisions`; ostatní dokumenty ze stránky ŠR (volební řád 2025,
výsledky voleb, výroční zprávy 2016–2018) staženy do `jednani/Data/skolska-rada-dokumenty/`.
Nerozpoznaní členové (Astrová, Taxová, Korouš, Hájková) zůstávají příjmením. Popis v
`lide/README.md` → „Školská rada ZŠ Pečky — členové 2009–2026“.

30. září 2026, večer (Jednání — školská rada, na žádost uživatele). Zápisy
školské rady ZŠ Pečky z webu školy (zspecky.cz → Zápisy a dokumenty ŠR) jsou
stažené do `jednani/Data/{datum}-skolska-rada/` (43 souborů, `Data/` je v
`.gitignore`) a vytěžené do nového `jednani/skolska-rada.json` (34 jednání
7. 9. 2009 – 28. 8. 2026, 61 usnesení) a zařazené do filtru „Komise“ na stránce Jednání
(trvalé odkazy `#skolska-rada-…`). Většina zápisů před 2023 jsou skeny (OCR), u 2009–2016
nízké rozlišení; jména členů jsou do 2014 a 2019–2022 jen příjmením, jak je píše zápis.
Zápis 7. 11. 2024 obsahuje diskuzi o personální záležitosti konkrétního zaměstnance —
záměrně nepřepsána. U jednání per rollam (2020–2022) zápis nejmenuje členy. Ve
`content/lide.html` se u členů školské rady počítá docházka; do `content/telocvicna.html`
přibyly dva řádky (17. 1. 2023, 28. 8. 2026) a tabulka se přejmenovala na „Tělocvična
v komisích rady města a ve školské radě“. Nový skript
`jednani/scripts/skolska-rada-check.py`, zapojený do skillu `DoPecek-komise-check`;
postup v `jednani/README.md` → „Školská rada“. `python3 scripts/build.py` bez chyby.

30. září 2026, večer (Jednání — komise, na žádost uživatele). Nově se
sledují zápisy komisí rady města z pecky.cz (Rada města → Komise RM) za obě
volební období, 2018–2022 i 2022–2026. Nový soubor `jednani/komise.json`
(49 jednání, 102 usnesení a doporučení). 2022–2026: sportovní komise 7
zápisů (4/2023–2/2026), kulturní komise a pracovní skupina pro oslavy 100 let
povýšení Peček dohromady 9 jednání (pět společných zápisů je na pecky.cz
vystavených dvakrát pod oběma orgány, v datech jsou jednou), stavebně-dopravní
komise 4 (1/2024–9/2025). 2018–2022: sportovní komise 8 (12/2018–6/2022),
kulturní komise 10 (12/2018–8/2022; u 4 zápisů z let 2019–2020 je zveřejněn jen
program), stavební komise 10 (12/2018–3/2022) a jediný zveřejněný zápis Sboru pro
občanské záležitosti (13. 12. 2018); společná jednání sportovní a stavební komise
23. 5. a 27. 6. 2019 jsou jednou se dvěma odkazy na zápis. Sociální komise zápisy
z důvodu ochrany osobních údajů nezveřejňuje — přiznáno v calloutu. Deset zápisů
je skenů (OCR). `content/jednani.html`: filtr „Komise“, trvalé odkazy
`#sportovni-komise-…` atd., krátké shrnutí z textu zápisu u každého jednání,
u sportovní komise usnesení pro každou dotaci oddílu zvlášť (hlasování včetně jmen
zdržení). `content/lide.html`: docházka členů komisí u jejich vazeb (jen ze zápisů,
které je jmenují; zápisy 2018–2022 se k dnešním vazbám nepočítají).
`content/telocvicna.html`: nová tabulka „Tělocvična v komisích rady města
(2019–2026)“ — 4 řádky z let 2025–2026 a 6 z let 2019–2022 (studie tělocvičny,
odhad cca 100 mil. Kč, hlasování stavební komise 8. 4. 2019). Nový skript
`jednani/scripts/komise-check.py` a skill `DoPecek-komise-check` (zapojen do
`DoPecek-update`), postup v `jednani/README.md` → „Zápisy komisí RM“.
Zjištěné rozpory se složením v Lidech (Metelák, Vodička, Katrnoška ve stavební
komisi; Šátková na webu chybí) jsou popsané v README a neopravené. Kalendář
a Domů komise zatím nezahrnují. `python3 scripts/build.py` bez chyby.

30. září 2026, večer (Kalendář, na žádost uživatele — kontrola akcí
je teď součástí týdenní kontroly Kalendáře i kontroly sociálních sítí).
Postup `kalendar/automation-plakat-akce.md` prošel Facebook Události
všech facebookových zdrojů a nejnovější příspěvky hlavních pořadatelů.
Do `kalendar/akce.json` přibylo: Slavnostní otevření dětského hřiště
(4. 10., 14:00, Centrální park; plakát sdílel KS Pečky, pořadatel Město
Pečky), Namaluj si akvarel na textil s Frantou Hálou (knihovna, 3. 10.),
Průvod sokolských světel (TJ Sokol, 8. 10.) a nový pondělní kroužek
Dětská jóga — zvířátková (Vzdělávací centrum, 34 termínů od 5. 10. 2026).
Kino pro děti 4. 10. má v názvu „ZRUŠENO" podle příspěvku KS Pečky
(zrušení potvrzeno jen z úvodu příspěvku), Slavnost v parku 3. 10. dostala
druhý doklad z Facebook Události. Vynechány Slavnosti podzimu a moštování
(Poděbrady). Kalendář synchronizován do Google automaticky (36 nových
událostí, 1 upravená). `python3 scripts/build.py` bez chyby.

30. září 2026 (týdenní kontrola sociálních sítí, skill
`DoPecek-socialni-site-check`). Projito všech 35 účtů v Claude in
Chrome. Facebook: počet z „sledující (N)", datum z nejvyššího
`creation_time` (u FB skupiny Máme rádi Pečky až po přepnutí na
chronologické řazení — bez něj skript vrátil starší 11. 9.). YouTube:
95 odběratelů, poslední video z playlistu Zasedání ZM (ZM 6/2026,
17. 9., beze změny). Instagram se načítal pomalu a část požadavků vracela
429, proto počty z meta popisu profilu a data z `<time datetime>`
dlaždic 1–4 (u `nase_pecky` i `peckynext` byly první 3 dlaždice
připíchnuté, nejnovější až dlaždice 4 = 29. 9.). Změny počtů:
Instagram NAŠE PEČKY 114 → 117, Instagram Pečky NEXT 139 → 141, Pečky
srdcem 101 → 102, FB skupina NAŠE PEČKY - komunita 518 → 519,
streetpeopleofpecky 1 214 → 1 213. Nová aktivita 29. 9. u 12 účtů a 30. 9.
u TJ Sokol Pečky; ostatní beze změny. Promítnuto i do Volby 2026 (8
překrývajících se odkazů). Instagram Nejen kavárna u Radu (8. 7.) a
ostatní neaktivní účty beze změny. `python3 scripts/build.py` bez chyby.

29. září 2026, odpoledne (starý web města, na žádost uživatele). Stránky
se zápisy výborů na pecky.as4u.cz porovnány s novým pecky.cz: tři zápisy
jsou jen na starém webu — FV 23. 11. 2023, KV 21. 5. 2025 a KV 19. 11. 2025
(na první a třetí se odkazovaly jiné zápisy jako na nezveřejněné). Stažené
do `jednani/Data/`, vytěžené do `jednani/vybory.json` (48 jednání),
promítnuté do Tělocvičny (nový řádek 23. 11. 2023) a Kalendáře, který se
poprvé synchronizoval do Google automaticky přímo z generátoru (3 nové
události). `jednani/scripts/vybory-check.py` nově kontroluje i starý web.
`python3 scripts/build.py` proběhl bez chyby.

29. září 2026 (jednání výborů zastupitelstva, na žádost uživatele krok
po kroku. Staženo a ručně vytěženo všech 45 zápisů finančního (11/2018–
6/2026) a kontrolního výboru (3/2020–6/2026) z pecky.cz do nového
`jednani/vybory.json` — účast všech členů, hosté, program, 75 usnesení
a doporučení doslova i s výsledkem hlasování (u starších zápisů často
chybí, přiznáno). 14 skenů čteno přes OCR, sporná místa ověřena proti
obrázku; dva zápisy mají na webu chybné datum v názvu souboru. Sekce
Jednání: filtr Finanční/Kontrolní výbor, trvalé odkazy, u bodů Rady/ZM
„Zápis/Zpráva z jednání výboru“ výčet jednání výboru od minulého
zasedání. Lidé: složení výborů 2022–2026 i 2018–2022 (nová osoba
Ing. Ladislav Zindr, na pokyn uživatele sloučeny dva záznamy Jany
Sladké), u členů počty účasti. Tělocvična: nová tabulka o financování
a úvěru (2022–2026). Pozemky: zjištění KV k parc. 1449/118. Kalendář:
kategorie `vybor`. Domů: poslední zápis každého výboru. Nový skill
`DoPecek-vybory-check` a skript `jednani/scripts/vybory-check.py`,
zařazeno do týdenní kontroly. Synchronizace Google Kalendáře v tomto
běhu nespuštěna. `python3 scripts/build.py` proběhl bez chyby.)

28. září 2026 (kontrola sociálních sítí, spuštěno ručně přes skill
`DoPecek-socialni-site-check`. Seznam v O webu → Sociální sítě má
nově 35 účtů (skill i `o-webu/automation-socialni-site.md` pořád mluví
o 14/15 — seznam se rozrostl 25. 9. se zdroji Kalendáře); zkontrolovány
všechny přes Claude in Chrome. Počet se změnil u 22 účtů, nová aktivita
u 18 z 28 účtů, které datum už měly, a u 7 dosud nedatovaných účtů
(Máme rádi Pečky, PEČKY město v Polabí, Pečecká desítka, NAŠE PEČKY -
komunita, AFK Pečky na Facebooku i Instagramu, Studio Anet) datum
poprvé doplněno. Instagram čten novým postupem přes `<time datetime>`
jednotlivých příspěvků (dlaždice 1–5, u připíchnutých 1–6): u
`nase_pecky` i `peckynext` byly dlaždice 1–3 připíchnuté a staré,
skutečně nejnovější příspěvek (27. 9.) až na dlaždici 4 — přesně chyták,
před kterým postup varuje. Facebook dál přes `creation_time`; dvě
nečekané hodnoty (Městská knihovna 27. 9., Pečecká desítka 7. 4.)
ověřeny i vizuálně na stránce. YouTube beze změny (95 odběratelů,
poslední video ZM 6/2026 17. 9.). Seznam znovu seřazen sestupně podle
počtu — nově přidané účty byly připojené na konec mimo pořadí.
Promítnuto i do odkazů na `/volby/2026/` (u Instagramu Pečky NEXT tam
datum dřív zaostávalo za O webu) a na žádost uživatele tam přibyl
Instagram NAŠE PEČKY — překrývajících se odkazů je teď 8. Opraven
i postup `o-webu/automation-socialni-site.md`: místo pevného výčtu 15
účtů odkazuje na aktuální stav `content/owebu.html` (s příkazem na
spočítání), výčet pro Volby 2026 rozšířen na 8. `python3 scripts/build.py`
proběhl bez chyby.)

24. září 2026 (kontrola jednání, spuštěno ručně přes skill
`DoPecek-jednani-check`. **Rada 34/2026 (21. 9. 2026)** dřív jen
s Pozvánkou, teď doplněn kompletní zápis a usnesení: 11 usnesení
(UR-300 až UR-310), plná agenda 19 bodů vč. předkladatelů a délky
projednávání (bod 3 „Aktuální informace vedení města" nejdelší, 59 min),
jmenovitá prezence 6 z 7 na začátku a průběžný příchod Ing. Petra
Dürra v 15:26. Bod 14 (krátkodobé užití pozemku parc. č. 1018, Park
pod vodojemem, žádost NAŠE PEČKY + PEČKY NEXT) hlasováním **nebyl
přijat** (1 pro, 4 proti, 2 zdržel se) — jde navíc o pronájem, ne
o prodej/nákup, takže mimo rozsah sekce Pozemky (Pozemky jen
zkontrolovány, beze změny). Na webu zatím žádné jednání nad rámec
Rady 34 (archiv beze změny 290 jednání). **Tělocvična:** bod 3 stejného
zápisu přidává dva nové detaily — čeká se nově i na vyjádření
geotechnika (dřív jen právní kancelář) a je naplánovaná schůzka se
zástupcem právní kanceláře; obsah ani termín schůzky zápis neuvádí,
žádné stanovisko pořád není k dispozici, rozpočet/cena/harmonogram se
nezmiňují — viz `telocvicna/README.md` → „Doplněno 24. 9. 2026".
**YouTube** (krok 6): video k ZM 3/2026 (25. 5. 2026) v playlistu
„Zasedání ZM" (32 videí) nadále chybí, žádná jiná mezera. **Časové
značky videa** (krok 7): beze změny, žádná nová mezera u jednání
s zápisem i videem zároveň — historický dluh u ZM 2022–2024 a ZM
1/2025 trvá (mimo rozsah, kapitoly v popisku tam nejsou vůbec).
Opraveny statické souhrny `pecky-jednani.json` → `meta`
(2 786 → 2 797 usnesení, `agenda_items_count` beze změny). Kalendář
přegenerován (`update-kalendar.py`, 3651 událostí) a synchronizován do
Google kalendáře (`sync-google.py`, klíč `.google-calendar-api-key.json`
k dispozici). Docházka přepočítána (`absence.py`) — stejný známý rozdíl
+1 u Rady 2022–2026 (vadný zápis RM 24/2024), žádný nový nevysvětlený
rozdíl. `python3 scripts/build.py` proběhl bez chyby, ověřeno na
`/jednani/` (počet usnesení v perexu 2 797, detail Rady 34 se správnými
badge SCHVÁLENO/ULOŽENO u bodů s usnesením, bez badge u zamítnutého
bodu 14) a na `/telocvicna/`.)

22. září 2026 (Kalendář propojený s Google Calendarem, zadal uživatel. Veřejný kalendář „Co se děje v Pečkách" teď plní nový skript `kalendar/scripts/sync-google.py`: čte hotový `kalendar/udalosti.json` a přes Google Calendar API doplní, co je nové, přepíše, co se změnilo, a smaže, co ze zdroje zmizelo. Přístup drží servisní účet, kterému uživatel kalendář nasdílel s právem „Provádět změny v událostech"; klíč `.google-calendar-api-key.json` leží v kořeni repa, je v `.gitignore` a do gitu nikdy nešel — ověřeno před prvním commitem. Běh je idempotentní: ID události v Googlu je `sha1` ze `source_ref`, takže opakované spuštění nic nezduplikuje, a skript sahá jen na události, které sám založil. První plný běh nahrál 1317 událostí a trval kolem 15 minut (~0,75 s na zápis, Google zápisy na jeden kalendář škrtí); kontrolní běh po něm hlásí 0 založit / 0 upravit / 0 smazat. Zdroj se během nahrávání změnil z 1312 na 1317 událostí, protože mezitím přibylo pět akcí — poslední průchod si jich všiml sám a doplnil je, což je přesně to, kvůli čemu je běh idempotentní. Repozitář tím získal **první externí závislost** (`google-api-python-client` + `google-auth`); ostatní skripty dál jedou na standardní knihovně a bez ní fungují dál, spadne jen tenhle. Synchronizace je zapsaná jako povinné pokračování do dvou automatizací — `kalendar/automation-plakat-akce.md` krok 6 a `jednani/automation-kontrola-usneseni-cz.md` krok 8b — ale podmíněně: chybí-li klíč, běh ji vynechá, pokračuje dál a napíše do shrnutí, že Google čeká na ruční spuštění. Bez toho by denní cloudová kontrola na chybějícím klíči spadla. Klíč do GitHub Actions zatím vědomě nešel, synchronizaci spouští uživatel ručně. Součástí téhož commitu jsou i změny, které do repa přibyly během dne: šest nových akcí v `kalendar/akce.json`, nový zdroj NAŠE PEČKY v seznamu pod mřížkou, přepsaný perex `/kalendar/` s odkazem na odběr kalendáře a emoji u položky Kalendář v patičkové navigaci.)

19. září 2026 (kontrola sociálních sítí, spuštěno ručně přes skill
`DoPecek-socialni-site-check`. Projito všech 15 odkazů přes
Claude in Chrome — počet sledujících a `creation_time` ze `<script>`
dat stránky, viz `o-webu/automation-socialni-site.md`. Počet
sledujících se změnil u 5 účtů: Pečky NEXT FB 307 → 308, Pečky
Pečákům 245 → 246, ODS a nezávislí 228 → 232, Instagram Pečky NEXT
130 → 131, Pečky srdcem 86 → 87. Nová aktivita u 8 účtů: Město Pečky
(18. 9.), NAŠE PEČKY (19. 9.), Alena Švejnohová (18. 9.), Pečky NEXT
FB (19. 9.), ODS a nezávislí (18. 9.), TJ Sokol Pečky (17. 9.),
YouTube Město Pečky (17. 9. — záznam Zastupitelstva 6/2026 konečně
zveřejněn na kanálu), FB skupina Lidé pro Pečky s podporou SPD
(19. 9.). **Zjištěna a opravena chyba v běhu 16. 9. 2026:** ten měl
u 5 účtů (Pečky-Virtuálně, Kulturní středisko, Městská knihovna,
Pečky Pečákům, Pečky srdcem) zapsané datum posledního příspěvku
shodné s datem kontroly napříč skoro všemi facebookovými účty
najednou — nápadná shoda, kterou dnešní ověření (`creation_time`
skript i vizuální kontrola stránky) nepotvrdilo: skutečná poslední
vlastní aktivita byla starší, 4.–14. 9. 2026, teď opravena na ověřené
datum. Beze změny zůstávají Facebook Město Pečky (2,9 tis.), Pečky-
Virtuálně (1,4 tis.), Instagram streetpeopleofpecky (1 216, datum
22. 8. trvá — Instagram od 2. 9. 2026 neumožňuje spolehlivě přečíst
datum z `img[alt]`, jen počet sledujících), Kulturní středisko (993),
Alena Švejnohová (956), Městská knihovna (483), TJ Sokol Pečky (224),
YouTube Město Pečky (95 odběratelů), FB skupina Lidé pro Pečky
s podporou SPD (40 členů). Překrývajících se 7 odkazů promítnuto
i do `/volby/2026/`. `python3 scripts/build.py` proběhl bez chyby,
ověřeno v prohlížeči na `/o-webu/` a `/volby/2026/`.)

16. září 2026 (týdenní kontrola zdrojů, spuštěno ručně přes nový
projektový skill `DoPecek-update` — nahrazuje starší
`pecky-online-daily-update`, který žil jen v datech appky Claude
(naplánovaná úloha), ne v repu; nový orchestrátor + dílčí skilly pro
Jednání/Noviny/Zakázky/Smlouvy/Tělocvičnu/sociální sítě žijí
v `.claude/skills/` (needituje se, celé v `.gitignore`). **Jednání:**
beze změny — Rada 33/2026 (14. 9.) a Zastupitelstvo 6/2026 (16. 9.,
dnes) nadále jen s Pozvánkou; YouTube i video_ts u nedávných jednání
v pořádku, historický dluh video_ts u 22 starších zastupitelstev
(2022–2025, žádná kapitola u žádného bodu) přetrvává — mimo rozsah
týdenní kontroly, k řešení jako samostatný úkol. **Tělocvična:**
zkontrolováno, beze změny — dnešní ZM 6/2026 má bod „Informace
o stavební akci“ na programu, zápis zatím nevyšel. **Smlouvy:**
zkontrolováno, beze změny — žádný nový podpis od WEBER HYDRAULIK
(7. 9.); pokračuje nevysvětlený úbytek v souhrnných číslech (skupina
182 → 181 smluv), čísla na stránce záměrně ponechána. **Zakázky:**
zkontrolováno, beze změny — 214 výsledků na Hlídači stejně jako 13. 9.,
žádné nové ID. **Pečecké noviny:** vydání 9/2026 doplněno do archivu
(206. vydání, 3160 stran) — nalezeno rovnou na archivním rozcestníku
pecky.cz, opraveny i 2 zastaralé počty v poznámkách pod starším
archivem. **O webu + Volby 2026:** zkontrolováno všech 15 sociálních
sítí, počty sledujících se změnily u 5 účtů, nová aktivita dnes u 12
z 15 (mj. Pečky-Virtuálně po 12 dnech ticha); opravena chyba v datu
posledního videa u YouTube kanálu Město Pečky — četlo se ze záložky
„Videa“ (zavádějící, viz `o-webu/automation-socialni-site.md“), teď ze
správného zdroje. `python3 scripts/build.py` proběhl bez chyby — 15
stránek + 1 neprolinkovaná podstránka, validace OK.)

15. září 2026 (týdenní kontrola zdrojů, spuštěno ručně přes skill
`pecky-online-daily-update` — pozn.: soubor skillu ještě mluví o „denní“
kontrole a režimu `denně`, ale repozitář (`README.md` → „Stav sekcí“,
`CLAUDE.md`) od 5. 9. 2026 běží na týdenním rytmu; podle vlastního
pravidla skillu platí repozitář, nesoulad k opravě v souboru skillu.
**Jednání:** beze změny — výpis na usneseni.cz (stav k 15. 9. 2026
15:55) identický se včerejškem, Rada 33/2026 (14. 9.) a Zastupitelstvo
6/2026 (16. 9.) nadále jen s Pozvánkou; YouTube playlist „Zasedání ZM“
beze změny (32 videí), známé mezery (video k reálnému ZM 3/2026
z 25. 5. 2026, video_ts u bodů 8–9 ZM 2/2026) trvají. **Tělocvična**
a **Pozemky:** zkontrolováno, beze změny — žádné nové jednání/usnesení
k vytěžení. **Smlouvy:** beze změny — Hlídač státu MCP potvrzuje přesně
stejná čísla jako 14. 9. (skupina 152 smluv / 95 486 533,66 Kč, úřad
47 / 33 473 888,05 Kč, nejnovější podpis nadále 7. 9. 2026). **Zakázky:**
beze změny — 176 unikátních ID formátu `P##V########` odpovídá přesně
baseline z 13. 9. Při té příležitosti průchod rozšířen na všech 5 stránek
výpisu (dřív se kontrolovaly 4) — objevilo se 18 dalších ID, ale všechna
mimo sledovaný formát (starší číselné/`Z`-prefixové položky z registru
před rokem 2016, nebo fulltextový šum jiných obcí jako u P22V00000346);
baseline soubor `pecky-zakazky-ids.json` proto zůstává nedotčen, jde jen
o potvrzení, že sledovaný formát je kompletní. **Pečecké noviny:**
beze změny — archiv na pecky.cz stále končí 7–8/2026. **O webu + Volby
2026:** zkontrolováno všech 15 sociálních sítí, viz řádky v tabulce
„Stav sekcí“ výše pro čísla; na úřední desce pecky.cz nic nového
k volbám od 10. 9. `python3 scripts/build.py` proběhl bez chyby —
15 stránek + 1 neprolinkovaná podstránka, validace OK.)

14. září 2026 (na žádost uživatele prohledána nová dávka Pečeckých
novin 2012–2015 (44 vydání) na zmínky relevantní pro sekci Tělocvična
— klíčová slova tělocvičn/kolaudac/pilot/základ/kuchyň/vývařovn/statik.
Většina zásahů byl falešný poplach, ale osm výtisků z let 2014–2016
vyplnilo mezeru v tabulce „Historie projektu“ mezi řádky 1. 9. 2008 a
červen 2016: PN 9/2014 (titulní článek o čekání na dotaci, tehdejší
odhad rozpočtu 78 mil. Kč), PN 10–11/2014 (Rada jedná s Ateliérem A11
o cenových návrzích a vybírá zpracovatele PD), **PN 4/2015 — nezávislé
potvrzení roku i zpracovatele (Ateliér A11) z tvrzení Aleny Švejnohové
o „dokumentaci z roku 2015“**, byť ne konkrétního údaje o délce pilot
(8,5 m) ani „kolaudačního“ charakteru dokumentu, PN 11/2015 (stavba
ještě neskončila) a PN 8/2016 („Vývařovna finišuje“). Promítnuto do
`content/telocvicna.html`: šest nových řádků tabulky, upravený úvodní
odstavec a gap-callout u „Historie projektu“, upravený první callout
v „Otevřené otázky“. Detaily v `telocvicna/README.md`.)

14. září 2026 (automatická kontrola usneseni.cz. **Jednání:** beze změny
— výpis na usneseni.cz (stav k 14. 9. 2026 08:26) ukazuje přesně to, co
už archiv má: **Zastupitelstvo 6/2026 (16. 9.)** a **Rada 33/2026
(14. 9.)** nadále jen s Pozvánkou, **Rada 32/2026 (7. 9.)** kompletní
od 10. 9. Žádné nové jednání, u žádného staršího nepřibyl zápis ani
usnesení; `pecky-jednani.json` nedotčen — archiv drží **289 jednání,
2 767 usnesení**. Playlist „Zasedání ZM" má 32 položek, beze změny proti
13. 9.: jediná novinka zůstává naplánovaný živý přenos **ZM 6/2026
(16. 9. 2026, 16:30)**, který se do `links.youtube` **nezapisuje** —
postup (krok 6) pracuje jen s jednáními v minulosti a odkaz se doplní
po zveřejnění záznamu. **Video k ZM 3/2026 z 25. 5. 2026 na kanálu
stále chybí**, známá mezera trvá. Časové značky bodů (`video_ts`)
prověřeny u všech zastupitelstev od ZM 2/2025: jediné chybějící jsou
„Volba pracovních komisí" (vlastní kapitolu v popisku nikdy nemá), body
8 a 9 u ZM 2/2026 a celé ZM 3/2026 bez videa — vše ověřené mezery, nic
k doplnění. **Tělocvična:** zkontrolováno, beze změny — nepřibylo
jednání, jehož program nebo usnesení by se stavby týkaly; bod
„Informace o stavební akci Dostavba učeben a tělocvičny v ZŠ Pečky"
z programu ZM 6/2026 je v sekci podchycen už od 10. 9. **Pozemky:**
žádné nové usnesení k prodeji/nákupu pozemku, `update-pozemky.py`
nespouštěn. Web přegenerován kontrolně (`scripts/build.py`), výstup
identický. Změněn jen tento changelog a datum kontroly u Jednání
a Tělocvičny v tabulce „Stav sekcí".)

13. září 2026 (týdenní kontrola zdrojů. **Jednání:** na usneseni.cz
přibylo jedno nové jednání — **Rada 33/2026 (14. 9. 2026)**, zatím jen
s Pozvánkou; zaznamenáno s programem o 9 bodech z pozvánkového PDF (mj.
Smlouva o zřízení práva stavby – kolárna u ČD, změna termínu plnění
usnesení UR-265-29/26 a souhlas s vyřazením nepotřebného DHM ZŠ Pečky).
U žádného staršího jednání nepřibyl zápis ani usnesení — Rada 32/2026
byla doplněná už 10. 9., Zastupitelstvo 6/2026 (16. 9.) má nadále jen
Pozvánku. Archiv má nově **289 jednání, 2 767 usnesení, 4 123 bodů
programu**. `jednani/absence.json` přepočítán, beze změny (nové jednání
zatím nemá prezenci). Playlist „Zasedání ZM" má 32 položek — proti
minulému běhu přibyl jen naplánovaný přenos ZM 6/2026 (16. 9. 2026),
žádný nový záznam; **video k ZM 3/2026 z 25. 5. 2026 na kanálu stále
chybí**, známá mezera trvá. Časové značky bodů (`video_ts`)
zkontrolovány — jediné nedoplněné jsou body 8 a 9 u ZM 2/2026, kde je
ověřeno, že vlastní kapitolu v popisku videa nemají.
**Tělocvična:** zkontrolováno, beze změny — program Rady 33/2026 žádný
bod ke stavbě, pilotám, statice ani dodatkům ke SoD neobsahuje (ověřeno
i u UR-265-29/26, na které se jeden bod odvolává: jde o oplocení
dětského hřiště na sídlišti, ne o tělocvičnu). **Pozemky:** nové
usnesení k prodeji/nákupu pozemku nepřibylo, `update-pozemky.py`
nespouštěn. **Pečecké noviny:** archiv pecky.cz nadále končí číslem
7–8/2026, zářijové vydání ještě nevyšlo. **Smlouvy:** konektor Hlídače
státu vrací **přesně stejná čísla jako 9. 9.** — skupina 152 smluv /
95 486 534 Kč, úřad 47 / 33 473 888 Kč, nejnovější podpis nadále
7. 9. 2026. Žádná nová smlouva, tabulky ani souhrny nedotčeny;
**nevysvětlený propad z 30. 8.–2. 9. (skupina 182 → 150) zůstává
nedorovnaný** a čísla v sekci jsou pošesté ponechána beze změny —
k rozhodnutí uživatele. **Zakázky:** diff proti
`zakazky/pecky-zakazky-ids.json` — **176 ID, 1 nové, 0 zmizelých**.
Nové ID `P22V00000346` je ale **fulltextový šum**: jde o zakázku
„Novostavba silnice III. třídy Nová Průběžná v obci **Zdiby** – PD"
zadavatele Středočeský kraj, s Pečkami nesouvisí. Do kontrolního snímku
zapsáno (aby se příště znovu nehlásilo), do tabulky „Nejnovější zakázky"
**ne**. Při té příležitosti zjištěno, že vyhledávání `Q=00239607` je
fulltext, ne filtr podle zadavatele — dopsáno jako pravidlo do
`zakazky/README.md` i do `sources.json`. Hlídač dnes hlásí 214 výsledků
celkem (dřív 193) při 176 unikátních ID. **Volby 2026:** na úřední desce
pecky.cz přibyly dva volební dokumenty, oba vyvěšené 10. 9. 2026 —
„Svolání prvního zasedání OVK" a „Školení k zásadám hlasování". Oba se
týkají okrskových volebních komisí, ne voličů; na stránku proto
nepromítnuty, jen hlášeny. **Sociální sítě (O webu + Volby 2026):**
zkontrolováno všech 15 účtů. Počty se změnily u 8: Alena Švejnohová
946 → 955, Kulturní středisko 992 → 993, Městská knihovna 482 → 483,
Pečky Pečákům 238 → 245, TJ Sokol Pečky 221 → 223, ODS a nezávislí
Pečky 217 → 221, Pečky srdcem 73 → 78, Instagram streetpeopleofpecky
1 218 → 1 216. Nová aktivita u 8 účtů: Město Pečky (13. 9.), NAŠE PEČKY
(12. 9.), Alena Švejnohová (13. 9.), Kulturní středisko (31. 8. →
10. 9.), Pečky NEXT FB (12. 9.), Pečky Pečákům (10. 9.), ODS a nezávislí
Pečky (13. 9.) a Pečky srdcem (28. 8. → 10. 9.). Měsíc před volbami jsou
tedy aktivní všechna volební uskupení kromě FB skupiny Lidé pro Pečky
s podporou SPD (nadále 27. 8. 2026). **Nová technická překážka
a její obejití:** Facebook od tohoto běhu nevykresluje datum příspěvku
ani jako zamíchané `<span>` znaky — značka je prázdný `<span>` doplněný
`<template>`, takže dosavadní postup (čtení znaků podle pozice na
obrazovce) vracel prázdno. Spolehlivě jde datum přečíst z
`creation_time`/`publish_time` ve `<script>` datech stránky; postup
ověřen proti relativnímu tvaru („7 h" u Města Pečky = 13. 9. 07:53)
a zapsán do `o-webu/automation-socialni-site.md`. U obou instagramových
účtů aktualizován jen počet sledujících — mezera v čtení data
posledního příspěvku (popsaná 2. 9.) **trvá**. `python3
scripts/build.py` proběhl bez chyby — 15 stránek + 1 neprolinkovaná
podstránka, validace OK. Vizuální kontrola na lokálním serveru v tomto
automatickém běhu neproběhla, nahradila ji strojová kontrola
vygenerovaných stránek.)

10. září 2026 (automatická kontrola usneseni.cz. **Jednání:** Rada
32/2026 (7. 9. 2026) doplněna o zápis a 12 usnesení (UR-282 až UR-293)
včetně prezence, průběžných příchodů/odchodů a délek jednotlivých bodů;
nově přibylo **Zastupitelstvo 6/2026 (16. 9. 2026)** zatím jen
s Pozvánkou — 23bodový program vytažen z PDF pozvánky. Archiv teď 288
jednání a 2 767 usnesení. Přepočítána `jednani/absence.json`. Playlist
„Zasedání ZM" — přibyl naplánovaný přenos ZM 6/2026 (16. 9. 2026), do
archivu zatím nezapsán (jednání ještě neproběhlo); **video k ZM 3/2026
z 25. 5. 2026 na kanálu stále chybí**, známá mezera trvá. Časové značky
bodů (`video_ts`) zkontrolovány — u ZM 2/2026 ověřeno v popisku videa,
že body 8 a 9 vlastní kapitolu nemají, takže tam nejde o mezeru.
**Tělocvična:** ze zápisu RM 32/2026 doplněny dvě věci — město přizvalo
externího pracovníka na sanace budov a připravuje vyjádření právní
kanceláře k dalšímu postupu; rozpočtová opatření č. 9/2026 zvyšují
letošní výdajovou položku stavby o 10 mil. Kč, podle důvodové zprávy ale
jako „předpoklad plateb v letošním roce", ne jako nově vyčíslené
vícenáklady (UR-288-32/26, 4 pro – 1 zdržel se; rozhodne ZM 16. 9.).
Přidán callout k programu ZM 6/2026, kde má stavba samostatný bod.
**Pozemky:** `update-pozemky.py` přegenerován, beze změny — obě nové
darovací smlouvy s General Property X (UR-291, UR-292) jsou bezúplatné
převody, které tabulky Nákup/Prodej nesledují.)

9. září 2026 (týdenní kontrola zdrojů. **Jednání:** na usneseni.cz nic
nového — Rada 32/2026 (7. 9. 2026) má nadále jen Pozvánku, zápis ani
usnesení zveřejněné nejsou; archiv beze změny (287 jednání, 2 755
usnesení). Playlist „Zasedání ZM" beze změny (31 videí, nejnovější
26. 8. 2026) — **video k ZM 3/2026 z 25. 5. 2026 na kanálu stále
chybí**, známá mezera trvá. Časové značky bodů (`video_ts`)
zkontrolovány, žádné jednání se zápisem i videem nezůstalo nedotažené.
**Tělocvična:** zkontrolováno, beze změny — v programu Rady 32/2026
(17 bodů z pozvánky) není žádný bod k dostavbě učeben a tělocvičny
ani k pilotám/statice; nový zápis, který by šlo vytěžit, nepřibyl.
**Pečecké noviny:** archiv pecky.cz nadále končí číslem 7–8/2026,
zářijové vydání ještě nevyšlo. **Zakázky:** diff proti
`zakazky/pecky-zakazky-ids.json` — 175 ID, 0 nových, 0 zmizelých,
soubor nedotčen. **Smlouvy:** konektor Hlídače státu vrátil **2 nové
smlouvy**, obě doplněny do tabulky „Nejnovější smlouvy" v
`content/smlouvy.html`: „Darovací smlouva — Město Pečky — zařízení
vyprošťovací hydraulické WEBER HYDRAULIK SP 49" (HZS Středočeského
kraje, podpis 7. 9. 2026, 642 510 Kč — přímo úřadu) a „S-4189/ŘDP/2026
— veřejnoprávní smlouva o poskytnutí dotace na bezplatné školní
stravování 2026/2027" (Středočeský kraj → ZŠ Pečky, podpis 31. 8. 2026,
298 960 Kč). Do tabulky „Největší smlouvy" ani jedna nepatří (nejmenší
tamní položka je 2,34 mil. Kč). Souhrny konektoru vzrostly **přesně
o tyto dvě smlouvy**: skupina 150 → 152 smluv a 94 545 064 →
95 486 534 Kč, úřad 46 → 47 a 32 831 378 → 33 473 888 Kč. To je poprvé
od 30. 8. pohyb nahoru a je beze zbytku vysvětlený — **nevysvětlený
zůstává starší propad** (16. 8.: skupina 182 / 102,4 mil., úřad 47 /
33,1 mil.), který se tímto nedorovnal. Souhrnná čísla v subject-boxu
a calloutu sekce Smlouvy proto **popáté ponechána beze změny** —
k rozhodnutí uživatele. **Volby 2026:** na úřední desce pecky.cz nic
nového k volbám — nejnovější volební dokument je nadále „Informace
o počtu a sídlech volebních okrsků" z 25. 8. 2026; nejnovější položka
desky vůbec je dopravní značení ze 7. 9. 2026. **Sociální sítě
(O webu + Volby 2026):** zkontrolováno všech 15 účtů (seznam v
`o-webu/automation-socialni-site.md` mluví o 14 — od 4. 9. 2026 přibyl
TJ Sokol Pečky, **nesoulad k opravě v automation dokumentu**). Změnily
se počty u 8 účtů: Alena Švejnohová 942 → 946, Městská knihovna
483 → 482, Pečky NEXT (FB) 291 → 306, ODS a nezávislí Pečky 213 → 217,
Instagram Pečky NEXT 120 → 128, Pečky srdcem 72 → 73, FB skupina Lidé
pro Pečky s podporou SPD 39 → 40 členů, Instagram streetpeopleofpecky
1 219 → 1 218. Nová aktivita u 8 účtů: Město Pečky (8. 9.),
Pečky-Virtuálně (4. 9.), NAŠE PEČKY (8. 9.), Alena Švejnohová (7. 9.),
Městská knihovna (8. 9.), Pečky NEXT FB (6. 9.), TJ Sokol Pečky (8. 9.)
a ODS a nezávislí Pečky (dnes 9. 9.). Nejvýraznější změna:
**Pečky Pečákům po třech měsících ticha zveřejnily 8. 9. vlastní
příspěvek** (5. 6. → 8. 9. 2026) — měsíc před volbami; ověřeno, že jde
o vlastní datum stránky, ne o datum sdíleného obsahu. U obou
instagramových účtů aktualizován jen počet sledujících — mezera
v čtení data posledního příspěvku (popsaná 2. 9. v
`o-webu/automation-socialni-site.md`) **trvá**. Datumy čteny
z absolutního tvaru, u relativních („16 h", „51 m") přepočteno vůči
9. 9. 2026 08:53. `python3 scripts/build.py` proběhl bez chyby —
15 stránek, validace OK. Vizuální kontrola na lokálním serveru v tomto
automatickém běhu neproběhla, nahradila ji strojová kontrola
vygenerovaných stránek.)

8. září 2026 (na žádost uživatele doplněno pravidlo do týdenní rutiny:
**bod jednání týkající se stavby tělocvičny musí aktualizovat i sekci
Tělocvična**, ne jen sekci Jednání, a **každý běh musí jmenovitě
vyreportovat, co změnil**. Zapsáno na čtyři místa: nový krok 9
„Tělocvična (pokud relevantní)" v `jednani/automation-kontrola-usneseni-cz.md`
(vč. seznamu hledaných formulací — nejen „tělocvična", ale i „Dostavba
učeben", „piloty", „statické zajištění", „Dodatek č. … k SoD" apod.;
následující kroky přečíslovány na 10 a 11, do kroku 11 přidán povinný
výpis změn); nová sekce „Pracovní postup: týdenní kontrola" v
`telocvicna/README.md` (kam který typ zjištění na stránce patří);
dvě nové odrážky v `CLAUDE.md` → „Konvence" (promítání bodů jednání do
věcně dotčených sekcí; povinný report změn). Režim sekce Tělocvična
v tabulce „Stav sekcí" změněn z `hlídat` na `týdně` — nově ji týdenní
rutina kontroluje sama, ne až na vyžádání; z legendy u režimu `hlídat`
proto odstraněn příklad „volby 2026". Obsah webu tato změna nemění,
jen postupy.)

5. září 2026 (na žádost uživatele překlopena automatická rutina z denní
na **týdenní** — běží v neděli večer, cron `0 18 * * 0` (fakticky
týdenní byla už dřív, jen se všude jmenovala „denní“). Sjednoceno
pojmenování: režim sekcí v tabulce „Stav sekcí“ i v legendě `denně` →
`týdně` (Jednání, O webu, Volby 2026, Pečecké noviny, Smlouvy,
Zakázky), přepsané postupy v `zakazky/README.md` (týdenní diff),
`smlouvy/README.md`, `o-webu/README.md`, `o-webu/automation-socialni-site.md`,
`volby/2026/README.md`, `jednani/automation-kontrola-usneseni-cz.md`
(nově upozorňuje, že za týden mohlo přibýt víc jednání najednou —
kontrolovat celé období od data v tabulce, ne jen poslední den)
a `telocvicna/README.md`. Na webu: `content/owebu.html` → sociální sítě
„aktualizuje se týdně“. Historické záznamy v tomto changelogu zmiňující
„denní kontrolu“ zůstávají beze změny — popisují běhy, které tak
skutečně proběhly.)

4. září 2026 (na žádost uživatele doplněn do `content/telocvicna.html`
obsah zápisu RM 31/2026 (Dodatek č. 1 ke smlouvě o dílo, viz zápis
usneseni.cz níže) — v době předchozích kontrol dostupný jen jako
pozvánka. Dodatek zahrnuje 13 změnových listů, mimo jiné „změny
související se statickým zajištěním stávajícího založení“ (piloty),
navyšuje cenu díla o 6 150 969 Kč bez DPH na 211,5 mil. Kč vč. DPH
(původně cca 205 mil.) — ale sám upozorňuje, že jde o vyúčtování už
uzavřených změn, ne odhad celkových nákladů na vyřešení pilot. Dopad
na harmonogram dodatek neřeší; radnice v něm výslovně uvádí, že jím
není dotčeno budoucí posouzení odpovědnosti zhotovitele/projektanta.
Promítnuto do stat-gridu, perexu, přepsaného řádku 31. 8. 2026
v tabulce „Zastavení stavby“ a nového callloutu v „Otevřené otázky“.
Detaily v `telocvicna/README.md`.)

4. září 2026 (automatická kontrola usneseni.cz. **Jednání:** Rada
31/2026 (31. 8. 2026) už má zveřejněný zápis, podepsaný zápis
i přijatá usnesení — doplněna do `jednani/pecky-jednani.json` v plném
rozsahu: 11 bodů programu s délkami a předkladateli, důvodové zprávy
u bodů 3–8, prezence 6/7 (Ing. Petr Dürr nepřítomen na začátku,
dorazil v 15:45), délka jednání 2h13min a 6 usnesení UR-276 až
UR-281-31/26. Věcně největší z nich: UR-277 — Dodatek č. 1 k SoD
„Dostavba učeben a tělocvičny v ZŠ Pečky“ (změnové listy ZL 01–13,
+6 150 969,14 Kč bez DPH na 174 765 820,14 Kč bez DPH, přijato 5-0-1).
Zároveň na webu přibylo nové jednání **Rada 32/2026 (7. 9. 2026)**,
zatím jen s Pozvánkou — zaznamenáno s programem o 17 bodech
z pozvánkového PDF (mj. tři smlouvy s General Property X s.r.o.
a termín/program zasedání ZM 16. 9. 2026). Archiv má nově 287 jednání,
2 755 usnesení, 4 091 bodů programu; číselná řada usnesení Rady 2026
je 1–281 bez děr. **YouTube (kroky 6 a 7):** playlist „Zasedání ZM"
beze změny (31 videí, nejnovější 26. 8. 2026) — video k ZM 3/2026
z 25. 5. 2026 na kanálu nadále chybí. Doplňovat časové značky nebylo
kde: jediná mezera v éře kapitol jsou body 8 a 9 u ZM 2/2026
(22. 4. 2026) a ověřeno přímo v popisku videa, že tyto dva body
kapitolu vůbec nedostaly — zůstávají tedy prázdné. Vizuální kontrola
na lokálním serveru v tomto automatickém běhu neproběhla, nahradila ji
strojová kontrola dat.)

4. září 2026 (na žádost uživatele znovu zkontrolovány Aktuality města
Pečky na `pecky.cz/default/default/21395_aktuality` — beze změny oproti
2. 9. 2026, nejnovější položka zůstává „Uzavírka ulice K. Havlíčka
Borovského“ z 3. 6. 2026. Ani po facebookovém vyjádření vedení města
tam samostatná zpráva o zastavení stavby zveřejněná není. Bulletka u
„Co přesně říká radnice“ v `content/telocvicna.html` aktualizována na
nové datum kontroly.)

4. září 2026 (na žádost uživatele přečten nový příspěvek na
`facebook.com/mestopecky` — první veřejné vyjádření samotného vedení
města k pozastavení stavby tělocvičny, zveřejněné 4. 9. 2026 v 0:20
(dosud mlčelo, viz kontroly Aktualit i Facebooku k 2. 9. 2026 v
předchozích záznamech). Potvrzuje technické jádro ze zápisu ZM a
upřesňuje: sanace pilot pod kuchyní byla plánovaná od začátku
zakládání stavby, ale bourací práce odhalily pochybnosti o kvalitě a
délce i STÁVAJÍCÍCH pilot; statik proto zpochybnil délku i dalších
pilot, ne jen původně kontrolovaných; město zvažuje sanaci základů,
nebo přeprojektování statiky celé stavby; dohoda se zhotovitelem o
pozastavení prací šetří náklady města. Na konkrétní tvrzení Aleny
Švejnohové z 2. 9. 2026 (rok 2015, jména Urban/Paluska, odepřené
podklady) ale vyjádření vůbec nereaguje. Promítnuto do
`content/telocvicna.html`: nový callout a odkaz v „Co přesně říká
radnice“, poznámka v obou calloutech „Otevřené otázky“, nový řádek
4. 9. 2026 v tabulce „Zastavení stavby“ (nad řádkem Švejnohové) a
opravené pasáže, které dřív (platně k 2. 9.) tvrdily, že radnice mlčí.
Detaily v `telocvicna/README.md`.)

3. září 2026 (denní kontrola zdrojů. **Jednání:** na usneseni.cz nic
nového — Rada 31/2026 (31. 8. 2026) má nadále jen Pozvánku, archiv beze
změny (286 jednání). Nově se „Zvukový záznam" objevil i u ZM 4/2026
(24. 6. 2026), nejen u ZM 5/2026 — pole se tedy doplňuje zpětně
i ke starším zasedáním; archiv ho neeviduje, zatím jen poznámka
v `sources.json`. Playlist „Zasedání ZM" beze změny (31 videí,
nejnovější ZM z 26. 8. 2026) — **video k ZM 3/2026 z 25. 5. 2026 na
kanálu stále chybí**, známá mezera trvá. Časové značky bodů (`video_ts`)
zkontrolovány, žádné jednání se zápisem i videem nezůstalo nedotažené.
**Pečecké noviny:** archiv pecky.cz nadále končí číslem 7–8/2026,
zářijové vydání ještě nevyšlo. **Zakázky:** diff proti
`zakazky/pecky-zakazky-ids.json` — 175 ID, 0 nových, 0 zmizelých,
soubor nedotčen. **Smlouvy:** konektor Hlídače státu v této relaci nebyl
k dispozici, čísla proto ověřena z veřejného webového vyhledávání Hlídače
smluv (`holding:00239607` a `ico:00239607` — stejné dva pohledy jako
u konektoru). Žádná nová smlouva (nejnovější podpis nadále 23. 7. 2026)
a **pokles se dál neprohluboval** — skupina 150 smluv / cca 95 mil. Kč,
úřad 46 / cca 33 mil. Kč, tedy přesně hodnoty naměřené 2. 9. Zároveň to
**vyvrací domněnku, že jde o chybu konektoru** — stejná snížená čísla
ukazuje i webové rozhraní Hlídače, takže úbytek 179 → 150 z 2. 9. je
skutečný stav zdroje. Čísla v sekci Smlouvy proto **počtvrté ponechána
beze změny** — k rozhodnutí uživatele. **Volby 2026:** na úřední desce
pecky.cz nic nového (nejnovější dokument je nadále zápis ze ZM 5/2026
vyvěšený 28. 8. 2026). **Sociální sítě (O webu + Volby 2026):**
zkontrolováno všech 14 účtů. Změnily se počty: Alena Švejnohová
933 → 942, streetpeopleofpecky 1 218 → 1 219, Instagram Pečky NEXT
119 → 120; ostatní beze změny. Nová aktivita u pěti účtů — Město Pečky
(2. 9.), Alena Švejnohová (2. 9.), NAŠE PEČKY a Pečky NEXT (oba dnes
3. 9.) a zejména **Pečky-Virtuálně, které po dvou měsících ticha
zveřejnily 2. 9. dva vlastní příspěvky** (26. 6. → 2. 9. 2026);
ověřeno, že jde o vlastní sdílení stránky, ne o datum sdíleného obsahu.
U obou instagramových účtů aktualizován jen počet sledujících — mezera
v čtení data posledního příspěvku (popsaná 2. 9. v
`o-webu/automation-socialni-site.md`) **trvá**, znovu ověřeno, že `alt`
u obrázků mřížky vrací popisek místo data a `time[datetime]` se
odhlášené relaci nevykreslí. **Technická překážka:** `scripts/build.py`
se v tomto běhu nepodařilo spustit — připojená složka odmítala číst
`scripts/build.py`, `assets/styles.css`, `templates/page.html`,
`assets/nav.html` i `assets/footer.html` s `Resource deadlock avoided`
(opakováno cca 20× během 2 minut, bez úspěchu). Zdrojové
`content/owebu.html` a `content/volby2026.html` jsou aktualizované
správně; do vygenerovaných `o-webu/index.html` a `volby/2026/index.html`
byly ty samé řetězce zapsány ručně, aby web nezůstal nekonzistentní.
**Doporučeno spustit `python3 scripts/build.py` ručně, až bude složka
čitelná** — výstup by měl být identický, ale ověřit to je na místě.)

2. září 2026 (na žádost uživatele prohledán `facebook.com/svejnohova`
— nalezen čerstvý veřejný příspěvek předsedkyně Kontrolního výboru
Aleny Švejnohové (v době kontroly ~13 minut starý): tvrdí, že vadná
dokumentace, podle níž byla zkolaudována kuchyň ZŠ a která posloužila
i jako podklad pro stavbu tělocvičny, je z roku 2015 — uváděla piloty
8,5 m, kontrolní zkoušky po poškození 3 pilot při bourání potvrdily
skutečnou délku jen 6,5–6,6 m. Jmenuje tehdejší vedení města (starosta
Milan Urban, místostarosta Milan Paluska — dnešní starosta) a popisuje,
že jí město jako předsedkyni výboru dokumenty nejprve odepřelo
(„Kontrolní výbor na ně nemá právo“), pak tvrdilo, že „ještě nejsou
dohledané“; vyzývá k trestnímu oznámení pro podezření z podvodu a
zmiňuje možný střet zájmů starosty Palusky. Promítnuto do
`content/telocvicna.html` jako důsledně odlišené, jednostranné tvrzení
volené zastupitelky pod jejím jménem — ne jako nezávisle ověřený závěr
(nový řádek „2015“ v tabulce „Historie projektu“, nový řádek „2. 9.
2026“ v tabulce „Zastavení stavby“, přepsané „Otevřené otázky“, přesná
čísla pilot doplněna k citaci radnice). Zároveň upřesněna dřívější
formulace „dokumentace sahá k 2008, ne 2015“ — obě data jsou reálná a
netýkají se stejného dokumentu (2008 = správní rozhodnutí o rozdělení
stavby na etapy, 2015 = dle Švejnohové kolaudační dokumentace kuchyně
s vadnými údaji o pilotách). Detaily v `telocvicna/README.md`.)

2. září 2026 (denní kontrola zdrojů. **Jednání:** na usneseni.cz nic
nového — Rada 31/2026 (31. 8. 2026) má nadále jen Pozvánku, archiv beze
změny (286 jednání). Nově web u ZM 5/2026 nabízí i „Zvukový záznam"
(dosud jen zápis a usnesení); archiv toto pole neeviduje, zatím jen
poznámka v `sources.json`. Playlist „Zasedání ZM" beze změny —
**video k ZM 3/2026 z 25. 5. 2026 na kanálu stále chybí**, známá mezera
trvá. Časové značky bodů (`video_ts`) zkontrolovány, žádné jednání se
zápisem i videem nezůstalo nedotažené. **Pečecké noviny:** archiv
pecky.cz nadále končí číslem 7–8/2026, zářijové vydání ještě nevyšlo.
**Zakázky:** diff proti `zakazky/pecky-zakazky-ids.json` — 175 ID, sada
shodná s baseline (ověřeno porovnáním SHA-256 seřazeného seznamu),
0 nových, 0 zmizelých, soubor nedotčen. **Smlouvy:** žádná nová smlouva
(nejnovější podpis nadále 23. 7. 2026), ale **nevysvětlený úbytek
záznamů u skupiny se prohloubil** — Hlídač státu teď vrací 150 smluv /
94 545 064 Kč místo 179 / 102 075 674 Kč z 30. 8. a 1. 9. (tedy −29
záznamů a −7,5 mil. Kč za dva dny), zatímco samotný úřad se drží na
46 / 32 831 378 Kč. Čísla v sekci Smlouvy proto **potřetí ponechána beze
změny**; dvojí pokles bez jediné nové smlouvy vypadá spíš na změnu
indexace skupiny na straně Hlídače než na skutečné stažení smluv
z registru — k rozhodnutí uživatele. **Volby 2026:** na úřední desce
pecky.cz nic nového k volbám (nejnovější dokument je zápis ze ZM 5/2026
z 28. 8. 2026). **Sociální sítě (O webu + Volby 2026):** zkontrolováno
všech 14 účtů. Změnily se počty: streetpeopleofpecky 1 220 → 1 218,
Pečky NEXT (FB) 290 → 291, ODS a nezávislí Pečky 210 → 213, Pečky NEXT
(Instagram) 118 → 119; ostatní beze změny. ODS a nezávislí Pečky má nový
příspěvek z dnešního dne (2. 9.). Při té příležitosti **opraveny tři
datumy poslední aktivity, které byly o den novější než skutečnost** —
Kulturní středisko 1. 9. → 31. 8., Pečky srdcem 29. 8. → 28. 8.,
FB skupina Lidé pro Pečky s podporou SPD 28. 8. → 27. 8.; příčinou byl
dopočet z relativního tvaru („4 d"), dnes už se čte absolutní datum
přímo z Facebooku. **Dvě nové technické překážky u sociálních sítí,
obě zapsané do `o-webu/automation-socialni-site.md`:** (1) Facebook u
části stránek rozsypal datum příspěvku do desítek jednoznakových
`<span>` promíchaných s návnadovými znaky — prosté čtení textu vrací
nesmysl nebo datum komentáře místo příspěvku; obchází se čtením znaků
v pořadí podle jejich pozice na obrazovce (`getBoundingClientRect`,
hotový skript je v automation dokumentu). (2) **Instagram přestal
prozrazovat datum posledního příspěvku** — atribut `alt` u obrázků
mřížky teď v české lokalizaci obsahuje popisek příspěvku místo dřívějšího
`"Photo by … on September 01, 2026."`, `?hl=en` to nezmění, `time[datetime]`
ani odkazy `/p/<kód>/` se odhlášené relaci nevykreslí a
`/api/v1/users/web_profile_info/` vrací HTML místo JSON; u obou
instagramových účtů proto aktualizován jen počet sledujících a datum
poslední aktivity ponecháno na hodnotě z posledního úspěšného čtení.)

2. září 2026 (na žádost uživatele prohledán celý archiv jednání —
`jednani/archive-2026-08-04.json` (2021–7/2026) a `jednani/pecky-
jednani.json` pro srpen 2026, mimo záběr staršího archivu — a fulltext
Pečeckých novin 2008–2026, hledání zmínek o projektu tělocvičny pro
sekci Tělocvična. Do `content/telocvicna.html` doplněny: (1) nová
podsekce „Historie projektu (2008–2022)“ — zápis Rady z 1. 9. 2008
(starosta Milan Urban) dělí „II. etapu dostavby ZŠ“ na vývařovnu a
tělocvičnu/aulu se zhotovitelem PD Ateliér A11 Hradec Králové; táž
firma znovu 2017; nová smlouva s OV ARCHITEKTI s.r.o. 2018 (studie od
nuly); zhotovitelem PD je 2022 už třetí kancelář, Atelier A99 s.r.o.
Dokumentace tak nesahá k roku 2015, jak se traduje mezi občany (a jak
tvrdí i needitovaná výzva v `telocvicna/vyzva.html`), ale minimálně
k roku 2008 — nikde v archivu do 8/2026 se přitom neobjevuje zmínka o
pilotách. (2) 3 nové řádky časové osy ze zápisů Rady, které dosud
sekce nepokrývala: RM 28/2026 (10. 8.) — nejstarší dohledaná zmínka o
„utržených pilotách“, 16 dní před zápisem ZM; RM 29/2026 (17. 8.) —
svolání mimořádného ZM právě kvůli tomu; RM 30/2026 (24. 8.) —
„opatření vyvolaná pozastavením stavby“, tedy stavba byla zastavená
ještě před zápisem ZM. Přidán i řádek o RM 31/2026 (31. 8., bod
„Dodatek č. 1 k SoD“) s poznámkou, že zápis/usnesení k tomu zatím
nejsou zveřejněné. Detaily a zdroje v `telocvicna/README.md`.)

2. září 2026 (na žádost uživatele odebrán blok „Veřejná výzva“ z
`content/telocvicna.html` — panel sekce Tělocvična je teď čistě věcný,
stejně jako zbytek webu. Osobní výzva místo toho žije v novém
samostatném souboru `telocvicna/vyzva.html`: needitovaný přepis
uživatelova původního podkladu (jen připojena hlavička/patička webu),
záměrně **mimo strukturu webu** — není v `scripts/build.py` MANIFEST,
nikde na ni nevede odkaz, není v `sitemap.xml`, má `<meta
name="robots" content="noindex, nofollow">`. Detaily v
`telocvicna/README.md`.)

2. září 2026 (přidána nová sekce **Tělocvična** (`/telocvicna/`) —
stavba „Dostavba učeben a tělocvičny ZŠ Pečky“ (205 mil. Kč, zahájena
3. 6. 2026) je od 26. 8. 2026 částečně zastavená: při obnažování šesti
původních pilot podpírajících sousední budovu kuchyně a jídelny se u
tří z nich zjistilo zkrácení cca 2 m a zkoušky PIT nepotvrdily délku
pilot dle zhotovovacích protokolů. Podklad dodal uživatel (návrh
veřejné výzvy), obsah před publikací nezávisle ověřen proti oficiálnímu
zápisu ze zasedání ZM 5/2026 (usneseni.cz, čteno přes claude-in-chrome
kvůli bot-ochraně) a proti videozáznamu na YouTube kanálu města — zápis
potvrzuje technické jádro (6 pilot, PIT zkoušky, dočasné zastavení
prací, i to, že Alena Švejnohová jako předsedkyně kontrolního výboru
byla na jednání omluvena), ale neobsahuje uživatelovu výzvu ani
přisouzení viny konkrétním osobám (Urban, Paluska, Švejnohová) — ty
zůstávají v samostatném bloku „Veřejná výzva“ výslovně označené jako
osobní názor autora webu, ne ověřené tvrzení. Sekce zařazena do
navigace za Plán, `scripts/build.py` MANIFEST/README_TO_SLUG doplněny,
web teď generuje 14 stránek.)

1. září 2026 (denní kontrola zdrojů. **Jednání:** na usneseni.cz nic
nového — Rada 31/2026 (31. 8. 2026) má nadále jen Pozvánku, zápis ani
usnesení zveřejněné nejsou; archiv proto beze změny (286 jednání).
Playlist „Zasedání ZM" na YouTube zkontrolován: nejnovější video je ZM
z 26. 8. 2026, které archiv už má, a **k jednání ZM 3/2026 z 25. 5. 2026
video na kanálu stále chybí** — známá mezera trvá. **Pečecké noviny:**
nejnovější číslo v archivu pecky.cz je nadále 7–8/2026, zářijové vydání
ještě nevyšlo. **Zakázky:** diff proti `zakazky/pecky-zakazky-ids.json` —
175 nalezených ID, 0 nových, 0 zmizelých, soubor nedotčen. **Smlouvy:**
žádná nová smlouva (nejnovější podpis nadále 23. 7. 2026) a souhrnná
čísla z Hlídače státu se drží na snížené úrovni zjištěné 30. 8. 2026
(skupina 179 smluv / 102 075 674 Kč, úřad 46 / 32 831 378 Kč) — pokles
proti 16. 8. (182/47) zůstává nevysvětlený, čísla v sekci Smlouvy proto
i tentokrát **záměrně ponechána beze změny**; k rozhodnutí uživatele.
**Volby 2026:** na úřední desce pecky.cz nalezen nový dokument
„Informace o počtu a sídlech volebních okrsků" (podepsal starosta Milan
Paluska 25. 8. 2026, vyvěšeno 25. 8. 2026) — do sekce přidán blok „Kde
se volí" se **6 okrsky** a jejich sídly (Kulturní středisko, ZŠ Tř. Jana
Švermy 342 pro okrsky 2 a 5, ZUŠ Barákova, Městská knihovna, knihovna
Velké Chvalovice) a poznámkou, že přiřazení ulic k okrskům dokument
neobsahuje; z téhož dokumentu doplněno, že se ve stejných dnech volí
i do třetiny Senátu. PDF je sken, adresy přepsány ručně (OCR vrstva má
překlepy). Zdroj zapsán do `sources.json`. **O webu → Sociální sítě:**
kontrola dnes neopakována — proběhla už dřív téhož dne (14 účtů, viz
předchozí záznam), opakovaný běh po pár hodinách by u malých lokálních
účtů nepřinesl nic nového.)

30. srpna 2026 (**architektura webu přepracována z jednosouborového
`index.html` na vícestránkový statický web**, motivace: web přerostl jednosouborovou
strukturu a chyběly trvalé odkazy na jednotlivé sekce i záložky uvnitř
nich. Obsah rozřezán do `content/<sekce>.html` (13 souborů), sdílené
části do `templates/page.html`, `assets/nav.html`, `assets/footer.html`,
`assets/styles.css`, `assets/common.js` (nav, tabulky, subtaby — teď
s trvalým odkazem na konkrétní záložku přes hash, např.
`/pozemky/#prodej`, dřív subtaby neměly URL vazbu vůbec) a
`assets/helpers.js` (funkce sdílené mezi Jednáním/Novinami/Lidmi:
`jEscapeHtml`, `jNorm`, `jHighlight`, `jInitials`). Nový
`scripts/build.py` skládá z těchto částí všech 13 veřejných stránek
(`/`, `/jednani/`, `/noviny/`, `/lide/`, `/plan/`, `/volby/2018/`,
`/volby/2022/`, `/volby/2026/`, `/smlouvy/`, `/zakazky/`, `/pozemky/`,
`/pokladna/`, `/o-webu/`) + `sitemap.xml`/`robots.txt` a validuje
HTML/JS. Staré odkazy typu `pecky.online/#pozemky` přesměrovává redirect
v `content/domu.html` na novou adresu (mapovací tabulka pro 5 sekcí, kde
se nová cesta liší od starého `data-panel` slugu: `zpravodaj`→`/noviny/`,
`owebu`→`/o-webu/`, `volby2018/2022/2026`→`/volby/RRRR/`). Zjištěná
a opravená chyba při migraci: `lApplyRoute()` v Lidé očekávala vždy hash
začínající `lide` (na jednostránkovém webu tam vždy byl), na samostatné
stránce `/lide/` bez hashe proto adresář vůbec nevykreslila — opraveno
uvolněním podmínky. Ověřeno jsdom smoke testem (13 stránek bez JS chyb,
fetch dat v Jednání/Novinách/Lidech, deep link na osobu, subtaby s
hashem) a samostatným testem redirect logiky (19+7 testů, vše OK) i
kontrolou, že všech 524 statických odkazů/src na vygenerovaných
stránkách míří na existující soubory. Staré duplicitní samostatné
stránky `pecky-jednani/index.html` a `pecky-noviny/index.html` smazány
(nahradily je plnohodnotné `/jednani/` a `/noviny/`). `update-pozemky.py`
upraven, aby psal do `content/pozemky.html` místo přímo do `index.html`
— dokumentace (`CLAUDE.md`, `pecky-jednani/automation-katastr-parcely.md`,
`pecky-jednani/README.md`, `pecky-noviny/README.md`,
`pecky-pozemky/README.md`, `pecky-zakazky/README.md` a další sekce)
aktualizována. Nepublikováno na GitHub — čeká na výslovné „Publikuj".)

30. srpna 2026 (denní kontrola čtyř zdrojů. **Jednání:** na usneseni.cz
přibyla Rada 31/2026 (31. 8. 2026) — zatím jen s Pozvánkou, přidána do
`pecky-jednani/pecky-jednani.json` jako záznam s `resolutions: []`,
`links.minutes`/`resolutions`/`pdf` = `null`, `time: "15:00"`, `venue`
a 11 body agendy vytaženými z PDF pozvánky přes pdf.js v prohlížeči
(postup viz `pecky-jednani/README.md` → „Jednání jen s Pozvánkou").
Při té příležitosti **přepočteny hodnoty v `meta`**, které se rozešly se
skutečností: `resolutions_count` 2743 → 2749 a `agenda_items_count`
4062 → 4074 (počítáno ze samotných dat, dřívější čísla nezahrnovala
přírůstek Rady 30/2026). Ověřeno, že usnesení ZM 5/2026 je na webu
nadále jediné (UZ-33-5/26) a že v playlistu „Zasedání ZM" stále chybí
video k ZM 3/2026 (25. 5. 2026) — známá mezera trvá. **Pečecké noviny:**
nejnovější číslo v archivu pecky.cz je 7–8/2026, tedy beze změny.
**Zakázky:** diff proti `pecky-zakazky/pecky-zakazky-ids.json` — 175
nalezených ID, 0 nových, 0 zmizelých, soubor nedotčen. **Smlouvy:**
žádná nová smlouva (nejnovější podpis je nadále 23. 7. 2026, už na webu),
ale konektor Hlídače státu vrací u téhož dotazu **méně** záznamů než při
kontrole 16. 8. 2026 — skupina 179 smluv / 102 075 674 Kč místo 182 /
102 416 276 Kč, samotný úřad 46 / 32 831 378 Kč místo 47 / 33 132 977 Kč.
Souhrnná čísla v sekci Smlouvy proto **záměrně ponechána beze změny** —
úbytek záznamů v registru není vysvětlený a přepsat ho naslepo by bylo
horší než přiznaná datace snímku; k rozhodnutí uživatele.)

25. srpna 2026 (pravidlo naplněno u Voleb 2022: do subpanelu „Výsledky voleb"
přidán blok „Kdo byl zvolen" — tabulka vedení a rady (7) s uskupením a
poměrem hlasů, každý řádek odkazuje na vlastní usnesení, a tabulka zbylých
14 zastupitelů po uskupeních, plus odkazy na zápis, všech 33 usnesení a
videozáznam ustavujícího zasedání. Při přípravě zjištěno, že **složení se
od ustavení dvakrát změnilo**, takže panel Lidé a Výsledky voleb 2022 se
už rozcházejí: Jaroslava Vosecká složila slib za uvolněný mandát Lenky
Třískové (ZM 4/2024, 11. 9. 2024) a Ondřej Schulz nastoupil po
Bc. Ivetě Dvořákové (ZM 1/2025, 26. 2. 2025). Obě změny popsány v
`pecky-volby/2022/README.md`; dřívější tvrzení v `pecky-lide/README.md`,
že se složení nezměnilo, opraveno. Uskupení Dvořákové a Třískové není
v usneseních uvedeno — dopočítáno z počtu mandátů a z kandidátky
náhradníků, na webu přiznáno jako odvozený údaj.)

25. srpna 2026 (nové pravidlo pro volební panely: subpanel „Výsledky voleb"
má u proběhlých ročníků uvádět jmenovitě zvolené vedení, radu i zbytek
zastupitelstva, zdrojem je ustavující zasedání ZM, ne výsledky voleb.
Zapsáno do `pecky-volby/README.md` vč. rozlišení „Lidé = aktuální stav,
Volby = stav při ustavení"; do `pecky-volby/2022/README.md` doplněna
konkrétní kotva — ZM 7/2022 z 20. 10. 2022 (volby 23.–24. 9. 2022) a
tabulka 7 zvolených členů vedení a rady s usneseními `UZ-90-7/22` až
`UZ-96-7/22` a poměry hlasů, ověřeno proti archivu jednání. U ročníku
2018 popsána mezera (usneseni.cz sahá jen do dubna 2021, ustavující
zasedání 2018 tam není), u 2026 poznámka hlídat ustavující zasedání
cca v listopadu 2026. Samotný obsah do `index.html` zatím nedoplněn —
jmenný seznam je nadále jen v panelu Lidé.)

24. srpna 2026 (tabulka „Barevná paleta uskupení" přesunuta z kořenového
`README.md` do `pecky-volby/README.md`, kde je pravidlo nejblíž práci
s volebními panely; v kořeni zůstal odkaz a samotné pravidlo, odkaz
opraven i v `pecky-lide/README.md`. Při přesunu tabulka ověřena proti
`index.html` a **opravena chyba**: NAŠE PEČKY měly uvedeno `#E20514` /
`#F9CDD2`, skutečnost je `#4A4A4A` / `#DADADA` (staré hexy se na webu
nevyskytovaly vůbec). Tabulka doplněna o KSČM (`#C1272D`, 2018), Pečky
srdcem (`#2E7D32`, 2026), sloupec s ročníky, názvy uskupení napříč
ročníky a názvy uskupení napříč ročníky. Zároveň doplněny chybějící CSS
definice v `index.html`: `.person-card.party-kscm` (`#F1CFD1`/`#C1272D`),
`.person-card.party-peckysrdcem` (`#D1E2D2`/`#2E7D32`) a
`party-peckypecakum` přivěšená ke sdruženému selektoru s `party-snk`.
Odstíny pozadí dopočítané stejným poměrem (78 % bílé), jakým vznikly
stávající — vzorec sedí na existující hodnoty na desetinu přesně.
Kontrolou pokrytí ověřeno, že všech 8 tříd použitých v HTML má teď
pravidlo. Kartičky programů (`.promise-card`) barvu uskupení nepřebírají
záměrně, barvu tam nese jen tečka `.swatch`.)

24. srpna 2026 (dokončeno stěhování obrázků k sekcím: 54 souborů z kořenové
`img/` přesunuto do složek volebních ročníků — `img/volebni-programy-2018/`
→ `pecky-volby/2018/volebni-programy-2018/`, `img/volebni-programy-2022/`
→ `pecky-volby/2022/volebni-programy-2022/` a `img/zastupitele/` (42
portrétů) → `pecky-volby/2022/zastupitele/`. Všech 67 odkazů v `index.html`
přepsáno na nové cesty a ověřeno, že se všechny lokální odkazy ve všech
třech stránkách rozklíčují na existující soubory. V kořenové `img/`
zůstávají jen celowebové `favicons/` a `peckybot/`. Umístění obrázků
zdokumentováno v `pecky-volby/README.md`, `pecky-volby/2018|2022/README.md`
a `pecky-lide/README.md`.)

24. srpna 2026 (soubor `pecky-zakazky-ids.json` přesunut z kořenové složky
`data/` do `pecky-zakazky/`, stejná konvence jako `pecky-jednani/`
a `pecky-noviny/`; `data/` tím zaniká. Pracovní postup denního diffu ID
zakázek, popis struktury souboru a známé mezery přesunuty z pole `note`
uvnitř JSONu do `pecky-zakazky/README.md`, které je nově hlavním
referenčním dokumentem sekce. Historické záznamy níže popisující starší
cestu `data/pecky-zakazky-ids.json` jsou ponechány beze změny jako dobový
záznam.)

21. srpna 2026 (na žádost uživatele: do archivu `pecky-jednani.json` doplněna 2 jednání,
která mají na usneseni.cz zatím jen Pozvánku — Zastupitelstvo 5/2026 z 26. 8. a Rada
30/2026 z 24. 8., archiv nyní 285 jednání; agenda obou vytažena přímo z PDF pozvánky
přes pdf.js v prohlížeči, ne jen odkaz. Dále opraven nesoulad v číslování videí na
YouTube kanálu města: jednání 3/2026 (25. 5. 2026) nemá záznam vůbec, video s titulkem
„ZM Pečky č. 3/2026" patří ve skutečnosti jednání 4/2026 — obě jednání teď mají pole
`video_note` s vysvětlením, viditelné i v panelu Jednání na webu. Detaily viz
`pecky-jednani/README.md`.)

21. srpna 2026 (sekce Jednání přesunuta do vlastní složky `pecky-jednani/`,
stejná konvence jako `pecky-noviny/` — `pecky-jednani.json` a
`archive-2026-08-04.json` přesunuty ze `sources/`, které tím zaniklo,
`README.md`/`SPEC.md`/`AUTOMATION.md` přesunuty se souborem archivu; nové
prázdné `Data/` a `img/` vyhrazené pro budoucí lokální archiv; nová
samostatná stránka `pecky-jednani/index.html` se stejným obsahem jako panel
Jednání. Všechny odkazy na staré cesty (`data/pecky-jednani.json`,
`sources/*`) v `index.html` a tomto souboru aktualizovány — historické
záznamy níže popisující starší cesty jsou ponechány beze změny jako
dobový záznam.)

20. srpna 2026 (kontrola zdrojů na výslovnou žádost uživatele: do `data/pecky-jednani.json`
doplněna 2 nová jednání Rady města — 28/2026 z 10. 8. 2026 (5 usnesení UR-259 až UR-263) a
29/2026 z 17. 8. 2026 (6 usnesení UR-264 až UR-269); archiv nyní čítá 283 jednání / 2 742
usnesení, promítnuto i do statických zmínek počtu v sekcích Plán a O webu. Mimoto zjištěno a
opraveno, že smlouvy zachycené při běhu 16. 8. 2026 (dar — zdravotnický batoh; spolupráce
Digitální odysea 26/27) byly zapsané v README/sources.json, ale chyběly v samotném
`index.html` — doplněny se stejnými částkami jako tehdy zaznamenané. Pečecké noviny a Zakázky
zkontrolovány, beze změny. Pozn.: nový plný snímek `sources/archive-2026-08-20.json` podle
`sources/SPEC.md` nebyl vytvořen kvůli velikosti souboru v tomto prostředí — aktuální je jen
odvozený index `data/pecky-jednani.json`; kompletní snímek doplnit při příštím spuštění
plného scraperu.)

16. srpna 2026 (sekce Zpravodaj přesunuta do vlastní složky `pecky-noviny/`
— obálky, fulltext, lokální kopie PDF i samostatná stránka na jednom místě;
přidány náhledy jednotlivých stránek u výsledků fulltextového hledání,
generované `pecky-noviny/render_pages.py`.)

16. srpna 2026 (denní kontrola zdrojů: do sekce Smlouvy doplněny 2 nové smlouvy
zachycené konektorem Hlídače státu — „Dar — zdravotnický batoh" 10 381 Kč
(Krajské ředitelství policie Středočeského kraje, 22. 7. 2026) a „Smlouva o
spolupráci — Digitální odysea 26/27" bez ceny (Sdružení knihoven ČR, Městská
knihovna Svatopluka Čecha, 14. 7. 2026); součty aktualizovány na 182 smluv ve
skupině (102 416 276 Kč) a 47 smluv jen za úřad (33 132 977 Kč). Jednání a
usnesení, Pečecké noviny a Zakázky zkontrolovány, beze změny — viz poznámka
u příslušných zdrojů v sources.json.)

6. srpna 2026 (nový zdroj knihovnapecky.cz → odhalil `pecky.as4u.cz`, čitelnou verzi
oficiálního webu města bez bot-ochrany. Uzavřena mezera u zákona 106/1999 Sb.
Oba zdroje zapsány do sources.json, doplněno pravidlo č. 6 do metodiky ověřování.)

6. srpna 2026 (na stránku Plán přidána sekce „Jak se plán plní?“ — spárování
vybraných položek plánu s archivem usnesení, dotacemi a Pečeckými novinami:
8 projektů se stavem, zjištění o dotačně řízených prioritách a explicitní
poznámka o hranicích srovnání. Zároveň do README doplněna povinná metodika
ověřování.)

6. srpna 2026 (přidána nová stránka Plán — souhrn Strategického plánu rozvoje
města Pečky 2016–2026: perex, klíčová čísla, konkrétní projekty a zjištění,
že sledování plnění aktivit se v dokumentu po roce 2017 přestalo aktualizovat.
Zařazena do navigace hned za stránku Lidé.)

6. srpna 2026 (denní kontrola zdrojů: do sekce Zakázky doplněna 1 nová zakázka
nalezená diffem proti `data/pecky-zakazky-ids.json` — P26V00002056, Obnova
dětského hřiště Sídliště, 18. 6. 2026, cena neuvedena. Jednání/usnesení,
Pečecké noviny a Smlouvy/dotace přes Hlídače státu zkontrolovány, beze změn.)

6. srpna 2026 (do sekce Pokladna přidán blok Bankovní účty — 9 konkrétních čísel
účtů u 5 bank dohledaných v auditorské zprávě k Závěrečnému účtu 2025, plus
souhrnné zůstatky a poznámka, že žádný účet není „transparentní")

6. srpna 2026 (přidána sekce Zakázky — výřez veřejných zakázek Města Pečky
z Hlídače veřejných zakázek, 193 nalezených záznamů)

6. srpna 2026 (přidána sekce Pokladna — rozpočet a hospodaření města z Monitoru
Státní pokladny a přehled dotací z Registru dotací)

5. srpna 2026 (doplněn jmenný seznam zastupitelstva a kompletní archiv
Pečeckých novin z pecky.cz — obě dřívější mezery vyřešeny procházením webu
přes prohlížeč, který bot ochranu neblokuje)
