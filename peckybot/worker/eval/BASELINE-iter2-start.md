# Baseline na začátku iterace 2 (index 5062 úryvků, 98 dotazů)

Spuštění: `cd peckybot/worker && npm run eval`. Zdroje kalendář, komise, výbory, ŠR, noviny, obědy, organizace už jsou v indexu,
proto jsou staré „pending“ dotazy převedeny na normální (titulky ověřeny) a pending zůstává jen „kdy je příští zastupitelstvo“.
(Iterace 1, index 3666 úryvků: 39/46 = 85 %, pending 0/13.)

| Skupina | Výsledek |
|---|---|
| **Celkem bez pending (97)** | **73/97 = 75 %**, MRR@8 = 0,600 |
| Pending (1) | 0/1 |
| Původních 59 dotazů | 46/59 (zdroje jsou už indexované: kalendář, komise, obědy, noviny 100 %) |
| Iter2 kolokviální/jednoslovné | 10/16 |
| Iter2 skupiny a role v čase | 5/11 |
| Iter2 ceny a čísla | 2/5 |
| Iter2 organizace a události | 3/7 |

## Třídy selhání (24 neúspěchů + 1 pending, seřazeno podle počtu vysvětlených dotazů)

1. **Soupis/složení skupin (8)** – „kdo je v radě města“, „kdo je v zastupitelstvu / Kolik je zastupitelů?“, „kdo sedí ve finančním/kontrolním výboru“,
   „kdo byl starostou 2018–2022 / po revoluci“, „první místostarostka 2018–2022“. Vyhrávají „Web — Volby“ a jednání typu „Volba členů výboru“; neexistuje úryvek se složením (rada, zastupitelstvo, výbory, vedení v čase).
   Navíc pro starosty vyhrává „Pakt starostů“ z RM.
   *Fix (Indexer):* generované úryvky „Složení rady / zastupitelstva / výborů / komisí (období)“ a „Starostové a místostarostové Peček 1990–dnes“. *(Search)* shoda role→osoba (starost*, místostar*) s váhou titulku „Lidé“.
2. **Organizace podle kategorie/synonyma (7)** – „spolky“, „sportovní kluby“, „škola/školka/skola kontakt“, „kde se dobře najíst“, „spolky … Sokol“, „kontakt knihovna“ (vyhrají Lidé díky PEOPLE_BOOST na „kontakt“).
   Úryvky Organizace nemají kategorická slova ani synonyma. *Fix (Indexer):* do textu Organizace přidat typ + synonyma (sportovní klub, školka=MŠ, restaurace, kde se najíst) a titulek „Spolky v Pečkách“ přehled. *(Search)* PEOPLE_BOOST jen pro dotazy s osobním jménem/funkcí, ne „kontakt knihovna“.
3. **Čísla a částky (5)** – „Kolik stojí dostavba školy/tělocvičny“, „rozpočet města kolik“, „kolik dotací“, „Má město dluhy nebo úvěr?“: vyhrávají dodatky/rozpočtová usnesení z jednání místo shrnující stránky (Pokladna, Tělocvična s 211,5 mil.).
   *Fix (Search):* pro dotazy s „kolik/stojí/částka/rozpočet/dluh“ zvýšit váhu úryvků „Web —“ shrnutí; *(Indexer)* krátké faktové úryvky („Cena dostavby: 211,5 mil. Kč…“, „Dluh města: 0 Kč“) s otázkovými frázemi.
4. **Hovorová slova bez stemové shody (4)** – „co se děje u školy… bagry“, „kdo je starosta“ (rank 3, Pakt starostů), „popelnice … papír“ (rank 4, vyhrají sever/jih/sídliště), „co je tento víkend“ (kalendářní záměr se nepozná).
   *Fix (Search):* slovník synonym (popelnice→odpad/svoz, bagry/stavba→dostavba, škola→ZŠ, víkend→datum sobota+neděle) a boost titulku při shodě všech dotazových tokenů; víkend/dnes/zítra mapovat na data v titulku „Kalendář — … (D. M. RRRR)“.
5. **Chybí úryvek budoucího jednání (1, pending)** – „kdy je příští zastupitelstvo“ (ZM 7/2026 jen v kalendáři, 7. 10. 2026). *Fix (Indexer):* úryvek „Kalendář — Zastupitelstvo n/RRRR (datum)“ pro nadcházející jednání.

Pozn.: všechny `titleRegex` jsou ověřeny proti indexu; `run.mts` hlásí očekávání, které se v indexu nenajde nikde (nyní žádné mimo pending). Dotaz „co je tento víkend“ je datově závislý (zadáno 10.–11. 10. 2026).
