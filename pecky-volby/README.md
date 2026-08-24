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

## Co mají volební panely společné
- **Výsledky voleb** (proběhlé ročníky) — počty hlasů/mandátů po
  uskupeních, obvykle záložka „Výsledky voleb".
- **Volební sliby/programy** — kartičky `.promises-grid` (klik přepíná
  zobrazený přepis slibu), obvykle záložka „Předvolební sliby"; u
  proběhlých voleb doplněné o „Rozbor" (jak se sliby naplnily).
- **Barevná paleta uskupení** — každé politické uskupení má na celém webu
  jednu pevně přiřazenou barvu, používanou konzistentně napříč sekcemi
  Lidé, Plán a všemi ročníky Voleb. Tabulka barev (CSS třídy
  `.person-card.party-*`) je v kořenovém `README.md` → „Barevná paleta
  uskupení" — při přidávání nového uskupení nebo nového ročníku vždy
  použít existující barvu z té tabulky (kontinuální uskupení), ne
  vymýšlet novou.
