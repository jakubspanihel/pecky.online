# Obchvat — severní obchvat Peček (silnice II/329)

Stránka `/obchvat/` (hlavní menu v `assets/nav.html`, před Tělocvičnou).
Obsah žije v `content/obchvat.html`; od 25. 10. 2026 se přesunul z dolního
bloku stránky Plán (`content/plan.html`), kde zůstal jen odkaz a řádek
„Severní obchvat“ v tabulkách.

## Obsah
- perex, situační mapa (`obchvat/situace.webp`; výřez z výkresu veřejně prospěšných staveb a opatření územního plánu (úplné znění po změně č. 2, 09/2023): pecky.cz/files/pecky/gallery/18707/699ece575ad43_537641-3.VPS.pdf; legenda barev: červeně plochy a koridory s možností vyvlastnění, modře s možností uplatnění předkupního práva),
- banner „Kde projekt stojí“ pod mapou (aktuální stav, čtyři kroky, poslední doložený krok, datum poslední kontroly zdrojů),
- blok „Výkup pozemků“ (vlastnictví parcel pod trasou podle katastru k 24. 11. 2026 + doložené kroky výkupu; před aktualizací znovu ověřit: parcely z výroku územního rozhodnutí v `o-webu/uredni-deska-monitoring/Text/2025/as4u-271227/`, RUIAN ID z ČÚZK, vlastníci z Nahlížení do KN po CAPTCHA; jen počty podle typu vlastníka, bez jmen),
- časová osa (od nejnovějších událostí po nejstarší) od původního územního plánu (před 1998) po právní moc územního
  rozhodnutí (RM 2. 3. 2026), volební programy, stará silnice II/329, územní plán
  a zástavba lokalit (na konci stránky) a zdroje.

## Zdroje časové osy
Zápisy rady a zastupitelstva z let 2001–2021 jsou v `jednani/noviny-jednani.json`, `starsi-jednani.json`, `as4u-archiv.json`, novější v `pecky-jednani.json`; fulltext novin v `noviny/pecky-noviny.json` (hledat „obchva“, „II/329“). Odkazy na noviny: `/noviny/Data/PN%20RRRR/RRRR-MM.pdf#page=N`.

## Pracovní postup
Nové body (usnesení rady a zastupitelstva k obchvatu, úřední deska — územní,
stavební řízení, výkupy pozemků) doplňovat nahoru tabulky časové osy (řazená od nejnovějších) a přepsat
banner „Kde projekt stojí“ (text, kroky, „Poslední doložený krok“; počítadlo „bez novinky“ v prvním řádku osy: přepsat `data-date` a text v `#obchvat-pocitadlo`; datum „Zdroje zkontrolovány“ přepsat při každé kontrole). Zmínky jednání jsou odkazy `/jednani/#<id>` (viz CLAUDE.md).
Kontrola při týdenní kontrole Jednání a Úřední desky; stavební povolení
a zahájení stavby zatím v dostupných zdrojích nejsou.
