# Změny očekávání v iteraci 2 (kolo 2)

Po přestavbě indexu (5098 úryvků) jsou v čele správné odpovědní úryvky („Složení …“, „Starostové…“, shrnutí). Očekávání se změnilo jen tam, kde úryvek v čele dotaz skutečně zodpovídá (text přečten v `chunks/`).

| Dotaz | Původní | Nové | Důvod |
|---|---|---|---|
| Kdo je předsedkyně kontrolního výboru? | ^Lidé — Mgr\. Alena Švejnohová \| top3 | ^(Lidé — Mgr\. Alena Švejnohová\|Složení — kontrolního výboru) \| text: Švejnohová \| top3 | Chunk „Složení — kontrolního výboru“ (rank 1) obsahuje „Mgr. Alena Švejnohová (předsedkyně)“. |
| Kdo zastupuje ČSSD v zastupitelstvu? | ^Lidé — (Ing\. Petr Dürr\|Ladislav Kejda) \| top8 | ^(Lidé — (Ing\. Petr Dürr\|Ladislav Kejda)\|Složení zastupitelstva města — současné) \| text: (Dürr\|Kejda) \| top8 | „Složení zastupitelstva — současné“ (rank 1) uvádí ČSSD a sjednocená levice 2 a jmenuje Dürra i Kejdu; textRegex vynucuje jejich jména. |
| Kdo byl první místostarostkou v letech 2018 až 2022? | ^Lidé — Bc\. Iveta Dvořáková \| top3 | ^(Lidé — Bc\. Iveta Dvořáková\|Místostarostové Peček v čase) \| text: Dvořáková \| top3 | „Místostarostové Peček v čase“ (rank 1): 14. 11. 2018 – 20. 10. 2022 Bc. Iveta Dvořáková (1. místostarostka). |
| Kdo sedí v radě města? | ^Lidé — \| text: člen rady města \| top8 | ^Složení rady města — současné \| text: Paluska \| top3 | Chunk obsahuje všech 7 členů rady. Zastupitelstvo však stále vyhrává (rank 2 pro radu) – inTop 3 ponecháno těsné. |
| Kolik je zastupitelů? | ^Web — Volby \| text: 21 (přímo\|zástupc\|mandát) \| top3 | ^Složení zastupitelstva města — současné \| text: počet zastupitelů: 21 \| top3 | Rank 1 přímo uvádí „počet zastupitelů: 21“. |
| Kdo je v zastupitelstvu? | ^Lidé —  \| text: člen zastupitelstva \| top8 | ^Složení zastupitelstva města — současné \| text: Paluska\|Fejfar \| top8 | Rank 1 vyjmenovává zastupitele podle uskupení (textRegex vyžaduje jména). |
| kdo sedí ve finančním výboru | ^Finanční výbor — zápis .*(členové\|účast) \| top8 | ^Složení — finančního výboru \| text: Krištoufek \| top3 | Rank 1 vyjmenovává 7 členů FV. |
| kdo je v kontrolním výboru | ^Kontrolní výbor — zápis .*(členové\|účast) \| top8 | ^Složení — kontrolního výboru \| text: Švejnohová \| top3 | Rank 1 vyjmenovává 7 členů KV. |
| kdo je členem školské rady | ^Školská rada — zápis .*(členové\|účast) \| top8 | ^Složení — školské rady ZŠ Pečky \| top3 | Ranky 1–3 jsou chunky Složení ŠR (zástupci zřizovatele/rodičů/pedagogů) s členy. |
| Kdo byl starostou v letech 2018 až 2022? | ^Lidé — Mgr\. Alena Švejnohová \| top3 | ^(Lidé — Mgr\. Alena Švejnohová\|Starostové a místostarostové\|Složení rady města — 2018–2022) \| text: Švejnohová \| top3 | „Starostové a místostarostové“ (rank 1) uvádí 14. 11. 2018 – 20. 10. 2022 Mgr. Alena Švejnohová (starostka). |
| kdo byl starostou po revoluci | ^Lidé — Ing\. František Pospíšil \| top3 | ^(Lidé — Ing\. František Pospíšil\|Starostové a místostarostové) \| text: Pospíšil \| top3 | Chunk „Starostové“ začíná 1990–2002 Ing. František Pospíšil. |
| kdo je v radě města | ^Lidé —  \| text: člen rady města \| top8 | ^Složení rady města — současné \| text: Paluska \| top3 | Viz „Kdo sedí v radě města?“. |
| kdo je starosta | ^Lidé — Milan Paluska \| top1 | ^(Lidé — Milan Paluska\|Starostové a místostarostové) \| text: Paluska \| top1 | Rank 1 „Starostové a místostarostové“ končí „2022 – dosud: Milan Paluska (starosta)“; výslovně přijímá i Lidé — Paluska. |
| úvěr na tělocvičnu | ^(ZM\|RM) \d+/2026 — Investiční úvěr \| top3 | ^((ZM\|RM) \d+/2026 — Investiční úvěr\|Web — Tělocvična — shrnutí: úvěr) \| top3 | Rank 1 „Web — Tělocvična — shrnutí: úvěr na dostavbu“ je přesná odpověď. |
| kdy je příští zastupitelstvo | pending | normální dotaz | Zdroj je v indexu, rank 1. |

Doplnění: u „první místostarostkou 2018–2022“ přidán i „Složení rady města — 2018–2022“ (obsahuje „Bc. Iveta Dvořáková (1. místostarostka …)“); po další změně indexu je chunk „Starostové a místostarostové“ na ranku 1, ale místostarosty neuvádí, takže se nepočítá.

## Ponechané skutečné neúspěchy
- „kolik město dostalo dotací“ – žádný úryvek v top-8 nezmiňuje 148 přijatých dotací; shrnutí Pokladna řeší zůstatek/rozpočet/dluh, ne dotace.
- (po poslední přestavbě indexu už prochází: „Kolik se platí za odpad?“, „popelnice kdy vyvazeji papir“ – v mezikole selhávaly.)
