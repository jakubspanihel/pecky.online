# Instrukce k sekci: Volby 2014 (`/volby/2014/`, panel `volby2014`)

Stránka ročníku 2014, zveřejněná 10. 10. 2026 (tlačítko 2014 v rozcestníku
ročníků). Registrovaná v `MANIFEST` (`scripts/build.py`, slug `volby2014`),
obsah v `content/volby2014.html`.

## Zdroje
- Výsledky uskupení a osobní hlasy zvolených (včetně pořadí na kandidátní
  listině): ČSÚ, `https://volby.gov.cz/pls/kv2014/vysledky_obec?datumvoleb=20141010&cislo_obce=537641`
  (XML). Shodné s tabulkou v Pečeckých novinách 11/2014, s. 5.
- Funkce zvolených (starosta, místostarosta, rada): Pečecké noviny 12/2014,
  s. 3, usnesení ustavujícího zasedání 5. 11. 2014 (PDF jsou obrazové skeny,
  text jen přes OCR).

## Mezery
Koaliční dohoda ani poměr hlasů při volbě starosty a rady v dostupných
zdrojích nejsou. Označení „koalice“ u KDU-ČSL vychází jen ze složení rady
(5× ODS, 2× KDU-ČSL). Kartám chybí úplné kandidátky (jen zvolení) a fotky.
Barvy: KDU-ČSL používá paletu `lidovci`, SNK Evropští demokraté paletu `snk`
(návaznost přes Jedličku a Pečenku) — v `lide/organizations.json` zatím
nejsou vlastní uskupení.
