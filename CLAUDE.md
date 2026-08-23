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
- **Jednání** → `pecky-jednani/README.md` (zadání, rozhodnutí exportu a
  postup stahování PDF), `pecky-jednani/SPEC.md` (specifikace),
  `pecky-jednani/AUTOMATION.md` (plán budoucí automatizace). Všechny
  soubory týkající se sekce Jednání (index pro fulltextové hledání,
  kompletní datový snímek, referenční dokumenty) patří do
  `pecky-jednani/`, ne do kořene repa ani do `data/` — i nově vznikající.
  Jediná výjimka: zobrazení v panelu zůstává v kořenovém `index.html`
  (jednosouborová struktura webu). Sekce má navíc i samostatnou stránku
  `pecky-jednani/index.html` (stejný obsah, bez hlavičky/navigace
  hlavního webu). `Data/{datum}/` obsahuje lokální PDF archiv
  (`podepsany-zapis.pdf` u všech jednání, `pozvanka.pdf` jen u jednání
  od cca 6/2026 — starší web trvale nevydá, viz „Známá omezení zdroje"
  v `pecky-jednani/README.md`); `img/` zatím prázdné.
  - **Pravidla pro aktualizaci archivu (platí od 21. 8. 2026):**
    - Do `pecky-jednani.json` zaznamenat i jednání, které má na webu
      zatím jen Pozvánku (bez zápisu/usnesení) — dřív se takové
      jednání při kontrole přeskakovalo, teď se má evidovat rovnou
      (s prázdnými poli zápisu/usnesení) a doplnit, jakmile web zveřejní
      zbytek.
    - Stahovat i samotné dokumenty, ne jen odkazy na ně — Pozvánku
      a podepsaný zápis, pokud jsou k dispozici — postupem popsaným
      v `pecky-jednani/README.md` → „Stahování pozvánek a podepsaných
      zápisů".

- **Pozemky** → tabulky Nákup/Prodej v panelu Pozemky (`index.html`) jsou
  statický výřez z usnesení o prodeji/nákupu pozemku (analogie Smluv).
  Po každé aktualizaci `pecky-jednani.json` spustit
  `python3 pecky-jednani/scripts/update-pozemky.py` — v jednom běhu
  přegeneruje obě tabulky vč. klikacích odkazů na parcely A ZÁROVEŇ
  `pecky-jednani/parcely-odkazy.json`, obecnou mapu pro prolinkování
  zmínek „parc. NNNN" kdekoli jinde v sekci Jednání (viz
  `pecky-jednani/AUTOMATION.md` → „Odkazy na parcely (katastr)" a
  „Tabulky Nákup/Prodej na stránce Pozemky"). Katastr-přesná cache:
  `pecky-jednani/parcely-pozemky.json`. Starý `katastr-odkazy.json`
  (globální mapa bez rozlišení katastru) byl 23. 8. 2026 smazaný —
  obsahoval prokázanou chybu u kolidujících čísel parcel; needit ho
  obnovovat ani na něj nic navazovat.

## Známé mezery (celoprojektové)
- Kompletní seznam 21 zastupitelů (pecky.cz blokuje bot přístup)

## Poznámky k datům
- Hlídač státu MCP: použij ICO_of_holding_structure (celá skupina),
  ne jen ICOs_of_contracting_party (jen úřad)
- with_serious_issues_only nespolehlivě vrací 0 — rizikové smlouvy
  identifikovat ručně z běžných výsledků
- Bot-chráněné / JS-vykreslované stránky (pecky.cz, mesto-pecky.usneseni.cz):
  web_fetch často vrací prázdný obsah — zkus claude-in-chrome (navigate +
  get_page_text/find), případně web_search jako fallback
- pecky.cz prošel redesignem (nová platforma, nové URL jako /office/board) —
  je aktuální, ale číst jen přes claude-in-chrome. Starší mirror
  pecky.as4u.cz od cca 3/2026 přestal být průběžně aktualizovaný (např.
  jeho úřední deska je zamrzlá na únoru/březnu 2026) — pro časově citlivý
  obsah (úřední deska, aktuality) použij pecky.cz, ne pecky.as4u.cz;
  as4u.cz zůstává užitečný pro starší/archivní obsah, viz sources.json
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
