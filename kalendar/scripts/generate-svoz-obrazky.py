#!/usr/bin/env python3
"""
Obrázky harmonogramu svozu odpadů k tisku na A4 (na šířku) — po jednom
pro každou lokalitu, vzhled podle PDF města, jen s barvami webu.

Čte kalendar/svoz-odpadu.json, píše kalendar/svoz/svoz-<lokalita>.svg,
.png (A4 na šířku, 3369 x 2382 px = ~288 dpi; náhled na webu) a .pdf
(vektorové A4 na šířku; tlačítko „Uložit“). PNG i PDF vykresluje headless
Google Chrome (na macOS /Applications/Google Chrome.app) — jiný nástroj
na SVG v repu není. Pouštět po každé změně kalendar/svoz-odpadu.json:

    python3 kalendar/scripts/generate-svoz-obrazky.py

Vzhled tabulek na webu (content/svoz.html) a obrázků má zůstat stejný —
barvy níže odpovídají proměnným --svoz-* v content/svoz.html.
"""
import datetime
import html
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'kalendar' / 'svoz-odpadu.json'
OUT = ROOT / 'kalendar' / 'svoz'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

W, H = 1123, 794            # A4 na šířku při 96 dpi
SCALE = 3

# barvy = design systém (assets/styles.css) + zelená banneru Pečeckých novin
INK, INK_SOFT, LINE, WHITE = '#1F241E', '#5B5347', '#D1D5DB', '#FFFFFF'
KOM, BIO, PLAST, PAPIR = '#BD253F', '#3F8A55', '#FFEF03', '#029BC5'
HLAVICKA, MESIC, PAS = '#8064A2', '#4B4630', '#E5E1D0'
FONT = "Helvetica, Arial, sans-serif"

LOKALITY = [
    ('sever', 'Pečky sever a Velké Chvalovice', 'komunalni-sever',
     'Komunální odpad každé druhé pondělí, od června do srpna každé pondělí.'),
    ('jih', 'Pečky jih', 'komunalni-jih',
     'Komunální odpad každé druhé úterý, od června do srpna každé úterý.'),
    ('sidliste', 'Pečky sídliště', 'komunalni-sidliste',
     'Komunální odpad každé pondělí.'),
]
MESICE = ['leden', 'únor', 'březen', 'duben', 'květen', 'červen',
          'červenec', 'srpen', 'září', 'říjen', 'listopad', 'prosinec']
DNY = ['po', 'út', 'st', 'čt', 'pá', 'so', 'ne']
BARVA = {'kom': KOM, 'bio': BIO, 'plast': PLAST, 'papir': PAPIR}
SVETLE = {'plast', 'papir'}


def e(t):
    return html.escape(str(t))


def tyden_radky(rok, m):
    """Řádky měsíce: [(pondělí, [datum nebo None x7])]."""
    prvni = datetime.date(rok, m, 1)
    posledni = (datetime.date(rok + (m == 12), m % 12 + 1, 1) - datetime.timedelta(days=1))
    pondeli = prvni - datetime.timedelta(days=prvni.weekday())
    radky = []
    while pondeli <= posledni:
        dny = []
        for i in range(7):
            d = pondeli + datetime.timedelta(days=i)
            dny.append(d if d.month == m else None)
        radky.append((pondeli, dny))
        pondeli += datetime.timedelta(days=7)
    return radky


def bunka(x, y, w, h, d, typy):
    out = []
    if len(typy) == 1:
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{BARVA[typy[0]]}"/>')
    elif len(typy) == 2:   # šikmé dělení jako na webu (45deg): levý dolní / pravý horní trojúhelník
        a, b = BARVA[typy[0]], BARVA[typy[1]]
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{b}"/>')
        out.append(f'<polygon points="{x:.1f},{y:.1f} {x:.1f},{y + h:.1f} {x + w:.1f},{y + h:.1f}" fill="{a}"/>')
    elif not typy:
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{WHITE}"/>')
    tmava = typy and all(t not in SVETLE for t in typy)
    vik = d.weekday() > 4
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="none" stroke="{LINE}" stroke-width="0.7"/>')
    out.append(f'<text x="{x + w / 2:.1f}" y="{y + h / 2 + 4:.1f}" text-anchor="middle" font-size="12" '
               f'font-weight="{700 if vik else 400}" fill="{WHITE if tmava else INK}">{d.day}</text>')
    return ''.join(out)


def pul(x0, y0, mesice, rok, mapa, rh):
    out = []
    mw, tw = 24, 34
    dw = (520 - mw - tw) / 7
    # hlavička
    for i, n in enumerate(DNY):
        x = x0 + mw + i * dw
        out.append(f'<rect x="{x:.1f}" y="{y0}" width="{dw:.1f}" height="16" fill="{HLAVICKA}" stroke="{WHITE}" stroke-width="0.7"/>')
        out.append(f'<text x="{x + dw / 2:.1f}" y="{y0 + 12}" text-anchor="middle" font-size="11" fill="{WHITE}">{n}</text>')
    out.append(f'<text x="{x0 + mw + 7 * dw + tw / 2:.1f}" y="{y0 + 12}" text-anchor="middle" font-size="9" '
               f'font-style="italic" fill="{INK_SOFT}">Týden</text>')
    y = y0 + 16
    for m in mesice:
        radky = tyden_radky(rok, m)
        vyska = len(radky) * rh
        out.append(f'<rect x="{x0}" y="{y:.1f}" width="{mw}" height="{vyska:.1f}" fill="{MESIC}" stroke="{WHITE}" stroke-width="0.7"/>')
        out.append(f'<text transform="translate({x0 + mw / 2 + 4:.1f},{y + vyska / 2:.1f}) rotate(-90)" '
                   f'text-anchor="middle" font-size="12" font-weight="700" fill="{WHITE}">{MESICE[m - 1]}</text>')
        for pond, dny in radky:
            for i, d in enumerate(dny):
                if d:
                    out.append(bunka(x0 + mw + i * dw, y, dw, rh, d, mapa.get(d.isoformat(), [])))
            out.append(f'<text x="{x0 + mw + 7 * dw + tw / 2:.1f}" y="{y + rh / 2 + 3:.1f}" text-anchor="middle" '
                       f'font-size="9" font-style="italic" fill="{INK_SOFT}">{pond.isocalendar()[1]}</text>')
            y += rh
        out.append(f'<line x1="{x0}" x2="{x0 + mw + 7 * dw:.1f}" y1="{y - vyska:.1f}" y2="{y - vyska:.1f}" '
                   f'stroke="{INK_SOFT}" stroke-width="1.4"/>')
    out.append(f'<line x1="{x0}" x2="{x0 + mw + 7 * dw:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{INK_SOFT}" stroke-width="1.4"/>')
    return ''.join(out)


