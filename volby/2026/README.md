# Instrukce k sekci: Volby 2026 (panel `volby2026`)

Referenční dokument pro práci na panelu `panel-volby2026` v `index.html`
webu pecky.online. Doplňuje obecné instrukce projektu i společný rozcestník
[`volby/README.md`](../README.md) — tohle je detail jen pro tenhle
ročník.

## Účel sekce
Příští komunální volby v Pečkách (9.–10. října 2026, dosud neproběhly).
Registrační úřad (Městský úřad Pečky) 18. 8. 2026 zaregistroval kandidátní
listiny pěti uskupení, která budou v Pečkách usilovat o 21 mandátů —
přehled i kompletní kandidátní listiny (pořadí a jména kandidátů,
105 celkem) jsou v tabulce „Volební uskupení". Volební programy zatím
zveřejněné nejsou — doplnit stejným způsobem jako u Voleb 2022, jakmile
budou k dispozici (typicky volební inzerce v Pečeckých novinách těsně
před volbami).

Zdroje (viz `sources.json`): Ministerstvo vnitra ČR (termíny), Úřední
deska města Pečky na pecky.cz (registrace, seznam uskupení) — číst přes
claude-in-chrome, viz kořenový `CLAUDE.md` → „Poznámky k datům" k
bot-ochraně a redesignu pecky.cz. Kandidátní listiny (jména, pořadí):
[volby.gov.cz — Jmenné seznamy a přehledy](https://volby.gov.cz/app/kv2026/cs/20261009/name-lists/!_0_1_2100_2104_537641)
(ČSÚ, JS-vykreslované — číst přes claude-in-chrome, `get_page_text`
zvládne celou tabulku napořád). Doplněno 30. 8. 2026 — u jmen zatím
jen barevný avatar s iniciálami (`av-init`), fotky nejsou k dispozici,
stejně jako u ročníků 2018/2022 před volbami. Průběžné oficiální
výsledky po volbách budou na volby.gov.cz a v otevřených datech ČSÚ.

## Kde se volí (volební okrsky) — zrušeno 17. 9. 2026
Blok „Kde se volí" (6 volebních okrsků a jejich sídla podle dokumentu
*Informace o počtu a sídlech volebních okrsků*, starosta Milan Paluska,
25. 8. 2026, úřední deska pecky.cz — záznam
`pecky-cz-uredni-deska-volby-2026-okrsky` v `sources.json`) byl
doplněn 1. 9. 2026 a k 17. 9. 2026 z `content/volby2026.html` odstraněn
na žádost uživatele. Zdrojový dokument v `sources.json` zůstává —
kdyby se blok měl vrátit, text (vč. upozornění na chyby v OCR skenu
a mezery v přiřazení ulic k okrskům) je v historii gitu.

## Po volbách: hlídat ustavující zasedání
Jakmile volby proběhnou, platí pravidlo „Zvolení zástupci patří do
Výsledků voleb" ([`volby/README.md`](../README.md)): do subpanelu
„Výsledky voleb" doplnit jmenovitě zvolené vedení, radu i zastupitelstvo.
Zdrojem není výsledek voleb, ale **ustavující zasedání zastupitelstva** —
u ročníku 2022 se konalo necelý měsíc po volbách (ZM 7/2022 dne
20. 10. 2022), takže u voleb 9.–10. 10. 2026 čekat ustavující zasedání
zhruba v **listopadu 2026**. Sledovat archiv jednání a pozvánky na
úřední desce; jednání se pozná podle bodů „složení slibu", „ověření
platnosti voleb" a „volba starosty".

Obsah panelu jinak žije v `content/volby2026.html` (žádná samostatná datová
sada). Zatím žádná další zvláštní pravidla nad rámec obecných konvencí v
kořenovém `CLAUDE.md`. Doplnit sem, až nějaká vzniknou.

## Odkaz na kandidátní listinu u každého uskupení (od 9. 9. 2026)

