# Newsletter — lokální záloha odeslaných mailů

Archiv newsletterů, které web **Do Peček.cz** (dopecek.cz) rozeslal. Slouží jako
lokální záloha přesného znění — co a kdy šlo čtenářům. Později se z něj bude
vycházet při tvorbě dalších čísel (tón, struktura, už zmíněná témata).

## Struktura

```
newsletter/
├── README.md                          tento soubor
├── export.py                          index.html → email.html (absolutní URL obrázků)
├── RRRR-MM-DD-<slug>.md               starší čísla: jen text (od 2. 10. 2026)
└── RRRR-MM-DD-<slug>/                 HTML čísla: jedna složka = jedno číslo
    ├── index.html                     zdroj e-mailu (tabulky + inline CSS, 600 px)
    ├── text.txt                       prostý text (alternativa pro Gmail / rozesílač)
    ├── email.html                     export pro odeslání (generuje export.py)
    └── img/                           obrázky tohoto čísla (graf, banner, závěrečný obrázek)
```

- Název: datum odeslání (ISO) + krátký slug tématu.
- Zdroj pravdy je `index.html` (náhled otevřít přímo v prohlížeči, obrázky mají
  relativní cesty). Před odesláním `python3 newsletter/export.py newsletter/<číslo>`
  — vznikne `email.html` s adresami `https://dopecek.cz/newsletter/<číslo>/img/…`.
  Obrázky proto musí být nejdřív pushnuté, jinak se v mailu nezobrazí.
- Do složky patří **odeslané** znění, ne koncepty. Opravy po odeslání se
  nepřepisují — případnou poznámku přidat na konec.
- Adresáty (e-maily třetích stran) do archivu nezapisovat.
- Pravidla pro HTML: tabulky, inline styly, šířka 600 px, jen systémová písma,
  žádný JavaScript. Odkazy `webcal://` a `mailto:` s předvyplněním se
  v e-mailech ruší — tlačítko k odběru kalendáře vede na `https://dopecek.cz/kalendar/`.
  Každý obrázek má `alt`.
- **Závěrečný obrázek** je v každém čísle jiný (koťátko z čísla 1 se neopakuje).
  Do `img/zaver.*` do cca 1 MB, šířka 528 px; v `index.html` doplnit `alt`
  a řádek se zdrojem a licencí. Jen obrázky s volnou licencí (Wikimedia Commons,
  Unsplash, vlastní foto z Peček) — ne cizí memy a GIFy bez povolení.

## Odeslaná čísla

| Datum | Soubor | Téma |
|---|---|---|
| 8. 10. 2026 (návrh, neodesláno) | [2026-10-08-tyden1.md](2026-10-08-tyden1.md) | Přehled novinek: kalendář, Na oběd, zasedání zastupitelstva, Jednání, Monitoring Facebooku a úřední desky, Prostory, PečkyBot na Instagramu |
| 2. 10. 2026 | [2026-10-02-novy-web.md](2026-10-02-novy-web.md) | Představení webu: archiv jednání, kalendář, noviny, přehled sekcí |

Při přidání nového čísla doplnit řádek do této tabulky (nejnovější nahoře).

## Zdroj zálohy

Čísla se ukládají z odeslaného mailu ve schránce dopecek@gmail.com (kopie
odeslané zprávy). Text se bere jako prostý text, formátování se ručně převádí
do Markdownu.

## Známé mezery

- **Obrázky a přílohy** se z mailu zatím nestahují. U čísla z 2. 10. 2026 chybí
  snímek obrazovky s koťátkem (`Snímek obrazovky 2026-10-02 v 10.02.51.png`).
  Pokud ho chcete uchovat, uložte ho ručně do `newsletter/img/` a odkažte
  ze souboru čísla.

## Pozor: složka je veřejná

Web běží na GitHub Pages z kořene repa, takže soubory v `newsletter/` jsou
po pushi dostupné i na `dopecek.cz/newsletter/…` (ne přes menu, ale přímou
adresou). Je to záloha odeslaných veřejných mailů, ale nevkládat sem nic
osobního ani interního. Kdyby to vadilo, přidat složku do `.gitignore`.
