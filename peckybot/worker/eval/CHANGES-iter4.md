# Změny očekávání v iteraci 4 (index 8448 úryvků)

| # | Dotaz | Původní | Nové | Důvod |
|---|---|---|---|---|
| 37 | Kdy jsou komunální volby 2026? | ^Web — Volby 2026 \| text: 9\.\W+10\. října | ^(Web — Volby 2026\|Kalendář — Volby do zastupitelstva) \| text: 9\. ?(10\. 2026\|října)\|9\.\W+10\. října | Volby proběhly 9.–10. 10. 2026; datum je teď v úryvku „Kalendář — Volby do zastupitelstva (9. 10. 2026)“ (rank 1), Web chunk má už jen výsledky. Termín zůstává vynucen textRegexem. |
| 42 | Kolik smluv má město v registru smluv? | ^Web — Smlouvy \| text: 182 smluv | ^Web — Smlouvy \| text: Skupina celkem \d+ smluv | Číslo (182 → 154) se mění s každým buildem; test hlídá strukturu „Skupina celkem N smluv (v textu s odřádkováním, proto `\s+`)“ v chunku Web — Smlouvy, ne konkrétní N. |
| 55 | Kdy hraje AFK Pečky doma? | ^Kalendář — Fotbal | ^Kalendář — (Fotbal\|AFK) | Titulky zápasů jsou nyní „Kalendář — AFK Pečky – … (datum)“; regex pokrývá obě podoby. |
| 94 | kdy hraje AFK doma | ^Kalendář — Fotbal | ^Kalendář — (Fotbal\|AFK) | Titulky zápasů jsou nyní „Kalendář — AFK Pečky – … (datum)“; regex pokrývá obě podoby. |
| 95 | kdy je příští zastupitelstvo | ^Kalendář — Příští (jednání\|zasedání) | ^Kalendář — Příští (jednání\|zasedání) | Regex beze změny (už je datově nezávislý), jen poznámka: chunk v indexu zatím neexistuje, protože v kalendáři nejsou žádná budoucí jednání. |
| 101 | Kdy se hraje fotbal | ^Kalendář — Fotbal | ^Kalendář — (Fotbal\|AFK) | Titulky zápasů jsou nyní „Kalendář — AFK Pečky – … (datum)“; regex pokrývá obě podoby. |
| nové | 6 případů (Okolo ×2, Voda, svoz po lokalitách, shrnutí rady ×2) | — | — | Nový obsah v indexu. |

Pozn.: #20, #27, #53, #61 selhaly v prvním běhu (před úpravou search.ts jiným agentem), v posledním běhu už procházejí; očekávání se nezměnila.

## Ponechané skutečné neúspěchy
- #11 první místostarostka 2018–2022 – známá slabina (rank 4).
- #38 „Kolik uskupení kandiduje ve volbách 2026“ – chunk „Web — Volby 2026 — Volby do zastupitelstva 2026“ („Kandidovalo pět uskupení“) je mimo top-8.
- #88 „kolik město dostalo dotací“ – známá mezera.
- #95 „kdy je příští zastupitelstvo“ – chunk „Příští jednání“ chybí, v kalendáři není žádné budoucí jednání (datově podmíněné).
- #101 „Kdy se hraje fotbal“ – AFK/Fotbal zápasy mimo top-3 (vyhrává „Kalendář — Nejbližší akce“, noviny).
- #117 „kolik stojí vodné a stočné“ – správný chunk „Voda — cena vodného a stočného“ rank 7; vyhrávají tři chunky „historie ceníku“.
- #119 „shrnutí poslední rady města“ – vyhrávají „RM 37/2026 — přehled jednání“; chunk „Shrnutí jednání — Rada města 37/2026“ není v top-3.
- #120 „o čem jednala rada 19. října 2026“ – datum v dotazu nevybere shrnutí RM 37/2026 (vyhrávají jiná shrnutí).

## Obchvat jako samostatná stránka (26. 10. 2026)
Commit 2536fb8 přesunul obsah o obchvatu z Plánu na novou stránku `/obchvat/` (úryvky „Web — Obchvat — …“).
Dotazy „obchvat“ (#60) a „Strategický plán rozvoje obchvat a cyklostezky“ (#46) proto přijímají
`^Web — (Strategický plán|Obchvat)`; textRegex (obchvat) zůstává.
