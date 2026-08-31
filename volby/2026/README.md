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