V tabulce „Volební uskupení" má teď každé uskupení ve sloupečku
„Poznámka" (první řádek `.socials-cell`, před Facebookem) odkaz přímo
na jeho kompletní kandidátní listinu na volby.gov.cz — filtrovaný na
konkrétní `KL` (kandidátní listinu), ne na obecný přehled všech 105
kandidátů. Vzor URL: `https://volby.gov.cz/app/kv2026/cs/20261009/name-lists/!_0_1_2100_2104_537641__{N}`,
kde `{N}` je číslo kandidátní listiny (`0`=přehled „Všichni platní
kandidáti", `1`=Zastupitelstva obcí, `2100_2104_537641`=kraj/okres/obec
Pečky, poslední číslo za dvojitou podtržítkovou mezerou = pořadové
číslo listiny). Ověřeno v claude-in-chrome/Browseru 9. 9. 2026 —
přepínáním filtru „Vyberte kandidátní listinu" na stránce a čtením
výsledné URL, u listiny 1 (Pečky srdcem) navíc obsahem tabulky (21
jmen sedí s daty na webu).

Mapování listina → uskupení (needit měnit bez ověření na volby.gov.cz,
čísla listin nejsou abecední ani podle výsledků 2022):

| Číslo listiny | Uskupení |
|---|---|
| 1 | Pečky srdcem |
| 2 | NAŠE PEČKY A PEČKY NEXT |
| 3 | Sdružení ODS, NK |
| 4 | Sdružení nezávislých kandidátů PEČKY PEČÁKŮM |
| 5 | Lidé pro Pečky a Velké Chvalovice s podporou SPD |

## Perex (od 9. 9. 2026)

