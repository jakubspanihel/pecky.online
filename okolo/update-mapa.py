#!/usr/bin/env python3
"""Vygeneruje okolo/mapa.json — obrysy obcí správního obvodu Peček pro SVG mapu.

Obrysy (hranice obcí) se stahují z OpenStreetMap přes Nominatim (relace
admin_level=8), promítnou se jednoduchým zeměpisným promítáním
(x = délka · cos φ0, y = šířka) do souřadnic SVG a uloží jako SVG cesty.
Seznam obcí a jejich OSM relací je v OBCE níže; názvy a ID shodné
s okolo/vesnice-okolo.json.

Spuštění z kořene repa:  python3 okolo/update-mapa.py
Potom:                   python3 scripts/build.py
"""
import json
import math
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'okolo' / 'mapa.json'
UA = 'pecky.online-map/1.0 (jakubspanihel@gmail.com)'

# id (slug jako v vesnice-okolo.json) -> OSM relace obce
OBCE = {
    'pečky': 441289,
    'cerhenice': 441309,
    'vrbčany': 441299,
    'dobřichov': 441302,
    'tatce': 441529,
    'chotutice': 441257,
    'plaňany': 441270,
    'radim': 441278,
    'ratenice': 441296,
}
WIDTH = 1000          # šířka viewBoxu
PAD = 14              # okraj kolem map
DEC = 1               # desetinná místa souřadnic ve výstupu


def stahni():
    ids = ','.join(f'R{r}' for r in OBCE.values())
    qs = urllib.parse.urlencode({
        'osm_ids': ids, 'format': 'jsonv2', 'polygon_geojson': 1,
        'polygon_threshold': 0.0002, 'accept-language': 'cs'})
    req = urllib.request.Request(
        'https://nominatim.openstreetmap.org/lookup?' + qs, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def kruhy(geom):
    """Vnější kruhy polygonu / multipolygonu (díry se pro obrysy nepoužívají)."""
    if geom['type'] == 'Polygon':
        return [geom['coordinates'][0]]
    if geom['type'] == 'MultiPolygon':
        return [p[0] for p in geom['coordinates']]
    raise ValueError(geom['type'])


def plocha(kruh):
    """Plocha a těžiště kruhu (shoelace) — pro popisek uprostřed obce."""
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(kruh, kruh[1:] + kruh[:1]):
        k = x0 * y1 - x1 * y0
        a += k
        cx += (x0 + x1) * k
        cy += (y0 + y1) * k
    a /= 2
    return abs(a), (cx / (6 * a), cy / (6 * a)) if a else kruh[0]


def main():
    data = stahni()
    podle_id = {int(e['osm_id']): e for e in data}
    chybi = [i for i in OBCE.values() if i not in podle_id]
    if chybi:
        sys.exit(f'Nominatim nevrátil relace: {chybi}')

    vsechny = [p for r in OBCE.values() for k in kruhy(podle_id[r]['geojson']) for p in k]
    lon0 = min(p[0] for p in vsechny)
    lat1 = max(p[1] for p in vsechny)
    kos = math.cos(math.radians(sum(p[1] for p in vsechny) / len(vsechny)))
    sx = lambda lon: (lon - lon0) * kos
    sy = lambda lat: lat1 - lat
    sirka = max(sx(p[0]) for p in vsechny)
    vyska = max(sy(p[1]) for p in vsechny)
    meritko = (WIDTH - 2 * PAD) / sirka

    def proj(p):
        return ((sx(p[0])) * meritko + PAD, (sy(p[1])) * meritko + PAD)

    obce = []
    for slug, rel in OBCE.items():
        e = podle_id[rel]
        cesty, nej = [], (0, None)
        for k in kruhy(e['geojson']):
            body = [proj(p) for p in k[:-1]]
            cesty.append('M' + 'L'.join(f'{x:.{DEC}f},{y:.{DEC}f}' for x, y in body) + 'Z')
            pl, tez = plocha(body)
            if pl > nej[0]:
                nej = (pl, tez)
        obce.append({
            'id': slug,
            'nazev': e['name'],
            'd': ''.join(cesty),
            'x': round(nej[1][0], 1), 'y': round(nej[1][1], 1),
        })
    OUT.write_text(json.dumps({
        'zdroj': 'OpenStreetMap (hranice obcí, admin_level=8), © přispěvatelé OpenStreetMap, ODbL',
        'stazeno': date.today().isoformat(),
        'sirka': WIDTH,
        'vyska': round(vyska * meritko + 2 * PAD),
        'obce': obce,
    }, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'Zapsáno {OUT.relative_to(ROOT)}: {len(obce)} obcí')


if __name__ == '__main__':
    main()
