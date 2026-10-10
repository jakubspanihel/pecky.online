# Změny očekávání v iteraci 3

| Dotaz | Původní | Nové | Důvod |
|---|---|---|---|
| Kdy má otevřeno městský úřad? | `^Kalendář — Městský úřad Pečky — úřední hodiny` | odstraněno | Zdrojová data smazána v main (commit 4896ef4), úryvek v indexu neexistuje; „bot nemá vědět“ nelze v rámci titleRegex vyjádřit. |
| kdy je otevreno na uradu | stejné | odstraněno | Totéž. |
| kdy je příští zastupitelstvo | `(Zastupitelstvo 7/2026\|ZM 7/2026)` | `^Kalendář — Příští (jednání\|zasedání)` | ZM 7/2026 (7. 10. 2026) už proběhlo; úryvek „Příští jednání“ je správná datově nezávislá odpověď. |
| kolik město dostalo dotací | beze změny | beze změny, poznámka „známá mezera“ | Fakt 148 dotací je jen v JS-vykreslené pokladna.html. |
| Kolik uskupení kandiduje ve volbách 2026? | beze změny | beze změny | Prověřeno: top-8 jsou Organizace chunky jednotlivých uskupení, počet neuvádějí; odpovídající úryvek (rank > 8) chybí, reálné selhání. |
| Kdo byl první místostarostkou … | beze změny | beze změny | Reálné selhání (rank 4). |
