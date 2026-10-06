#!/usr/bin/env python3
"""Z newsletter/<číslo>/index.html udělá email.html s absolutními URL obrázků.

Použití (z kořene repa):  python3 newsletter/export.py newsletter/2026-10-05-kalendar-facebook
Výstup: <číslo>/email.html (to se vkládá do Gmailu / rozesílače). Obrázky musí být
už na dopecek.cz (push), jinak se v mailu nezobrazí.
"""
import re, sys, pathlib

BASE = 'https://dopecek.cz/newsletter'
d = pathlib.Path(sys.argv[1].rstrip('/'))
html = (d / 'index.html').read_text(encoding='utf-8')
html = re.sub(r'<!--.*?-->', lambda m: m.group(0) if 'preheader' in m.group(0) else '', html, flags=re.S)
html = re.sub(r'(src=")img/', rf'\g<1>{BASE}/{d.name}/img/', html)
for marker in ('DOPLNIT',):
    if marker in html:
        sys.exit(f'Zbývá nevyplněné „{marker}“ — doplň závěrečný obrázek, pak export spusť znovu.')
(d / 'email.html').write_text(html, encoding='utf-8')
print(f'{d / "email.html"}: {len(html)} znaků')
