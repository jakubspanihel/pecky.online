#!/usr/bin/env python3
"""Kontrola nových zápisů školské rady ZŠ Pečky na webu školy.

Projde stránku https://www.zspecky.cz/skola/skolska-rada/zapisy-a-dokumenty-sr/,
u každého záznamu, který v názvu nese „zápis“ / „rady školy“, otevře jeho
podstránku a porovná datum jednání (z názvu záznamu) s jednani/skolska-rada.json.
Zápis, který v datech ještě není, stáhne do
jednani/Data/{datum}-skolska-rada/ (PDF jako zapis.pdf, obrázky jako
zapis-N.jpg) a přidá zdroj.txt s odkazem na stránku školy.

Skript nic nevytěžuje a nezapisuje do skolska-rada.json — to je ruční krok
podle jednani/README.md → „Školská rada“. Datum je jen z názvu záznamu:
vždy ho ověř proti textu zápisu (zápisy bývají skeny; u starších záznamů
web drží víc jednání v jednom souboru, např. „Zápis 2009-10“).
Záznamy bez data v názvu (souhrnné „Zápis 2010-11“, „Zápisy 2011-12“)
skript hlásí jen, když je na webu nový takový záznam.

Použití:  python3 jednani/scripts/skolska-rada-check.py [--dry-run]
"""
import hashlib
import html
import json
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SR_JSON = ROOT / 'jednani' / 'skolska-rada.json'
DATA = ROOT / 'jednani' / 'Data'
BASE = 'https://www.zspecky.cz'
LIST = BASE + '/skola/skolska-rada/zapisy-a-dokumenty-sr/'
UA = 'Mozilla/5.0'
# souhrnné záznamy bez data v názvu, už vytěžené (podstránka -> jednání)
ZNAME = {
    'zapis-2009-10-25': '2009-09-07, 2009-10-13',
    'zapis-2010-11-26': '2010-09-23',
    'zapisy-2011-12-42': '2011-10-06, 2012-04-24',
    'zapis-z-jednani-rady-skoly-110': '2013-10-10 (titulní strana)',
    'zapis-z-jednani-skolske-rady-109': '(bez přílohy)',
}


def get(url):
    r = subprocess.run(['curl', '-sSfL', '-A', UA, url], capture_output=True)
    if r.returncode:
        raise RuntimeError(f'{url}: {r.stderr.decode(errors="replace").strip()}')
    return r.stdout


def datum(t):
    m = re.search(r'(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})', t)
    return f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}' if m else None


def main():
    dry = '--dry-run' in sys.argv
    known = {m['date'] for m in json.loads(SR_JSON.read_text(encoding='utf-8'))['meetings']}
    page = get(LIST).decode('utf-8', errors='replace')
    i = page.find('id="2026')  # akordeon po školních letech začíná nejnovějším
    seg = page[max(i - 300, 0):] if i >= 0 else page
    items, seen = [], set()
    for h, t in re.findall(r'<a[^>]+href="(/skola/skolska-rada/zapisy-a-dokumenty-sr/[^"]+\.html[^"]*)"[^>]*>(.*?)</a>', seg, re.S):
        t = re.sub(r'<[^>]+>', '', html.unescape(t)).strip()
        if h in seen:
            continue
        seen.add(h)
        if re.search(r'z[aá]pis|rady školy', t, re.I):
            items.append((t, h))
    print(f'Na webu školy {len(items)} záznamů se zápisy; v datech {len(known)} jednání.')
    nove = []
    for t, h in items:
        slug = h.split('/')[-1].split('.html')[0]
        d = datum(t)
        if d is None:
            if not any(slug.startswith(k) for k in ZNAME):
                nove.append((t, None, h))
            continue
        if d not in known:
            nove.append((t, d, h))
    if not nove:
        print('\nŽádný nový zápis — skolska-rada.json pokrývá všechny záznamy na webu.')
        return
    print(f'\nNOVÉ ZÁPISY ({len(nove)}):')
    for t, d, h in nove:
        print(f'   {d or "DATUM NEZJIŠTĚNO":10}  {t[:60]}')
        if dry or not d:
            continue
        sub = get(BASE + h).decode('utf-8', errors='replace')
        files = [(html.unescape(u), urllib.parse.unquote(html.unescape(o))) for u, o in
                 re.findall(r'href="(/e_download\.php\?file=[^"&]+&amp;original=([^"]*))"', sub)]
        files = [(BASE + u, 'pdf') for u, _ in files] + \
                [(BASE + u, u.rsplit('.', 1)[-1]) for u in sorted(set(re.findall(r'href="(/data/uredni_deska/[^"?]+\.(?:jpg|jpeg|png))', sub)))]
        if not files:
            print('      ! stránka nemá přílohu')
            continue
        cil = DATA / f'{d}-skolska-rada'
        cil.mkdir(parents=True, exist_ok=True)
        pdfs = [f for f in files if f[1] == 'pdf']
        for n, (u, ext) in enumerate(files, 1):
            b = get(u)
            if ext == 'pdf' and not b.startswith(b'%PDF'):
                print(f'      ! {u} není PDF — přeskočeno')
                continue
            name = 'zapis.pdf' if ext == 'pdf' and len(pdfs) == 1 else f'zapis-{n}.{ext}'
            (cil / name).write_bytes(b)
            print(f'      -> {(cil / name).relative_to(ROOT)} (MD5 {hashlib.md5(b).hexdigest()[:12]}…)')
        (cil / 'zdroj.txt').write_text(f'Zdroj: {BASE}{h.split("?")[0]}\nNázev na webu: {t}\n', encoding='utf-8')
    print('\nDalší krok: ověřit datum proti textu zápisu a vytěžit podle jednani/README.md → „Školská rada“.')


if __name__ == '__main__':
    main()
