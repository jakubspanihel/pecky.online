# Zadání: novinářský článek z jednoho bodu jednání

Jak z archivu jednání (`pecky-jednani.json` + `archive-*.json`) vyrobit krátký
faktický text o jednom projednávaném bodu — pro řadového občana Peček, který
zápis sám číst nebude.

**Stav:** zadání sepsáno 21. 8. 2026, zatím jednorázový ruční postup.
Ověřeno na jednom vzorku (Rada 22/2026, bod 6) — viz „Vzorový výstup" níže.

---

## Role a cíl

Píšeš jako **investigativní novinář**, jehož čtenářem je **řadový občan města**,
kterého se přijatá rozhodnutí mohou týkat. Cílem není rozbor pro odborníka ani
převyprávěný zápis, ale **přehledné a srozumitelné představení toho, co rada
nebo zastupitelstvo skutečně rozhodlo**.

Vyznění musí být **faktické, ale čtivé**. Nic si nevymýšlet — platí stejná
zásada jako pro celý web (viz kořenový `CLAUDE.md`): každý údaj buď doložit ze
zápisu, nebo přiznat jako mezeru.

---

## Vstup

**Prvotní zdroj je vždy Zápis z jednání** — ne usnesení, ne pozvánka. Usnesení
uvádí jen výsledek; zápis obsahuje navíc předkladatele, důvodovou zprávu,
průběh diskuse, časy a jmenný seznam těch, kdo se k bodu vyjádřili.

Zadání od uživatele má tvar „bod N z jednání rady/zastupitelstva č. M"
(např. bod 6 z jednání rady č. 22). Není-li uveden rok, ber **nejnovější
ročník**, ve kterém jednání s tímto číslem existuje, a v textu rok vždy uveď.

### Kde data najít

| Co | Kde |
|---|---|
| Seznam jednání, program, čísla usnesení, odkazy | `pecky-jednani.json` (lehký, 2,5 MB) |
| Plný text bodu, předkladatel, časy, diskuse, hlasování | `archive-YYYY-MM-DD.json`, klíč `meetings[].minutes.agenda_items[]` |
| Struktura obou souborů | [README.md](README.md) |

Postup: v `pecky-jednani.json` najdi jednání podle `type` + `number` + `year`,
vezmi `uuid`, tím dohledej záznam ve velkém archivu a v něm `agenda_items`
s odpovídajícím `number`.

**Technická past:** velké `archive-*.json` čtené přímo z připojené složky občas
skončí `OSError: [Errno 35] Resource deadlock avoided`. Nejdřív
`cp archive-*.json /tmp/`, pak pracovat s kopií.

---

## Co z bodu vytěžit

Povinně:

- **Název bodu** (`title_raw`) a jeho číslo v programu
- **Předkladatel** (`predkladatel`) a **navrhovatel** usnesení (v `raw_text`
  řádek `Navrhovatel: …`) — bývají titíž, ale ne vždy; když se liší, zmínit obojí
- **Důvodová zpráva** — často jediné vysvětlení, proč se bod vůbec projednával
- **Přijatá usnesení** — čísla (`adopted_resolution_number`) a jejich text
- **Výsledek hlasování** — pro / proti / zdržel se / nehlasoval
- **Délka projednávání** — viz níže
- **Odkaz na zdroj** — `links.minutes` a `links.resolutions` daného jednání

Volitelně, když to bod dává:

- Kdo se zapojil do diskuse (`K tomuto bodu se vyjádřili:`)
- Poměr délky diskuse vůči délce hlasování
- Účast na jednání (`presence`) — a zejména **rozpor mezi úvodní prezencí a
  počtem hlasujících** (radní dorazivší později); u zastupitelstva i jmenovité
  hlasování, které rada nezveřejňuje
