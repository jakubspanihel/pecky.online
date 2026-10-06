# Baseline vyhledávání (index 3666 úryvků, 59 dotazů)

Spuštění: `cd peckybot/worker && npm run eval` (`node eval/run.mts`). Dotazy: `queries.json`
(`titleRegex` + volitelně `textRegex` musí platit pro jeden úryvek v top-8; `inTop` = požadovaná pozice).
`pending: true` = zdroj ještě není v indexu (jejich `titleRegex` je odhad budoucího titulku).

| Skupina | Výsledek |
|---|---|
| Celkem bez pending (46) | **39/46 = 85 %**, MRR@8 = 0,708 |
| Pending (13) | **0/13 = 0 %** |
| Lidé | 10/14 |
| Jednání (+ Pozemky) | 16/16 |
| Tělocvična | 3/5 |
| Volby | 6/6 |
| Smlouvy/zakázky/finance/plán | 4/5 |

## Vzorce selhání
1. **Chybějící zdroje** (kalendář, komise, výbory, ŠR, noviny, obědy, organizace): žádný úryvek neexistuje, dotaz padne na šum z jednání
   (např. „Co mají dnes k obědu u Marka?" → AFK/restaurace na hřišti; „Zápis ze školské rady" → RM „zápis změny v rejstříku škol").
2. **Dotaz na skupinu osob (strana, funkce)**: text osoby neobsahuje zkratku strany ani „člen rady" tak, aby vyhrál nad stránkami Volby
   (tagy `cssd`, `nasepecky` v people.json se do úryvku nedostanou). „Kdo zastupuje ČSSD…", „Kdo je za Naše Pečky…", „Kdo sedí v radě města?" → vítězí „Web — Volby 2022".
3. **Lidé: dotaz podle role/historie**: „první místostarostkou 2018–2022" → vyhraje Fejfar (stejný kmen „mistos"), správná Iveta Dvořáková není v top-8.
4. **Ceny/čísla vs. historie jednání**: „Kolik stojí dostavba tělocvičny?" → vyhrají dodatky ke SoD z RM/ZM (slova „dostavba tělocvična"), a stránka Web — Tělocvična s částkou 211,5 mil. Kč se do top-3 nedostane.
   Podobně „Má město dluhy nebo úvěr?" → „Investiční úvěr…" z jednání je před Pokladnou (správně až 5.).
5. **Vágní/hovorové formulace bez klíčových slov**: „co se děje u školy, proč tam stojí bagry" – žádná shoda se slovy tělocvična/stavba; potřeba synonym (škola→dostavba, bagry→stavba).
6. Slabá diskriminace titulků: všechny úryvky sekcí mají titulek „Web — <sekce>" (stejný pro 50+ úryvků), takže se z titulku nepozná téma; pro hodnocení se musí použít `textRegex`.
   Slabší pozice (rank 3–5) mají synonyma: „popelnice"→odpad, „čistírna odpadních vod"→ČOV, „školka"→MŠ.

Poznámka: očekávání jsou ověřená proti `lide/people.json`, `content/*.html` a titulkům jednání; `run.mts` označí očekávání, které v indexu nenajde nikde.

Pozn.: tato čísla jsou z indexu z doby založení (před změnami ostatních agentů). Při opakovaném běhu po přestavbě
indexu s novými zdroji vyšlo 41/46 (89 %) a pending 12/13 – viz aktuální `npm run eval`.
