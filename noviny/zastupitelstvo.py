#!/usr/bin/env python3
"""Vystřihne z PDF Pečeckých novin články o zasedáních zastupitelstva podle
noviny/zastupitelstvo.json do noviny/zastupitelstvo/ZM-RRRR-MM-DD.jpg (200 DPI).
Volitelné `mask` = [[x0, y0, x1, y1], …] (body PDF) přebarví obdélníky bílou
(sousední plakát nebo inzerát, který do článku nepatří). Stránku
/noviny/zastupitelstvo.html pak skládá scripts/build.py.
Použití: python3 noviny/zastupitelstvo.py [RRRR-MM-DD ...]  (bez parametrů všechny)"""
import json, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DPI = 200
K = DPI / 72


def vybel(ppm, crop, masky):
    """Přebarví v PPM (P6) obdélníky masek bílou; souřadnice v bodech PDF."""
    d = bytearray(ppm.read_bytes())
    hlavicka = d.split(b'\n', 3)
    w, h = (int(x) for x in hlavicka[1].split())
    start = len(hlavicka[0]) + len(hlavicka[1]) + len(hlavicka[2]) + 3
    for x0, y0, x1, y1 in masky:
        a, b = max(0, round((x0 - crop[0]) * K)), min(w, round((x1 - crop[0]) * K))
        for r in range(max(0, round((y0 - crop[1]) * K)), min(h, round((y1 - crop[1]) * K))):
            d[start + (r * w + a) * 3:start + (r * w + b) * 3] = b'\xff' * ((b - a) * 3)
    ppm.write_bytes(d)


cfg = json.loads((ROOT / 'zastupitelstvo.json').read_text(encoding='utf-8'))
chtene = set(sys.argv[1:])
(ROOT / 'zastupitelstvo').mkdir(exist_ok=True)
for c in cfg['clanky']:
    if chtene and c['zm'] not in chtene:
        continue
    pdf = ROOT / 'Data' / f'PN {c["issue"][:4]}' / f'{c["issue"]}.pdf'
    x0, y0, x1, y1 = c['crop']
    cil = ROOT / 'zastupitelstvo' / f'ZM-{c["zm"]}.jpg'
    with tempfile.TemporaryDirectory() as tmp:
        ppm = Path(tmp) / 'v.ppm'
        with ppm.open('wb') as f:
            subprocess.run(['pdftoppm', '-r', str(DPI), '-singlefile',
                            '-f', str(c['page']), '-l', str(c['page']),
                            '-x', str(round(x0 * K)), '-y', str(round(y0 * K)),
                            '-W', str(round((x1 - x0) * K)), '-H', str(round((y1 - y0) * K)),
                            str(pdf)], check=True, stdout=f, stderr=subprocess.DEVNULL)
        if c.get('mask'):
            vybel(ppm, c['crop'], c['mask'])
        subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '80',
                        str(ppm), '--out', str(cil)], check=True, stdout=subprocess.DEVNULL)
    print(cil.relative_to(ROOT.parent))