- Zasazení do kontextu: navazuje bod na starší usnesení
  (`resolution_numbers_mentioned`)? Byl na program doplněn až na místě
  (viz bod „Schválení programu jednání")?

### Výpočet délky bodu

V `raw_text` bodu jsou dvě věty:

```
Projednávání bodu bylo zahájeno v HH:MM:SS
Projednávání bodu bylo ukončeno v HH:MM:SS
```

Rozdíl = délka projednávání. Uveď ji v minutách a sekundách. Silnější je číslo
**v kontextu** — spočítej totéž pro všechny body jednání a řekni, kolikátý
nejdelší bod to byl a jak dlouhé bylo celé jednání (`Jednání zahájeno …` /
`Jednání ukončeno …` v `minutes.full_text`).

Užitečné je i rozdělit dobu na **diskusi** (od zahájení bodu po čas prvního
`V HH:MM:SS předsedající zahájil hlasování`) a **hlasování** (zbytek).

---

## Výstup

Pořadí a rozsah:

1. **Titulek** — jedna věta, konkrétní, bez klikbaitu. Pojmenuj rozhodnutí
   a jeho dopad; když je v bodu doložená mezera (nezveřejněná částka, chybějící
   podklad), patří i ta do titulku.
2. **Perex** — 3–5 vět. Kdo, kdy, co rozhodl, jak dopadlo hlasování, jak dlouho
   se o tom jednalo. Čtenář, který dál nečte, musí vědět to podstatné.
3. **Krátké vysvětlení** — čím bod byl, co konkrétně se schválilo (tabulka,
   je-li usnesení víc), a co v zápisu naopak **chybí**.
4. **Zdroj** — odkaz na zápis a usnesení daného jednání.

Celkem cca 300–500 slov. Delší text už není pro cílového čtenáře.

---

## Pravidla psaní

- **Česky, srozumitelně**, bez úřednické mluvy. „Příspěvková organizace" ano,
  ale při prvním výskytu vysvětlit; „PO", „ZM", „RM" nikdy bez rozepsání.
- **Nic nedomýšlet.** Zápis neuvádí, *proč* radní diskutovali 37 minut — tak to
  netvrď. Doložený je čas, ne motiv.
- **Verbatim u citací.** Text usnesení i důvodové zprávy cituj přesně; nezlomitelné
  mezery a překlepy zdroje (např. „mimořádno odměnu") při citaci neopravuj,
  při parafrázi je prostě nepoužívej.
- **Začerněné údaje (█) jsou zpráva, ne chyba.** Anonymizovanou částku nikdy
  neodhaduj. Napiš, že v zápisu není, a co se kvůli tomu občan nedozví.
- **Funkce ověřovat.** Že je Milan Paluska starosta, plyne z panelu Lidé, ne ze
  zápisu. Osobě, jejíž roli neumíš doložit (např. host v diskusi), funkci
  nepřipisuj — uveď jen jméno, nebo ji vynech.
- **Žádné hodnocení.** Nepiš, že odměny jsou vysoké, rozhodnutí správné nebo
  utajování skandální. Ukaž čísla, mezery a nechej závěr na čtenáři.
- **Jednomyslnost není samozřejmost.** Poměr hlasů uveď vždy — i „6 : 0 : 0"
  je informace.

---

## Vzorový výstup (Rada 22/2026, bod 6)

Zpracováno 21. 8. 2026 jako referenční vzorek zadání.

> **Titulek:** Radní schválili mimořádné odměny šesti ředitelům městských
> organizací. Kolik dostali, se občan nedozví
>
> **Perex:** Rada města Pečky na svém 22. jednání 8. června 2026 jednomyslně
> odsouhlasila mimořádné odměny ředitelům všech šesti příspěvkových organizací
> města — od základní školy po knihovnu — za splnění mimořádných úkolů v první
> polovině roku. Bod předložil starosta Milan Paluska, projednávání trvalo
> 42 minut a 45 sekund a šlo o třetí nejdelší bod celého tříapůlhodinového
> jednání. Konkrétní částky jsou ale ve zveřejněném zápisu začerněné.

Doložená fakta, o která se text opírá:

- Předkladatel i navrhovatel všech šesti usnesení: Milan Paluska (starosta)
- Šest samostatných usnesení UR-202-22/26 až UR-207-22/26, každé pro jednoho
  ředitele; všechna přijata 6 pro / 0 proti / 0 zdržel se, termín IHNED
- Důvodová zpráva: odměny „za splnění mimořádných úkolů v období 1 - 6/2026"
- Zahájeno 16:55:11, ukončeno 17:37:56 → 42 min 45 s; první hlasování až
  v 17:32:33 → 37 min diskuse, ~5 min hlasování
- Výše odměn u všech šesti usnesení anonymizována (█)
- Úvodní prezence 4 ze 7 radních, u bodu hlasovalo 6 → dva dorazili později
- Celé jednání 15:06:08–18:39:10 (3 h 33 min); delší byly jen bod 4 (49:01)
  a bod 2 (45:18)

---

## Otevřené otázky (k rozhodnutí, až se k tomu vrátíme)

- **Kam s výstupem?** Samostatná stránka, panel na webu, nebo jen podklad pro
  Facebook / Pečecké noviny? Zatím není rozhodnuto.
- **Automatizace.** Postup je popsatelný skriptem až po sběr dat (bod, časy,
  hlasování, délky); psaní textu zůstává na modelu. Souvisí s
  [automation-kontrola-usneseni-cz.md](automation-kontrola-usneseni-cz.md).
- **Výběr bodů.** Zpracovávat všechny body, nebo jen ty, které projdou filtrem
  zajímavosti (dlouhá diskuse, nejednomyslné hlasování, začerněné údaje,
  finanční objem)? Poslední varianta dává pro čtenáře nejvíc smysl.
- **Archiv článků.** Pokud jich vznikne víc, potřebují vlastní složku a
  konvenci názvů (např. `clanky/2026-06-08-rada-22-bod-6.md`).
