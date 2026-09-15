# Instrukce k sekci: Zakázky (panel `zakazky`)

Referenční dokument pro práci na panelu `panel-zakazky` v
`content/zakazky.html` (generuje se do veřejné stránky `/zakazky/`,
viz `scripts/build.py`). Doplňuje obecné instrukce projektu (Project instructions
/ CLAUDE.md) — tohle je detail jen pro tuhle jednu sekci.

## Účel sekce
Veřejné zakázky Města Pečky — výběrová řízení na dodavatele, fáze před
podpisem samotné smlouvy (tu eviduje sekce Smlouvy). Zdroj: Hlídač
veřejných zakázek (veřejné vyhledávání, ne konektor), IČO 00239607 —
statický výřez, ne živá data.

Zobrazovaný obsah panelu žije v `content/zakazky.html` (needit
vygenerovanou veřejnou stránku `zakazky/index.html` přímo, vždy přes
`content/zakazky.html` + `scripts/build.py` — viz `ARCHITEKTURA-MIGRACE.md`
v kořeni repa). Ve složce sekce je navíc jeden pomocný datový soubor,
který se na webu nezobrazuje a slouží jen ke kontrole novinek.

## Datový soubor `pecky-zakazky-ids.json`

Snímek (snapshot) seznamu ID veřejných zakázek města, který slouží jako
základ pro **týdenní diff** — tedy porovnání „co bylo minule" proti „co je
na Hlídači dnes". Není to zdroj obsahu pro web, jen kontrolní otisk.

Umístění: `zakazky/pecky-zakazky-ids.json`
(do 24. 8. 2026 ležel v kořenové složce `data/`, která tím zanikla).

Struktura:

| Pole | Význam |
|---|---|
| `source` | URL vyhledávání na Hlídači veřejných zakázek, ze kterého snímek pochází |
| `snapshot_date` | Datum pořízení snímku (YYYY-MM-DD) |
| `note` | Stručná poznámka k poslednímu běhu — co přibylo, na co narazit |
| `count` | Počet ID v poli `ids` (musí souhlasit s jeho délkou) |
| `ids` | Pole unikátních ID zakázek ve formátu `P##V########` |

## Pracovní postup: týdenní diff

1. Otevřít vyhledávání na Hlídači veřejných zakázek pro IČO 00239607
   (hodnota pole `source`) a projít **všechny** stránky výsledků.
   Stránka je bot-chráněná / JS-vykreslovaná — `web_fetch` často vrací
   prázdno, použít claude-in-chrome (navigate + get_page_text).
2. Vytáhnout z výpisu všechna ID ve formátu `P##V########` a
   deduplikovat je.
3. Porovnat s polem `ids` v tomto souboru. **Nová ID = nové nebo změněné
   zakázky.**
4. U každého nového ID dohledat detail (název, datum, cena, dodavatel)
   a promítnout ho do tabulky „Nejnovější zakázky" v `content/zakazky.html`,
   pak spustit `python3 scripts/build.py`. Chybějící údaj se přiznává
   (např. „cena neuvedena"), nikdy nedopočítává.
5. Aktualizovat v tomto souboru `ids`, `count`, `snapshot_date` a `note`.
   `count` vždy přepočítat z délky pole, ne dopisovat ručně.
6. Zapsat běh do kořenového `CHANGELOG.md` a k příslušnému
   zdroji v `sources.json`.

## Poznámky a známé mezery

- Hlídač hlásil u posledního průchodu (13. 9. 2026) **214 výsledků
  celkem**, ale potvrzených unikátních ID je **176**. Rozdíl jde za
  reklamní/duplicitní řádky ve výpisu — nepovažovat 214 za počet zakázek.
  (Dřívější průchody hlásily 193 výsledků / 175 ID.)
- **Vyhledávání `Q=00239607` je fulltextové, ne filtr podle zadavatele.**
  Vrací i zakázky cizích úřadů, kde se to číslo objeví kdekoli v textu
  (Obec Úholičky, Město Tachov, hl. m. Praha, Středočeský kraj…). Nové ID
  proto vždy nejdřív ověřit v detailu a do tabulky „Nejnovější zakázky"
  promítnout jen zakázky, kde je zadavatelem Město Pečky nebo jeho
  organizace. Případ z 13. 9. 2026: `P22V00000346` = „Novostavba silnice
  III. třídy Nová Průběžná v obci **Zdiby** – PD" (zadavatel Středočeský
  kraj) — do snímku zapsáno, na web ne.
- Historická chyba: snímek k 6. 8. 2026 uváděl `count: 172`, ačkoli pole
  `ids` obsahovalo 174 položek. Opraveno tamtéž; proto krok 5 výše trvá
  na přepočtu.
- Poslední přírůstek zachycený diffem: `P26V00002056` — Obnova dětského
  hřiště Sídliště, 18. 6. 2026, cena neuvedena.
- Zakázky bez uvedené ceny jsou běžné; nedoplňovat je odhadem ani
  částkou z navazující smlouvy (to patří do sekce Smlouvy).
