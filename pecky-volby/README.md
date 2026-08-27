# Instrukce k sekcím: Volby (panely `volby2018`, `volby2022`, `volby2026`)

Referenční rozcestník pro práci na volebních panelech v `index.html` webu
pecky.online. Doplňuje obecné instrukce projektu (Project instructions /
CLAUDE.md) — tohle je společný detail pro všechny volební ročníky.

## Struktura — jedna podsložka na volební ročník
Každý ročník komunálních voleb má vlastní podsložku `pecky-volby/{rok}/`
s vlastním `README.md`. Až přibude další ročník (další komunální volby po
2026), založit stejným vzorem novou podsložku `pecky-volby/{rok}/` — ne
novou složku na kořenové úrovni repa.

- [`2018/README.md`](2018/README.md) — panel `volby2018`
- [`2022/README.md`](2022/README.md) — panel `volby2022`
- [`2026/README.md`](2026/README.md) — panel `volby2026`

## Obrázky patří do složky ročníku
Skeny volebních inzerátů i portréty zastupitelů žijí ve složce ročníku,
ke kterému patří, **ne** v kořenové složce `img/` (ta je vyhrazená pro
celoweb: `img/favicons/`, `img/peckybot/`):

| Složka | Obsah |
|---|---|
| `pecky-volby/2018/volebni-programy-2018/` | 6 skenů volební inzerce z Pečeckých novin 9/2018 |
| `pecky-volby/2022/volebni-programy-2022/` | 6 skenů volební inzerce z Pečeckých novin 9/2022 |
| `pecky-volby/2022/zastupitele/` | 42 portrétů zastupitelů zvolených 2022 (používá i panel Lidé) |

V `index.html` se na ně odkazuje plnou cestou od kořene repa, např.
`pecky-volby/2022/zastupitele/paluska.jpg`. Pojmenování souboru:
příjmení bez diakritiky malými písmeny, u shody příjmení s křestním
(`hruska-ivan.jpg`, `vodicka-tomas.jpg`).

## Co mají volební panely společné
- **Výsledky voleb** (proběhlé ročníky) — počty hlasů/mandátů po
  uskupeních, obvykle záložka „Výsledky voleb".
- **Volební sliby/programy** — kartičky `.promises-grid` (klik přepíná
  zobrazený přepis slibu), obvykle záložka „Předvolební sliby"; u
  proběhlých voleb doplněné o „Rozbor" (jak se sliby naplnily).
- **Barevná paleta uskupení** — každé uskupení má na celém webu jednu
  pevně přiřazenou barvu, viz samostatná kapitola níže.

## Zvolení zástupci patří do „Výsledků voleb" (POVINNÉ)

Subpanel **„Výsledky voleb"** každého proběhlého ročníku neuvádí jen
počty hlasů a mandátů po uskupeních, ale i **jmenovitě, kdo byl zvolen** —
zvlášť vedení města a rada (starosta, místostarostové, radní) a zvlášť
zbytek zastupitelstva. Bez toho výsledky říkají, jak lidé hlasovali, ale
ne co z toho vzešlo.

**Zdrojem je ustavující zasedání zastupitelstva**, ne volební výsledky
samotné. Koná se zhruba měsíc po volbách a teprve na něm se volí vedení
města — hlasy voličů rozdělí mandáty, ale starostu volí zastupitelé mezi
sebou. Ustavující zasedání se pozná podle programu: složení slibu
zvolenými členy zastupitelstva, ověření platnosti voleb, určení počtu
místostarostů a uvolněných funkcí, volba starosty, místostarostů, členů
rady a výborů.

U každé zvolené funkce uvádět i **poměr hlasů** (pro–proti–zdržel se),
je-li v archivu — právě on ukazuje, že volba vedení nebyla jednomyslná,
a je to údaj, který se z výsledků voleb vyčíst nedá.

**Nezaměňovat s panelem Lidé.** Panel Lidé ukazuje **aktuální** složení
zastupitelstva a rady, tj. stav k dnešku. „Výsledky voleb" ukazují
**stav při ustavení**, tedy historický fakt, který se zpětně nemění.
Dokud během volebního období nikdo neodstoupí, jsou oba seznamy shodné a
je svůdné je sloučit — nedělat to. Jakmile přijde rezignace, kooptace
náhradníka nebo změna ve vedení, seznamy se rozejdou a každý má být
opravitelný zvlášť.

