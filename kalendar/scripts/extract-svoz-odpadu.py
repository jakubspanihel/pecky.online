#!/usr/bin/env python3
"""
Vytěžení harmonogramu svozu odpadů z PDF města do kalendar/svoz-odpadu.json.

Harmonogram (jednostránkové PDF na pecky.cz, 2026 poprvé zapojené
24. 9. 2026) je roční kalendář, ve kterém je termín svozu vyznačený jen
BARVOU BUŇKY - text dne v PDF je stejný u všech dní. Skript proto:
1. vezme polohy čísel dnů z textové vrstvy (`pdftotext -bbox`),
2. přiřadí každé číslo ke sloupci dne v týdnu a dopočítá datum
   (po sobě jdoucí řádky, přechod 31 -> 1 = další měsíc; levá polovina
   leden-červen, pravá červenec-prosinec),
3. z vykreslené stránky (`pdftoppm`, 200 dpi, PPM bez PIL) přečte barvu
   pozadí buňky a podle legendy ji převede na typ svozu.
Každé dopočítané datum se kontroluje proti dni v týdnu jeho sloupce
(neshoda = skript spadne, nic nezapíše).

Závislost: poppler (`pdftotext`, `pdftoppm`) - na macOS `brew install poppler`.
Mimo `kalendar/scripts/update-kalendar.py` ho není potřeba pouštět:
výstup je uložený v repu, spouští se jen při novém harmonogramu (typicky
jednou ročně). Barvy a sloupce odpovídají šabloně 2026 - u dalšího
ročníku nejdřív zkontrolovat okem proti PDF (viz kalendar/README.md ->
"Svoz odpadů").

Použití:
    python3 kalendar/scripts/extract-svoz-odpadu.py harmonogram.pdf 2026
"""
import collections
import datetime
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'kalendar' / 'svoz-odpadu.json'
DPI = 200

# středy sloupců (body PDF) v levé polovině; pravá je posunutá o POSUN
SLOUPCE_L = [107.3, 138.1, 167.9, 197.1, 226.2, 255.3, 284.5, 313.7, 342.9, 372.0]
POSUN_R = 354.4
DEN_SLOUPCE = [0, 0, 1, 1, 2, 3, 4, 4, 5, 6]   # po po út út st čt pá pá so ne
Y_MIN, Y_MAX = 70, 490                          # mezi záhlavím a legendou


def typ_podle_barvy(rgb):
    r, g, b = rgb
    if r > 235 and g > 235 and b > 235:
        return None                              # bílá = bez svozu
    if r > 200 and g < 60 and b < 60:
        return 'komunalni-jih'                   # červená
    if r > 230 and 150 < g < 215 and b < 60:
        return 'komunalni-sever'                 # oranžová
    if r > 230 and g > 230 and b < 100:
        return 'plast'                           # žlutá
    if r < 80 and g > 150 and b < 120:
        return 'bio'                             # zelená
    if r < 60 and g > 150 and b > 200:
        return 'papir'                           # modrá
    if 150 < r < 200 and 140 < g < 190 and b > 190:
        return 'komunalni-sidliste'              # levandulová
    raise SystemExit(f'Neznámá barva buňky {rgb} - zkontroluj legendu PDF')


def main():
    pdf, rok = Path(sys.argv[1]), int(sys.argv[2])
    with tempfile.TemporaryDirectory() as tmp:
        bbox = Path(tmp) / 'bbox.html'
        subprocess.run(['pdftotext', '-bbox', str(pdf), str(bbox)], check=True)
        subprocess.run(['pdftoppm', '-r', str(DPI), '-singlefile', str(pdf), f'{tmp}/p'], check=True)
        raw = (Path(tmp) / 'p.ppm').read_bytes()
        words = re.findall(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]+)<',
                           bbox.read_text(encoding='utf-8'))

    hlav = re.match(rb'P6\s+(\d+)\s+(\d+)\s+(\d+)\s', raw)
    sirka, off, s = int(hlav[1]), hlav.end(), DPI / 72

    def pixel(x, y):
        o = off + (int(y * s) * sirka + int(x * s)) * 3
        return tuple(raw[o:o + 3])

    vysledek = collections.defaultdict(set)
    for sloupce, mesic0 in ((SLOUPCE_L, 1), ([c + POSUN_R for c in SLOUPCE_L], 7)):
        cisla = []
        for x0, y0, x1, y1, t in words:
            x0, y0, x1, y1 = map(float, (x0, y0, x1, y1))
            if not t.isdigit() or not (Y_MIN < y0 < Y_MAX):
                continue
            cx = (x0 + x1) / 2
            j = min(range(10), key=lambda k: abs(sloupce[k] - cx))
            if abs(sloupce[j] - cx) > 10:
                continue                         # číslo týdne apod.
            cisla.append(((y0 + y1) / 2, sloupce[j], j, int(t)))
        cisla.sort()
        mesic, predchozi = mesic0, 0
        for yc, xc, j, den in cisla:
            if den < predchozi - 20:
                mesic += 1
            predchozi = den
            datum = datetime.date(rok, mesic, den)
            if datum.weekday() != DEN_SLOUPCE[j]:
                raise SystemExit(f'{datum} neodpovídá sloupci {j} - zkontroluj rozvržení PDF')
            barvy = collections.Counter(
                t for t in (typ_podle_barvy(pixel(xc + dx, yc + dy)) for dx in (-12, 12) for dy in (-4, 4)) if t)
            if barvy:
                vysledek[barvy.most_common(1)[0][0]].add(datum.isoformat())

    data = json.loads(OUT_JSON.read_text(encoding='utf-8'))
    for typ in data['types']:
        typ['dates'] = sorted(vysledek.get(typ['id'], ()))
        print(f'{typ["id"]}: {len(typ["dates"])} termínů')
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
