#!/usr/bin/env python3
"""Kontrola nových zápisů komisí rady města na pecky.cz.

Projde pecky.cz → Rada města → Komise RM, u každé komise stránky s odkazy
„2022-2026“ / „Zápisy …“ (i pracovní skupinu pro oslavy 100 let, která
visí pod kulturní komisí), porovná PDF s jednani/komise.json a každý dosud
neznámý zápis stáhne do jednani/Data/{datum}-{komise}/zapis.pdf.

Porovnává se podle komise + data z názvu souboru, ne podle URL: společná
jednání kulturní komise a pracovní skupiny má pecky.cz vystavená dvakrát
(dva různé soubory, stejný obsah) a v datech jsou jednou.

Datum je jen z názvu souboru — vždy ho ověř proti textu zápisu (u výborů
už byl název dvakrát chybný). Skript nic nevytěžuje a nezapisuje do
komise.json — to je ruční krok podle jednani/README.md → „Kontrola nových
zápisů komisí“. Vypíše i složení komisí podle webu (k porovnání s Lidmi)
a upozorní, když zápisy začne zveřejňovat komise, které je dnes nezveřejňují
(sociální komise a případné další zápisy Sboru pro občanské záležitosti).

Rozsah: obě volební období, 2018–2022 i 2022–2026 (zápisy před rokem 2018 web nemá).

Použití:  python3 jednani/scripts/komise-check.py [--dry-run]
"""
import hashlib
import json
import re
import subprocess
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KOMISE_JSON = ROOT / 'jednani' / 'komise.json'
DATA = ROOT / 'jednani' / 'Data'
BASE = 'https://pecky.cz'
UA = 'Mozilla/5.0'
INDEX = '/default/default/21179_komise-rm'
# stránka komise (podle čísla v URL) -> (název, skupina pro párování, přípona složky v Data/)
KOMISE = {
    '21200': ('Komise sportovní', 'sportovni', 'sportovni-komise'),
    '21204': ('Kulturní komise (+ pracovní skupina pro oslavy 100 let)', 'kulturni', 'kulturni-komise'),
    '21206': ('Sbor pro občanské záležitosti', 'sbor', 'sbor'),
    '21208': ('Komise stavebně-dopravní a ŽP', 'stavebni', 'stavebni-komise'),
    '21304': ('Komise pro otázky sociální, zdravotní a bytové', 'socialni', 'socialni-komise'),
}
# typ jednání v komise.json -> skupina pro párování
TYPE_GROUP = {
    'Sportovní komise': 'sportovni',
    'Kulturní komise': 'kulturni',
    'Pracovní skupina pro oslavy 100 let': 'kulturni',
    'Stavebně-dopravní komise': 'stavebni',
    'Sbor pro občanské záležitosti': 'sbor',
}


def get(url):
    r = subprocess.run(['curl', '-sSfL', '-A', UA, url], capture_output=True)
    if r.returncode:
        raise RuntimeError(f'{url}: {r.stderr.decode(errors="replace").strip()}')
    return r.stdout


def text(html):
    t = re.sub(r'<[^>]+>', '\n', html)
    return [r for r in (unescape(x).strip() for x in t.splitlines()) if r]


def datum_z_nazvu(nazev):
    nazev = nazev.split('_', 1)[-1]  # předpona galerie („69e5ee76…_“) obsahuje číslice
    m = re.search(r'(?<!\d)(\d{1,2})[-._](\d{1,2})[-._](\d{4}|\d{2})(?!\d)', nazev)
    if not m:
        return None
    d, mo, y = map(int, m.groups())
    if y < 100:
        y += 2000
    return f'{y}-{mo:02d}-{d:02d}'


def slozeni(html):
    """Tabulka Jméno / Funkce na stránce komise -> [(jméno, funkce)]."""
    radky = text(html)
    try:
        i = radky.index('Funkce') + 1
    except ValueError:
        return []
    out = []
    while i + 1 < len(radky) and re.match(r'(před|mís|čl)', radky[i + 1]):
        out.append((radky[i], radky[i + 1]))
        i += 2
    return out