Kotvy k jednotlivým ročníkům jsou v README ročníku: pro 2022 viz
[`2022/README.md`](2022/README.md) → „Ustavující zasedání", pro 2018 tam
je popsaná mezera v datech.

## Barevná paleta uskupení

Každé politické uskupení má na celém webu jednu pevně přiřazenou barvu.
Používá se konzistentně u kartiček lidí (panel Lidé), kartiček volebních
programů, sloupcového grafu mandátů i barevných teček (`.swatch`)
v tabulkách výsledků — a to napříč ročníky: uskupení, které kandiduje
opakovaně, si barvu drží, i když se mu mění název.

| Uskupení (názvy napříč ročníky) | Třída | Zvýrazňovací barva | Pozadí kartičky | Ročníky |
|---|---|---|---|---|
| SNK NAŠE PEČKY → NAŠE PEČKY (STAN + nezávislí) → NAŠE PEČKY A PEČKY NEXT | `party-nasepecky` | `#4A4A4A` | `#DADADA` | 2018, 2022, 2026 |
| Sdružení ODS a nezávislých kandidátů → ODS a nezávislí kandidáti | `party-ods` | `#1F2363` | `#CCD2E5` | 2018, 2022, 2026 |
| PEČKY PEČÁKŮM → SNK Pečky Pečákům → Sdružení nezávislých kandidátů PEČKY PEČÁKŮM | `party-snk` (2018 `party-peckypecakum`) | `#A6528F` | `#EBD9E6` | 2018, 2022, 2026 |
| Lidé pro Pečky s podporou SPD → … a Velké Chvalovice s podporou SPD | `party-spd` | `#8B5A2B` | `#E5DBD0` | 2022, 2026 |
| Česká strana sociálně demokratická → ČSSD a sjednocená levice | `party-cssd` | `#FF5F60` | `#FFDFDF` | 2018, 2022 |
| LIDOVCI A NEZÁVISLÍ → Lidovci a nezávislí | `party-lidovci` | `#EBB91E` | `#F7E6B8` | 2018, 2022 |
| Komunistická strana Čech a Moravy | `party-kscm` | `#C1272D` | `#F1CFD1` | 2018 |
| Pečky srdcem | `party-peckysrdcem` | `#2E7D32` | `#D1E2D2` | 2026 |

**Kde barvy žijí v kódu.** Pozadí kartiček je v `<style>` v `index.html`
jako `.person-card.party-*` (`background` + `border-color`); tečky
`.swatch` a graf mandátů mají hex napsaný inline v `style="background:…"`.
Zvýrazňovací barva ve třetím sloupci = hodnota `border-color` u kartičky
i barva tečky — je to jedno a totéž číslo.

**Pravidlo.** Při přidávání nového místa na webu, kde se zobrazuje
uskupení nebo jeho člen (nová kartička, graf, tabulka, nový ročník),
použij existující barvu z této tabulky, ne novou. Novou barvu zakládat
jen pro uskupení, které tu ještě není.

**Stav pokrytí** (ověřeno proti `index.html` 24. 8. 2026): všech osm
tříd použitých v HTML má svoje `.person-card.party-*` pravidlo, žádné
uskupení už nevypadne do neutrálního defaultu. Dvě poznámky:

- `party-peckysrdcem` je zatím definovaná „do zásoby" — Pečky srdcem
  kandidují 2026 a nemají v panelu Lidé žádného člena, takže se
  pravidlo nikde neuplatní. Až uskupení získá mandát, kartička je
  připravená.
- PEČKY PEČÁKŮM mají historicky dvě třídy pro tutéž barvu:
  `party-peckypecakum` (panel Volby 2018) a `party-snk` (jinde). Řeší
  to sdružený selektor `.person-card.party-snk, .person-card.party-peckypecakum`.
  Nesjednocovat je zpětně — třída je v HTML na několika místech
  a rozdíl nic nerozbíjí.

**Kartičky programů barvu uskupení nepřebírají.** Třídy `party-*` na
`.promise-card` (záložky „Předvolební sliby") jsou jen sémantický hook,
žádné `.promise-card.party-*` pravidlo neexistuje a kartičky programů
zůstávají pergamenové pro všechna uskupení — barva se tam nese jen
tečkou `.swatch` v popisce. Je to záměr, ne mezera.
