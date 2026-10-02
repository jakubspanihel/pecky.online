# Newsletter — lokální záloha odeslaných mailů

Archiv newsletterů, které web **Do Peček.cz** (dopecek.cz) rozeslal. Slouží jako
lokální záloha přesného znění — co a kdy šlo čtenářům. Později se z něj bude
vycházet při tvorbě dalších čísel (tón, struktura, už zmíněná témata).

## Struktura

```
newsletter/
├── README.md                       tento soubor
└── RRRR-MM-DD-<slug>.md            jedno odeslané číslo = jeden soubor
```

- Název souboru: datum odeslání (ISO) + krátký slug tématu.
- Každý soubor začíná hlavičkou (datum a čas odeslání, odesílatel, přílohy),
  pak následuje text mailu v Markdownu tak, jak odešel. Odkazy jsou zachované.
- Do souboru patří **odeslané** znění, ne koncepty. Opravy po odeslání se
  nepřepisují — případnou poznámku přidat na konec souboru.
- Adresáty (e-maily třetích stran) do archivu nezapisovat.

## Odeslaná čísla

| Datum | Soubor | Téma |
|---|---|---|
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
