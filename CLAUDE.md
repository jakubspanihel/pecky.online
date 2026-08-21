# pecky.online

Neoficiální občanský transparentní web o městě Pečky (okres Kolín).
Jednosouborová statická stránka — index.html, žádný build proces,
žádné závislosti kromě Google Fonts CDN.

## Struktura
Jediný soubor index.html, panely přepínané přes JS (data-panel atributy):
Domů, Lidé, Plán, Volby 2018, Volby 2022, Volby 2026, Jednání, Smlouvy,
Zakázky, Pokladna, Pečecké noviny, O webu.
Styl: pergamenově-úřední (Fraunces + IBM Plex Sans/Mono), viz <style> v hlavičce.

## Konvence
- Web celý v češtině, srozumitelným jazykem pro širokou veřejnost
- Žádná vymyšlená data — každý fakt buď označit jako ověřený (.stamp),
  nebo přiznat jako mezeru (.callout)
- Zachovávat jednosouborovou strukturu, needit do samostatných JS/CSS souborů
- Zdroje: pecky.cz, facebook.com/mestopecky, Hlídač státu (IČO 00239607)
- Každý nový zdroj přidaný do sources.json, který nemá vlastní kontextovou
  citaci jinde na webu (např. konkrétní tabulku nebo callout), doplnit i
  jako odkaz do quicklinks v sekci O webu → Odkazy — i když je jeho status
  zatím "nevytěženo" (obsah nepoužit, ale odkaz má být dohledatelný).

## Dokumentace jednotlivých sekcí
Některé sekce mají vlastní podrobnější referenční dokument a/nebo
samostatnou projektovou složku. Načíst při práci na dané sekci:
- **Zpravodaj / Pečecké noviny** → `pecky-noviny/ZPRAVODAJ.md` (stav dat,
  vzor URL PDF, postupy měsíční kontroly nových vydání, konvence
  zobrazení). Všechny soubory týkající se Pečeckých novin (referenční
  doc, extrahovaný fulltext JSON, obálky, stažená PDF, skripty) patří do
  `pecky-noviny/`, ne do kořene repa ani do `data/`/`img/` — i nově
  vznikající. Jediná výjimka: zobrazení v panelu zůstává v kořenovém
  `index.html` (jednosouborová struktura webu). Sekce má navíc i
  samostatnou stránku `pecky-noviny/index.html` (stejný obsah, bez
  hlavičky/navigace hlavního webu) — detaily v `ZPRAVODAJ.md`.
- **Jednání** → `pecky-jednani/README.md` (zadání a rozhodnutí exportu),
  `pecky-jednani/SPEC.md` (specifikace), `pecky-jednani/AUTOMATION.md`
  (plán budoucí automatizace). Všechny soubory týkající se sekce Jednání
  (index pro fulltextové hledání, kompletní datový snímek, referenční
  dokumenty) patří do `pecky-jednani/`, ne do kořene repa ani do
  `data/`/`sources/` — i nově vznikající. Jediná výjimka: zobrazení
  v panelu zůstává v kořenovém `index.html` (jednosouborová struktura
  webu). Sekce má navíc i samostatnou stránku `pecky-jednani/index.html`
  (stejný obsah, bez hlavičky/navigace hlavního webu). `Data/` a `img/`
  uvnitř jsou zatím prázdné (vyhrazené pro budoucí lokální archiv
  dokumentů/obrázků k jednáním, stejná konvence jako `pecky-noviny/`).

## Známé mezery (celoprojektové)
- Kompletní seznam 21 zastupitelů (pecky.cz blokuje bot přístup)

## Poznámky k datům
- Hlídač státu MCP: použij ICO_of_holding_structure (celá skupina),
  ne jen ICOs_of_contracting_party (jen úřad)
- with_serious_issues_only nespolehlivě vrací 0 — rizikové smlouvy
  identifikovat ručně z běžných výsledků
- Bot-chráněné stránky (pecky.cz, mesto-pecky.usneseni.cz): zkus
  web_search jako fallback, když web_fetch selže
- Velké soubory v `pecky-jednani/` (`archive-*.json`) čtené přímo z cesty
  přes připojenou složku občas skončí `OSError: [Errno 35] Resource
  deadlock avoided` (Python `open()`, `cat`, `head`...). Obejití: nejdřív
  `cp soubor /tmp/kopie.json`, pak pracovat s kopií — `cp` samo selhání
  nemělo.

## Git / GitHub
Remote: https://github.com/jakubspanihel/pecky.online.git
Před pushem vždy commit s popisnou zprávou, zachovej historii verzí webu.
GitHub Integration konektor v chatu je zablokovaný OAuth konfliktem —
publikuj přes přímý git CLI/GitHub API s vlastním GitHub přihlášením (token).
Token (bez expirace) je uložený lokálně v `.github-pat` (v .gitignore,
nikdy nejde do gitu) — před publikací ho odtud načíst, needit znovu žádat.