def main():
    dry = '--dry-run' in sys.argv
    meetings = json.loads(KOMISE_JSON.read_text(encoding='utf-8'))['meetings']
    # společné jednání dvou komisí (m['bodies']) se páruje na každý z orgánů
    znama = {(TYPE_GROUP[b], m['date']) for m in meetings for b in (m.get('bodies') or [m['type']])}
    index = get(BASE + INDEX).decode('utf-8', errors='replace')
    stranky = dict.fromkeys(re.findall(r'/default/default/(\d+)_[^"\']+', index))
    nove = []
    videne = set()
    for cid, (nazev, skupina, suffix) in KOMISE.items():
        m = re.search(rf'href="(?:https://pecky\.cz)?(/default/default/{cid}_[^"]+)"', index)
        if not m:
            print(f'\n== {nazev}: ODKAZ NA STRÁNCE KOMISE RM NENALEZEN (změnila se struktura webu?)')
            continue
        html = get(BASE + m.group(1)).decode('utf-8', errors='replace')
        print(f'\n== {nazev}: složení podle webu')
        sl = slozeni(html)
        for jmeno, funkce in sl:
            print(f'   {funkce:12} {jmeno}')
        if not sl:
            print('   (tabulka složení nenalezena)')
        # PDF přímo na stránce komise + na podstránkách (roky, pracovní skupina)
        pdfs = set(re.findall(r'/files/pecky/gallery/[^"\']+\.pdf', html))
        podstranky = sorted(set(re.findall(r'href="(https://pecky\.cz/default/default/\d+_[^"]+)" class="article__item"', html)))
        for url in podstranky:
            if url in videne:
                continue
            videne.add(url)
            rok_html = get(url).decode('utf-8', errors='replace')
            pdfs |= {p for p in re.findall(r'/files/pecky/gallery/[^"\']+\.pdf', rok_html) if p}
        for pdf in sorted(pdfs):
            nazev_souboru = pdf.rsplit('/', 1)[-1]
            if 'Jednaci-rad' in nazev_souboru or 'informace-' in nazev_souboru.lower():
                continue
            datum = datum_z_nazvu(nazev_souboru)
            if datum and (skupina, datum) in znama:
                continue
            nove.append((nazev, suffix, datum, BASE + pdf))
    # deduplikace téhož zápisu vystaveného na dvou stránkách (podle skupiny + data)
    uniq, seen = [], set()
    for n in nove:
        key = (n[1], n[2]) if n[2] else n
        if key in seen:
            continue
        seen.add(key)
        uniq.append(n)
    if not uniq:
        print('\nŽádný nový zápis — komise.json pokrývá všechna PDF na webu (obě volební období).')
        return
    print(f'\nNOVÉ ZÁPISY ({len(uniq)}):')
    for nazev, suffix, datum, url in uniq:
        print(f'   {nazev[:34]:34} {datum or "DATUM NEZJIŠTĚNO"}  {url}')
        if dry or not datum:
            continue
        cil = DATA / f'{datum}-{suffix}' / 'zapis.pdf'
        if cil.exists():
            print(f'      ! {cil.relative_to(ROOT)} už existuje — nepřepisuji, zkontroluj ručně')
            continue
        obsah = get(url)
        if not obsah.startswith(b'%PDF'):
            print('      ! stažený soubor není PDF — přeskočeno')
            continue
        cil.parent.mkdir(parents=True, exist_ok=True)
        cil.write_bytes(obsah)
        print(f'      -> {cil.relative_to(ROOT)} (MD5 {hashlib.md5(obsah).hexdigest()[:12]}…)')
    print('\nDalší krok: ověřit datum proti textu zápisu a vytěžit podle jednani/README.md.')
    print('Pozn.: složka „kulturni-komise“ platí i pro pracovní skupinu — u pracovní skupiny ji přejmenuj na „…-pracovni-skupina“.')


if __name__ == '__main__':
    main()