def svg_lokalita(rok, nazev, kom_id, kom_text, typy):
    mapa = {}
    for klic, tid in (('kom', kom_id), ('bio', 'bio'), ('plast', 'plast'), ('papir', 'papir')):
        for d in typy[tid]['dates']:
            mapa.setdefault(d, []).append(klic)
    radku = max(sum(len(tyden_radky(rok, m)) for m in range(a, a + 6)) for a in (1, 7))
    rh = min(22.0, (H - 90 - 16 - 118) / radku)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
           f'<rect width="{W}" height="{H}" fill="{WHITE}"/>',
           f'<rect x="30" y="18" width="{W - 60}" height="58" fill="{PAS}"/>',
           f'<text x="{W / 2}" y="46" text-anchor="middle" font-size="27" font-weight="700" fill="{INK}">{e(nazev.upper())}</text>',
           f'<text x="{W / 2}" y="67" text-anchor="middle" font-size="14" fill="{INK_SOFT}">'
           f'Harmonogram svozu odpadů z domácností {rok}</text>',
           pul(30, 88, range(1, 7), rok, mapa, rh),
           pul(573, 88, range(7, 13), rok, mapa, rh)]
    # legenda
    ly = 88 + 16 + radku * rh + 14
    radky = [([BARVA['kom']], kom_text), ([BARVA['bio']], 'BIO odpad každé úterý podle rozpisu.'),
             ([BARVA['plast'], BARVA['papir']], 'Plast a papír vždy první pátek v měsíci.')]
    out.append(f'<rect x="30" y="{ly:.1f}" width="{W - 60}" height="{len(radky) * 22}" fill="none" stroke="{INK}" stroke-width="1"/>')
    for i, (barvy, text) in enumerate(radky):
        y = ly + i * 22
        if len(barvy) == 1:
            out.append(f'<rect x="30" y="{y:.1f}" width="26" height="22" fill="{barvy[0]}"/>')
        else:
            out.append(f'<rect x="30" y="{y:.1f}" width="26" height="22" fill="{barvy[1]}"/>'
                       f'<polygon points="30,{y:.1f} 30,{y + 22:.1f} 56,{y + 22:.1f}" fill="{barvy[0]}"/>')
        out.append(f'<line x1="30" x2="{W - 30}" y1="{y + 22:.1f}" y2="{y + 22:.1f}" stroke="{INK}" stroke-width="1"/>')
        out.append(f'<line x1="56" x2="56" y1="{y:.1f}" y2="{y + 22:.1f}" stroke="{INK}" stroke-width="1"/>')
        out.append(f'<text x="64" y="{y + 15:.1f}" font-size="13" fill="{INK}">{e(text)}</text>')
    out.append(f'<text x="{W - 30}" y="{H - 10}" text-anchor="end" font-size="9" fill="{INK_SOFT}">'
               f'Zdroj: harmonogram města Pečky · zpracováno na dopecek.cz/kalendar/svoz.html</text>')
    out.append('</svg>')
    return '\n'.join(out)


def main():
    data = json.loads(SRC.read_text(encoding='utf-8'))
    rok = data['meta']['year']
    typy = {t['id']: t for t in data['types']}
    OUT.mkdir(exist_ok=True)
    for lid, nazev, kom_id, kom_text in LOKALITY:
        svg = OUT / f'svoz-{lid}.svg'
        svg.write_text(svg_lokalita(rok, nazev, kom_id, kom_text, typy), encoding='utf-8')
        png = OUT / f'svoz-{lid}.png'
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / 'p.html'
            page.write_text(f'<!doctype html><meta charset="utf-8"><style>html,body{{margin:0}}img{{display:block}}</style>'
                            f'<img src="{svg.as_uri()}" width="{W}" height="{H}">', encoding='utf-8')
            subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                            f'--window-size={W},{H}', f'--force-device-scale-factor={SCALE}',
                            f'--screenshot={png}', '--allow-file-access-from-files', page.as_uri()],
                           check=True, capture_output=True)
            pdf = OUT / f'svoz-{lid}.pdf'
            page.write_text('<!doctype html><meta charset="utf-8"><style>@page{size:A4 landscape;margin:0}'
                            'html,body{margin:0}img{display:block;width:297mm;height:210mm}</style>'
                            f'<img src="{svg.as_uri()}">', encoding='utf-8')
            subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                            f'--print-to-pdf={pdf}', '--allow-file-access-from-files', page.as_uri()],
                           check=True, capture_output=True)
        print('OK', png.relative_to(ROOT), pdf.relative_to(ROOT))


if __name__ == '__main__':
    main()
