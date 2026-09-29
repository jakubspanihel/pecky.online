#!/usr/bin/env python3
"""Kontrola nových zápisů finančního a kontrolního výboru na pecky.cz.

Projde stránky „Zápisy {rok}“ obou výborů (pecky.cz → Zastupitelstvo →
Výbory ZM), porovná odkazy na PDF s `links.minutes` v jednani/vybory.json
a každý dosud neznámý zápis stáhne do
jednani/Data/{datum}-{financni|kontrolni}-vybor/zapis.pdf.

Datum složky je jen z názvu souboru na webu — ten bývá chybný (viz
jednani/README.md, KV_23.09.2023 byl ve skutečnosti 20. 9.), takže ho
je nutné ověřit proti textu zápisu a případně složku přejmenovat.
Skript nic nevytěžuje a nezapisuje do vybory.json — to je ruční krok
podle jednani/README.md → „Kontrola nových zápisů výborů“.

Vypíše i aktuální složení výborů podle webu, ať jde porovnat s Lidmi.

Použití:  python3 jednani/scripts/vybory-check.py [--dry-run]
"""
import hashlib
import json
import re
import subprocess
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VYBORY_JSON = ROOT / 'jednani' / 'vybory.json'
DATA = ROOT / 'jednani' / 'Data'
BASE = 'https://pecky.cz'
UA = 'Mozilla/5.0'
VYBORY = {
    'financni-vybor': ('Finanční výbor', '/default/default/21145_financni-vybor'),
    'kontrolni-vybor': ('Kontrolní výbor', '/default/default/21141_kontrolni-vybor'),
}


def get(url):
    r = subprocess.run(['curl', '-sSfL', '-A', UA, url], capture_output=True)
    if r.returncode:
        raise RuntimeError(f'{url}: {r.stderr.decode(errors="replace").strip()}')
    return r.stdout


def datum_z_nazvu(nazev):
    m = re.search(r'(\d{1,2})[-._](\d{1,2})[-._](\d{4})', nazev)
    if not m:
        return None
    d, mo, y = map(int, m.groups())
    return f'{y}-{mo:02d}-{d:02d}'


def slozeni(html):
    """Tabulka Jméno / Funkce na stránce výboru -> [(jméno, funkce)]."""
    text = re.sub(r'<[^>]+>', '\n', html)
    radky = [unescape(r).strip() for r in text.splitlines()]
    radky = [r for r in radky if r]
    try:
        i = radky.index('Funkce') + 1
    except ValueError:
        return []
    out = []
    while i + 1 < len(radky) and radky[i + 1] in ('předseda', 'předsedkyně', 'člen', 'členka', 'místopředseda'):
        out.append((radky[i], radky[i + 1]))
        i += 2
    return out


def main():
    dry = '--dry-run' in sys.argv
    zname = {m['links']['minutes'] for m in json.loads(VYBORY_JSON.read_text(encoding='utf-8'))['meetings']}
    nove = []
    for suffix, (nazev, cesta) in VYBORY.items():
        html = get(BASE + cesta).decode('utf-8', errors='replace')
        print(f'\n== {nazev}: složení podle webu')
        for jmeno, funkce in slozeni(html):
            print(f'   {funkce:12} {jmeno}')
        roky = sorted(set(re.findall(r'href="(https://pecky\.cz/default/default/\d+_zapisy-\d{4})"', html)))
        for rok_url in roky:
            rok_html = get(rok_url).decode('utf-8', errors='replace')
            for pdf in sorted(set(re.findall(r'/files/pecky/gallery/[^"\']+\.pdf', rok_html))):
                url = BASE + pdf
                if url in zname:
                    continue
                datum = datum_z_nazvu(pdf.rsplit('/', 1)[-1])
                nove.append((nazev, suffix, datum, url))
    if not nove:
        print('\nŽádný nový zápis — vybory.json pokrývá všechna PDF na webu.')
        return
    print(f'\nNOVÉ ZÁPISY ({len(nove)}):')
    for nazev, suffix, datum, url in nove:
        print(f'   {nazev:16} {datum or "DATUM NEZJIŠTĚNO"}  {url}')
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


if __name__ == '__main__':
    main()