Dvojice `.stat-card` pod perexem („9.–10. 10. 2026" / „52,36 % volební
účast ve volbách 2022") byla odstraněná — oba údaje byly duplicitní
(termín voleb je v samotném perexu, účast 2022 je v grafu „Volební
účast stoupá" na `/volby/`). Datum voleb je místo toho tučně
zvýrazněné přímo v textu perexu (`<strong>9.–10. října 2026</strong>`).

## Podzáložky (od 8. 9. 2026)

Stránka teď má stejnou `.subtabs`/`.subpanel` strukturu jako Volby 2018/2022
(dřív byla plochá, bez záložek): **Volební uskupení** (tabulka uskupení +
Kde se volí + stavové callouty) a **Předvolební sliby** — druhá se ale
nejmenuje `sliby`/`uskupeni` jako u starších ročníků, ale `sliby2026`/
`uskupeni2026`, protože `id="subpanel-…"` musí být na webu jedinečné napříč
sekcemi a build skládá jen jednu stránku najednou (kolize by teoreticky
nevadila, ale konvence pojmenování `<sekce><rok>` je zavedená už z
`content/volby2018.html`).

## Volební programy (od 8. 9. 2026, doplněno 16. 9. 2026)

Obrázky volebních programů/materiálů leží ve `volby/2026/volebni-programy-2026/`
(stejná konvence jako `volby/2022/volebni-programy-2022/`). Od 16. 9. 2026
mají program dohledaný všech pět uskupení:

- `pecky-srdcem.jpg` (bodový program ve 4 oblastech) a `pecky-pecakum.jpg`
  (jen portréty kandidátky a heslo, bez bodového programu) — oba doplnil
  přímo uživatel k 8. 9. 2026, přesný zdroj a datum prvního zveřejnění
  nejsou ověřené.
- `nase-pecky.jpg` — vystřiženo ze samostatného podkladového PDF
  `nase-pecky-noviny.pdf` (dodal uživatel, tiskový layout, 2 strany:
  str. 1 „Priority 2026" + „Na Plný Pečky!", str. 2 „Naši kandidáti" se
  všemi 21 portréty — na web zatím jen str. 1, str. 2 zůstává v repu jako
  zdroj pro případné budoucí doplnění kandidátských fotek).
- `ods.jpg` a `lide-pro-pecky.jpg` — vystřiženy z **Pečeckých novin 9/2026**
  (`noviny/Data/PN 2026/2026-09.pdf`, str. 9 a 10; volební inzerce
  uskupení č. 2 na str. 8 té samé novinové sazby posloužila jako ověření
  `nase-pecky.jpg` — obsahově identická s podkladovým PDF).

Postup extrakce: `pdftoppm -r 300 -x -y -W -H` (poppler) ořízne konkrétní
ad přímo z PDF v cílovém rozlišení — přesnější a rychlejší než screenshot
+ oříznutí rastrového obrázku. Hraniční souřadnice odhadnuté vizuální
kontrolou nízkorozlišených náhledů stránek (`noviny/pages/2026-09/`), pak
zpřesněné podle skutečného ořezu.

Z `pecky-pecakum.jpg` (materiál obsahuje portrétní fotky jen kandidátů na
prvních pěti místech listiny) jsme 8. 9. 2026 vystřihli jednotlivé avatary
a přiřadili je jmenovitě: Ing. Martin Jedlička → `jedlicka.webp`, Milan
Pečenka → `pecenka-milan.webp` (rozlišeno od kandidáta Vojtěcha Pečenky na
téže listině, který fotku nemá), Ing. Šárka Jedličková → `jedlickova.webp`,
Pavel Sedláček → `sedlacek.webp`, Alena Cihlářová → `cihlarova.webp` — vše
ve `volby/2026/zastupitele/`. Zapsáno i do `lide/people.json` (pole
`photos`, `year: 2026`) u všech pěti, aby se fotky ukázaly i na stránce
Lidé — u Martina Jedličky jde už o druhou fotku v poli (starší z roku 2022
z webu města zůstává, viz `lide/README.md` → „Fotky"), u zbylých čtyř o
první fotku vůbec.

## Politická zkušenost kandidátů (doplněno 17. 9. 2026)

Sloupeček „Poznámka" u každého uskupení má teď (za větou o kandidátech,
kteří dřív kandidovali za jiné uskupení) i větu o tom, kolik z 21
kandidátů obhajuje aktuální funkci a kolik kandiduje poprvé. Zdroj dat:
`lide/affiliations.json` u sekce Lidé — všech 105 kandidátů 2026 je tam
už spárováno se svým `person_id` a affiliations obsahují i historii
dřívějších funkcí (role_type `zastupitel`/`starosta`/`rada`/
`mistostarosta` u organizace `mesto-pecky`, s `current: true/false`
a daty `from`/`to`).

Souhrn (105 kandidátů celkem): 17 obhajuje aktuální mandát (1 starosta,
2 místostarostové, 3 radní, zbytek řadoví zastupitelé — 81 % dnešního
zastupitelstva kandiduje znovu), 2 byli ve vedení města dřív a dnes už
ne (Ing. František Pospíšil, starosta 1990–2002 — první porevoluční,
vrací se po 24 letech; Ing. Petr Zedník, radní 2014–2018), 42 už dřív
kandidovalo (2018/2022) bez zvolení a 44 kandiduje poprvé. Zvláštní
případ je Mgr. Alena Švejnohová (NAŠE PEČKY) — dnes zastupitelka a
předsedkyně kontrolního výboru, ale byla i starostkou 2018–2022, takže
patří do obou skupin zároveň (v textu u uskupení zmíněno jen jednou).
Nikdo z 105 kandidátů (mimo výše zmíněné zastupitele) není podle dat
zaměstnancem úřadu ani žádné příspěvkové organizace města.

Přesná čísla za uskupení (obhajuje / bylo ve vedení dřív / kandidovalo
dřív bez zvolení / nováček, součet vždy 21): ODS a nezávislí Pečky
5/1/11/4, NAŠE PEČKY A PEČKY NEXT 4/1/6/10, PEČKY PEČÁKŮM 3/0/11/7,
Lidé pro Pečky a Velké Chvalovice s SPD 3/0/6/12, Pečky srdcem 2/0/8/11.

## Sociální sítě uskupení

U každého odkazu na sociální síť v tabulce „Volební uskupení" (sloupeček
„Poznámka") je v závorce počet sledujících/členů a datum **posledního
příspěvku na dané síti** (ne datum naší kontroly — ukazatel, jak moc je
stránka aktivní) — aktualizuje se týdně. Těchto 7 odkazů je podmnožinou
delšího seznamu v sekci [O webu](../../o-webu/README.md) → „Sociální
sítě", kde žije i samotný postup kontroly:
[o-webu/automation-socialni-site.md](../../o-webu/automation-socialni-site.md)
— při každé aktualizaci se zapisuje na obě místa najednou. Poznámka je
zúžená na max. 50 % šířky tabulky (`assets/styles.css`,
`#panel-volby2026 table.register td:last-child`), aby ji dlouhý text
u některých uskupení nenafukoval na úkor sloupečku „Lidé".
